internal static class PathGuardCommand
{
    private const string ExpectedVendorCommit = "fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327";
    private const string SourceRelative = "course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project";
    private static readonly string[] AllowedPhases = { "guard", "race_test", "lock_test", "source_lock_test", "subpath_reparse_test", "bd", "hdl" };

    public static int Run(string[] args)
    {
        try
        {
            Dictionary<string, string> options = Parse(args);
            string repoRoot = GetRequired(options, "--repo-root");
            string vendorRoot = GetRequired(options, "--vendor-root");
            string outputDir = GetRequired(options, "--output-dir");
            string mode = options.TryGetValue("--mode", out string selectedMode) ? selectedMode : "native";
            string phase = options.TryGetValue("--phase", out string selectedPhase) ? selectedPhase : "bd";

            if (!OperatingSystem.IsWindows()) throw new IOException("WINDOWS_PATH_GUARD_REQUIRES_WINDOWS");
            if (mode != "native" && mode != "azynq_metadata") throw new IOException("INVALID_MODE");
            if (Array.IndexOf(AllowedPhases, phase) < 0) throw new IOException("INVALID_PHASE");

            repoRoot = RequireAbsolutePath(repoRoot, "REPO_ROOT");
            vendorRoot = RequireAbsolutePath(vendorRoot, "VENDOR_ROOT");
            outputDir = RequireAbsolutePath(outputDir, "OUTPUT_DIR");

            string expectedVendorRoot = Path.GetFullPath(Path.Combine(repoRoot, "tmp", "stage3_reference", "AX7020_2023.1"));
            if (!PathEquals(vendorRoot, expectedVendorRoot)) throw new IOException("VENDOR_ROOT_NOT_FIXED_REFERENCE_COPY");
            string sourceRoot = Path.GetFullPath(Path.Combine(vendorRoot, SourceRelative.Replace('/', Path.DirectorySeparatorChar)));
            string guardScript = Path.GetFullPath(Path.Combine(repoRoot, "scripts", "s3_validate_hdmi_only_bd.tcl"));
            if (!File.Exists(guardScript)) throw new IOException("SHARED_GUARD_SCRIPT_MISSING");

            string initialStatus = S3PathGuardR3.Begin(repoRoot, guardScript, vendorRoot, sourceRoot, outputDir, phase);
            string actualCommit = ReadGit(repoRoot, vendorRoot, "rev-parse", "HEAD").Trim();
            if (!String.Equals(actualCommit, ExpectedVendorCommit, StringComparison.Ordinal)) throw new IOException("VENDOR_COMMIT_MISMATCH");

            string changes = ReadGit(repoRoot, vendorRoot, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching", "--", SourceRelative);
            if (!String.IsNullOrWhiteSpace(changes)) throw new IOException("VENDOR_SOURCE_NOT_CLEAN");

            string[] manifest = ReadManifest(vendorRoot);
            string[] pinnedPaths = new[] { "ps_config.tcl", "pl_config.tcl" }.Concat(manifest).ToArray();
            S3PathGuardR3.HoldSourceFile(sourceRoot, "ps_config.tcl");
            S3PathGuardR3.HoldSourceFile(sourceRoot, "pl_config.tcl");
            foreach (string relative in manifest) S3PathGuardR3.HoldSourceFile(sourceRoot, relative);
            ValidateVendorInputs(sourceRoot, manifest);
            VerifyPinnedInputs(repoRoot, vendorRoot, sourceRoot, actualCommit, pinnedPaths);

            string result = S3PathGuardR3.Prepare(mode, phase, sourceRoot, manifest);
            if (String.IsNullOrWhiteSpace(result)) throw new IOException("PATH_GUARD_EMPTY_RESULT");
            if (phase != "guard" && initialStatus != "RESULT=PATHS_LOCKED")
            {
                throw new IOException("PATH_GUARD_UNEXPECTED_INITIAL_RESULT");
            }

            Console.WriteLine(result.TrimEnd('\r', '\n'));
            Console.WriteLine("VENDOR_COMMIT_ACTUAL=" + actualCommit);
            Console.WriteLine("PINNED_SOURCE_GIT_BLOBS=PASS;FILES=" + pinnedPaths.Length.ToString(System.Globalization.CultureInfo.InvariantCulture));
            Console.WriteLine("POST_LOCK_GIT_STATUS=PASS");
            string metadataRoot = StatusValue(result, "METADATA");
            if (!String.IsNullOrEmpty(metadataRoot))
            {
                int metadataCount = Int32.Parse(StatusValue(result, "METADATA_COUNT"), System.Globalization.CultureInfo.InvariantCulture);
                if (metadataCount != manifest.Length) throw new IOException("GUARDED_METADATA_COPY_FILE_COUNT_MISMATCH");
                MetadataDigest digest = ComputeMetadataDigest(metadataRoot, manifest);
                Console.WriteLine("METADATA_COPY_FILE_COUNT=" + metadataCount.ToString(System.Globalization.CultureInfo.InvariantCulture));
                Console.WriteLine("METADATA_TREE_SHA256=" + digest.TreeSha256);
                Console.WriteLine("METADATA_COPY_MANIFEST_SHA256=" + digest.ManifestSha256);
                Console.WriteLine("METADATA_COPY_MANIFEST_TEXT_B64=" + Convert.ToBase64String(Encoding.UTF8.GetBytes(digest.ManifestText)));
            }
            Console.Out.Flush();
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("OUTPUT_PATH_ISOLATION_FAILED: " + error.Message);
            return 2;
        }
    }

    private static Dictionary<string, string> Parse(string[] args)
    {
        Dictionary<string, string> options = new Dictionary<string, string>(StringComparer.Ordinal);
        if (args == null || args.Length == 0) throw new ArgumentException("PATH_GUARD_ARGUMENTS_REQUIRED");
        for (int index = 0; index < args.Length; index++)
        {
            string key = args[index];
            if (key != "--repo-root" && key != "--vendor-root" && key != "--output-dir" && key != "--mode" && key != "--phase")
                throw new ArgumentException("UNKNOWN_PATH_GUARD_ARGUMENT: " + key);
            if (options.ContainsKey(key)) throw new ArgumentException("DUPLICATE_PATH_GUARD_ARGUMENT: " + key);
            if (index + 1 >= args.Length || args[index + 1].StartsWith("--", StringComparison.Ordinal))
                throw new ArgumentException("MISSING_PATH_GUARD_ARGUMENT_VALUE: " + key);
            options.Add(key, args[++index]);
        }
        return options;
    }

    private static string GetRequired(Dictionary<string, string> options, string name)
    {
        if (!options.TryGetValue(name, out string value) || String.IsNullOrWhiteSpace(value))
            throw new ArgumentException("REQUIRED_PATH_GUARD_ARGUMENT_MISSING: " + name);
        return value;
    }

    private static string RequireAbsolutePath(string path, string label)
    {
        if (!Path.IsPathFullyQualified(path)) throw new IOException(label + "_MUST_BE_ABSOLUTE");
        string portable = path.Replace('\\', '/');
        foreach (string component in portable.Split('/'))
            if (component == "." || component == "..") throw new IOException(label + "_TRAVERSAL_REJECTED");
        return Path.GetFullPath(path);
    }

    private static bool PathEquals(string left, string right)
    {
        return String.Equals(Path.TrimEndingDirectorySeparator(Path.GetFullPath(left)),
            Path.TrimEndingDirectorySeparator(Path.GetFullPath(right)), StringComparison.OrdinalIgnoreCase);
    }

    private static string ReadGit(string repoRoot, string vendorRoot, params string[] arguments)
    {
        ProcessStartInfo start = new ProcessStartInfo();
        start.FileName = "git";
        if (!String.IsNullOrEmpty(repoRoot)) start.WorkingDirectory = repoRoot;
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.RedirectStandardOutput = true;
        start.RedirectStandardError = true;
        start.StandardOutputEncoding = new UTF8Encoding(false);
        start.StandardErrorEncoding = new UTF8Encoding(false);
        start.ArgumentList.Add("-C");
        start.ArgumentList.Add(vendorRoot);
        foreach (string argument in arguments) start.ArgumentList.Add(argument);

        using (Process process = Process.Start(start))
        {
            if (process == null) throw new IOException("GIT_PROCESS_START_FAILED");
            string stdout = process.StandardOutput.ReadToEnd();
            string stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();
            if (process.ExitCode != 0) throw new IOException("GIT_COMMAND_FAILED: " + stderr.Trim());
            return stdout;
        }
    }

    private static string[] ReadManifest(string vendorRoot)
    {
        string output = ReadGit(String.Empty, vendorRoot, "ls-files", "-z", "--", SourceRelative + "/my_ip");
        string prefix = SourceRelative + "/my_ip/";
        List<string> manifest = new List<string>();
        foreach (string entry in output.Split('\0', StringSplitOptions.RemoveEmptyEntries))
        {
            if (!entry.StartsWith(prefix, StringComparison.Ordinal)) throw new IOException("UNEXPECTED_TRACKED_IP_PATH");
            string relative = entry.Substring((SourceRelative + "/").Length);
            ValidateRelativePath(relative);
            manifest.Add(relative);
        }
        manifest.Sort(StringComparer.Ordinal);
        if (manifest.Count == 0) throw new IOException("EMPTY_TRACKED_IP_REPOSITORY");
        if (manifest.Distinct(StringComparer.Ordinal).Count() != manifest.Count) throw new IOException("DUPLICATE_TRACKED_IP_PATH");
        return manifest.ToArray();
    }

    private static Dictionary<string, string> ReadHeadBlobIds(string vendorRoot, string fixedCommit)
    {
        string output = ReadGit(String.Empty, vendorRoot, "ls-tree", "-rz", "-r", fixedCommit, "--", SourceRelative);
        string prefix = SourceRelative + "/";
        Dictionary<string, string> blobs = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (string record in output.Split('\0', StringSplitOptions.RemoveEmptyEntries))
        {
            int tab = record.IndexOf('\t');
            if (tab <= 0) throw new IOException("MALFORMED_HEAD_TREE_RECORD");
            string[] metadata = record.Substring(0, tab).Split(' ', StringSplitOptions.RemoveEmptyEntries);
            if (metadata.Length != 3 || metadata[1] != "blob") continue;
            string path = record.Substring(tab + 1);
            if (!path.StartsWith(prefix, StringComparison.Ordinal)) throw new IOException("HEAD_TREE_PATH_ESCAPES_VENDOR_SOURCE");
            string relative = path.Substring(prefix.Length);
            if (!blobs.TryAdd(relative, metadata[2])) throw new IOException("DUPLICATE_HEAD_TREE_PATH");
        }
        return blobs;
    }

    private static void VerifyPinnedInputs(string repoRoot, string vendorRoot, string sourceRoot, string expectedCommit, string[] relativePaths)
    {
        string commitAfterLocks = ReadGit(repoRoot, vendorRoot, "rev-parse", "HEAD").Trim();
        if (!String.Equals(commitAfterLocks, expectedCommit, StringComparison.Ordinal) ||
            !String.Equals(commitAfterLocks, ExpectedVendorCommit, StringComparison.Ordinal))
            throw new IOException("VENDOR_COMMIT_CHANGED_AFTER_SOURCE_LOCKS");

        string statusAfterLocks = ReadGit(repoRoot, vendorRoot, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching", "--", SourceRelative);
        if (!String.IsNullOrWhiteSpace(statusAfterLocks)) throw new IOException("VENDOR_SOURCE_CHANGED_AFTER_SOURCE_LOCKS");

        Dictionary<string, string> headBlobs = ReadHeadBlobIds(vendorRoot, expectedCommit);
        foreach (string relative in relativePaths)
        {
            string repositoryPath = SourceRelative + "/" + relative.Replace('\\', '/');
            if (!headBlobs.TryGetValue(relative.Replace('\\', '/'), out string expectedBlob))
                throw new IOException("PINNED_SOURCE_PATH_NOT_IN_FIXED_HEAD_TREE: " + repositoryPath);
            string fullPath = Path.GetFullPath(Path.Combine(sourceRoot, relative.Replace('/', Path.DirectorySeparatorChar)));
            string actualBlob = ReadGit(repoRoot, vendorRoot, "hash-object", "--", fullPath).Trim();
            if (!String.Equals(actualBlob, expectedBlob, StringComparison.OrdinalIgnoreCase))
                throw new IOException("PINNED_SOURCE_BLOB_MISMATCH: " + repositoryPath);
        }

        if (!String.Equals(ReadGit(repoRoot, vendorRoot, "rev-parse", "HEAD").Trim(), expectedCommit, StringComparison.Ordinal))
            throw new IOException("VENDOR_COMMIT_CHANGED_DURING_PINNED_SOURCE_VERIFICATION");
        if (!String.IsNullOrWhiteSpace(ReadGit(repoRoot, vendorRoot, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching", "--", SourceRelative)))
            throw new IOException("VENDOR_SOURCE_CHANGED_DURING_PINNED_SOURCE_VERIFICATION");
    }

    private static void ValidateRelativePath(string relative)
    {
        if (String.IsNullOrWhiteSpace(relative) || relative.StartsWith("/", StringComparison.Ordinal) ||
            relative.Contains('\\') || relative.Contains(':') || relative.Contains('\t'))
            throw new IOException("INVALID_TRACKED_IP_RELATIVE_PATH");
        foreach (string part in relative.Split('/'))
            if (part.Length == 0 || part == "." || part == "..") throw new IOException("INVALID_TRACKED_IP_PATH_COMPONENT");
    }

    private static string ReadPinnedText(string path)
    {
        using (FileStream stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
        using (StreamReader reader = new StreamReader(stream, new UTF8Encoding(false, true), true))
            return reader.ReadToEnd();
    }

    private static string StatusValue(string text, string key)
    {
        foreach (string line in text.Split('\n', StringSplitOptions.RemoveEmptyEntries))
        {
            string prefix = key + "=";
            if (line.StartsWith(prefix, StringComparison.Ordinal)) return line.Substring(prefix.Length).TrimEnd('\r');
        }
        return String.Empty;
    }

    private sealed class MetadataDigest
    {
        public string TreeSha256;
        public string ManifestSha256;
        public string ManifestText;
    }

    private static MetadataDigest ComputeMetadataDigest(string metadataRoot, string[] manifest)
    {
        SortedDictionary<string, string> hashes = new SortedDictionary<string, string>(StringComparer.Ordinal);
        foreach (string entry in manifest)
        {
            string[] parts = entry.Replace('\\', '/').Split('/');
            if (parts.Length < 2 || parts[0] != "my_ip") throw new IOException("METADATA_HASH_SOURCE_PATH_INVALID");
            foreach (string part in parts)
                if (String.IsNullOrWhiteSpace(part) || part == "." || part == ".." || part.IndexOfAny(new[] { '\\', '/', ':' }) >= 0)
                    throw new IOException("METADATA_HASH_PATH_COMPONENT_INVALID");
            string relative = String.Join("/", parts.Skip(1));
            string path = Path.Combine(metadataRoot, Path.Combine(parts.Skip(1).ToArray()));
            using (SafeFileHandle handle = S3T03SafeFile.OpenReadLeaf(path))
            using (FileStream stream = new FileStream(handle, FileAccess.Read))
                hashes.Add(relative, Convert.ToHexString(SHA256.HashData(stream)));
        }
        if (hashes.Count == 0 || hashes.Count != manifest.Length) throw new IOException("METADATA_HASH_CARDINALITY_MISMATCH");

        StringBuilder canonical = new StringBuilder();
        canonical.Append("FILE_COUNT=").Append(hashes.Count.ToString(System.Globalization.CultureInfo.InvariantCulture)).Append('\n');
        StringBuilder manifestText = new StringBuilder();
        manifestText.Append("ROOT=").Append(metadataRoot).Append('\n');
        manifestText.Append(canonical);
        foreach (KeyValuePair<string, string> item in hashes)
        {
            string record = item.Value.ToUpperInvariant() + "  " + item.Key + "\n";
            canonical.Append(record);
            manifestText.Append(record);
        }
        byte[] utf8 = new UTF8Encoding(false).GetBytes(canonical.ToString());
        byte[] manifestUtf8 = new UTF8Encoding(false).GetBytes(manifestText.ToString());
        return new MetadataDigest
        {
            TreeSha256 = Convert.ToHexString(SHA256.HashData(utf8)),
            ManifestSha256 = Convert.ToHexString(SHA256.HashData(manifestUtf8)),
            ManifestText = manifestText.ToString()
        };
    }

    private static void ValidateVendorInputs(string sourceRoot, string[] manifest)
    {
        string plPath = Path.Combine(sourceRoot, "pl_config.tcl");
        string plText = ReadPinnedText(plPath);
        if (System.Text.RegularExpressions.Regex.IsMatch(plText, "(?im)^\\s*(read_xdc|source\\s+[^\\r\\n]*\\.xdc)"))
            throw new IOException("PL_CONFIG_ATTEMPTS_TO_LOAD_XDC");
        if (System.Text.RegularExpressions.Regex.IsMatch(plText, "(?i)ov5640|camera"))
            throw new IOException("SOURCE_IS_NOT_HDMI_ONLY");
        foreach (string vlnv in new[] { "digilentinc.com:ip:axi_dynclk:1.0", "digilentinc.com:ip:rgb2dvi:1.3" })
            if (!plText.Contains(vlnv, StringComparison.Ordinal)) throw new IOException("MISSING_EXPECTED_HDMI_IP_" + vlnv);

        string ipRoot = Path.Combine(sourceRoot, "my_ip");
        string[] componentFiles = Directory.EnumerateDirectories(ipRoot, "*", SearchOption.TopDirectoryOnly)
            .Select(path => Path.Combine(path, "component.xml"))
            .Where(File.Exists)
            .Select(Path.GetFullPath)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToArray();
        string[] expectedFiles =
        {
            Path.GetFullPath(Path.Combine(ipRoot, "axi_dynclk_v1_0", "component.xml")),
            Path.GetFullPath(Path.Combine(ipRoot, "rgb2dvi_v1_3", "component.xml"))
        };
        if (!componentFiles.SequenceEqual(expectedFiles.OrderBy(path => path, StringComparer.OrdinalIgnoreCase), StringComparer.OrdinalIgnoreCase))
            throw new IOException("UNEXPECTED_COMPONENT_XML_SET");

        foreach (string pair in new[] { "axi_dynclk_v1_0|axi_dynclk", "rgb2dvi_v1_3|rgb2dvi" })
        {
            string[] fields = pair.Split('|');
            string relative = "my_ip/" + fields[0] + "/component.xml";
            if (!manifest.Contains(relative, StringComparer.Ordinal)) throw new IOException("COMPONENT_XML_NOT_TRACKED: " + fields[0]);
            S3PathGuardR3.HoldSourceFile(sourceRoot, relative);
            string xml = ReadPinnedText(Path.Combine(ipRoot, fields[0], "component.xml"));
            if (!xml.Contains("<spirit:name>" + fields[1] + "</spirit:name>", StringComparison.Ordinal))
                throw new IOException("COMPONENT_XML_NAME_MISMATCH_" + fields[0]);
        }
    }
}
