using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Text;
using Microsoft.Win32.SafeHandles;
public static class S3PathGuardR3
{
    private const uint Delete = 0x00010000, ReadAttributes = 0x80, WriteData = 0x02;
    private const uint GenericRead = 0x80000000, GenericWrite = 0x40000000, Synchronize = 0x00100000;
    private const uint ShareRead = 1, ShareWrite = 2, OpenExisting = 3, BackupSemantics = 0x02000000, OpenReparse = 0x00200000;
    private const uint DirectoryFile = 1, NonDirectoryFile = 0x40, SyncIo = 0x20, FileOpen = 1, FileCreate = 2;
    private const uint AttrDirectory = 0x10, AttrReparse = 0x400, MountPointTag = 0xA0000003, FsctlSetReparsePoint = 0x000900A4;
    private const int FileAttributeTagInfoClass = 9;
    private struct AttributeTagInfo { public uint Attributes; public uint Tag; }
    private struct UnicodeString { public ushort Length, MaximumLength; public IntPtr Buffer; }
    private struct ObjectAttributes { public uint Length; public IntPtr RootDirectory, ObjectName; public uint Attributes; public IntPtr SecurityDescriptor, SecurityQualityOfService; }
    private struct IoStatusBlock { public IntPtr Status; public UIntPtr Information; }
    private static readonly List<SafeFileHandle> DirectHandles = new List<SafeFileHandle>();
    private static readonly List<SafeFileHandle> SourceHandles = new List<SafeFileHandle>();
    private static readonly List<FileStream> DataHandles = new List<FileStream>();
    private static readonly Dictionary<string, SafeFileHandle> Directories = new Dictionary<string, SafeFileHandle>(StringComparer.OrdinalIgnoreCase);
    private static string RepoFinal, ScriptsFinal, TmpFinal, AuthorizedOutputParentFinal, VendorFinal, SourceFinal, OutputFinal, OutputLeaf;

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
    {
        path = path.Replace('/', '\\');
        if (path.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase)) path = @"\\" + path.Substring(8);
        else if (path.StartsWith(@"\\?\", StringComparison.OrdinalIgnoreCase)) path = path.Substring(4);
        string root = Path.GetPathRoot(path);
        if (root == null) throw new IOException("PATH_HAS_NO_ROOT");
        if (path.Length > root.Length) path = path.TrimEnd('\\');
        return path;
    }
    private static string FinalPath(SafeFileHandle handle)
    {
        StringBuilder buffer = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
        if (length == 0 || length >= buffer.Capacity) throw new Win32Exception(Marshal.GetLastWin32Error());
        return Normalize(buffer.ToString());
    }
    private static AttributeTagInfo Info(SafeFileHandle handle)
    {
        AttributeTagInfo info;
        if (!GetFileInformationByHandleEx(handle, FileAttributeTagInfoClass, out info, (uint)Marshal.SizeOf(typeof(AttributeTagInfo)))) throw new Win32Exception(Marshal.GetLastWin32Error());
        return info;
    }
    private static bool Under(string parent, string child)
    {
        parent = Normalize(parent); child = Normalize(child);
        if (String.Equals(parent, child, StringComparison.OrdinalIgnoreCase)) return true;
        string prefix = parent.EndsWith("\\", StringComparison.Ordinal) ? parent : parent + "\\";
        return child.StartsWith(prefix, StringComparison.OrdinalIgnoreCase);
    }
    private static string Join(string parent, string leaf)
    {
        if (String.IsNullOrWhiteSpace(leaf) || leaf == "." || leaf == ".." || leaf.IndexOfAny(new char[] {'\\', '/', ':'}) >= 0) throw new IOException("INVALID_SINGLE_PATH_COMPONENT");
        return Normalize(parent.TrimEnd('\\') + "\\" + leaf);
    }
    private static void RegisterDirectory(SafeFileHandle handle, string parent)
    {
        AttributeTagInfo info = Info(handle);
        if ((info.Attributes & AttrDirectory) == 0) throw new IOException("PATH_COMPONENT_NOT_DIRECTORY");
        if ((info.Attributes & AttrReparse) != 0) throw new IOException("REPARSE_POINT_COMPONENT_REJECTED");
        string finalPath = FinalPath(handle);
        if (parent != null && !Under(parent, finalPath)) throw new IOException("DIRECTORY_FINAL_PATH_ESCAPED_PARENT");
        DirectHandles.Add(handle);
        if (!Directories.ContainsKey(finalPath)) Directories.Add(finalPath, handle);
    }
    private static string AcquireAnchor(string path)
    {
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
    }
    private static string AcquireSubtree(string anchor, string path)
    {
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
    }
    private static SafeFileHandle GetDirectory(string path)
    {
        SafeFileHandle handle;
        if (!Directories.TryGetValue(Normalize(path), out handle) || handle.IsClosed || handle.IsInvalid) throw new IOException("DIRECTORY_HANDLE_NOT_HELD");
        return handle;
    }
    private static SafeFileHandle NtOpen(SafeFileHandle parent, string leaf, uint disposition, uint options, uint access, uint share = ShareRead | ShareWrite)
    {
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
            int status = NtCreateFile(out raw, access, ref attributes, out io, IntPtr.Zero, 0, share, disposition, options | OpenReparse | SyncIo, IntPtr.Zero, 0);
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
    }
    private static string CreateDirectoryChild(string parent, string leaf)
    {
        SafeFileHandle handle = NtOpen(GetDirectory(parent), leaf, FileCreate, DirectoryFile, Delete | ReadAttributes | Synchronize);
        bool retained = false;
        try {
        RegisterDirectory(handle, parent);
            string finalPath = FinalPath(handle);
            if (!String.Equals(finalPath, Join(parent, leaf), StringComparison.OrdinalIgnoreCase)) throw new IOException("CREATED_DIRECTORY_PHYSICAL_PATH_MISMATCH");
            retained = true; return finalPath;
        } finally { if (!retained) handle.Dispose(); }
    }
    private static string EnsureDirectoryChild(string parent, string leaf)
    {
        string expected = Join(parent, leaf);
        if (Directories.ContainsKey(expected)) return expected;
        return CreateDirectoryChild(parent, leaf);
    }
    private static bool ChildExists(SafeFileHandle parent, string leaf)
    {
        SafeFileHandle handle = null;
        try {
            handle = NtOpen(parent, leaf, FileOpen, 0, ReadAttributes | Synchronize);
            return true;
        } catch (FileNotFoundException) { return false; }
        finally { if (handle != null) handle.Dispose(); }
    }
    private static void HoldRegularScript(string path, string expectedParent)
    {
        string full = Path.GetFullPath(path);
        if (!String.Equals(Normalize(Path.GetDirectoryName(full)), expectedParent, StringComparison.OrdinalIgnoreCase)) throw new IOException("SCRIPT_PATH_PARENT_MISMATCH");
        SafeFileHandle handle = CreateFileW(full, GenericRead | ReadAttributes, ShareRead, IntPtr.Zero, OpenExisting, OpenReparse, IntPtr.Zero);
        if (handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
        AttributeTagInfo info = Info(handle);
        if ((info.Attributes & (AttrReparse | AttrDirectory)) != 0 || !String.Equals(FinalPath(handle), full, StringComparison.OrdinalIgnoreCase)) {
            handle.Dispose(); throw new IOException("SCRIPT_FILE_REPARSE_OR_ALIAS_REJECTED");
        }
        SourceHandles.Add(handle);
    }
    private static SafeFileHandle OpenSourceFile(string fullPath)
    {
        AcquireSubtree(VendorFinal, Path.GetDirectoryName(Path.GetFullPath(fullPath)));
        SafeFileHandle file = CreateFileW(Path.GetFullPath(fullPath), GenericRead | ReadAttributes, ShareRead, IntPtr.Zero, OpenExisting, OpenReparse, IntPtr.Zero);
        if (file.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error());
        AttributeTagInfo info = Info(file);
        if ((info.Attributes & (AttrReparse | AttrDirectory)) != 0) { file.Dispose(); throw new IOException("SOURCE_FILE_REPARSE_OR_DIRECTORY_REJECTED"); }
        SourceHandles.Add(file); return file;
    }
    public static void HoldSourceFile(string sourceRoot, string relativePath)
    {
        string[] parts = relativePath.Replace('\\', '/').Split('/');
        foreach (string part in parts) if (part.Length == 0 || part == "." || part == ".." || part.IndexOfAny(new char[] {':', '\\'}) >= 0) throw new IOException("INVALID_SOURCE_MANIFEST_PATH");
        string path = sourceRoot; foreach (string part in parts) path = Path.Combine(path, part);
        OpenSourceFile(path);
    }
    private static byte[] TransformMetadata(byte[] sourceBytes, string component)
    {
        string xml;
        using (MemoryStream input = new MemoryStream(sourceBytes, false))
        using (StreamReader reader = new StreamReader(input, new UTF8Encoding(false, true), true))
            xml = reader.ReadToEnd();
        if (Count(xml, "<xilinx:supportedFamilies>") != 1 || Count(xml, "</xilinx:supportedFamilies>") != 1)
            throw new IOException("INVALID_SUPPORTED_FAMILIES_BLOCK_" + component);
        if (Count(xml, "<xilinx:family[^>]*>zynq</xilinx:family>") != 1 || Count(xml, "<xilinx:family[^>]*>azynq</xilinx:family>") != 0)
            throw new IOException("UNEXPECTED_FAMILY_METADATA_" + component);
        xml = xml.Replace("</xilinx:supportedFamilies>", "      <xilinx:family xilinx:lifeCycle=\"Pre-Production\">azynq</xilinx:family>\n</xilinx:supportedFamilies>");
        return new UTF8Encoding(false).GetBytes(xml);
    }
    private static void CopyFile(string sourcePath, string destinationParent, string leaf, string component)
    {
        SafeFileHandle source = OpenSourceFile(sourcePath);
        FileStream input = new FileStream(source, FileAccess.Read);
        byte[] content;
        using (MemoryStream buffer = new MemoryStream()) { input.CopyTo(buffer); content = buffer.ToArray(); }
        if (component != null) content = TransformMetadata(content, component);
        SafeFileHandle destination = NtOpen(GetDirectory(destinationParent), leaf, FileCreate, NonDirectoryFile,
            GenericWrite | ReadAttributes | WriteData | Synchronize, ShareRead);
        FileStream output = new FileStream(destination, FileAccess.Write);
        output.Write(content, 0, content.Length); output.Flush(true);
        DataHandles.Add(input); DataHandles.Add(output);
    }
    private static int Count(string value, string expression) { return System.Text.RegularExpressions.Regex.Matches(value, expression).Count; }
    private static string ComponentForMetadataPath(string relative)
    {
        if (relative == "my_ip/axi_dynclk_v1_0/component.xml") return "axi_dynclk";
        if (relative == "my_ip/rgb2dvi_v1_3/component.xml") return "rgb2dvi";
        return null;
    }
    private static void SetJunction(string path, string target)
    {
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
    }
    private static bool ChildIsReparse(string parent, string leaf)
    {
        SafeFileHandle handle = NtOpen(GetDirectory(parent), leaf, FileOpen, DirectoryFile, ReadAttributes | Synchronize);
        try { return (Info(handle).Attributes & AttrReparse) != 0; } finally { handle.Dispose(); }
    }
    private static void TestJunction(string parent, string leaf, string target)
    {
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
    }
    private static void TestParentJunction(string parent, string leaf, string target, string childLeaf)
    {
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
    }
    private static string TestLockedRename(string source, string destination)
    {
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
    }
    private static Process StartInternal(string[] arguments)
    {
        string host = Environment.ProcessPath;
        string assembly = Assembly.GetEntryAssembly() == null ? String.Empty : Assembly.GetEntryAssembly().Location;
        if (String.IsNullOrWhiteSpace(host) || String.IsNullOrWhiteSpace(assembly)) throw new IOException("INTERNAL_TEST_HELPER_IDENTITY_UNAVAILABLE");
        ProcessStartInfo start = new ProcessStartInfo();
        start.FileName = host;
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.RedirectStandardOutput = true;
        start.RedirectStandardError = true;
        start.ArgumentList.Add(assembly);
        foreach (string argument in arguments) start.ArgumentList.Add(argument);
        Process process = Process.Start(start);
        if (process == null) throw new IOException("INTERNAL_TEST_PROCESS_START_FAILED");
        return process;
    }
    private static string FinishInternal(Process process, int timeoutMilliseconds, string timeoutCode)
    {
        if (!process.WaitForExit(timeoutMilliseconds))
        {
            try { process.Kill(true); } catch { }
            process.WaitForExit(5000);
            throw new IOException(timeoutCode);
        }
        string stdout = process.StandardOutput.ReadToEnd().Trim();
        string stderr = process.StandardError.ReadToEnd().Trim();
        if (process.ExitCode != 0) throw new IOException("INTERNAL_TEST_CHILD_FAILED:" + process.ExitCode + ":" + stderr);
        return stdout;
    }
    private static string TestConcurrentOutputCreate(string target)
    {
        string suffix = Guid.NewGuid().ToString("N");
        string readyAName = "Local\\S3T03_RaceReadyA_" + suffix;
        string readyBName = "Local\\S3T03_RaceReadyB_" + suffix;
        string startName = "Local\\S3T03_RaceStart_" + suffix;
        using (EventWaitHandle readyA = new EventWaitHandle(false, EventResetMode.ManualReset, readyAName))
        using (EventWaitHandle readyB = new EventWaitHandle(false, EventResetMode.ManualReset, readyBName))
        using (EventWaitHandle start = new EventWaitHandle(false, EventResetMode.ManualReset, startName))
        {
            Process first = null, second = null;
            try
            {
                first = StartInternal(new[] { "--internal-race-try", target, readyAName, startName });
                second = StartInternal(new[] { "--internal-race-try", target, readyBName, startName });
                if (!readyA.WaitOne(10000) || !readyB.WaitOne(10000)) throw new IOException("RACE_CHILDREN_NOT_READY");
                start.Set();
                string resultA = FinishInternal(first, 10000, "RACE_CHILD_A_TIMEOUT");
                string resultB = FinishInternal(second, 10000, "RACE_CHILD_B_TIMEOUT");
                int created = (resultA == "CREATED" ? 1 : 0) + (resultB == "CREATED" ? 1 : 0);
                int collisions = (resultA == "COLLISION" ? 1 : 0) + (resultB == "COLLISION" ? 1 : 0);
                if (created != 1 || collisions != 1) throw new IOException("RACE_DID_NOT_PRODUCE_ONE_CREATE_AND_ONE_COLLISION:" + resultA + "," + resultB);
                if (Directory.GetFileSystemEntries(target).Length != 0) throw new IOException("CONCURRENT_OUTPUT_CREATE_TARGET_NOT_EMPTY");
                S3T03SafeFile.DeleteEmptyDirectory(target);
                return "RESULT=PASS_ATOMIC_CONCURRENT_OUTPUT_CREATE\nOUTPUT=" + target + "\nRACE_WINNERS=1\nRACE_COLLISIONS=1\nTARGET_FILES_WRITTEN=0\nFIXTURE_CLEANED=YES";
            }
            finally
            {
                start.Set();
                foreach (Process process in new[] { first, second })
                {
                    if (process == null) continue;
                    try { if (!process.HasExited) process.Kill(true); } catch { }
                    try { process.WaitForExit(5000); } catch { }
                    process.Dispose();
                }
            }
        }
    }
    private static string TestPinnedSourceWrite(string sourceRoot)
    {
        string path = Path.Combine(sourceRoot, "ps_config.tcl");
        string result = FinishInternal(StartInternal(new[] { "--internal-source-write-probe", path }), 10000, "SOURCE_WRITE_PROBE_TIMEOUT");
        if (result != "SOURCE_WRITE_DENIED") throw new IOException("PINNED_SOURCE_WRITE_PROBE_UNEXPECTED_RESULT:" + result);
        return "SOURCE_WRITE_ACCESS_DENIED_WHILE_PINNED=PASS";
    }
    public static string Begin(string repo, string script, string vendor, string source, string output, string phase)
    {
        RepoFinal = AcquireAnchor(repo);
        ScriptsFinal = AcquireSubtree(RepoFinal, Join(RepoFinal, "scripts"));
        if (!String.Equals(ScriptsFinal, Join(RepoFinal, "scripts"), StringComparison.OrdinalIgnoreCase)) throw new IOException("REPO_SCRIPTS_ALIAS_REJECTED");
        HoldRegularScript(script, ScriptsFinal);
        TmpFinal = AcquireSubtree(RepoFinal, Join(RepoFinal, "tmp"));
        if (!String.Equals(TmpFinal, Join(RepoFinal, "tmp"), StringComparison.OrdinalIgnoreCase)) throw new IOException("REPO_TMP_ALIAS_REJECTED");
        AuthorizedOutputParentFinal = AcquireSubtree(TmpFinal, Join(TmpFinal, "s3r04"));
        if (!String.Equals(AuthorizedOutputParentFinal, Join(TmpFinal, "s3r04"), StringComparison.OrdinalIgnoreCase)) throw new IOException("AUTHORIZED_S3R04_ALIAS_REJECTED");
        VendorFinal = AcquireSubtree(TmpFinal, vendor); SourceFinal = AcquireSubtree(VendorFinal, source);
        if (!Under(VendorFinal, SourceFinal)) throw new IOException("VENDOR_SOURCE_ESCAPES_VENDOR_ROOT");
        string portableOutput = output.Replace('\\', '/');
        foreach (string component in portableOutput.Split('/'))
            if (component == "." || component == "..") throw new IOException("OUTPUT_PATH_TRAVERSAL_REJECTED");
        string full = Path.GetFullPath(output); OutputLeaf = Path.GetFileName(full);
        if (String.IsNullOrWhiteSpace(OutputLeaf) || OutputLeaf == "." || OutputLeaf == "..") throw new IOException("OUTPUT_PATH_MUST_NAME_NEW_DIRECTORY");
        string inputParent = Normalize(Path.GetDirectoryName(full));
        if (!String.Equals(inputParent, AuthorizedOutputParentFinal, StringComparison.OrdinalIgnoreCase)) throw new IOException("OUTPUT_MUST_BE_DIRECT_CHILD_OF_AUTHORIZED_S3R04");
        string candidate = Join(AuthorizedOutputParentFinal, OutputLeaf);
        bool overlaps = Under(VendorFinal, candidate) || Under(candidate, VendorFinal);
        if (overlaps) throw new IOException("OUTPUT_AND_VENDOR_PATHS_MUST_BE_DISJOINT");
        if (ChildExists(GetDirectory(AuthorizedOutputParentFinal), OutputLeaf)) throw new IOException("OUTPUT_PATH_ALREADY_EXISTS");
        if (phase == "guard") return "RESULT=PASS_PATH_PREFLIGHT\nREPO=" + RepoFinal + "\nTMP=" + TmpFinal + "\nAUTHORIZED_OUTPUT_PARENT=" + AuthorizedOutputParentFinal + "\nVENDOR=" + VendorFinal + "\nSOURCE=" + SourceFinal + "\nOUTPUT=" + candidate;
        return "RESULT=PATHS_LOCKED";
    }
    public static string Prepare(string mode, string phase, string sourceRoot, string[] manifest)
    {
        if (phase == "guard") return "RESULT=PASS_PATH_PREFLIGHT\nREPO=" + RepoFinal + "\nTMP=" + TmpFinal + "\nAUTHORIZED_OUTPUT_PARENT=" + AuthorizedOutputParentFinal + "\nOUTPUT=" + Join(AuthorizedOutputParentFinal, OutputLeaf);
        if (phase == "race_test") return TestConcurrentOutputCreate(Join(AuthorizedOutputParentFinal, OutputLeaf));
        OutputFinal = CreateDirectoryChild(AuthorizedOutputParentFinal, OutputLeaf);
        if (Under(VendorFinal, OutputFinal) || Under(OutputFinal, VendorFinal)) throw new IOException("OUTPUT_AND_VENDOR_PATHS_MUST_BE_DISJOINT_AFTER_CREATE");
        if (phase == "source_lock_test") return "RESULT=PASS_SOURCE_LOCK_FIXTURE\nOUTPUT=" + OutputFinal + "\n" + TestPinnedSourceWrite(sourceRoot) + "\nTARGET_FILES_WRITTEN=0";
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
                CopyFile(sourcePath, parent, parts[parts.Length - 1], ComponentForMetadataPath(relative)); copied++;
            }
            foreach (string relative in new[] { "axi_dynclk_v1_0/component.xml", "rgb2dvi_v1_3/component.xml" })
            {
                string path = Path.Combine(metadataPath, relative.Replace('/', Path.DirectorySeparatorChar));
                try { using (S3T03SafeFile.OpenLeaf(path, false)) { } }
                catch (Win32Exception error) when (error.NativeErrorCode == 32) { continue; }
                throw new IOException("METADATA_WRITE_ACCESS_NOT_DENIED_WHILE_HASHING:" + relative);
            }
        } else if (mode != "native") throw new IOException("INVALID_MODE");
        return "RESULT=PASS_PATH_GUARD_PREPARATION\nOUTPUT=" + OutputFinal + "\nPROJECT=" + project + "\nMETADATA=" + metadataPath + "\nMETADATA_COUNT=" + copied + "\nMETADATA_WRITE_LOCK=PASS\nTARGET_FILES_WRITTEN=" + copied;
    }
}
