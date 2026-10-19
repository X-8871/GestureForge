using System;
using System.ComponentModel;
using System.IO;
using System.Reflection;
using System.Threading;

internal static class T03InternalCommands
{
    private const string SourceRelative = "course_s2_vitis/14_vdma_hdmi_out/Vivado/auto_create_project";

    private static string AuthorizedOutputRoot()
    {
        string assemblyPath = Assembly.GetEntryAssembly() == null ? String.Empty : Assembly.GetEntryAssembly().Location;
        if (String.IsNullOrWhiteSpace(assemblyPath)) throw new IOException("INTERNAL_HELPER_ASSEMBLY_PATH_UNAVAILABLE");

        DirectoryInfo current = new DirectoryInfo(Path.GetDirectoryName(Path.GetFullPath(assemblyPath)));
        while (current != null)
        {
            DirectoryInfo temporary = current.Parent;
            if (String.Equals(current.Name, "s3r04", StringComparison.OrdinalIgnoreCase) &&
                temporary != null && String.Equals(temporary.Name, "tmp", StringComparison.OrdinalIgnoreCase) &&
                temporary.Parent != null)
            {
                string root = Path.GetFullPath(current.FullName);
                string relativeAssembly = Path.GetRelativePath(root, Path.GetFullPath(assemblyPath));
                if (relativeAssembly == "." || relativeAssembly == ".." || relativeAssembly.StartsWith(".." + Path.DirectorySeparatorChar, StringComparison.Ordinal))
                    throw new IOException("INTERNAL_HELPER_NOT_INSIDE_AUTHORIZED_S3R04");
                using (S3T03SafeFile.OpenDirectory(root)) { }
                return root;
            }
            current = current.Parent;
        }
        throw new IOException("INTERNAL_HELPER_NOT_INSIDE_AUTHORIZED_S3R04");
    }

    public static string GetAuthorizedOutputRootForInternalUse()
    {
        return AuthorizedOutputRoot();
    }

    private static string DirectOutputChild(string target)
    {
        string root = AuthorizedOutputRoot();
        if (String.IsNullOrWhiteSpace(target) || !Path.IsPathFullyQualified(target))
            throw new IOException("RACE_TARGET_MUST_BE_ABSOLUTE");
        string portable = target.Replace('\\', '/');
        foreach (string component in portable.Split('/'))
            if (component == "." || component == "..") throw new IOException("RACE_TARGET_TRAVERSAL_REJECTED");

        string full = Path.GetFullPath(target);
        string parent = Path.GetDirectoryName(full);
        string leaf = Path.GetFileName(full);
        if (!String.Equals(Path.TrimEndingDirectorySeparator(parent), Path.TrimEndingDirectorySeparator(root), StringComparison.OrdinalIgnoreCase) ||
            String.IsNullOrWhiteSpace(leaf) || leaf == "." || leaf == "..")
            throw new IOException("RACE_TARGET_OUTSIDE_AUTHORIZED_S3R04");
        return full;
    }

    public static int ValidateRaceTarget(string target)
    {
        try
        {
            DirectOutputChild(target);
            Console.WriteLine("RACE_TARGET=AUTHORIZED_DIRECT_CHILD");
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.Message);
            return 2;
        }
    }

    public static int TryCreateRaceTarget(string target, string readyEventName, string startEventName)
    {
        try
        {
            string full = DirectOutputChild(target);
            using (EventWaitHandle ready = EventWaitHandle.OpenExisting(readyEventName))
            using (EventWaitHandle start = EventWaitHandle.OpenExisting(startEventName))
            {
                ready.Set();
                if (!start.WaitOne(10000)) throw new IOException("RACE_START_GATE_TIMEOUT");
            }

            try
            {
                using (S3T03SafeFile.CreateDirectoryWithinRoot(full, AuthorizedOutputRoot())) { }
                Console.WriteLine("CREATED");
                return 0;
            }
            catch (IOException error) when (error.Message == "SECURE_DIRECTORY_CREATE_COLLISION")
            {
                Console.WriteLine("COLLISION");
                return 0;
            }
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.Message);
            return 2;
        }
    }

    public static int ProbePinnedSourceWrite(string path)
    {
        try
        {
            string root = AuthorizedOutputRoot();
            string repository = Directory.GetParent(Directory.GetParent(root).FullName).FullName;
            string sourceRoot = Path.GetFullPath(Path.Combine(repository, "tmp", "stage3_reference", "AX7020_2023.1", SourceRelative.Replace('/', Path.DirectorySeparatorChar)));
            string expected = Path.GetFullPath(Path.Combine(sourceRoot, "ps_config.tcl"));
            if (!String.Equals(Path.GetFullPath(path), expected, StringComparison.OrdinalIgnoreCase))
                throw new IOException("SOURCE_WRITE_PROBE_TARGET_NOT_FIXED_PS_CONFIG");

            try
            {
                using (S3T03SafeFile.OpenLeaf(expected, false)) { }
                Console.Error.WriteLine("SOURCE_WRITE_ACCESS_UNEXPECTEDLY_OPENED");
                return 3;
            }
            catch (Win32Exception error) when (error.NativeErrorCode == 32)
            {
                Console.WriteLine("SOURCE_WRITE_DENIED");
                return 0;
            }
        }
        catch (Exception error)
        {
            Console.Error.WriteLine(error.Message);
            return 2;
        }
    }
}
