using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Security.Cryptography;
using Microsoft.Win32.SafeHandles;

internal static class SecureFileCommands
{
    private const long MaximumPayloadBytes = 64L * 1024L * 1024L;
    private const string SourceRelative = "course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project";

    private static string Canonical(string path, string label)
    {
        if (String.IsNullOrWhiteSpace(path) || !Path.IsPathFullyQualified(path)) throw new IOException(label + "_MUST_BE_ABSOLUTE");
        string portable = path.Replace('\\', '/');
        foreach (string component in portable.Split('/'))
            if (component == "." || component == "..") throw new IOException(label + "_TRAVERSAL_REJECTED");
        string root = Path.GetPathRoot(path);
        if (path.IndexOfAny(new[] { '\0', '\r', '\n', '\t' }) >= 0 || path.IndexOf(':', root.Length) >= 0)
            throw new IOException(label + "_CONTROL_OR_ALTERNATE_STREAM_REJECTED");
        return Path.GetFullPath(path);
    }

    private static string AuthorizedRoot()
    {
        return T03InternalCommands.GetAuthorizedOutputRootForInternalUse();
    }

    private static string RepositoryRoot(string authorizedRoot)
    {
        DirectoryInfo tmp = Directory.GetParent(authorizedRoot);
        if (tmp == null || !String.Equals(tmp.Name, "tmp", StringComparison.OrdinalIgnoreCase) || tmp.Parent == null)
            throw new IOException("SECURE_IO_REPOSITORY_ROOT_DERIVATION_FAILED");
        return Path.GetFullPath(tmp.Parent.FullName);
    }

    private static string ValidateRunRoot(string runRoot)
    {
        string authorized = AuthorizedRoot();
        string full = Canonical(runRoot, "SECURE_IO_RUN_ROOT");
        if (!String.Equals(Path.GetDirectoryName(full), authorized, StringComparison.OrdinalIgnoreCase))
            throw new IOException("SECURE_IO_RUN_ROOT_NOT_DIRECT_S3R04_CHILD");
        using (S3T03SafeFile.OpenDirectory(full)) { }
        return full;
    }

    private static string ValidateOutputLeaf(string runRoot, string path)
    {
        string full = Canonical(path, "SECURE_IO_TARGET");
        string prefix = runRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        if (!full.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) throw new IOException("SECURE_IO_TARGET_OUTSIDE_RUN_ROOT");
        return full;
    }

    private static byte[] ReadLimitedInput()
    {
        using (MemoryStream memory = new MemoryStream())
        {
            Console.OpenStandardInput().CopyTo(memory);
            if (memory.Length > MaximumPayloadBytes * 4 / 3 + 16) throw new IOException("SECURE_IO_INPUT_TOO_LARGE");
            return Convert.FromBase64String(System.Text.Encoding.ASCII.GetString(memory.ToArray()).Trim());
        }
    }

    public static int Run(string[] args)
    {
        try
        {
            if (args == null || args.Length == 0) throw new ArgumentException("SECURE_IO_OPERATION_REQUIRED");
            string operation = args[0];
            if (operation == "write" || operation == "write-hash") return Write(operation, args);
            if (operation == "read") return Read(args, false);
            if (operation == "read-input") return Read(args, true);
            if (operation == "hash-files") return HashFiles(args);
            if (operation == "tree-hash") return TreeHash(args);
            if (operation == "create-run-root") return CreateRunRoot(args);
            if (operation == "create-directory") return CreateOutputDirectory(args);
            if (operation == "delete-owned-test-root") return DeleteOwnedTestRoot(args);
            throw new ArgumentException("UNKNOWN_SECURE_IO_OPERATION: " + operation);
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("S3_SECURE_IO=FAIL:" + error.Message.Replace('\r', '_').Replace('\n', '_'));
            return 3;
        }
    }

    private static int Write(string operation, string[] args)
    {
        if (args.Length != 4) throw new ArgumentException("SECURE_IO_WRITE_ARGUMENTS_INVALID");
        string root = ValidateRunRoot(args[1]);
        string path = ValidateOutputLeaf(root, args[2]);
        bool createNew;
        if (args[3] == "CreateNew") createNew = true;
        else if (args[3] == "OpenExisting") createNew = false;
        else throw new ArgumentException("SECURE_IO_WRITE_MODE_INVALID");
        if (operation == "write-hash" && createNew) throw new ArgumentException("SECURE_IO_HASH_WRITE_REQUIRES_EXISTING_LEAF");
        byte[] bytes = ReadLimitedInput();
        if (operation == "write-hash")
        {
            string digest = S3T03SafeFile.WriteWithinRootAndHash(path, root, bytes);
            Console.WriteLine("S3_SECURE_WRITE=PASS:" + digest);
        }
        else
        {
            S3T03SafeFile.WriteWithinRoot(path, root, createNew, bytes);
            Console.WriteLine("S3_SECURE_WRITE=PASS");
        }
        return 0;
    }

    private static byte[] ReadLeaf(string path)
    {
        using (SafeFileHandle handle = S3T03SafeFile.OpenReadLeaf(path)) return S3T03SafeFile.ReadHandle(handle);
    }

    private static int Read(string[] args, bool allowTrustedInput)
    {
        if (args.Length != 3) throw new ArgumentException("SECURE_IO_READ_ARGUMENTS_INVALID");
        string root = ValidateRunRoot(args[1]);
        string path = Canonical(args[2], "SECURE_IO_READ_TARGET");
        if (allowTrustedInput)
        {
            bool allowed = false;
            foreach (string item in TrustedReadRoots(root)) if (Under(item, path)) { allowed = true; break; }
            if (!allowed) throw new IOException("SECURE_IO_READ_PATH_OUTSIDE_TRUSTED_ROOTS");
        }
        else path = ValidateOutputLeaf(root, path);
        byte[] bytes = ReadLeaf(path);
        Console.WriteLine("S3_SECURE_READ=" + Convert.ToHexString(SHA256.HashData(bytes)) + ":" + Convert.ToBase64String(bytes));
        return 0;
    }

    private static bool Under(string root, string path)
    {
        string prefix = root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
        return path.StartsWith(prefix, StringComparison.OrdinalIgnoreCase);
    }

    private static string[] TrustedReadRoots(string runRoot)
    {
        string repository = RepositoryRoot(AuthorizedRoot());
        string vendor = Path.GetFullPath(Path.Combine(repository, "tmp", "stage3_reference", "AX7020_2023.1"));
        string source = Path.GetFullPath(Path.Combine(vendor, SourceRelative.Replace('/', Path.DirectorySeparatorChar)));
        return new[]
        {
            Path.GetFullPath(Path.Combine(repository, "scripts")),
            source,
            Path.GetFullPath(Path.Combine(runRoot, "project")),
            Path.GetFullPath(Path.Combine(runRoot, "vendor_ip_metadata")),
            Path.GetFullPath(Path.Combine(runRoot, "reports")),
            Path.GetFullPath(Path.Combine(runRoot, "inputs")),
            Path.GetFullPath(Path.Combine(runRoot, "checkpoints")),
            Path.GetFullPath(Path.Combine(runRoot, "sentinels"))
        };
    }

    private static int HashFiles(string[] args)
    {
        if (args.Length < 3) throw new ArgumentException("SECURE_IO_HASH_FILES_ARGUMENTS_INVALID");
        string runRoot = ValidateRunRoot(args[1]);
        string[] roots = TrustedReadRoots(runRoot);
        HashSet<string> unique = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (string raw in args.Skip(2))
        {
            string path = Canonical(raw, "SECURE_IO_HASH_PATH");
            bool allowed = false;
            foreach (string root in roots) if (Under(root, path)) { allowed = true; break; }
            if (!allowed) throw new IOException("SECURE_IO_HASH_PATH_OUTSIDE_TRUSTED_ROOTS");
            if (!unique.Add(path)) throw new IOException("SECURE_IO_HASH_PATH_DUPLICATE");
            using (SafeFileHandle handle = S3T03SafeFile.OpenReadLeaf(path))
            using (FileStream stream = new FileStream(handle, FileAccess.Read))
                Console.WriteLine(Convert.ToHexString(SHA256.HashData(stream)) + "\t" + path);
        }
        Console.Out.Flush();
        return 0;
    }

    private static int TreeHash(string[] args)
    {
        if (args.Length != 3) throw new ArgumentException("SECURE_IO_TREE_HASH_ARGUMENTS_INVALID");
        string runRoot = ValidateRunRoot(args[1]);
        string root = Canonical(args[2], "SECURE_IO_TREE_ROOT");
        bool allowed = false;
        foreach (string item in TrustedReadRoots(runRoot))
            if (String.Equals(item, root, StringComparison.OrdinalIgnoreCase)) { allowed = true; break; }
        if (!allowed) throw new IOException("SECURE_IO_TREE_ROOT_NOT_ALLOWLISTED");

        SortedDictionary<string, string> hashes = new SortedDictionary<string, string>(StringComparer.Ordinal);
        List<SafeFileHandle> directoryHandles = new List<SafeFileHandle>();
        Stack<string> pending = new Stack<string>();
        try
        {
            directoryHandles.Add(S3T03SafeFile.OpenDirectory(root));
            pending.Push(root);
            string prefix = root.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
            while (pending.Count > 0)
            {
                string directory = pending.Pop();
                foreach (string entry in Directory.GetFileSystemEntries(directory))
                {
                    string full = Canonical(entry, "SECURE_IO_TREE_ENTRY");
                    if (!Under(root, full)) throw new IOException("SECURE_IO_TREE_ENTRY_OUTSIDE_ROOT");
                    FileAttributes attributes = File.GetAttributes(full);
                    if ((attributes & FileAttributes.ReparsePoint) != 0) throw new IOException("SECURE_IO_TREE_REPARSE_POINT_REJECTED");
                    if ((attributes & FileAttributes.Directory) != 0)
                    {
                        directoryHandles.Add(S3T03SafeFile.OpenDirectory(full));
                        pending.Push(full);
                        continue;
                    }
                    string relative = full.Substring(prefix.Length).Replace('\\', '/');
                    if (String.IsNullOrWhiteSpace(relative) || relative.Contains('\t') || relative.Contains('\r') || relative.Contains('\n') || relative.Contains(':'))
                        throw new IOException("SECURE_IO_TREE_RELATIVE_PATH_INVALID");
                    using (SafeFileHandle handle = S3T03SafeFile.OpenReadLeaf(full))
                    using (FileStream stream = new FileStream(handle, FileAccess.Read))
                    {
                        if (stream.Length > MaximumPayloadBytes) throw new IOException("SECURE_IO_TREE_FILE_TOO_LARGE");
                        if (!hashes.TryAdd(relative, Convert.ToHexString(SHA256.HashData(stream))))
                            throw new IOException("SECURE_IO_TREE_DUPLICATE_RELATIVE_PATH");
                    }
                }
            }
        }
        finally
        {
            for (int index = directoryHandles.Count - 1; index >= 0; index--) directoryHandles[index].Dispose();
        }
        if (hashes.Count == 0) throw new IOException("SECURE_IO_TREE_EMPTY");
        foreach (KeyValuePair<string, string> entry in hashes)
            Console.WriteLine("S3_SECURE_TREE_SHA256=" + entry.Value + "\t" + entry.Key);
        StringBuilder canonical = new StringBuilder();
        canonical.Append("FILE_COUNT=").Append(hashes.Count.ToString(System.Globalization.CultureInfo.InvariantCulture)).Append('\n');
        foreach (KeyValuePair<string, string> entry in hashes)
            canonical.Append(entry.Value).Append("  ").Append(entry.Key).Append('\n');
        Console.WriteLine("S3_SECURE_TREE_ROOT_SHA256=" + Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(canonical.ToString()))));
        Console.Out.Flush();
        return 0;
    }

    private static int CreateRunRoot(string[] args)
    {
        if (args.Length != 2) throw new ArgumentException("SECURE_IO_CREATE_RUN_ROOT_ARGUMENTS_INVALID");
        string target = Canonical(args[1], "SECURE_IO_CREATE_RUN_ROOT");
        string authorized = AuthorizedRoot();
        if (!String.Equals(Path.GetDirectoryName(target), authorized, StringComparison.OrdinalIgnoreCase))
            throw new IOException("SECURE_IO_CREATE_RUN_ROOT_NOT_DIRECT_S3R04_CHILD");
        using (S3T03SafeFile.CreateDirectoryWithinRoot(target, authorized)) { }
        Console.WriteLine("S3_SECURE_DIRECTORY_CREATE=PASS:" + target);
        return 0;
    }

    private static int CreateOutputDirectory(string[] args)
    {
        if (args.Length != 3) throw new ArgumentException("SECURE_IO_CREATE_DIRECTORY_ARGUMENTS_INVALID");
        string runRoot = ValidateRunRoot(args[1]);
        string target = ValidateOutputLeaf(runRoot, args[2]);
        if (!String.Equals(Path.GetDirectoryName(target), runRoot, StringComparison.OrdinalIgnoreCase))
            throw new IOException("SECURE_IO_DIRECTORY_MUST_BE_DIRECT_RUN_ROOT_CHILD");
        using (S3T03SafeFile.CreateDirectoryWithinRoot(target, runRoot)) { }
        Console.WriteLine("S3_SECURE_DIRECTORY_CREATE=PASS:" + target);
        return 0;
    }

    private static int DeleteOwnedTestRoot(string[] args)
    {
        if (args.Length != 3) throw new ArgumentException("SECURE_IO_DELETE_OWNED_ROOT_ARGUMENTS_INVALID");
        string root = Canonical(args[1], "SECURE_IO_DELETE_OWNED_ROOT");
        string authorized = AuthorizedRoot();
        if (!String.Equals(Path.GetDirectoryName(root), authorized, StringComparison.OrdinalIgnoreCase))
            throw new IOException("SECURE_IO_DELETE_ROOT_NOT_DIRECT_S3R04_CHILD");
        if (!Path.GetFileName(root).StartsWith("s3_t03_tcl_selftest_", StringComparison.Ordinal))
            throw new IOException("SECURE_IO_DELETE_ROOT_NAME_NOT_SELFTEST_OWNED");
        string markerPath = Path.Combine(root, ".s3_t03_selftest_owner");
        string marker = Encoding.UTF8.GetString(ReadLeaf(markerPath));
        if (!String.Equals(marker, args[2], StringComparison.Ordinal)) throw new IOException("SECURE_IO_DELETE_OWNER_MARKER_MISMATCH");

        List<string> files = new List<string>();
        List<string> directories = new List<string>();
        Stack<string> pending = new Stack<string>();
        pending.Push(root);
        while (pending.Count > 0)
        {
            string directory = pending.Pop();
            using (S3T03SafeFile.OpenDirectory(directory)) { }
            directories.Add(directory);
            foreach (string entry in Directory.GetFileSystemEntries(directory))
            {
                string full = Canonical(entry, "SECURE_IO_DELETE_ENTRY");
                if (!Under(root, full)) throw new IOException("SECURE_IO_DELETE_ENTRY_OUTSIDE_OWNED_ROOT");
                FileAttributes attributes = File.GetAttributes(full);
                if ((attributes & FileAttributes.ReparsePoint) != 0) throw new IOException("SECURE_IO_DELETE_REPARSE_REJECTED");
                if ((attributes & FileAttributes.Directory) != 0) pending.Push(full);
                else files.Add(full);
            }
        }
        foreach (string file in files) S3T03SafeFile.DeleteRegularFile(file);
        directories.Sort((left, right) => right.Length.CompareTo(left.Length));
        foreach (string directory in directories) S3T03SafeFile.DeleteEmptyDirectory(directory);
        Console.WriteLine("SELFTEST_TMP_CLEANUP=PASS");
        return 0;
    }
}
