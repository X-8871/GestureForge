param(
    [Parameter(Mandatory=$true)][string]$Root,
    [Parameter(Mandatory=$true)][string]$Boundary,
    [Parameter(Mandatory=$true)][string]$OwnerText
)

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;

public static class S3T03TclSelfTestCleanup {
    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation {
        public uint Attributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime, AccessTime, WriteTime;
        public uint VolumeSerialNumber, SizeHigh, SizeLow, LinkCount, IndexHigh, IndexLow;
    }
    [StructLayout(LayoutKind.Sequential)]
    private struct FileDispositionInfo { public byte DeleteFile; }
    [StructLayout(LayoutKind.Sequential)]
    private struct UnicodeString { public ushort Length, MaximumLength; public IntPtr Buffer; }
    [StructLayout(LayoutKind.Sequential)]
    private struct ObjectAttributes {
        public uint Length;
        public IntPtr RootDirectory, ObjectName;
        public uint Attributes;
        public IntPtr SecurityDescriptor, SecurityQualityOfService;
    }
    [StructLayout(LayoutKind.Sequential)]
    private struct IoStatusBlock { public IntPtr Status; public UIntPtr Information; }

    private const uint GenericRead = 0x80000000, DeleteAccess = 0x00010000, ReadAttributes = 0x00000080;
    private const uint GenericWrite = 0x40000000, SynchronizeAccess = 0x00100000;
    private const uint ShareRead = 1, ShareWrite = 2, OpenExisting = 3, CreateNew = 2;
    private const uint OpenReparsePoint = 0x00200000, BackupSemantics = 0x02000000;
    private const uint DirectoryFile = 0x00000001, NonDirectoryFile = 0x00000040, SynchronousIo = 0x00000020;
    private const uint AttributeDirectory = 0x10, AttributeReparsePoint = 0x400, FileTypeDisk = 1;

    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetFileInformationByHandle(SafeFileHandle handle, out ByHandleFileInformation info);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern uint GetFileType(SafeFileHandle handle);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle, StringBuilder path, uint length, uint flags);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetFileInformationByHandle(SafeFileHandle handle, int infoClass, ref FileDispositionInfo info, uint size);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetFilePointerEx(SafeFileHandle handle, long distance, out long position, uint method);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool ReadFile(SafeFileHandle handle, byte[] buffer, uint count, out uint read, IntPtr overlapped);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetEndOfFile(SafeFileHandle handle);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool WriteFile(SafeFileHandle handle, byte[] buffer, uint count, out uint written, IntPtr overlapped);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool CloseHandle(IntPtr handle);
    [DllImport("ntdll.dll")] private static extern int NtCreateFile(out IntPtr handle, uint access, ref ObjectAttributes attributes,
        out IoStatusBlock status, IntPtr allocationSize, uint fileAttributes, uint share, uint disposition,
        uint options, IntPtr extendedAttributes, uint extendedAttributesLength);

    private static string FullKey(string path) {
        return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
    }
    private static string FinalKey(SafeFileHandle handle) {
        StringBuilder value = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandleW(handle, value, (uint)value.Capacity, 0);
        if (length == 0 || length >= value.Capacity) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_FINAL_PATH_FAILED");
        string result = value.ToString();
        if (result.StartsWith("\\\\?\\UNC\\", StringComparison.OrdinalIgnoreCase)) result = "\\\\" + result.Substring(8);
        else if (result.StartsWith("\\\\?\\", StringComparison.OrdinalIgnoreCase)) result = result.Substring(4);
        return FullKey(result);
    }
    private static SafeFileHandle Open(string path, bool directory, bool requireReparse) {
        string full = Path.GetFullPath(path);
        uint flags = OpenReparsePoint | (directory ? BackupSemantics : 0U);
        SafeFileHandle handle = CreateFileW(full, GenericRead | DeleteAccess | ReadAttributes, ShareRead | ShareWrite,
            IntPtr.Zero, OpenExisting, flags, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_HANDLE_OPEN_FAILED");
        try {
            ByHandleFileInformation info;
            if (!GetFileInformationByHandle(handle, out info)) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_HANDLE_INFO_FAILED");
            bool actualDirectory = (info.Attributes & AttributeDirectory) != 0;
            bool actualReparse = (info.Attributes & AttributeReparsePoint) != 0;
            if (actualDirectory != directory) throw new IOException("SELFTEST_PATH_TYPE_MISMATCH");
            if (actualReparse != requireReparse) throw new IOException(actualReparse ? "SELFTEST_REPARSE_POINT_REJECTED" : "SELFTEST_EXPECTED_REPARSE_POINT_MISSING");
            if (GetFileType(handle) != FileTypeDisk) throw new IOException("SELFTEST_NOT_DISK_ENTRY");
            if (!directory && info.LinkCount != 1) throw new IOException("SELFTEST_FILE_LINK_COUNT_NOT_ONE");
            string actual = FinalKey(handle), expected = FullKey(full);
            if (!String.Equals(actual, expected, StringComparison.OrdinalIgnoreCase))
                throw new IOException("SELFTEST_FINAL_PATH_MISMATCH: " + actual + " != " + expected);
            return handle;
        } catch { handle.Dispose(); throw; }
    }
    public static SafeFileHandle OpenDirectory(string path) { return Open(path, true, false); }
    public static SafeFileHandle OpenRegularFile(string path) { return Open(path, false, false); }
    public static SafeFileHandle OpenReparseDirectory(string path) { return Open(path, true, true); }
    private static SafeFileHandle CreateChild(SafeFileHandle parent, string parentPath, string leaf, bool directory) {
        if (parent == null || parent.IsInvalid || parent.IsClosed) throw new IOException("SELFTEST_CREATE_PARENT_HANDLE_INVALID");
        if (String.IsNullOrWhiteSpace(leaf) || leaf == "." || leaf == ".." || leaf.IndexOfAny(new char[] { '\\', '/', ':' }) >= 0)
            throw new IOException("SELFTEST_CREATE_INVALID_CHILD_NAME");
        IntPtr name = Marshal.StringToHGlobalUni(leaf), nameStruct = IntPtr.Zero, raw = IntPtr.Zero;
        try {
            UnicodeString unicode = new UnicodeString();
            unicode.Length = checked((ushort)(leaf.Length * 2));
            unicode.MaximumLength = checked((ushort)(unicode.Length + 2));
            unicode.Buffer = name;
            nameStruct = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(UnicodeString)));
            Marshal.StructureToPtr(unicode, nameStruct, false);
            ObjectAttributes attributes = new ObjectAttributes();
            attributes.Length = (uint)Marshal.SizeOf(typeof(ObjectAttributes));
            attributes.RootDirectory = parent.DangerousGetHandle();
            attributes.ObjectName = nameStruct;
            attributes.Attributes = 0x40;
            IoStatusBlock io;
            uint options = (directory ? DirectoryFile : NonDirectoryFile) | OpenReparsePoint | SynchronousIo;
            int status = NtCreateFile(out raw, GenericRead | GenericWrite | DeleteAccess | ReadAttributes | SynchronizeAccess,
                ref attributes, out io, IntPtr.Zero, 0, ShareRead | ShareWrite, CreateNew, options, IntPtr.Zero, 0);
            if (status < 0) {
                if ((uint)status == 0xC0000035) throw new IOException("SELFTEST_CREATE_CHILD_COLLISION");
                throw new IOException("SELFTEST_NT_CREATE_CHILD_FAILED_0x" + ((uint)status).ToString("X8"));
            }
            SafeFileHandle created = new SafeFileHandle(raw, true);
            raw = IntPtr.Zero;
            try {
                string actualParent = FinalKey(parent);
                if (!String.Equals(actualParent, FullKey(parentPath), StringComparison.OrdinalIgnoreCase))
                    throw new IOException("SELFTEST_CREATE_PARENT_FINAL_PATH_MISMATCH");
                ValidateCreated(created, Path.Combine(actualParent, leaf), directory);
                return created;
            }
            catch { created.Dispose(); throw; }
        } finally {
            if (raw != IntPtr.Zero) CloseHandle(raw);
            if (nameStruct != IntPtr.Zero) Marshal.FreeHGlobal(nameStruct);
            Marshal.FreeHGlobal(name);
        }
    }
    private static void ValidateCreated(SafeFileHandle handle, string expectedPath, bool directory) {
        ByHandleFileInformation info;
        if (!GetFileInformationByHandle(handle, out info)) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_CREATED_CHILD_INFO_FAILED");
        if (((info.Attributes & AttributeDirectory) != 0) != directory || (info.Attributes & AttributeReparsePoint) != 0)
            throw new IOException("SELFTEST_CREATED_CHILD_TYPE_OR_REPARSE_MISMATCH");
        if (!directory && info.LinkCount != 1) throw new IOException("SELFTEST_CREATED_FILE_LINK_COUNT_NOT_ONE");
        if (GetFileType(handle) != FileTypeDisk || !String.Equals(FinalKey(handle), FullKey(expectedPath), StringComparison.OrdinalIgnoreCase))
            throw new IOException("SELFTEST_CREATED_CHILD_FINAL_PATH_MISMATCH");
    }
    public static SafeFileHandle CreateDirectoryChild(SafeFileHandle parent, string parentPath, string leaf) {
        return CreateChild(parent, parentPath, leaf, true);
    }
    public static SafeFileHandle CreateNewFileChild(SafeFileHandle parent, string parentPath, string leaf) {
        return CreateChild(parent, parentPath, leaf, false);
    }
    public static void WriteUtf8(SafeFileHandle handle, string value) {
        byte[] bytes = new UTF8Encoding(false, true).GetBytes(value);
        long position;
        if (!SetFilePointerEx(handle, 0, out position, 0) || !SetEndOfFile(handle))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_CREATE_NEW_WRITE_PREPARE_FAILED");
        uint written;
        if (!WriteFile(handle, bytes, (uint)bytes.Length, out written, IntPtr.Zero) || written != bytes.Length)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_CREATE_NEW_WRITE_FAILED");
    }
    private static byte[] ReadBytes(SafeFileHandle handle) {
        long position;
        if (!SetFilePointerEx(handle, 0, out position, 0)) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_READ_SEEK_FAILED");
        using (MemoryStream output = new MemoryStream()) {
            byte[] buffer = new byte[4096];
            while (true) {
                uint read;
                if (!ReadFile(handle, buffer, (uint)buffer.Length, out read, IntPtr.Zero))
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_READ_FAILED");
                if (read == 0) break;
                output.Write(buffer, 0, (int)read);
            }
            return output.ToArray();
        }
    }
    public static string ReadUtf8(SafeFileHandle handle) { return new UTF8Encoding(false, true).GetString(ReadBytes(handle)); }
    public static string Sha256Hex(SafeFileHandle handle) {
        using (SHA256 sha = SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(ReadBytes(handle))).Replace("-", "");
    }
    public static void MarkForDelete(SafeFileHandle handle) {
        if (handle == null || handle.IsInvalid || handle.IsClosed) throw new IOException("SELFTEST_DELETE_HANDLE_INVALID");
        FileDispositionInfo info = new FileDispositionInfo();
        info.DeleteFile = 1;
        if (!SetFileInformationByHandle(handle, 4, ref info, (uint)Marshal.SizeOf(typeof(FileDispositionInfo))))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_HANDLE_DELETE_FAILED");
    }
}
'@

function Remove-OwnedTestRoot {
    $rootHandle = $null
    $ownerHandle = $null
    $secureHandle = $null
    $reportsHandle = $null
    try {
        $rootHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
        $entries = @([IO.Directory]::GetFileSystemEntries($script:root))
        $names = @($entries | ForEach-Object { [IO.Path]::GetFileName($_) })
        if ($entries.Count -ne 3 -or -not ($names -ccontains '.s3_t03_selftest_owner') -or
            -not ($names -ccontains 'reports') -or -not ($names -ccontains 'secure_leaf.txt')) {
            throw 'SELFTEST_CLEANUP_UNEXPECTED_ROOT_CONTENTS'
        }
        $ownerHandle = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:ownerPath)
        if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($ownerHandle), $script:ownerText, [StringComparison]::Ordinal)) {
            throw 'SELFTEST_OWNER_MARKER_MISMATCH'
        }
        $secureHandle = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:secureLeafPath)
        if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($secureHandle), 'second', [StringComparison]::Ordinal)) {
            throw 'SELFTEST_SECURE_LEAF_CONTENT_MISMATCH'
        }
        $reportsHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:reportsPath)
        if (@([IO.Directory]::GetFileSystemEntries($script:reportsPath)).Count -ne 0) { throw 'SELFTEST_CLEANUP_REPORTS_NOT_EMPTY' }
        [S3T03TclSelfTestCleanup]::MarkForDelete($reportsHandle)
        $reportsHandle.Dispose()
        $reportsHandle = $null
        [S3T03TclSelfTestCleanup]::MarkForDelete($secureHandle)
        $secureHandle.Dispose()
        $secureHandle = $null
        [S3T03TclSelfTestCleanup]::MarkForDelete($ownerHandle)
        $ownerHandle.Dispose()
        $ownerHandle = $null
        if (@([IO.Directory]::GetFileSystemEntries($script:root)).Count -ne 0) { throw 'SELFTEST_CLEANUP_ROOT_NOT_EMPTY_AFTER_CHILD_DELETE' }
        [S3T03TclSelfTestCleanup]::MarkForDelete($rootHandle)
    } finally {
        if ($reportsHandle) { $reportsHandle.Dispose() }
        if ($secureHandle) { $secureHandle.Dispose() }
        if ($ownerHandle) { $ownerHandle.Dispose() }
        if ($rootHandle) { $rootHandle.Dispose() }
    }
    if ([IO.Directory]::Exists($script:root)) { throw 'SELFTEST_HANDLE_CLEANUP_FAILED' }
}

function Remove-ControlLeaves {
    $rootHandle = $null
    $ownerHandle = $null
    $secureHandle = $null
    $reportsHandle = $null
    $controlHandles = @()
    try {
        $rootHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
        $ownerHandle = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:ownerPath)
        if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($ownerHandle), $script:ownerText, [StringComparison]::Ordinal)) {
            throw 'SELFTEST_OWNER_MARKER_MISMATCH'
        }
        $secureHandle = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:secureLeafPath)
        if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($secureHandle), 'second', [StringComparison]::Ordinal)) {
            throw 'SELFTEST_SECURE_LEAF_CONTENT_MISMATCH'
        }
        $reportsHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:reportsPath)
        $expected = @('generated_clock_xdc.lease_request','generated_clock_xdc.lease_ack','generated_clock_xdc.lease_error')
        $entries = @([IO.Directory]::GetFileSystemEntries($script:reportsPath))
        $names = @($entries | ForEach-Object { [IO.Path]::GetFileName($_) })
        if ($entries.Count -ne $expected.Count) { throw 'SELFTEST_CONTROL_LEAF_COUNT_MISMATCH' }
        foreach ($leaf in $expected) {
            if (-not ($names -ccontains $leaf)) { throw ('SELFTEST_CONTROL_LEAF_MISSING:' + $leaf) }
            $handle = [S3T03TclSelfTestCleanup]::OpenRegularFile((Join-Path $script:reportsPath $leaf))
            if (-not (Test-ControlLeafContent $leaf ([S3T03TclSelfTestCleanup]::ReadUtf8($handle)))) { $handle.Dispose(); throw ('SELFTEST_CONTROL_LEAF_CONTENT_MISMATCH:' + $leaf) }
            $controlHandles += $handle
        }
        foreach ($handle in $controlHandles) {
            [S3T03TclSelfTestCleanup]::MarkForDelete($handle)
            $handle.Dispose()
        }
        $controlHandles = @()
    } finally {
        foreach ($handle in $controlHandles) { $handle.Dispose() }
        if ($reportsHandle) { $reportsHandle.Dispose() }
        if ($secureHandle) { $secureHandle.Dispose() }
        if ($ownerHandle) { $ownerHandle.Dispose() }
        if ($rootHandle) { $rootHandle.Dispose() }
    }
}

function Remove-OwnedSentinel {
    $rootHandle = $null
    $fileHandle = $null
    try {
        $rootHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:sentinelRoot)
        $entries = @([IO.Directory]::GetFileSystemEntries($script:sentinelRoot))
        if ($entries.Count -ne 1 -or [IO.Path]::GetFileName($entries[0]) -cne 'generated_clock_xdc.lease_request') { throw 'SELFTEST_SENTINEL_UNEXPECTED_CONTENTS' }
        $fileHandle = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:sentinelMarker)
        if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($fileHandle), $script:sentinelText, [StringComparison]::Ordinal)) {
            throw 'SELFTEST_SENTINEL_OWNER_MISMATCH'
        }
        [S3T03TclSelfTestCleanup]::MarkForDelete($fileHandle)
        $fileHandle.Dispose()
        $fileHandle = $null
        if (@([IO.Directory]::GetFileSystemEntries($script:sentinelRoot)).Count -ne 0) { throw 'SELFTEST_SENTINEL_ROOT_NOT_EMPTY' }
        [S3T03TclSelfTestCleanup]::MarkForDelete($rootHandle)
    } finally {
        if ($fileHandle) { $fileHandle.Dispose() }
        if ($rootHandle) { $rootHandle.Dispose() }
    }
    if ([IO.Directory]::Exists($script:sentinelRoot)) { throw 'SELFTEST_SENTINEL_CLEANUP_FAILED' }
}

function Test-ControlLeafContent {
    param([string]$Leaf, [string]$Text)
    if ($Text -ceq '') { return $true }
    if ($Leaf -ceq 'generated_clock_xdc.lease_request') {
        $relativePath = './tmp/' + $script:rootLeaf + '/project/s3_hdmi_only.gen/sources_1/bd/s3_hdmi_only/ip/s3_hdmi_only_rgb2dvi_0_0/rgb2dvi_0_0/src/rgb2dvi_clocks.xdc'
        $pathBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($relativePath))
        $expected = "S3_GENERATED_CLOCK_LEASE=1`nPATH_B64=$pathBase64`nSHA256=$('A' * 64)`n"
        return [string]::Equals($Text, $expected, [StringComparison]::Ordinal)
    }
    if ($Leaf -ceq 'generated_clock_xdc.lease_error') {
        $expected = "S3_GENERATED_CLOCK_LEASE=FAIL`nERROR=TCL_WAIT_TIMEOUT`n"
        return [string]::Equals($Text, $expected, [StringComparison]::Ordinal)
    }
    return $false
}

function Remove-EmptyReports {
    $rootHandle = $null
    $reportsHandle = $null
    try {
        $rootHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
        $reportsHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:reportsPath)
        if (@([IO.Directory]::GetFileSystemEntries($script:reportsPath)).Count -ne 0) { throw 'SELFTEST_CLEANUP_REPORTS_NOT_EMPTY' }
        [S3T03TclSelfTestCleanup]::MarkForDelete($reportsHandle)
        $reportsHandle.Dispose()
        $reportsHandle = $null
    } finally {
        if ($reportsHandle) { $reportsHandle.Dispose() }
        if ($rootHandle) { $rootHandle.Dispose() }
    }
}

$script:root = [IO.Path]::GetFullPath($Root)
$script:boundary = [IO.Path]::GetFullPath($Boundary).TrimEnd([char]92)
$script:rootParent = [IO.Path]::GetDirectoryName($script:root).TrimEnd([char]92)
$script:rootLeaf = [IO.Path]::GetFileName($script:root)
$script:ownerText = $OwnerText
$script:ownerPath = Join-Path $script:root '.s3_t03_selftest_owner'
$script:secureLeafPath = Join-Path $script:root 'secure_leaf.txt'
$script:reportsPath = Join-Path $script:root 'reports'
$script:tempParent = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd([char]92)
$script:sentinelRoot = Join-Path $script:tempParent ('s3_t03_tcl_sentinel_' + [Guid]::NewGuid().ToString('N'))
$script:sentinelMarker = Join-Path $script:sentinelRoot 'generated_clock_xdc.lease_request'
$script:sentinelText = 'S3_T03_EXTERNAL_SENTINEL_' + [Guid]::NewGuid().ToString('N')
$script:sentinelCreated = $false
$script:junctionCreated = $false
$script:sentinelRootHandle = $null
$script:sentinelFileHandle = $null
$script:primaryError = $null

if (-not [string]::Equals($script:rootParent, $script:boundary, [StringComparison]::OrdinalIgnoreCase) -or
    $script:rootLeaf -notmatch '^s3_t03_tcl_selftest_[0-9]+_[0-9]+$') { throw 'SELFTEST_CLEANUP_ROOT_NOT_OWNED' }
if ($script:tempParent.StartsWith($script:boundary + [char]92, [StringComparison]::OrdinalIgnoreCase)) { throw 'SELFTEST_SENTINEL_PARENT_NOT_EXTERNAL' }

try {
    $rootHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
    try {
        $initialEntries = @([IO.Directory]::GetFileSystemEntries($script:root))
        $initialNames = @($initialEntries | ForEach-Object { [IO.Path]::GetFileName($_) })
        if ($initialEntries.Count -ne 3 -or -not ($initialNames -ccontains 'reports') -or
            -not ($initialNames -ccontains '.s3_t03_selftest_owner') -or -not ($initialNames -ccontains 'secure_leaf.txt')) {
            throw 'SELFTEST_INITIAL_ROOT_CONTENTS_MISMATCH'
        }
        $initialOwner = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:ownerPath)
        try {
            if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($initialOwner), $script:ownerText, [StringComparison]::Ordinal)) {
                throw 'SELFTEST_INITIAL_OWNER_MARKER_MISMATCH'
            }
        } finally { $initialOwner.Dispose() }
        $initialSecureLeaf = [S3T03TclSelfTestCleanup]::OpenRegularFile($script:secureLeafPath)
        try {
            if (-not [string]::Equals([S3T03TclSelfTestCleanup]::ReadUtf8($initialSecureLeaf), 'second', [StringComparison]::Ordinal)) {
                throw 'SELFTEST_INITIAL_SECURE_LEAF_MISMATCH'
            }
        } finally { $initialSecureLeaf.Dispose() }
        $initialReports = [S3T03TclSelfTestCleanup]::OpenDirectory($script:reportsPath)
        try {
            $expectedLeaves = @('generated_clock_xdc.lease_request','generated_clock_xdc.lease_ack','generated_clock_xdc.lease_error')
            $initialLeaves = @([IO.Directory]::GetFileSystemEntries($script:reportsPath))
            $initialLeafNames = @($initialLeaves | ForEach-Object { [IO.Path]::GetFileName($_) })
            if ($initialLeaves.Count -ne $expectedLeaves.Count) { throw 'SELFTEST_INITIAL_REPORTS_COUNT_MISMATCH' }
            foreach ($leaf in $expectedLeaves) {
                if (-not ($initialLeafNames -ccontains $leaf)) { throw ('SELFTEST_INITIAL_REPORTS_LEAF_MISSING:' + $leaf) }
                $leafHandle = [S3T03TclSelfTestCleanup]::OpenRegularFile((Join-Path $script:reportsPath $leaf))
                try { if (-not (Test-ControlLeafContent $leaf ([S3T03TclSelfTestCleanup]::ReadUtf8($leafHandle)))) { throw ('SELFTEST_INITIAL_REPORTS_LEAF_CONTENT_MISMATCH:' + $leaf) } }
                finally { $leafHandle.Dispose() }
            }
        } finally { $initialReports.Dispose() }
    } finally { $rootHandle.Dispose() }

    $sentinelParentHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:tempParent)
    try {
        $sentinelLeaf = [IO.Path]::GetFileName($script:sentinelRoot)
        $script:sentinelRootHandle = [S3T03TclSelfTestCleanup]::CreateDirectoryChild($sentinelParentHandle, $script:tempParent, $sentinelLeaf)
        $script:sentinelCreated = $true
        $script:sentinelFileHandle = [S3T03TclSelfTestCleanup]::CreateNewFileChild($script:sentinelRootHandle, $script:sentinelRoot, 'generated_clock_xdc.lease_request')
        [S3T03TclSelfTestCleanup]::WriteUtf8($script:sentinelFileHandle, $script:sentinelText)
    } finally { $sentinelParentHandle.Dispose() }

    $sentinelHashBefore = [S3T03TclSelfTestCleanup]::Sha256Hex($script:sentinelFileHandle)
    Remove-ControlLeaves
    Remove-EmptyReports
    $junctionParentHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
    try {
        $namesBeforeJunction = @([IO.Directory]::GetFileSystemEntries($script:root) | ForEach-Object { [IO.Path]::GetFileName($_) })
        if ($namesBeforeJunction.Count -ne 2 -or -not ($namesBeforeJunction -ccontains '.s3_t03_selftest_owner') -or
            -not ($namesBeforeJunction -ccontains 'secure_leaf.txt')) { throw 'SELFTEST_JUNCTION_PARENT_CONTENTS_MISMATCH' }
        $null = New-Item -ItemType Junction -Path $script:reportsPath -Target $script:sentinelRoot -ErrorAction Stop
    } finally { $junctionParentHandle.Dispose() }
    $script:junctionCreated = $true
    $reparseControlLeavesRejected = $false
    try { Remove-ControlLeaves }
    catch { $reparseControlLeavesRejected = $_.Exception.Message -match 'SELFTEST_REPARSE_POINT_REJECTED' }
    if (-not $reparseControlLeavesRejected) { throw 'SELFTEST_CONTROL_CLEANUP_DID_NOT_REJECT_JUNCTION' }
    $reparseRejected = $false
    try { Remove-OwnedTestRoot }
    catch { $reparseRejected = $_.Exception.Message -match 'SELFTEST_REPARSE_POINT_REJECTED' }
    if (-not $reparseRejected) { throw 'SELFTEST_CLEANUP_DID_NOT_REJECT_JUNCTION' }
    if (-not [IO.File]::Exists($script:ownerPath)) { throw 'SELFTEST_CLEANUP_PARTIALLY_DELETED_OWNER' }
    $sentinelHashAfterRejectedCleanup = [S3T03TclSelfTestCleanup]::Sha256Hex($script:sentinelFileHandle)
    if ($sentinelHashAfterRejectedCleanup -cne $sentinelHashBefore) { throw 'SELFTEST_SENTINEL_CHANGED_AFTER_REJECTED_CLEANUP' }
    Write-Output ('SELFTEST_EXTERNAL_SENTINEL=UNCHANGED;SHA256=' + $sentinelHashAfterRejectedCleanup)

    $junctionHandle = [S3T03TclSelfTestCleanup]::OpenReparseDirectory($script:reportsPath)
    try { [S3T03TclSelfTestCleanup]::MarkForDelete($junctionHandle) }
    finally { $junctionHandle.Dispose() }
    $script:junctionCreated = $false
    if ([IO.Directory]::Exists($script:reportsPath)) { throw 'SELFTEST_JUNCTION_HANDLE_UNLINK_FAILED' }
    if ([S3T03TclSelfTestCleanup]::Sha256Hex($script:sentinelFileHandle) -cne $sentinelHashBefore) { throw 'SELFTEST_SENTINEL_CHANGED_AFTER_JUNCTION_UNLINK' }
    $rootForReportsHandle = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
    try {
        $newReportsHandle = [S3T03TclSelfTestCleanup]::CreateDirectoryChild($rootForReportsHandle, $script:root, 'reports')
        $newReportsHandle.Dispose()
    } finally { $rootForReportsHandle.Dispose() }
    Remove-OwnedTestRoot
    if (Test-Path -LiteralPath $script:root) { throw 'SELFTEST_CLEANUP_FAILED' }

    [S3T03TclSelfTestCleanup]::MarkForDelete($script:sentinelFileHandle)
    $script:sentinelFileHandle.Dispose()
    $script:sentinelFileHandle = $null
    if (@([IO.Directory]::GetFileSystemEntries($script:sentinelRoot)).Count -ne 0) { throw 'SELFTEST_SENTINEL_NOT_EMPTY_AFTER_FILE_DELETE' }
    [S3T03TclSelfTestCleanup]::MarkForDelete($script:sentinelRootHandle)
    $script:sentinelRootHandle.Dispose()
    $script:sentinelRootHandle = $null
    $script:sentinelCreated = $false
    if ([IO.Directory]::Exists($script:sentinelRoot)) { throw 'SELFTEST_SENTINEL_CLEANUP_FAILED' }
    Write-Output 'SELFTEST_TMP_CLEANUP=PASS'
} catch {
    $script:primaryError = $_.Exception.ToString()
} finally {
    if ($script:junctionCreated) {
        try {
            $knownLink = [S3T03TclSelfTestCleanup]::OpenReparseDirectory($script:reportsPath)
            try { [S3T03TclSelfTestCleanup]::MarkForDelete($knownLink) } finally { $knownLink.Dispose() }
            $script:junctionCreated = $false
        } catch { if (-not $script:primaryError) { $script:primaryError = $_.Exception.ToString() } }
    }
    if ($script:sentinelFileHandle) { $script:sentinelFileHandle.Dispose(); $script:sentinelFileHandle = $null }
    if ($script:sentinelRootHandle) { $script:sentinelRootHandle.Dispose(); $script:sentinelRootHandle = $null }
    if ($script:sentinelCreated -and [IO.Directory]::Exists($script:sentinelRoot)) {
        try { Remove-OwnedSentinel; $script:sentinelCreated = $false }
        catch { if (-not $script:primaryError) { $script:primaryError = $_.Exception.ToString() } }
    }
    if ([IO.Directory]::Exists($script:root)) {
        try {
            $rootCheck = [S3T03TclSelfTestCleanup]::OpenDirectory($script:root)
            try {
                $namesAtCleanup = @([IO.Directory]::GetFileSystemEntries($script:root) | ForEach-Object { [IO.Path]::GetFileName($_) })
                if (-not ($namesAtCleanup -ccontains 'reports')) {
                    $newReports = [S3T03TclSelfTestCleanup]::CreateDirectoryChild($rootCheck, $script:root, 'reports')
                    $newReports.Dispose()
                }
            } finally { $rootCheck.Dispose() }
            Remove-OwnedTestRoot
        } catch { if (-not $script:primaryError) { $script:primaryError = $_.Exception.ToString() } }
    }
}

if ($script:primaryError) { throw $script:primaryError }
if ($script:sentinelCreated -or $script:junctionCreated -or [IO.Directory]::Exists($script:root) -or [IO.Directory]::Exists($script:sentinelRoot)) {
    throw 'SELFTEST_CLEANUP_ARTIFACT_REMAINS'
}
