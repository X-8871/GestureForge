public static class S3T03SafeFile
{
    public const uint GenericRead = 0x80000000, GenericWrite = 0x40000000, FileReadAttributes = 0x80;
    public const uint ShareRead = 1, ShareWrite = 2, OpenExisting = 3, CreateNew = 1;
    public const uint OpenReparsePoint = 0x00200000, BackupSemantics = 0x02000000;
    public const uint AttributeDirectory = 0x10, AttributeReparsePoint = 0x400, FileTypeDisk = 1;
    private const uint FileBegin = 0;
    private const uint DirectoryFile = 0x00000001, SynchronousIo = 0x00000020, FileCreateDisposition = 2;
    private const uint DeleteAccess = 0x00010000, SynchronizeAccess = 0x00100000;

    [StructLayout(LayoutKind.Sequential)]
    private struct UnicodeString
    {
        public ushort Length, MaximumLength;
        public IntPtr Buffer;
    }
    [StructLayout(LayoutKind.Sequential)]
    private struct ObjectAttributes
    {
        public uint Length;
        public IntPtr RootDirectory, ObjectName;
        public uint Attributes;
        public IntPtr SecurityDescriptor, SecurityQualityOfService;
    }
    [StructLayout(LayoutKind.Sequential)]
    private struct IoStatusBlock
    {
        public IntPtr Status;
        public UIntPtr Information;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct FileInfo
    {
        public uint Attributes;
        public uint CreationLow, CreationHigh, AccessLow, AccessHigh, WriteLow, WriteHigh;
        public uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct FileDispositionInfo
    {
        [MarshalAs(UnmanagedType.Bool)] public bool DeleteFile;
    }

    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern SafeFileHandle CreateFileW(string name, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("ntdll.dll")]
    private static extern int NtCreateFile(out IntPtr handle, uint access, ref ObjectAttributes attributes,
        out IoStatusBlock status, IntPtr allocationSize, uint fileAttributes, uint share, uint disposition,
        uint options, IntPtr extendedAttributes, uint extendedAttributesLength);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool GetFileInformationByHandle(SafeFileHandle handle, out FileInfo info);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern uint GetFileType(SafeFileHandle handle);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern uint GetFinalPathNameByHandleW(SafeFileHandle handle, StringBuilder path, uint length, uint flags);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetFilePointerEx(SafeFileHandle handle, long distance, out long position, uint method);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetEndOfFile(SafeFileHandle handle);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool WriteFile(SafeFileHandle handle, byte[] buffer, uint count, out uint written, IntPtr overlapped);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool ReadFile(SafeFileHandle handle, byte[] buffer, uint count, out uint read, IntPtr overlapped);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool SetFileInformationByHandle(SafeFileHandle handle, int informationClass, ref FileDispositionInfo information, uint size);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern bool DeleteFileW(string path);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern bool RemoveDirectoryW(string path);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern bool CreateSymbolicLinkW(string link, string target, uint flags);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern bool CreateHardLinkW(string link, string target, IntPtr securityAttributes);
    [DllImport("kernel32.dll", SetLastError=true)] private static extern bool CloseHandle(IntPtr handle);

    private static string FullKey(string path) { return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar); }
    private static string FinalKey(SafeFileHandle handle)
    {
        StringBuilder value = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandleW(handle, value, (uint)value.Capacity, 0);
        if (length == 0 || length >= value.Capacity) throw new Win32Exception(Marshal.GetLastWin32Error(), "FINAL_PATH_QUERY_FAILED");
        string result = value.ToString();
        if (result.StartsWith("\\\\?\\UNC\\", StringComparison.OrdinalIgnoreCase)) result = "\\\\" + result.Substring(8);
        else if (result.StartsWith("\\\\?\\", StringComparison.OrdinalIgnoreCase)) result = result.Substring(4);
        return FullKey(result);
    }

    public static void ValidateAttributesForTest(uint attributes, bool directory)
    {
        if ((attributes & AttributeReparsePoint) != 0) throw new IOException("OUTPUT_REPARSE_POINT_REJECTED");
        if (directory != ((attributes & AttributeDirectory) != 0)) throw new IOException("OUTPUT_LEAF_TYPE_MISMATCH");
    }

    private static void Validate(SafeFileHandle handle, string path, bool directory)
    {
        FileInfo info;
        if (!GetFileInformationByHandle(handle, out info)) throw new Win32Exception(Marshal.GetLastWin32Error(), "HANDLE_INFO_FAILED");
        ValidateAttributesForTest(info.Attributes, directory);
        if (GetFileType(handle) != FileTypeDisk) throw new IOException("OUTPUT_NOT_DISK_FILE");
        if (!directory && info.Links != 1) throw new IOException("OUTPUT_LINK_COUNT_NOT_ONE");
        string actual = FinalKey(handle), expected = FullKey(path);
        if (!String.Equals(actual, expected, StringComparison.OrdinalIgnoreCase))
            throw new IOException("OUTPUT_FINAL_PATH_MISMATCH: " + actual + " != " + expected);
    }

    public static uint GetLinkCount(SafeFileHandle handle)
    {
        if (handle == null || handle.IsInvalid || handle.IsClosed) throw new IOException("OUTPUT_LINK_AUDIT_HANDLE_INVALID");
        FileInfo info;
        if (!GetFileInformationByHandle(handle, out info)) throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_LINK_AUDIT_INFO_FAILED");
        return info.Links;
    }

    public static void CreateHardLink(string link, string target)
    {
        string fullLink = Path.GetFullPath(link), fullTarget = Path.GetFullPath(target);
        if (!CreateHardLinkW(fullLink, fullTarget, IntPtr.Zero))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "CREATE_HARD_LINK_FAILED");
    }

    public static SafeFileHandle OpenLeaf(string path, bool createNew)
    {
        string full = Path.GetFullPath(path);
        SafeFileHandle handle = CreateFileW(full, GenericRead | GenericWrite | FileReadAttributes, ShareRead | ShareWrite,
            IntPtr.Zero, createNew ? CreateNew : OpenExisting, OpenReparsePoint, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), createNew ? "SECURE_CREATE_NEW_FAILED" : "SECURE_OPEN_EXISTING_FAILED");
        try { Validate(handle, full, false); return handle; } catch { handle.Dispose(); throw; }
    }

    public static SafeFileHandle OpenReadLeaf(string path)
    {
        string full = Path.GetFullPath(path);
        SafeFileHandle handle = CreateFileW(full, GenericRead | FileReadAttributes, ShareRead | ShareWrite,
            IntPtr.Zero, OpenExisting, OpenReparsePoint, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), "SECURE_READ_OPEN_FAILED");
        try { Validate(handle, full, false); return handle; } catch { handle.Dispose(); throw; }
    }

    public static SafeFileHandle OpenReadLease(string path)
    {
        string full = Path.GetFullPath(path);
        SafeFileHandle handle = CreateFileW(full, GenericRead | FileReadAttributes, ShareRead,
            IntPtr.Zero, OpenExisting, OpenReparsePoint, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), "SECURE_READ_LEASE_OPEN_FAILED");
        try { Validate(handle, full, false); return handle; } catch { handle.Dispose(); throw; }
    }

    private static SafeFileHandle CreateDirectoryChild(SafeFileHandle parent, string leaf)
    {
        if (String.IsNullOrWhiteSpace(leaf) || leaf == "." || leaf == ".." || leaf.IndexOfAny(new char[] { '\\', '/', ':' }) >= 0)
            throw new IOException("INVALID_DIRECTORY_LEAF");
        IntPtr name = Marshal.StringToHGlobalUni(leaf), nameStruct = IntPtr.Zero, raw = IntPtr.Zero;
        try
        {
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
            int status = NtCreateFile(out raw, DeleteAccess | FileReadAttributes | SynchronizeAccess, ref attributes, out io,
                IntPtr.Zero, 0, ShareRead | ShareWrite, FileCreateDisposition,
                DirectoryFile | OpenReparsePoint | SynchronousIo, IntPtr.Zero, 0);
            if (status < 0)
            {
                if ((uint)status == 0xC0000035) throw new IOException("SECURE_DIRECTORY_CREATE_COLLISION");
                throw new IOException("SECURE_DIRECTORY_NT_CREATE_FAILED_0x" + ((uint)status).ToString("X8"));
            }
            SafeFileHandle created = new SafeFileHandle(raw, true);
            raw = IntPtr.Zero;
            return created;
        }
        finally
        {
            if (raw != IntPtr.Zero) CloseHandle(raw);
            if (nameStruct != IntPtr.Zero) Marshal.FreeHGlobal(nameStruct);
            Marshal.FreeHGlobal(name);
        }
    }

    public static SafeFileHandle CreateDirectoryWithinRoot(string path, string boundaryRoot)
    {
        string full = Path.GetFullPath(path);
        List<SafeFileHandle> parents = LockParentChain(full, boundaryRoot);
        try
        {
            string leaf = Path.GetFileName(full);
            SafeFileHandle created = CreateDirectoryChild(parents[parents.Count - 1], leaf);
            try { Validate(created, full, true); return created; }
            catch { created.Dispose(); throw; }
        }
        finally { for (int i = parents.Count - 1; i >= 0; --i) parents[i].Dispose(); }
    }

    public static SafeFileHandle OpenDirectory(string path)
    {
        string full = Path.GetFullPath(path);
        SafeFileHandle handle = CreateFileW(full, FileReadAttributes, ShareRead | ShareWrite, IntPtr.Zero,
            OpenExisting, OpenReparsePoint | BackupSemantics, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), "SECURE_DIRECTORY_OPEN_FAILED");
        try { Validate(handle, full, true); return handle; } catch { handle.Dispose(); throw; }
    }

    private static void WriteAll(SafeFileHandle handle, byte[] bytes)
    {
        long position;
        if (!SetFilePointerEx(handle, 0, out position, FileBegin)) throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_SEEK_FAILED");
        if (!SetEndOfFile(handle)) throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_TRUNCATE_FAILED");
        int offset = 0;
        while (offset < bytes.Length)
        {
            int count = Math.Min(bytes.Length - offset, 1024 * 1024);
            byte[] part = new byte[count]; Buffer.BlockCopy(bytes, offset, part, 0, count);
            uint written;
            if (!WriteFile(handle, part, (uint)count, out written, IntPtr.Zero) || written == 0)
                throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_WRITE_FAILED");
            offset += (int)written;
        }
    }

    public static void WriteHeldInternal(SafeFileHandle handle, byte[] bytes) { WriteAll(handle, bytes); }
    private static List<SafeFileHandle> LockParentChain(string path, string boundaryRoot)
    {
        string full = Path.GetFullPath(path), root = FullKey(boundaryRoot) + Path.DirectorySeparatorChar;
        if (!full.StartsWith(root, StringComparison.OrdinalIgnoreCase)) throw new IOException("SECURE_WRITE_OUTSIDE_BOUNDARY_ROOT");
        root = root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        string parent = Path.GetDirectoryName(full);
        string remainder = parent.Substring(root.Length).Trim(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        List<SafeFileHandle> handles = new List<SafeFileHandle>();
        string current = root;
        try
        {
            handles.Add(OpenDirectory(current));
            if (remainder.Length > 0)
                foreach (string part in remainder.Split(new char[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar }, StringSplitOptions.RemoveEmptyEntries))
                {
                    current = Path.Combine(current, part);
                    handles.Add(OpenDirectory(current));
                }
            return handles;
        }
        catch { foreach (SafeFileHandle h in handles) h.Dispose(); throw; }
    }
    public static void WriteSingle(string path, bool createNew, byte[] bytes)
    {
        using (SafeFileHandle h = OpenLeaf(path, createNew)) WriteAll(h, bytes);
    }
    private static void MarkForDelete(SafeFileHandle handle)
    {
        FileDispositionInfo information = new FileDispositionInfo();
        information.DeleteFile = true;
        if (!SetFileInformationByHandle(handle, 4, ref information, (uint)Marshal.SizeOf(typeof(FileDispositionInfo))))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_SAFE_DELETE_FAILED");
    }
    private static SafeFileHandle OpenDeleteTarget(string path, bool directory)
    {
        string full = Path.GetFullPath(path);
        uint flags = OpenReparsePoint | (directory ? BackupSemantics : 0U);
        SafeFileHandle handle = CreateFileW(full, DeleteAccess | FileReadAttributes, ShareRead | ShareWrite,
            IntPtr.Zero, OpenExisting, flags, IntPtr.Zero);
        if (handle == null || handle.IsInvalid) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_SAFE_DELETE_OPEN_FAILED");
        return handle;
    }
    public static void DeleteRegularFile(string path)
    {
        string full = Path.GetFullPath(path);
        using (SafeFileHandle handle = OpenDeleteTarget(full, false))
        {
            Validate(handle, full, false);
            MarkForDelete(handle);
        }
    }
    public static void DeleteEmptyDirectory(string path)
    {
        string full = Path.GetFullPath(path);
        using (SafeFileHandle handle = OpenDeleteTarget(full, true))
        {
            Validate(handle, full, true);
            MarkForDelete(handle);
        }
    }
    public static void DeleteKnownReparsePoint(string path, bool directory)
    {
        string full = Path.GetFullPath(path);
        // 调用方仅传入本轮自测刚创建并记录的链接；这两个 Win32 API 只解除目录项，不递归访问目标。
        bool removed = directory ? RemoveDirectoryW(full) : DeleteFileW(full);
        if (!removed)
        {
            int error = Marshal.GetLastWin32Error();
            throw new Win32Exception(error, "SELFTEST_KNOWN_REPARSE_UNLINK_FAILED_WIN32_" + error.ToString());
        }
    }
    public static void WriteWithinRoot(string path, string boundaryRoot, bool createNew, byte[] bytes)
    {
        List<SafeFileHandle> parents = LockParentChain(path, boundaryRoot);
        try { using (SafeFileHandle h = OpenLeaf(path, createNew)) WriteAll(h, bytes); }
        finally { for (int i = parents.Count - 1; i >= 0; --i) parents[i].Dispose(); }
    }
    public static string WriteWithinRootAndHash(string path, string boundaryRoot, byte[] bytes)
    {
        List<SafeFileHandle> parents = LockParentChain(path, boundaryRoot);
        try
        {
            using (SafeFileHandle h = OpenLeaf(path, false))
            {
                WriteAll(h, bytes);
                using (SHA256 sha = SHA256.Create())
                {
                    byte[] digest = sha.ComputeHash(ReadHandle(h));
                    return BitConverter.ToString(digest).Replace("-", "");
                }
            }
        }
        finally { for (int i = parents.Count - 1; i >= 0; --i) parents[i].Dispose(); }
    }
    public static void WriteCreateOrExisting(string path, string boundaryRoot, byte[] bytes)
    {
        try { WriteWithinRoot(path, boundaryRoot, true, bytes); }
        catch (Win32Exception ex) { if (ex.NativeErrorCode != 80 && ex.NativeErrorCode != 183) throw; WriteWithinRoot(path, boundaryRoot, false, bytes); }
    }
    public static byte[] ReadHandle(SafeFileHandle handle)
    {
        FileInfo info;
        if (!GetFileInformationByHandle(handle, out info)) throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_READ_INFO_FAILED");
        long size = ((long)info.SizeHigh << 32) | info.SizeLow;
        if (size < 0 || size > 64L * 1024L * 1024L) throw new IOException("OUTPUT_READ_SIZE_OUT_OF_RANGE");
        long position;
        if (!SetFilePointerEx(handle, 0, out position, FileBegin)) throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_READ_SEEK_FAILED");
        using (MemoryStream stream = new MemoryStream((int)size))
        {
            byte[] buffer = new byte[65536];
            while (true)
            {
                uint read;
                if (!ReadFile(handle, buffer, (uint)buffer.Length, out read, IntPtr.Zero)) throw new Win32Exception(Marshal.GetLastWin32Error(), "OUTPUT_READ_FAILED");
                if (read == 0) break;
                stream.Write(buffer, 0, (int)read);
            }
            return stream.ToArray();
        }
    }
    public static bool TryCreateSymbolicLink(string link, string target, bool directory) { return CreateSymbolicLinkW(link, target, directory ? 1U : 0U); }
}

public sealed class S3T03OutputLeaseSet : IDisposable
{
    private readonly string root;
    private readonly Dictionary<string, SafeFileHandle> files = new Dictionary<string, SafeFileHandle>(StringComparer.OrdinalIgnoreCase);
    private readonly Dictionary<string, SafeFileHandle> dirs = new Dictionary<string, SafeFileHandle>(StringComparer.OrdinalIgnoreCase);
    public S3T03OutputLeaseSet(string outputRoot) { root = Path.GetFullPath(outputRoot).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar); }
    private string Check(string path)
    {
        string full = Path.GetFullPath(path);
        if (!String.Equals(full, root, StringComparison.OrdinalIgnoreCase) && !full.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("OUTPUT_LEASE_OUTSIDE_ROOT: " + full);
        return full;
    }
    public void LockDirectory(string path) { string p=Check(path); if (!dirs.ContainsKey(p)) dirs.Add(p, S3T03SafeFile.OpenDirectory(p)); }
    public bool HasDirectoryLease(string path)
    {
        string p=Check(path); SafeFileHandle h;
        return dirs.TryGetValue(p, out h) && h != null && !h.IsClosed && !h.IsInvalid;
    }
    public bool HasFileLease(string path)
    {
        string p=Check(path); SafeFileHandle h;
        return files.TryGetValue(p, out h) && h != null && !h.IsClosed && !h.IsInvalid;
    }
    public void ReleaseLeasesUnder(string path)
    {
        string boundary=Check(path), prefix=boundary + Path.DirectorySeparatorChar;
        List<string> fileKeys=new List<string>();
        foreach(string key in files.Keys)
            if(String.Equals(key,boundary,StringComparison.OrdinalIgnoreCase) || key.StartsWith(prefix,StringComparison.OrdinalIgnoreCase)) fileKeys.Add(key);
        foreach(string key in fileKeys) { files[key].Dispose(); files.Remove(key); }
        List<string> directoryKeys=new List<string>();
        foreach(string key in dirs.Keys)
            if(String.Equals(key,boundary,StringComparison.OrdinalIgnoreCase) || key.StartsWith(prefix,StringComparison.OrdinalIgnoreCase)) directoryKeys.Add(key);
        foreach(string key in directoryKeys) { dirs[key].Dispose(); dirs.Remove(key); }
    }
    public void AdoptDirectory(string path, SafeFileHandle handle)
    {
        string p = Check(path);
        if (dirs.ContainsKey(p)) throw new IOException("DUPLICATE_OUTPUT_DIRECTORY_LEASE: " + p);
        dirs.Add(p, handle);
    }
    public void CreateDirectory(string path)
    {
        string p = Check(path);
        if (dirs.ContainsKey(p)) throw new IOException("DUPLICATE_OUTPUT_DIRECTORY_LEASE: " + p);
        string parent = Path.GetDirectoryName(p);
        SafeFileHandle parentHandle;
        if (!dirs.TryGetValue(parent, out parentHandle)) throw new IOException("OUTPUT_DIRECTORY_PARENT_LEASE_MISSING: " + parent);
        SafeFileHandle created = S3T03SafeFile.CreateDirectoryWithinRoot(p, root);
        dirs.Add(p, created);
    }
    public void LockDirectoryChain(string path)
    {
        string full = Check(path);
        string relative = full.Length == root.Length ? "" : full.Substring(root.Length).TrimStart(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        LockDirectory(root);
        string current = root;
        if (relative.Length == 0) return;
        foreach (string part in relative.Split(new char[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar }, StringSplitOptions.RemoveEmptyEntries))
        {
            current = Path.Combine(current, part);
            LockDirectory(current);
        }
    }
    public void LockParentDirectory(string path)
    {
        string p = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        if (!root.StartsWith(p + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new IOException("OUTPUT_PARENT_LOCK_OUTSIDE_CHAIN: " + p);
        if (!dirs.ContainsKey(p)) dirs.Add(p, S3T03SafeFile.OpenDirectory(p));
    }
    public void LockExisting(string path) { string p=Check(path); if (files.ContainsKey(p)) throw new IOException("DUPLICATE_OUTPUT_LEASE: " + p); files.Add(p, S3T03SafeFile.OpenLeaf(p, false)); }
    public void LockExistingReadOnly(string path) { string p=Check(path); if (files.ContainsKey(p)) throw new IOException("DUPLICATE_OUTPUT_LEASE: " + p); files.Add(p, S3T03SafeFile.OpenReadLease(p)); }
    public void SealExistingReadOnly(string path)
    {
        string p=Check(path); SafeFileHandle previous;
        if (!files.TryGetValue(p, out previous) || previous.IsClosed || previous.IsInvalid) throw new IOException("OUTPUT_LEASE_MISSING_FOR_SEAL: " + p);
        files.Remove(p);
        previous.Dispose();
        SafeFileHandle sealedHandle = null;
        try { sealedHandle = S3T03SafeFile.OpenReadLease(p); files.Add(p, sealedHandle); }
        catch { if (sealedHandle != null) sealedHandle.Dispose(); throw; }
    }
    public void ReserveNew(string path) { string p=Check(path); if (files.ContainsKey(p)) throw new IOException("DUPLICATE_OUTPUT_LEASE: " + p); files.Add(p, S3T03SafeFile.OpenLeaf(p, true)); }
    public void WriteHeld(string path, byte[] bytes) { string p=Check(path); SafeFileHandle h; if(!files.TryGetValue(p,out h)) throw new IOException("OUTPUT_LEASE_MISSING: " + p); S3T03SafeFile.WriteHeldInternal(h,bytes); }
    public byte[] ReadHeld(string path) { string p=Check(path); SafeFileHandle h; if(!files.TryGetValue(p,out h)) throw new IOException("OUTPUT_LEASE_MISSING: " + p); return S3T03SafeFile.ReadHandle(h); }
    public string AuditFileLinkCounts()
    {
        int checkedCount = 0;
        foreach (KeyValuePair<string, SafeFileHandle> entry in files)
        {
            string pathBase64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(entry.Key));
            try
            {
                uint links = S3T03SafeFile.GetLinkCount(entry.Value);
                if (links != 1)
                {
                    string code = links > 1 ? "OUTPUT_HARDLINK_DETECTED" : "OUTPUT_LINK_COUNT_INVALID";
                    return code + ";PATH_B64=" + pathBase64 + ";LINK_COUNT=" + links + ";FILES_CHECKED=" + checkedCount;
                }
            }
            catch (Exception ex)
            {
                string message = (ex.GetType().Name + ":" + ex.Message).Replace("\r", "_").Replace("\n", "_").Replace(";", "_");
                string errorBase64 = Convert.ToBase64String(Encoding.UTF8.GetBytes(message));
                return "OUTPUT_LINK_AUDIT_FAILED;PATH_B64=" + pathBase64 + ";ERROR_B64=" + errorBase64 + ";FILES_CHECKED=" + checkedCount;
            }
            checkedCount++;
        }
        return "PASS;FILES_CHECKED=" + checkedCount;
    }
    public void Dispose() { foreach(SafeFileHandle h in files.Values) h.Dispose(); foreach(SafeFileHandle h in dirs.Values) h.Dispose(); files.Clear(); dirs.Clear(); }
}

public sealed class S3T03TreeMonitor : IDisposable
{
    private FileSystemWatcher watcher;
    private int changeCount;
    private int errorCount;
    private string lastError = "";

    public S3T03TreeMonitor(string root)
    {
        watcher = new FileSystemWatcher(Path.GetFullPath(root));
        watcher.IncludeSubdirectories = true;
        watcher.NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName | NotifyFilters.LastWrite |
            NotifyFilters.Size | NotifyFilters.Attributes | NotifyFilters.CreationTime | NotifyFilters.Security;
        watcher.InternalBufferSize = 65536;
        watcher.Changed += OnChanged;
        watcher.Created += OnChanged;
        watcher.Deleted += OnChanged;
        watcher.Renamed += OnRenamed;
        watcher.Error += OnError;
        watcher.EnableRaisingEvents = true;
    }

    private void OnChanged(object sender, FileSystemEventArgs args) { System.Threading.Interlocked.Increment(ref changeCount); }
    private void OnRenamed(object sender, RenamedEventArgs args) { System.Threading.Interlocked.Increment(ref changeCount); }
    private void OnError(object sender, ErrorEventArgs args)
    {
        System.Threading.Interlocked.Increment(ref errorCount);
        Exception error = args.GetException();
        lastError = error == null ? "UNKNOWN" : error.GetType().Name + ":" + error.Message.Replace("\r", "_").Replace("\n", "_");
    }

    public string Status()
    {
        int changes = System.Threading.Interlocked.CompareExchange(ref changeCount, 0, 0);
        int errors = System.Threading.Interlocked.CompareExchange(ref errorCount, 0, 0);
        return "EVENT_COUNT=" + changes + ";ERROR_COUNT=" + errors + ";ERROR=" + lastError;
    }

    public void StopAndDrain()
    {
        if (watcher == null) return;
        System.Threading.Thread.Sleep(1000);
        watcher.EnableRaisingEvents = false;
        System.Threading.Thread.Sleep(100);
    }

    public void Dispose()
    {
        if (watcher == null) return;
        watcher.EnableRaisingEvents = false;
        watcher.Dispose();
        watcher = null;
    }
}
