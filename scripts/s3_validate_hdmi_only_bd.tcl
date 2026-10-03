# 在全新隔离目录验证 AX7020 官方 HDMI-only BD；不调用厂商自动构建脚本。
# 用法：vivado -mode batch -source s3_validate_hdmi_only_bd.tcl -tclargs <厂商根目录> <tmp 下的新唯一运行目录> ?native|azynq_metadata? ?guard|race_test|lock_test|subpath_reparse_test|bd|hdl?

proc s3_launch_secure_guardian {vendor_root source_root output_dir mode phase} {
    set token "[pid]_[clock clicks]"
    set ready_event [format {Local\S3Stage3PathGuard_%s_Ready} $token]
    set status_map [format {Local\S3Stage3PathGuard_%s_Status} $token]
    set ::env(S3_GUARD_VENDOR_ROOT) $vendor_root
    set ::env(S3_GUARD_SOURCE_ROOT) $source_root
    set ::env(S3_GUARD_REPO_ROOT) $::s3_repo_root
    set ::env(S3_GUARD_SCRIPT_PATH) $::s3_script_path
    set ::env(S3_GUARD_OUTPUT_DIR) $output_dir
    set ::env(S3_GUARD_MODE) $mode
    set ::env(S3_GUARD_PHASE) $phase
    set ::env(S3_GUARD_OWNER_PID) [pid]
    set ::env(S3_GUARD_READY_EVENT) $ready_event
    set ::env(S3_GUARD_STATUS_MAP) $status_map
    set native_code [string map [list @L@ \{ @R@ \}] {
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using Microsoft.Win32.SafeHandles;
public static class S3PathGuardR3
@L@
    private const uint Delete = 0x00010000, ReadAttributes = 0x80, WriteData = 0x02;
    private const uint GenericRead = 0x80000000, GenericWrite = 0x40000000, Synchronize = 0x00100000;
    private const uint ShareRead = 1, ShareWrite = 2, OpenExisting = 3, BackupSemantics = 0x02000000, OpenReparse = 0x00200000;
    private const uint DirectoryFile = 1, NonDirectoryFile = 0x40, SyncIo = 0x20, FileOpen = 1, FileCreate = 2;
    private const uint AttrDirectory = 0x10, AttrReparse = 0x400, MountPointTag = 0xA0000003, FsctlSetReparsePoint = 0x000900A4;
    private const int FileAttributeTagInfoClass = 9;
    private struct AttributeTagInfo @L@ public uint Attributes; public uint Tag; @R@
    private struct UnicodeString @L@ public ushort Length, MaximumLength; public IntPtr Buffer; @R@
    private struct ObjectAttributes @L@ public uint Length; public IntPtr RootDirectory, ObjectName; public uint Attributes; public IntPtr SecurityDescriptor, SecurityQualityOfService; @R@
    private struct IoStatusBlock @L@ public IntPtr Status; public UIntPtr Information; @R@
    private static readonly List<SafeFileHandle> DirectHandles = new List<SafeFileHandle>();
    private static readonly List<SafeFileHandle> SourceHandles = new List<SafeFileHandle>();
    private static readonly List<FileStream> DataHandles = new List<FileStream>();
    private static readonly Dictionary<string, SafeFileHandle> Directories = new Dictionary<string, SafeFileHandle>(StringComparer.OrdinalIgnoreCase);
    private static string RepoFinal, ScriptsFinal, TmpFinal, VendorFinal, SourceFinal, OutputFinal, OutputLeaf;

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(string path, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle, StringBuilder path, uint size, uint flags);
    [DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
    private static extern bool GetFileInformationByHandleEx(SafeFileHandle handle, int infoClass, out AttributeTagInfo info, uint size);
    [DllImport("ntdll.dll")]
    private static extern int NtCreateFile(out IntPtr handle, uint access, ref ObjectAttributes attributes, out IoStatusBlock status, IntPtr allocationSize, uint fileAttributes, uint share, uint disposition, uint options, IntPtr ea, uint eaLength);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    private static extern bool CreateDirectoryW(string path, IntPtr security);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, ExactSpelling = true, SetLastError = true)]
    private static extern bool RemoveDirectoryW(string path);
    [DllImport("kernel32.dll", ExactSpelling = true, SetLastError = true)]
    private static extern bool DeviceIoControl(SafeFileHandle handle, uint code, byte[] input, uint inputSize, IntPtr output, uint outputSize, out uint returned, IntPtr overlapped);
    [DllImport("kernel32.dll", ExactSpelling = true)]
    private static extern bool CloseHandle(IntPtr handle);

    private static string Normalize(string path)
    @L@
        path = path.Replace('/', '\\');
        if (path.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase)) path = @"\\" + path.Substring(8);
        else if (path.StartsWith(@"\\?\", StringComparison.OrdinalIgnoreCase)) path = path.Substring(4);
        string root = Path.GetPathRoot(path);
        if (root == null) throw new IOException("PATH_HAS_NO_ROOT");
        if (path.Length > root.Length) path = path.TrimEnd('\\');
        return path;
    @R@
    private static string FinalPath(SafeFileHandle handle)
    @L@
        StringBuilder buffer = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
        if (length == 0 || length >= buffer.Capacity) throw new Win32Exception(Marshal.GetLastWin32Error());
        return Normalize(buffer.ToString());
    @R@
    private static AttributeTagInfo Info(SafeFileHandle handle)
    @L@
        AttributeTagInfo info;
        if (!GetFileInformationByHandleEx(handle, FileAttributeTagInfoClass, out info, (uint)Marshal.SizeOf(typeof(AttributeTagInfo)))) throw new Win32Exception(Marshal.GetLastWin32Error());
        return info;
    @R@
    private static bool Under(string parent, string child)
    @L@
        parent = Normalize(parent); child = Normalize(child);
        if (String.Equals(parent, child, StringComparison.OrdinalIgnoreCase)) return true;
        string prefix = parent.EndsWith("\\", StringComparison.Ordinal) ? parent : parent + "\\";
        return child.StartsWith(prefix, StringComparison.OrdinalIgnoreCase);
    @R@
    private static string Join(string parent, string leaf)
    @L@
        if (String.IsNullOrWhiteSpace(leaf) || leaf == "." || leaf == ".." || leaf.IndexOfAny(new char[] @L@'\\', '/', ':'@R@) >= 0) throw new IOException("INVALID_SINGLE_PATH_COMPONENT");
        return Normalize(parent.TrimEnd('\\') + "\\" + leaf);
    @R@
    private static void RegisterDirectory(SafeFileHandle handle, string parent)
    @L@
        AttributeTagInfo info = Info(handle);
        if ((info.Attributes & AttrDirectory) == 0) throw new IOException("PATH_COMPONENT_NOT_DIRECTORY");
        if ((info.Attributes & AttrReparse) != 0) throw new IOException("REPARSE_POINT_COMPONENT_REJECTED");
        string finalPath = FinalPath(handle);
        if (parent != null && !Under(parent, finalPath)) throw new IOException("DIRECTORY_FINAL_PATH_ESCAPED_PARENT");
        DirectHandles.Add(handle);
        if (!Directories.ContainsKey(finalPath)) Directories.Add(finalPath, handle);
    @R@
    private static string AcquireAnchor(string path)
    @L@
        string full = Normalize(Path.GetFullPath(path));
        SafeFileHandle currentHandle = CreateFileW(full, ReadAttributes | Synchronize, ShareRead | ShareWrite, IntPtr.Zero, OpenExisting, BackupSemantics | OpenReparse, IntPtr.Zero);
        if (currentHandle.IsInvalid) {
            int error = Marshal.GetLastWin32Error();
            throw new IOException("PATH_ANCHOR_OPEN_FAILED_" + error + ":" + full, new Win32Exception(error));
        }
        RegisterDirectory(currentHandle, null);
        string finalPath = FinalPath(currentHandle);
        if (!String.Equals(full, finalPath, StringComparison.OrdinalIgnoreCase)) throw new IOException("PATH_ANCHOR_ALIAS_OR_REPARSE_REJECTED");
        return finalPath;
    @R@
    private static string AcquireSubtree(string anchor, string path)
    @L@
        anchor = Normalize(anchor);
        string full = Normalize(Path.GetFullPath(path));
        if (!Under(anchor, full)) throw new IOException("PATH_SUBTREE_ESCAPED_ANCHOR");
        string current = anchor;
        string tail = full.Length == anchor.Length ? "" : full.Substring(anchor.Length).Trim('\\');
        if (tail.Length == 0) return current;
        string[] parts = tail.Split('\\');
        for (int index = 0; index < parts.Length; index++) {
            string part = parts[index];
            if (part.Length == 0 || part == "." || part == "..") throw new IOException("INVALID_PATH_COMPONENT");
            string candidate = Join(current, part);
            SafeFileHandle next = CreateFileW(candidate, ReadAttributes | Synchronize, ShareRead | ShareWrite, IntPtr.Zero, OpenExisting, BackupSemantics | OpenReparse, IntPtr.Zero);
            if (next.IsInvalid) {
                int error = Marshal.GetLastWin32Error();
                throw new IOException("PATH_COMPONENT_OPEN_FAILED_" + error + ":" + candidate, new Win32Exception(error));
            }
            bool retained = false;
            try {
                RegisterDirectory(next, current);
                current = FinalPath(next);
                retained = true;
            } finally { if (!retained) next.Dispose(); }
        }
        return current;
    @R@
    private static SafeFileHandle GetDirectory(string path)
    @L@
        SafeFileHandle handle;
        if (!Directories.TryGetValue(Normalize(path), out handle) || handle.IsClosed || handle.IsInvalid) throw new IOException("DIRECTORY_HANDLE_NOT_HELD");
        return handle;
    @R@
    private static SafeFileHandle NtOpen(SafeFileHandle parent, string leaf, uint disposition, uint options, uint access)
    @L@
        IntPtr name = Marshal.StringToHGlobalUni(leaf), nameStruct = IntPtr.Zero, raw = IntPtr.Zero;
        try {
            UnicodeString unicode = new UnicodeString();
            unicode.Length = checked((ushort)(leaf.Length * 2)); unicode.MaximumLength = checked((ushort)(unicode.Length + 2)); unicode.Buffer = name;
            nameStruct = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(UnicodeString)));
            Marshal.StructureToPtr(unicode, nameStruct, false);
            ObjectAttributes attributes = new ObjectAttributes();
            attributes.Length = (uint)Marshal.SizeOf(typeof(ObjectAttributes)); attributes.RootDirectory = parent.DangerousGetHandle();
            attributes.ObjectName = nameStruct; attributes.Attributes = 0x40;
            IoStatusBlock io;
            int status = NtCreateFile(out raw, access, ref attributes, out io, IntPtr.Zero, 0, ShareRead | ShareWrite, disposition, options | OpenReparse | SyncIo, IntPtr.Zero, 0);
            if (status < 0) {
                if ((uint)status == 0xC0000035) throw new IOException("NT_OBJECT_NAME_COLLISION");
                if ((uint)status == 0xC0000034 || (uint)status == 0xC000003A) throw new FileNotFoundException("NT_OBJECT_NOT_FOUND");
                throw new IOException("NT_CREATE_FILE_FAILED_0x" + ((uint)status).ToString("X8"));
            }
            SafeFileHandle result = new SafeFileHandle(raw, true); raw = IntPtr.Zero; return result;
        } finally {
            if (raw != IntPtr.Zero) CloseHandle(raw);
            if (nameStruct != IntPtr.Zero) Marshal.FreeHGlobal(nameStruct);
            Marshal.FreeHGlobal(name);
        }
    @R@
    private static string CreateDirectoryChild(string parent, string leaf)
    @L@
        SafeFileHandle handle = NtOpen(GetDirectory(parent), leaf, FileCreate, DirectoryFile, Delete | ReadAttributes | Synchronize);
        bool retained = false;
        try {
        RegisterDirectory(handle, parent);
            string finalPath = FinalPath(handle);
            if (!String.Equals(finalPath, Join(parent, leaf), StringComparison.OrdinalIgnoreCase)) throw new IOException("CREATED_DIRECTORY_PHYSICAL_PATH_MISMATCH");
            retained = true; return finalPath;
        } finally { if (!retained) handle.Dispose(); }
    @R@
    private static string EnsureDirectoryChild(string parent, string leaf)
    @L@
        string expected = Join(parent, leaf);
        if (Directories.ContainsKey(expected)) return expected;
        return CreateDirectoryChild(parent, leaf);
    @R@
    private static bool ChildExists(SafeFileHandle parent, string leaf)
    @L@
        SafeFileHandle handle = null;
        try {
            handle = NtOpen(parent, leaf, FileOpen, 0, ReadAttributes | Synchronize);
            return true;
        } catch (FileNotFoundException) { return false; }
        finally { if (handle != null) handle.Dispose(); }
    @R@
    private static void HoldRegularScript(string path, string expectedParent)
    @L@
        string full = Path.GetFullPath(path);
        if (!String.Equals(Normalize(Path.GetDirectoryName(full)), expectedParent, StringComparison.OrdinalIgnoreCase)) throw new IOException("SCRIPT_PATH_PARENT_MISMATCH");
        SafeFileHandle handle = CreateFileW(full, GenericRead | ReadAttributes, ShareRead, IntPtr.Zero, OpenExisting, OpenReparse, IntPtr.Zero);
        if (handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
        AttributeTagInfo info = Info(handle);
        if ((info.Attributes & (AttrReparse | AttrDirectory)) != 0 || !String.Equals(FinalPath(handle), full, StringComparison.OrdinalIgnoreCase)) {
            handle.Dispose(); throw new IOException("SCRIPT_FILE_REPARSE_OR_ALIAS_REJECTED");
        }
        SourceHandles.Add(handle);
    @R@
    private static SafeFileHandle OpenSourceFile(string fullPath)
    @L@
        AcquireSubtree(VendorFinal, Path.GetDirectoryName(Path.GetFullPath(fullPath)));
        SafeFileHandle file = CreateFileW(Path.GetFullPath(fullPath), GenericRead | ReadAttributes, ShareRead, IntPtr.Zero, OpenExisting, OpenReparse, IntPtr.Zero);
        if (file.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
        AttributeTagInfo info = Info(file);
        if ((info.Attributes & (AttrReparse | AttrDirectory)) != 0) { file.Dispose(); throw new IOException("SOURCE_FILE_REPARSE_OR_DIRECTORY_REJECTED"); }
        SourceHandles.Add(file); return file;
    @R@
    public static void HoldSourceFile(string sourceRoot, string relativePath)
    @L@
        string[] parts = relativePath.Replace('\\', '/').Split('/');
        foreach (string part in parts) if (part.Length == 0 || part == "." || part == ".." || part.IndexOfAny(new char[] @L@':', '\\'@R@) >= 0) throw new IOException("INVALID_SOURCE_MANIFEST_PATH");
        string path = sourceRoot; foreach (string part in parts) path = Path.Combine(path, part);
        OpenSourceFile(path);
    @R@
    private static void CopyFile(string sourcePath, string destinationParent, string leaf)
    @L@
        SafeFileHandle source = OpenSourceFile(sourcePath);
        SafeFileHandle destination = NtOpen(GetDirectory(destinationParent), leaf, FileCreate, NonDirectoryFile, GenericWrite | ReadAttributes | WriteData | Synchronize);
        FileStream input = new FileStream(source, FileAccess.Read);
        FileStream output = new FileStream(destination, FileAccess.Write);
        input.CopyTo(output); output.Flush(true);
        DataHandles.Add(input); DataHandles.Add(output);
    @R@
    private static int Count(string value, string expression) @L@ return System.Text.RegularExpressions.Regex.Matches(value, expression).Count; @R@
    private static void RewriteMetadata(string parent, string leaf, string component)
    @L@
        SafeFileHandle handle = NtOpen(GetDirectory(parent), leaf, FileOpen, NonDirectoryFile, GenericRead | GenericWrite | ReadAttributes | Synchronize);
        if ((Info(handle).Attributes & (AttrReparse | AttrDirectory)) != 0) { handle.Dispose(); throw new IOException("METADATA_FILE_REPARSE_REJECTED"); }
        FileStream stream = new FileStream(handle, FileAccess.ReadWrite);
        using (StreamReader reader = new StreamReader(stream, new UTF8Encoding(false), true, 4096, true)) {
            string xml = reader.ReadToEnd();
            if (Count(xml, "<xilinx:supportedFamilies>") != 1 || Count(xml, "</xilinx:supportedFamilies>") != 1) throw new IOException("INVALID_SUPPORTED_FAMILIES_BLOCK_" + component);
            if (Count(xml, "<xilinx:family[^>]*>zynq</xilinx:family>") != 1 || Count(xml, "<xilinx:family[^>]*>azynq</xilinx:family>") != 0) throw new IOException("UNEXPECTED_FAMILY_METADATA_" + component);
            xml = xml.Replace("</xilinx:supportedFamilies>", "      <xilinx:family xilinx:lifeCycle=\"Pre-Production\">azynq</xilinx:family>\n</xilinx:supportedFamilies>");
            byte[] bytes = new UTF8Encoding(false).GetBytes(xml);
            stream.Position = 0; stream.SetLength(0); stream.Write(bytes, 0, bytes.Length); stream.Flush(true);
        }
        DataHandles.Add(stream);
    @R@
    private static void SetJunction(string path, string target)
    @L@
        if (OutputFinal == null || !Under(OutputFinal, path) || !Under(OutputFinal, target)) throw new IOException("JUNCTION_FIXTURE_MUST_REMAIN_INSIDE_RUN_ROOT");
        if (!CreateDirectoryW(path, IntPtr.Zero)) throw new Win32Exception(Marshal.GetLastWin32Error());
        SafeFileHandle handle = null;
        try {
            handle = CreateFileW(path, GenericWrite | ReadAttributes, ShareRead | ShareWrite, IntPtr.Zero, OpenExisting, BackupSemantics | OpenReparse, IntPtr.Zero);
            if (handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
            string normalized = Normalize(target), substitute = "\\??\\" + normalized;
            byte[] sub = Encoding.Unicode.GetBytes(substitute), print = Encoding.Unicode.GetBytes(normalized);
            int pathBytes = sub.Length + 2 + print.Length + 2; byte[] data = new byte[16 + pathBytes];
            Buffer.BlockCopy(BitConverter.GetBytes(MountPointTag), 0, data, 0, 4);
            Buffer.BlockCopy(BitConverter.GetBytes((ushort)(8 + pathBytes)), 0, data, 4, 2);
            Buffer.BlockCopy(BitConverter.GetBytes((ushort)0), 0, data, 6, 2);
            Buffer.BlockCopy(BitConverter.GetBytes((ushort)0), 0, data, 8, 2);
            Buffer.BlockCopy(BitConverter.GetBytes((ushort)sub.Length), 0, data, 10, 2);
            Buffer.BlockCopy(BitConverter.GetBytes((ushort)(sub.Length + 2)), 0, data, 12, 2);
            Buffer.BlockCopy(BitConverter.GetBytes((ushort)print.Length), 0, data, 14, 2);
            Buffer.BlockCopy(sub, 0, data, 16, sub.Length);
            Buffer.BlockCopy(print, 0, data, 18 + sub.Length, print.Length);
            uint returned;
            if (!DeviceIoControl(handle, FsctlSetReparsePoint, data, (uint)data.Length, IntPtr.Zero, 0, out returned, IntPtr.Zero)) throw new Win32Exception(Marshal.GetLastWin32Error());
        } catch {
            if (handle != null && !handle.IsInvalid) handle.Dispose();
            RemoveDirectoryW(path);
            throw;
        } finally { if (handle != null && !handle.IsInvalid) handle.Dispose(); }
    @R@
    private static bool ChildIsReparse(string parent, string leaf)
    @L@
        SafeFileHandle handle = NtOpen(GetDirectory(parent), leaf, FileOpen, DirectoryFile, ReadAttributes | Synchronize);
        try { return (Info(handle).Attributes & AttrReparse) != 0; } finally { handle.Dispose(); }
    @R@
    private static void TestJunction(string parent, string leaf, string target)
    @L@
        string path = Join(parent, leaf); bool created = false;
        try {
            SetJunction(path, target); created = true;
            if (!ChildIsReparse(parent, leaf)) throw new IOException("REPARSE_TEST_NOT_DETECTED_" + leaf);
            bool rejected = false;
            try { CreateDirectoryChild(parent, leaf); }
            catch (IOException error) {
                if (error.Message != "NT_OBJECT_NAME_COLLISION") throw;
                rejected = true;
            }
            if (!rejected) throw new IOException("EXCLUSIVE_CREATE_ACCEPTED_REPARSE_" + leaf);
        } finally {
            if (created && !RemoveDirectoryW(path)) throw new Win32Exception(Marshal.GetLastWin32Error());
        }
    @R@
    private static void TestParentJunction(string parent, string leaf, string target, string childLeaf)
    @L@
        string path = Join(parent, leaf); bool created = false;
        try {
            SetJunction(path, target); created = true;
            bool rejected = false;
            try { AcquireSubtree(OutputFinal, Join(path, childLeaf)); }
            catch (IOException error) {
                if (error.Message != "REPARSE_POINT_COMPONENT_REJECTED") throw;
                rejected = true;
            }
            if (!rejected) throw new IOException("PARENT_REPARSE_COMPONENT_NOT_REJECTED");
        } finally {
            if (created && !RemoveDirectoryW(path)) throw new Win32Exception(Marshal.GetLastWin32Error());
        }
    @R@
    private static string TestLockedRename(string source, string destination)
    @L@
        if (!Under(OutputFinal, source) || !Under(OutputFinal, destination)) throw new IOException("LOCK_TEST_PATH_ESCAPES_RUN_ROOT");
        if (!Directory.Exists(source) || File.Exists(source)) throw new IOException("LOCK_TEST_SOURCE_MISSING");
        if (Directory.Exists(destination) || File.Exists(destination)) throw new IOException("LOCK_TEST_DESTINATION_ALREADY_EXISTS");
        bool moved = false;
        try {
            try { Directory.Move(source, destination); moved = true; }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
            if (moved) throw new IOException("SECURE_DIRECTORY_HANDLE_GUARD_ALLOWED_RENAME");
            if (!Directory.Exists(source) || Directory.Exists(destination)) throw new IOException("LOCK_TEST_PATH_STATE_CHANGED");
            return "DELETE_ACCESS_NO_DELETE_SHARE_RENAME_TEST=PASS";
        } finally {
            if (moved && Directory.Exists(destination) && !Directory.Exists(source)) Directory.Move(destination, source);
        }
    @R@
    public static string Begin(string repo, string script, string vendor, string source, string output, string phase)
    @L@
        RepoFinal = AcquireAnchor(repo);
        ScriptsFinal = AcquireSubtree(RepoFinal, Join(RepoFinal, "scripts"));
        if (!String.Equals(ScriptsFinal, Join(RepoFinal, "scripts"), StringComparison.OrdinalIgnoreCase)) throw new IOException("REPO_SCRIPTS_ALIAS_REJECTED");
        HoldRegularScript(script, ScriptsFinal);
        TmpFinal = AcquireSubtree(RepoFinal, Join(RepoFinal, "tmp"));
        if (!String.Equals(TmpFinal, Join(RepoFinal, "tmp"), StringComparison.OrdinalIgnoreCase)) throw new IOException("REPO_TMP_ALIAS_REJECTED");
        VendorFinal = AcquireSubtree(TmpFinal, vendor); SourceFinal = AcquireSubtree(VendorFinal, source);
        if (!Under(VendorFinal, SourceFinal)) throw new IOException("VENDOR_SOURCE_ESCAPES_VENDOR_ROOT");
        string full = Path.GetFullPath(output); OutputLeaf = Path.GetFileName(full);
        if (String.IsNullOrWhiteSpace(OutputLeaf) || OutputLeaf == "." || OutputLeaf == "..") throw new IOException("OUTPUT_PATH_MUST_NAME_NEW_DIRECTORY");
        string inputParent = Normalize(Path.GetDirectoryName(full));
        if (!String.Equals(inputParent, TmpFinal, StringComparison.OrdinalIgnoreCase)) throw new IOException("OUTPUT_MUST_BE_DIRECT_CHILD_OF_CANONICAL_REPO_TMP");
        string candidate = Join(TmpFinal, OutputLeaf);
        bool overlaps = Under(VendorFinal, candidate) || Under(candidate, VendorFinal);
        if (overlaps) throw new IOException("OUTPUT_AND_VENDOR_PATHS_MUST_BE_DISJOINT");
        if (ChildExists(GetDirectory(TmpFinal), OutputLeaf)) throw new IOException("OUTPUT_PATH_ALREADY_EXISTS");
        if (phase == "guard") return "RESULT=PASS_PATH_PREFLIGHT\nREPO=" + RepoFinal + "\nTMP=" + TmpFinal + "\nVENDOR=" + VendorFinal + "\nSOURCE=" + SourceFinal + "\nOUTPUT=" + candidate;
        return "RESULT=PATHS_LOCKED";
    @R@
    public static string Prepare(string mode, string phase, string sourceRoot, string[] manifest)
    @L@
        if (phase == "guard") return "RESULT=PASS_PATH_PREFLIGHT\nREPO=" + RepoFinal + "\nTMP=" + TmpFinal + "\nOUTPUT=" + Join(TmpFinal, OutputLeaf);
        if (phase == "race_test") {
            string target = Join(TmpFinal, OutputLeaf);
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "powershell.exe";
            string targetEncoded = Convert.ToBase64String(Encoding.Unicode.GetBytes(target));
            string script = "$target = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('" + targetEncoded + "')); [IO.Directory]::CreateDirectory($target) | Out-Null";
            start.Arguments = "-NoProfile -NonInteractive -EncodedCommand " + Convert.ToBase64String(Encoding.Unicode.GetBytes(script));
            start.UseShellExecute = false; start.CreateNoWindow = true;
            using (Process process = Process.Start(start)) { process.WaitForExit(); if (process.ExitCode != 0) throw new IOException("RACE_FIXTURE_CREATION_FAILED"); }
            bool rejected = false;
            try { CreateDirectoryChild(TmpFinal, OutputLeaf); }
            catch (IOException error) {
                if (error.Message != "NT_OBJECT_NAME_COLLISION") throw;
                rejected = true;
            }
            if (!rejected) throw new IOException("EXCLUSIVE_OUTPUT_CREATE_ACCEPTED_EXISTING_TARGET");
            if (Directory.GetFileSystemEntries(target).Length != 0) throw new IOException("EXISTING_OR_RACE_OUTPUT_NOT_EMPTY");
            if (!RemoveDirectoryW(target)) throw new Win32Exception(Marshal.GetLastWin32Error());
            return "RESULT=PASS_CONCURRENT_OUTPUT_CREATE_REJECTED\nOUTPUT=" + target + "\nTARGET_FILES_WRITTEN=0\nFIXTURE_CLEANED=YES";
        }
        OutputFinal = CreateDirectoryChild(TmpFinal, OutputLeaf);
        if (Under(VendorFinal, OutputFinal) || Under(OutputFinal, VendorFinal)) throw new IOException("OUTPUT_AND_VENDOR_PATHS_MUST_BE_DISJOINT_AFTER_CREATE");
        if (phase == "lock_test") {
            string lockSource = CreateDirectoryChild(OutputFinal, "lock_fixture");
            string lockDestination = Join(OutputFinal, "lock_fixture_rename_probe");
            return "RESULT=PASS_LOCK_FIXTURE\nOUTPUT=" + OutputFinal + "\n" + TestLockedRename(lockSource, lockDestination) + "\nTARGET_FILES_WRITTEN=0";
        }
        if (phase == "subpath_reparse_test") {
            string fixtureTarget = CreateDirectoryChild(OutputFinal, "junction_target");
            CreateDirectoryChild(fixtureTarget, "nested");
            TestParentJunction(OutputFinal, "parent_junction", fixtureTarget, "nested");
            TestJunction(OutputFinal, "vendor_ip_metadata", fixtureTarget);
            TestJunction(OutputFinal, "project", fixtureTarget);
            string metadata = CreateDirectoryChild(OutputFinal, "vendor_ip_metadata");
            string rgb = CreateDirectoryChild(metadata, "rgb2dvi_v1_3");
            TestJunction(rgb, "src", fixtureTarget);
            if (Directory.GetFiles(OutputFinal, "*", SearchOption.AllDirectories).Length != 0) throw new IOException("REPARSE_TEST_LEFT_TARGET_FILES");
            return "RESULT=PASS_PARENT_AND_SUBPATH_REPARSE_REJECTED\nOUTPUT=" + OutputFinal + "\nJUNCTION_TARGET=" + fixtureTarget + "\nTARGET_FILES_WRITTEN=0";
        }
        string project = CreateDirectoryChild(OutputFinal, "project"), metadataPath = "";
        int copied = 0;
        if (mode == "azynq_metadata") {
            metadataPath = CreateDirectoryChild(OutputFinal, "vendor_ip_metadata");
            foreach (string relative in manifest) {
                string[] parts = relative.Replace('\\', '/').Split('/');
                if (parts.Length < 2 || parts[0] != "my_ip") throw new IOException("TRACKED_IP_PATH_OUTSIDE_EXPECTED_REPOSITORY");
                string parent = metadataPath;
                for (int i = 1; i < parts.Length - 1; i++) parent = EnsureDirectoryChild(parent, parts[i]);
                string sourcePath = Path.Combine(sourceRoot, "my_ip");
                for (int i = 1; i < parts.Length; i++) sourcePath = Path.Combine(sourcePath, parts[i]);
                CopyFile(sourcePath, parent, parts[parts.Length - 1]); copied++;
            }
            RewriteMetadata(Path.Combine(metadataPath, "axi_dynclk_v1_0"), "component.xml", "axi_dynclk");
            RewriteMetadata(Path.Combine(metadataPath, "rgb2dvi_v1_3"), "component.xml", "rgb2dvi");
        } else if (mode != "native") throw new IOException("INVALID_MODE");
        return "RESULT=PASS_PATH_GUARD_PREPARATION\nOUTPUT=" + OutputFinal + "\nPROJECT=" + project + "\nMETADATA=" + metadataPath + "\nMETADATA_COUNT=" + copied + "\nTARGET_FILES_WRITTEN=" + copied;
    @R@
@R@
    }]
    # 压缩内嵌 C#，避免超过 Windows 子进程环境块限制。
    set native_code_zlib [zlib compress [encoding convertto utf-8 $native_code]]
    set ::env(S3_GUARD_NATIVE_CODE) [string trim [binary encode base64 -maxlen 0 $native_code_zlib]]
    set child_script [string trim {
$ErrorActionPreference = 'Stop'
$map = [IO.MemoryMappedFiles.MemoryMappedFile]::OpenExisting($env:S3_GUARD_STATUS_MAP)
$view = $map.CreateViewAccessor()
$event = [Threading.EventWaitHandle]::OpenExisting($env:S3_GUARD_READY_EVENT)
function Set-Status([string]$value) {
    $bytes = [Text.Encoding]::UTF8.GetBytes($value)
    $view.Write(0, [int]$bytes.Length)
    $view.WriteArray(4, $bytes, 0, $bytes.Length)
    $view.Flush()
    $event.Set()
}
try {
    $wrappedNativeCode = [Convert]::FromBase64String($env:S3_GUARD_NATIVE_CODE)
    if ($wrappedNativeCode.Length -le 6) { throw 'COMPRESSED_GUARD_CODE_TOO_SHORT' }
    $rawNativeCode = New-Object byte[] ($wrappedNativeCode.Length - 6)
    [Array]::Copy($wrappedNativeCode, 2, $rawNativeCode, 0, $rawNativeCode.Length)
    $nativeInput = New-Object IO.MemoryStream(,$rawNativeCode)
    $nativeDeflate = New-Object IO.Compression.DeflateStream($nativeInput, [IO.Compression.CompressionMode]::Decompress)
    $nativeReader = New-Object IO.StreamReader($nativeDeflate, [Text.Encoding]::UTF8)
    $nativeCode = $nativeReader.ReadToEnd()
    $nativeReader.Dispose(); $nativeDeflate.Dispose(); $nativeInput.Dispose()
    Add-Type -TypeDefinition $nativeCode
    $preflight = [S3PathGuardR3]::Begin($env:S3_GUARD_REPO_ROOT, $env:S3_GUARD_SCRIPT_PATH, $env:S3_GUARD_VENDOR_ROOT, $env:S3_GUARD_SOURCE_ROOT, $env:S3_GUARD_OUTPUT_DIR, $env:S3_GUARD_PHASE)
        $actualCommit = (& git -C $env:S3_GUARD_VENDOR_ROOT rev-parse HEAD 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -ne 0 -or $actualCommit -ne 'fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327') { throw 'VENDOR_COMMIT_OR_GIT_CHECK_FAILED' }
        $sourceRelative = 'course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project'
        $changes = (& git -C $env:S3_GUARD_VENDOR_ROOT status --porcelain=v1 --untracked-files=all --ignored=matching -- $sourceRelative 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -ne 0 -or $changes.Length -ne 0) { throw 'VENDOR_SOURCE_NOT_CLEAN' }
        $tracked = @(& git -C $env:S3_GUARD_VENDOR_ROOT ls-files -- ($sourceRelative + '/my_ip'))
        if ($LASTEXITCODE -ne 0 -or $tracked.Count -eq 0) { throw 'EMPTY_TRACKED_IP_REPOSITORY' }
        $manifest = @()
        foreach ($relative in $tracked) {
            $relative = $relative.Trim()
            $prefix = $sourceRelative + '/my_ip/'
            if (-not $relative.StartsWith($prefix, [StringComparison]::Ordinal)) { throw 'UNEXPECTED_TRACKED_IP_PATH' }
            $manifest += 'my_ip/' + $relative.Substring($prefix.Length)
        }
        foreach ($relative in @('ps_config.tcl', 'pl_config.tcl') + $manifest) { [S3PathGuardR3]::HoldSourceFile($env:S3_GUARD_SOURCE_ROOT, $relative) }
        $plText = [IO.File]::ReadAllText([IO.Path]::Combine($env:S3_GUARD_SOURCE_ROOT, 'pl_config.tcl'), [Text.Encoding]::UTF8)
        if ($plText -match '(?im)^\s*(read_xdc|source\s+[^\r\n]*\.xdc)') { throw 'PL_CONFIG_ATTEMPTS_TO_LOAD_XDC' }
        if ($plText -match '(?i)ov5640|camera') { throw 'SOURCE_IS_NOT_HDMI_ONLY' }
        foreach ($vlnv in @('digilentinc.com:ip:axi_dynclk:1.0', 'digilentinc.com:ip:rgb2dvi:1.3')) { if (-not $plText.Contains($vlnv)) { throw ('MISSING_EXPECTED_HDMI_IP_' + $vlnv) } }
        foreach ($check in @(@('axi_dynclk_v1_0', 'axi_dynclk'), @('rgb2dvi_v1_3', 'rgb2dvi'))) {
            $xmlPath = [IO.Path]::Combine($env:S3_GUARD_SOURCE_ROOT, 'my_ip', $check[0], 'component.xml')
            $xml = [IO.File]::ReadAllText($xmlPath, [Text.Encoding]::UTF8)
            if (-not $xml.Contains('<spirit:name>' + $check[1] + '</spirit:name>')) { throw ('COMPONENT_XML_NAME_MISMATCH_' + $check[0]) }
        }
    Set-Status ([S3PathGuardR3]::Prepare($env:S3_GUARD_MODE, $env:S3_GUARD_PHASE, $env:S3_GUARD_SOURCE_ROOT, $manifest))
    $owner = [Diagnostics.Process]::GetProcessById([int]$env:S3_GUARD_OWNER_PID)
    while (-not $owner.HasExited) { Start-Sleep -Milliseconds 100 }
} catch {
    Set-Status ('ERROR=' + $_.Exception.Message)
    exit 3
} finally {
    $view.Dispose(); $map.Dispose(); $event.Dispose()
}
    }]
    set ::env(S3_GUARD_CHILD_ENCODED) [binary encode base64 [encoding convertto unicode $child_script]]
    set launcher_script [string trim {
$ErrorActionPreference = 'Stop'
$map = [IO.MemoryMappedFiles.MemoryMappedFile]::CreateOrOpen($env:S3_GUARD_STATUS_MAP, 65536)
$view = $map.CreateViewAccessor()
$event = [Threading.EventWaitHandle]::new($false, [Threading.EventResetMode]::ManualReset, $env:S3_GUARD_READY_EVENT)
$child = Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -PassThru -ArgumentList ('-NoProfile -NonInteractive -EncodedCommand ' + $env:S3_GUARD_CHILD_ENCODED)
$signaled = $false
for ($i = 0; $i -lt 600 -and -not $signaled; $i++) { $signaled = $event.WaitOne(100); if ($child.HasExited -and -not $signaled) { break } }
if (-not $signaled) { throw 'DIRECTORY_GUARDIAN_SETUP_TIMEOUT_OR_EARLY_EXIT' }
$length = $view.ReadInt32(0)
if ($length -lt 0 -or $length -gt 65500) { throw 'INVALID_DIRECTORY_GUARDIAN_STATUS_LENGTH' }
$bytes = New-Object byte[] $length
$null = $view.ReadArray(4, $bytes, 0, $length)
$status = [Text.Encoding]::UTF8.GetString($bytes)
Write-Output ('S3_GUARD_STATUS=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($status)))
$view.Dispose(); $map.Dispose(); $event.Dispose()
    }]
    set encoded [binary encode base64 [encoding convertto unicode $launcher_script]]
    set failed [catch {set result [exec powershell.exe -NoProfile -NonInteractive -EncodedCommand $encoded 2>@1]} err opts]
    unset -nocomplain ::env(S3_GUARD_NATIVE_CODE) ::env(S3_GUARD_CHILD_ENCODED)
    if {$failed} {return -options $opts $err}
    if {![regexp {S3_GUARD_STATUS=([^\r\n]+)} $result -> encoded_status]} {error "SECURE_GUARDIAN_NO_STATUS: $result"}
    set status [encoding convertfrom utf-8 [binary decode base64 $encoded_status]]
    if {[string first "ERROR=" $status] == 0} {error "SECURE_GUARDIAN_REJECTED: [string range $status 6 end]"}
    if {$phase eq "guard"} {
        append status "\nGUARD_READY_EVENT=$ready_event\nGUARD_STATUS_MAP=$status_map"
    }
    return $status
}

proc s3_read_utf8 {path} {
    set channel [open $path r]
    fconfigure $channel -encoding utf-8 -translation auto
    set value [read $channel]
    close $channel
    return $value
}

proc s3_guard_status_dict {status} {
    set parsed {}
    foreach line [split [string trim $status "\r\n"] "\n"] {
        if {$line eq ""} {continue}
        if {![regexp {^([A-Z_]+)=(.*)$} $line -> key value]} {
            error "INVALID_GUARD_STATUS_LINE: $line"
        }
        if {[dict exists $parsed $key]} {error "DUPLICATE_GUARD_STATUS_KEY: $key"}
        dict set parsed $key $value
    }
    if {![dict exists $parsed RESULT]} {error "GUARD_STATUS_MISSING_RESULT"}
    return $parsed
}

proc s3_write_utf8 {path value} {
    set channel [open $path {WRONLY CREAT EXCL}]
    fconfigure $channel -encoding utf-8 -translation lf
    puts -nonewline $channel $value
    close $channel
}

if {$argc < 2 || $argc > 4} {
    puts stderr "用法：<厂商根目录> <新绝对输出目录> ?native|azynq_metadata? ?guard|bd|hdl?"
    exit 2
}

set vendor_root [lindex $argv 0]
set output_dir [lindex $argv 1]
set mode native
set phase bd
if {$argc >= 3} {set mode [lindex $argv 2]}
if {$argc >= 4} {set phase [lindex $argv 3]}

set expected_commit fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327
set source_relative course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project
set ::s3_script_path [info script]
set ::s3_repo_root [file dirname [file dirname $::s3_script_path]]
set source_root [file join $vendor_root course_s2_vitis 14_vdma_hdmi_out Vivado auto_create_project]
set actual_commit NOT_CHECKED
set part_name xa7z020clg400-1I
set part_family NOT_CHECKED
set cell_count NOT_REACHED
set cell_names NOT_REACHED
set bd_intf_ports NOT_REACHED
set bd_ports NOT_REACHED
set ip_repo_used NOT_SELECTED
set wrapper_names NOT_GENERATED
set result FAILED
if {$mode ni {native azynq_metadata}} {
    puts stderr "INVALID_MODE"
    exit 2
}
if {$phase ni {guard race_test lock_test subpath_reparse_test bd hdl}} {
    puts stderr "INVALID_PHASE"
    exit 2
}
if {[file pathtype $vendor_root] ne "absolute" || [regexp {(^|/)(\.|\.\.)(/|$)} [string map [list "\\" "/"] $vendor_root]]} {
    puts stderr "INVALID_VENDOR_ROOT"
    exit 2
}
if {[file pathtype $output_dir] ne "absolute" || [regexp {(^|/)(\.|\.\.)(/|$)} [string map [list "\\" "/"] $output_dir]]} {
    puts stderr "OUTPUT_PATH_MUST_BE_ABSOLUTE_AND_TRAVERSAL_FREE"
    exit 2
}
if {[catch {set guard_status [s3_launch_secure_guardian $vendor_root $source_root $output_dir $mode $phase]} path_error path_error_options]} {
    puts stderr "OUTPUT_PATH_ISOLATION_FAILED: $path_error"
    if {[dict exists $path_error_options -errorinfo]} {
        puts stderr [dict get $path_error_options -errorinfo]
    }
    flush stderr
    exit 2
}
set guard_data [s3_guard_status_dict $guard_status]
set guard_result [dict get $guard_data RESULT]
if {[dict exists $guard_data OUTPUT]} {set output_dir [dict get $guard_data OUTPUT]}
if {[dict exists $guard_data PROJECT]} {set project_dir [dict get $guard_data PROJECT]}
if {[dict exists $guard_data METADATA]} {set guarded_metadata_dir [dict get $guard_data METADATA]}
if {[dict exists $guard_data METADATA_COUNT]} {set guarded_metadata_count [dict get $guard_data METADATA_COUNT]}
if {$phase in {guard race_test lock_test subpath_reparse_test}} {
    puts $guard_status
    exit 0
}
if {[catch {
    set actual_commit [string trim [exec git -C $vendor_root rev-parse HEAD]]
    if {$actual_commit ne $expected_commit} {error "VENDOR_COMMIT_MISMATCH"}
    set changes [exec git -C $vendor_root status --porcelain=v1 --untracked-files=all --ignored=matching -- $source_relative]
    if {[string trim $changes] ne ""} {error "VENDOR_SOURCE_NOT_CLEAN"}
    foreach relative_file {ps_config.tcl pl_config.tcl} {
        if {![file isfile [file join $source_root $relative_file]]} {error "MISSING_SOURCE_$relative_file"}
    }
    set source_ip_repo [file join $source_root my_ip]
    if {![file isdirectory $source_ip_repo]} {error "MISSING_VENDOR_IP_REPOSITORY"}
    set pl_text [s3_read_utf8 [file join $source_root pl_config.tcl]]
    if {[regexp -nocase {(^|\n)[ \t]*(read_xdc|source[ \t]+[^\n]*\.xdc)} $pl_text]} {
        error "PL_CONFIG_ATTEMPTS_TO_LOAD_XDC"
    }
    if {[regexp -nocase {ov5640|camera} $pl_text]} {error "SOURCE_IS_NOT_HDMI_ONLY"}
    foreach required_vlnv {digilentinc.com:ip:axi_dynclk:1.0 digilentinc.com:ip:rgb2dvi:1.3} {
        if {[string first $required_vlnv $pl_text] < 0} {error "MISSING_EXPECTED_HDMI_IP_$required_vlnv"}
    }
    set custom_cores [list [list axi_dynclk_v1_0 axi_dynclk] [list rgb2dvi_v1_3 rgb2dvi]]
    set component_xmls {}
    foreach ip_directory [glob -nocomplain -types d [file join $source_ip_repo *]] {
        set candidate_xml [file join $ip_directory component.xml]
        if {[file isfile $candidate_xml]} {lappend component_xmls $candidate_xml}
    }
    set component_xmls [lsort $component_xmls]
    set expected_xmls {}
    foreach core $custom_cores {
        lassign $core directory component_name
        set xml_path [file join $source_ip_repo $directory component.xml]
        if {![file isfile $xml_path]} {error "MISSING_EXPECTED_COMPONENT_XML_$directory"}
        lappend expected_xmls $xml_path
        set xml [s3_read_utf8 $xml_path]
        if {[string first "<spirit:name>$component_name</spirit:name>" $xml] < 0} {
            error "COMPONENT_XML_NAME_MISMATCH_$directory"
        }
    }
    if {[lsort $expected_xmls] ne $component_xmls} {error "UNEXPECTED_COMPONENT_XML_SET"}
    set_param general.maxThreads 1
    set part_matches [get_parts -quiet $part_name]
    if {[llength $part_matches] != 1 || ![string equal -nocase [lindex $part_matches 0] $part_name]} {
        error "EXACT_PART_NOT_UNIQUE_OR_UNAVAILABLE"
    }
    set part_family [get_property FAMILY [lindex $part_matches 0]]
    if {$mode eq "azynq_metadata" && $part_family ne "azynq"} {
        error "METADATA_MODE_REQUIRES_AZYNQ_PART_FAMILY"
    }
} preflight_error]} {
    puts stderr "PREFLIGHT_FAILED: $preflight_error"
    exit 2
}

set failed [catch {
    if {$mode ni {native azynq_metadata}} {error "INVALID_MODE"}
    if {[file pathtype $vendor_root] ne "absolute" || [regexp {(^|/)(\.|\.\.)(/|$)} [string map [list "\\" "/"] $vendor_root]] || ![file isdirectory $vendor_root]} {
        error "INVALID_VENDOR_ROOT"
    }

    set actual_commit [string trim [exec git -C $vendor_root rev-parse HEAD]]
    if {$actual_commit ne $expected_commit} {error "VENDOR_COMMIT_MISMATCH"}
    set changes [exec git -C $vendor_root status --porcelain=v1 --untracked-files=all --ignored=matching -- $source_relative]
    if {[string trim $changes] ne ""} {error "VENDOR_SOURCE_NOT_CLEAN"}

    set source_root [file join $vendor_root course_s2_vitis 14_vdma_hdmi_out Vivado auto_create_project]
    foreach relative_file {ps_config.tcl pl_config.tcl} {
        if {![file isfile [file join $source_root $relative_file]]} {error "MISSING_SOURCE_$relative_file"}
    }
    set source_ip_repo [file join $source_root my_ip]
    if {![file isdirectory $source_ip_repo]} {error "MISSING_VENDOR_IP_REPOSITORY"}
    set pl_text [s3_read_utf8 [file join $source_root pl_config.tcl]]
    if {[regexp -nocase {(^|\n)[ \t]*(read_xdc|source[ \t]+[^\n]*\.xdc)} $pl_text]} {
        error "PL_CONFIG_ATTEMPTS_TO_LOAD_XDC"
    }
    if {[regexp -nocase {ov5640|camera} $pl_text]} {error "SOURCE_IS_NOT_HDMI_ONLY"}
    foreach required_vlnv {digilentinc.com:ip:axi_dynclk:1.0 digilentinc.com:ip:rgb2dvi:1.3} {
        if {[string first $required_vlnv $pl_text] < 0} {error "MISSING_EXPECTED_HDMI_IP_$required_vlnv"}
    }

    # 按该例程的真实自定义 IP 清单检查组件 XML；tmds_v1_0 仅提供接口定义。
    set custom_cores [list [list axi_dynclk_v1_0 axi_dynclk] [list rgb2dvi_v1_3 rgb2dvi]]
    set component_xmls {}
    foreach ip_directory [glob -nocomplain -types d [file join $source_ip_repo *]] {
        set candidate_xml [file join $ip_directory component.xml]
        if {[file isfile $candidate_xml]} {lappend component_xmls $candidate_xml}
    }
    set component_xmls [lsort $component_xmls]
    set expected_xmls {}
    foreach core $custom_cores {
        lassign $core directory component_name
        set xml_path [file join $source_ip_repo $directory component.xml]
        if {![file isfile $xml_path]} {error "MISSING_EXPECTED_COMPONENT_XML_$directory"}
        lappend expected_xmls $xml_path
        set xml [s3_read_utf8 $xml_path]
        if {[string first "<spirit:name>$component_name</spirit:name>" $xml] < 0} {
            error "COMPONENT_XML_NAME_MISMATCH_$directory"
        }
    }
    if {[lsort $expected_xmls] ne $component_xmls} {error "UNEXPECTED_COMPONENT_XML_SET"}

    set_param general.maxThreads 1
    set part_matches [get_parts -quiet $part_name]
    if {[llength $part_matches] != 1 || ![string equal -nocase [lindex $part_matches 0] $part_name]} {
        error "EXACT_PART_NOT_UNIQUE_OR_UNAVAILABLE"
    }
    set part_family [get_property FAMILY [lindex $part_matches 0]]
    if {$mode eq "azynq_metadata"} {
        if {$part_family ne "azynq"} {error "METADATA_MODE_REQUIRES_AZYNQ_PART_FAMILY"}
        if {![info exists guarded_metadata_dir] || $guarded_metadata_dir eq ""} {error "GUARDIAN_DID_NOT_RETURN_METADATA_PATH"}
        set ip_repo_used $guarded_metadata_dir
        set metadata_file_count $guarded_metadata_count
        puts "METADATA_COPY_FILE_COUNT=$metadata_file_count"
    } else {
        set ip_repo_used $source_ip_repo
    }

    # 只新建本子任务工程；不复用或 source 厂商自动构建入口。
    if {![info exists project_dir] || $project_dir eq ""} {error "GUARDIAN_DID_NOT_RETURN_PROJECT_PATH"}
    create_project s3_hdmi_only $project_dir -part [lindex $part_matches 0]
    set_property ip_repo_paths [list $ip_repo_used] [current_project]
    update_ip_catalog
    create_bd_design s3_hdmi_only
    create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
    source -encoding utf-8 [file join $source_root ps_config.tcl]
    set_ps_config processing_system7_0
    source -encoding utf-8 [file join $source_root pl_config.tcl]

    set expected_cells [lsort -dictionary {axi_dynclk_0 axi_smc axi_vdma_0 processing_system7_0 ps7_0_axi_periph rgb2dvi_0 rst_ps7_0_100M rst_ps7_0_142M v_axi4s_vid_out_0 v_tc_0 xlconcat_0}]
    set cell_names {}
    foreach cell [get_bd_cells -quiet] {lappend cell_names [get_property NAME $cell]}
    set cell_names [lsort -dictionary $cell_names]
    set cell_count [llength $cell_names]
    if {$cell_names ne $expected_cells || $cell_count != 11} {error "UNEXPECTED_HDMI_ONLY_BD_CELL_TOPOLOGY"}

    set bd_intf_ports {}
    foreach port [get_bd_intf_ports -quiet] {lappend bd_intf_ports [get_property NAME $port]}
    set bd_intf_ports [lsort -dictionary $bd_intf_ports]
    if {$bd_intf_ports ne [lsort -dictionary {DDR FIXED_IO TMDS hdmi_ddc}]} {error "UNEXPECTED_HDMI_ONLY_BD_INTERFACE_PORTS"}
    set bd_ports {}
    foreach port [get_bd_ports -quiet] {lappend bd_ports [get_property NAME $port]}
    set bd_ports [lsort -dictionary $bd_ports]
    foreach required_port {hdmi_oen TMDS_clk_n TMDS_clk_p TMDS_data_n TMDS_data_p} {
        if {[lsearch -exact $bd_ports $required_port] < 0} {error "MISSING_REQUIRED_HDMI_BD_PORT_$required_port"}
    }
    if {[regexp -nocase {camera|ov5640|cmos} [join $bd_ports " "]]} {error "CAMERA_SIGNAL_FOUND_IN_HDMI_ONLY_BD"}
    set constraint_files [get_files -quiet -of_objects [get_filesets constrs_1]]
    if {[llength $constraint_files] != 0} {error "PROJECT_LEVEL_XDC_MUST_NOT_BE_LOADED"}

    validate_bd_design
    save_bd_design
    set bd_files [get_files -quiet */s3_hdmi_only.bd]
    if {[llength $bd_files] != 1} {error "EXPECTED_SINGLE_HDMI_ONLY_BD_FILE"}
    if {$phase eq "hdl"} {
        # 仅生成 IP/BD HDL 与顶层包装器，不启动综合或实现流程。
        generate_target all $bd_files
        set wrapper_names [make_wrapper -files $bd_files -top]
        if {[llength $wrapper_names] == 0} {error "NO_GENERATED_BD_WRAPPER"}
        foreach wrapper $wrapper_names {
            if {![file isfile $wrapper]} {error "GENERATED_BD_WRAPPER_MISSING"}
        }
        add_files -norecurse $wrapper_names
        set_property top s3_hdmi_only_wrapper [current_fileset]
        update_compile_order -fileset sources_1
    }
    close_project

    if {$mode eq "azynq_metadata"} {
        set result "PASS_[string toupper $phase]_EXPERIMENTAL_METADATA_ONLY"
    } else {
        set result "PASS_[string toupper $phase]_NATIVE_METADATA_ONLY"
    }
    set result
} error_message error_options]

if {$failed} {
    set result FAILED
    set diagnostic "ERROR=$error_message\n"
    if {[dict exists $error_options -errorinfo]} {
        append diagnostic "ERRORINFO=[dict get $error_options -errorinfo]\n"
    }
    catch {close_project}
} else {
    set diagnostic "ERROR=NONE\n"
}

set vivado_version UNKNOWN
catch {set vivado_version [version -short]}
set report_text "RESULT=$result\nVIVADO=$vivado_version\nVENDOR_COMMIT_EXPECTED=$expected_commit\nVENDOR_COMMIT_ACTUAL=$actual_commit\nSOURCE_RELATIVE=$source_relative\nPART=$part_name\nPART_FAMILY=$part_family\nMODE=$mode\nPHASE=$phase\nBD_CELL_COUNT=$cell_count\nBD_CELLS=$cell_names\nBD_INTERFACE_PORTS=$bd_intf_ports\nBD_PORTS=$bd_ports\nIP_REPOSITORY=$ip_repo_used\nGENERATED_WRAPPERS=$wrapper_names\nPROJECT_LEVEL_XDC_LOADED=NO\nSCOPE=HDMI_ONLY_BD_VALIDATION_AND_OPTIONAL_HDL_GENERATION; NO_BOARD_XDC; NO_SYNTHESIS_OR_IMPLEMENTATION; NO_BITSTREAM; NO_XSA; NO_HARDWARE\n"
set report_error ""
if {[catch {
    s3_write_utf8 [file join $output_dir result.txt] $report_text
    s3_write_utf8 [file join $output_dir diagnostics.txt] $diagnostic
} report_error]} {
    puts stderr "REPORT_WRITE_FAILED: $report_error"
    puts stderr $diagnostic
    exit 2
}

puts $report_text
if {$failed} {exit 2}
exit 0
