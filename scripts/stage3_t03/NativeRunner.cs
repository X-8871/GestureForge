public sealed class S3T03DeadlineExceededException : Exception
{
    public uint ProcessId { get; private set; }
    public int ExitCode { get; private set; }
    public string AbortPhase { get; private set; }

    public S3T03DeadlineExceededException(uint processId, int exitCode, string abortPhase)
        : base("HARD_TIMEOUT_60_MIN:" + abortPhase)
    {
        ProcessId = processId;
        ExitCode = exitCode;
        AbortPhase = abortPhase;
    }
}

public sealed class S3T03RunnerProcess : IDisposable
{
    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct STARTUPINFO
    {
        public int cb;
        public string lpReserved, lpDesktop, lpTitle;
        public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
        public short wShowWindow, cbReserved2;
        public IntPtr lpReserved2, hStdInput, hStdOutput, hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct STARTUPINFOEX
    {
        public STARTUPINFO StartupInfo;
        public IntPtr lpAttributeList;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PROCESS_INFORMATION
    {
        public IntPtr hProcess, hThread;
        public uint dwProcessId, dwThreadId;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct PROCESSENTRY32W
    {
        public uint dwSize, cntUsage, th32ProcessID;
        public UIntPtr th32DefaultHeapID;
        public uint th32ModuleID, cntThreads, th32ParentProcessID;
        public int pcPriClassBase;
        public uint dwFlags;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 260)] public string szExeFile;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SECURITY_ATTRIBUTES
    {
        public int nLength;
        public IntPtr lpSecurityDescriptor;
        [MarshalAs(UnmanagedType.Bool)] public bool bInheritHandle;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct BASIC_LIMIT_INFORMATION
    {
        public long PerProcessUserTimeLimit, PerJobUserTimeLimit;
        public uint LimitFlags;
        public UIntPtr MinimumWorkingSetSize, MaximumWorkingSetSize;
        public uint ActiveProcessLimit;
        public UIntPtr Affinity;
        public uint PriorityClass, SchedulingClass;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct IO_COUNTERS
    {
        public ulong ReadOperationCount, WriteOperationCount, OtherOperationCount;
        public ulong ReadTransferCount, WriteTransferCount, OtherTransferCount;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EXTENDED_LIMIT_INFORMATION
    {
        public BASIC_LIMIT_INFORMATION BasicLimitInformation;
        public IO_COUNTERS IoInfo;
        public UIntPtr ProcessMemoryLimit, JobMemoryLimit, PeakProcessMemoryUsed, PeakJobMemoryUsed;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct BASIC_ACCOUNTING_INFORMATION
    {
        public long TotalUserTime, TotalKernelTime, ThisPeriodTotalUserTime, ThisPeriodTotalKernelTime;
        public uint TotalPageFaults, TotalProcesses, ActiveProcesses, TotalTerminatedProcesses;
    }

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateJobObjectW(IntPtr attributes, string name);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetInformationJobObject(IntPtr job, int infoClass, ref EXTENDED_LIMIT_INFORMATION info, uint length);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool QueryInformationJobObject(IntPtr job, int infoClass, out BASIC_ACCOUNTING_INFORMATION info, uint length, out uint returnLength);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CreatePipe(out IntPtr readPipe, out IntPtr writePipe, ref SECURITY_ATTRIBUTES attributes, uint size);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetHandleInformation(IntPtr handle, uint mask, uint flags);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(string path, uint access, uint share, ref SECURITY_ATTRIBUTES attributes, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CreateProcessW(string applicationName, StringBuilder commandLine, IntPtr processAttributes, IntPtr threadAttributes, bool inheritHandles, uint creationFlags, IntPtr environment, string currentDirectory, ref STARTUPINFOEX startupInfo, out PROCESS_INFORMATION processInformation);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool InitializeProcThreadAttributeList(IntPtr attributeList, int attributeCount, uint flags, ref IntPtr size);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool UpdateProcThreadAttribute(IntPtr attributeList, uint flags, IntPtr attribute, IntPtr value, UIntPtr size, IntPtr previousValue, IntPtr returnSize);
    [DllImport("kernel32.dll")]
    private static extern void DeleteProcThreadAttributeList(IntPtr attributeList);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr OpenProcess(uint desiredAccess, bool inheritHandle, uint processId);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool DuplicateHandle(IntPtr sourceProcess, IntPtr sourceHandle, IntPtr targetProcess,
        out IntPtr targetHandle, uint desiredAccess, bool inheritHandle, uint options);
    [DllImport("kernel32.dll")]
    private static extern IntPtr GetCurrentProcess();
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint GetProcessId(IntPtr process);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool IsProcessInJob(IntPtr process, IntPtr job, out bool result);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool QueryFullProcessImageNameW(IntPtr process, uint flags, StringBuilder imageName, ref uint size);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateEventW(ref SECURITY_ATTRIBUTES attributes, bool manualReset, bool initialState, string name);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetEvent(IntPtr handle);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint ResumeThread(IntPtr thread);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint WaitForSingleObject(IntPtr handle, uint milliseconds);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetExitCodeProcess(IntPtr process, out uint exitCode);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool TerminateJobObject(IntPtr job, uint exitCode);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool TerminateProcess(IntPtr process, uint exitCode);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetNamedPipeClientProcessId(SafePipeHandle namedPipe, out uint clientProcessId);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr CreateToolhelp32Snapshot(uint flags, uint processId);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, EntryPoint = "Process32FirstW", SetLastError = true)]
    private static extern bool Process32FirstW(IntPtr snapshot, ref PROCESSENTRY32W entry);
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, EntryPoint = "Process32NextW", SetLastError = true)]
    private static extern bool Process32NextW(IntPtr snapshot, ref PROCESSENTRY32W entry);

    private IntPtr jobHandle, processHandle, threadHandle;
    private IntPtr outputReadHandle;
    private Thread outputReaderThread;
    private NamedPipeServerStream prepareDigestPipe;
    private IAsyncResult prepareDigestPipeWait;
    private Thread prepareDigestPipeReaderThread;
    private readonly object prepareDigestSync = new object();
    private readonly string expectedPrepareRunId;
    private readonly string expectedPrepareTclExecutable;
    private string prepareDigestRunId, prepareDigestSha256, prepareDigestError;
    private uint prepareDigestTclProcessId, observedPrepareDigestClientProcessId;
    private uint observedPrepareDigestClientParentProcessId;
    private uint boundPrepareTclProcessId, boundPrepareTclParentProcessId;
    private IntPtr boundPrepareTclProcessHandle;
    private int prepareDigestFileCount, prepareDigestMessageCount;
    public uint ProcessId { get; private set; }
    public string CommandLine { get; private set; }

    private S3T03RunnerProcess(IntPtr job, PROCESS_INFORMATION process, string commandLine,
        IntPtr childOutputReadHandle, string digestRunId, string expectedTclExecutable,
        NamedPipeServerStream digestPipe, IAsyncResult digestPipeWait)
    {
        jobHandle = job;
        processHandle = process.hProcess;
        threadHandle = process.hThread;
        outputReadHandle = childOutputReadHandle;
        expectedPrepareRunId = digestRunId;
        expectedPrepareTclExecutable = expectedTclExecutable;
        prepareDigestPipe = digestPipe;
        prepareDigestPipeWait = digestPipeWait;
        ProcessId = process.dwProcessId;
        CommandLine = commandLine;
        if (prepareDigestPipe != null)
        {
            prepareDigestPipeReaderThread = new Thread(ReadPrepareDigestPipe);
            prepareDigestPipeReaderThread.IsBackground = true;
            prepareDigestPipeReaderThread.Name = "S3T03 authenticated prepare digest reader";
            prepareDigestPipeReaderThread.Start();
        }
        outputReaderThread = new Thread(ReadChildOutput);
        outputReaderThread.IsBackground = true;
        outputReaderThread.Name = "S3T03 supervised output reader";
        outputReaderThread.Start();
    }

    private static DateTime ReadUtcNow(Func<DateTime> clock)
    {
        DateTime now = clock == null ? DateTime.UtcNow : clock();
        if (now.Kind != DateTimeKind.Utc) throw new InvalidOperationException("SUPERVISED_CLOCK_MUST_RETURN_UTC");
        return now;
    }

    public static S3T03RunnerProcess Start(string applicationName, string commandLine, string currentDirectory)
    {
        return Start(applicationName, commandLine, currentDirectory, DateTime.MaxValue, null);
    }

    public static S3T03RunnerProcess Start(string applicationName, string commandLine, string currentDirectory, DateTime deadlineUtc)
    {
        return Start(applicationName, commandLine, currentDirectory, deadlineUtc, null);
    }

    public static S3T03RunnerProcess Start(string applicationName, string commandLine, string currentDirectory,
        DateTime deadlineUtc, Func<DateTime> clock)
    {
        return StartInternal(applicationName, commandLine, currentDirectory, deadlineUtc, clock, null, null, null, null);
    }

    public static S3T03RunnerProcess StartForPrepare(string applicationName, string commandLine,
        string currentDirectory, string expectedRunId, string expectedTclExecutable, string digestPipeName)
    {
        if (String.IsNullOrWhiteSpace(expectedRunId) || !System.Text.RegularExpressions.Regex.IsMatch(expectedRunId, "^[A-Za-z0-9_-]{1,80}$"))
            throw new ArgumentException("PREPARE_DIGEST_RUN_ID_INVALID", "expectedRunId");
        if (String.IsNullOrWhiteSpace(expectedTclExecutable) || !Path.IsPathRooted(expectedTclExecutable))
            throw new ArgumentException("PREPARE_TCL_EXECUTABLE_MUST_BE_ABSOLUTE", "expectedTclExecutable");
        if (String.IsNullOrWhiteSpace(digestPipeName) || !System.Text.RegularExpressions.Regex.IsMatch(digestPipeName, "^[A-Za-z0-9_]{1,80}$"))
            throw new ArgumentException("PREPARE_DIGEST_PIPE_NAME_INVALID", "digestPipeName");
        NamedPipeServerStream digestPipe = CreateCurrentUserOnlyPipeServer(digestPipeName);
        try
        {
            IAsyncResult digestPipeWait = digestPipe.BeginWaitForConnection(null, null);
            return StartInternal(applicationName, commandLine, currentDirectory, DateTime.MaxValue, null,
                expectedRunId, Path.GetFullPath(expectedTclExecutable), digestPipe, digestPipeWait);
        }
        catch
        {
            digestPipe.Dispose();
            throw;
        }
    }

    private static NamedPipeServerStream CreateCurrentUserOnlyPipeServer(string pipeName)
    {
        FieldInfo currentUserOnlyField = typeof(PipeOptions).GetField("CurrentUserOnly");
        if (currentUserOnlyField != null)
        {
            PipeOptions currentUserOnly = (PipeOptions)currentUserOnlyField.GetValue(null);
            return new NamedPipeServerStream(pipeName, PipeDirection.In, 1, PipeTransmissionMode.Byte,
                PipeOptions.Asynchronous | currentUserOnly);
        }

        object security = CreateCurrentUserPipeSecurity();
        Type securityType = security.GetType();
        Type[] constructorTypes = new Type[] { typeof(string), typeof(PipeDirection), typeof(int),
            typeof(PipeTransmissionMode), typeof(PipeOptions), typeof(int), typeof(int), securityType };
        ConstructorInfo secureConstructor = typeof(NamedPipeServerStream).GetConstructor(constructorTypes);
        if (secureConstructor == null)
            throw new InvalidOperationException("PREPARE_DIGEST_SECURE_PIPE_CONSTRUCTOR_UNAVAILABLE");
        return (NamedPipeServerStream)secureConstructor.Invoke(new object[] { pipeName, PipeDirection.In, 1,
            PipeTransmissionMode.Byte, PipeOptions.Asynchronous, 0, 0, security });
    }

    private static object CreateCurrentUserPipeSecurity()
    {
        SecurityIdentifier currentUser = WindowsIdentity.GetCurrent().User;
        if (currentUser == null) throw new InvalidOperationException("PREPARE_DIGEST_CURRENT_USER_SID_MISSING");
        Type securityType = typeof(NamedPipeServerStream).Assembly.GetType("System.IO.Pipes.PipeSecurity", false);
        if (securityType == null) securityType = Type.GetType("System.IO.Pipes.PipeSecurity, System.Core", false);
        if (securityType == null) securityType = Type.GetType("System.IO.Pipes.PipeSecurity, System.IO.Pipes", false);
        if (securityType == null) throw new InvalidOperationException("PREPARE_DIGEST_PIPE_SECURITY_TYPE_UNAVAILABLE");
        object security = Activator.CreateInstance(securityType);
        securityType.GetMethod("SetAccessRuleProtection", new Type[] { typeof(bool), typeof(bool) })
            .Invoke(security, new object[] { true, false });
        securityType.GetMethod("SetOwner", new Type[] { typeof(IdentityReference) })
            .Invoke(security, new object[] { currentUser });
        Type ruleType = securityType.Assembly.GetType("System.IO.Pipes.PipeAccessRule", false);
        Type rightsType = securityType.Assembly.GetType("System.IO.Pipes.PipeAccessRights", false);
        if (ruleType == null || rightsType == null)
            throw new InvalidOperationException("PREPARE_DIGEST_PIPE_ACCESS_TYPES_UNAVAILABLE");
        object fullControl = Enum.Parse(rightsType, "FullControl");
        ConstructorInfo ruleConstructor = ruleType.GetConstructor(new Type[] { typeof(IdentityReference), rightsType,
            typeof(System.Security.AccessControl.AccessControlType) });
        if (ruleConstructor == null) throw new InvalidOperationException("PREPARE_DIGEST_PIPE_ACCESS_RULE_CONSTRUCTOR_UNAVAILABLE");
        object rule = ruleConstructor.Invoke(new object[] { currentUser, fullControl,
            System.Security.AccessControl.AccessControlType.Allow });
        securityType.GetMethod("AddAccessRule", new Type[] { ruleType }).Invoke(security, new object[] { rule });
        return security;
    }

    public static bool VerifyCurrentUserPipeAclForSelfTest()
    {
        object security = CreateCurrentUserPipeSecurity();
        Type securityType = security.GetType();
        SecurityIdentifier currentUser = WindowsIdentity.GetCurrent().User;
        bool protectedRules = (bool)securityType.GetProperty("AreAccessRulesProtected").GetValue(security, null);
        object rules = securityType.GetMethod("GetAccessRules", new Type[] { typeof(bool), typeof(bool), typeof(Type) })
            .Invoke(security, new object[] { true, true, typeof(SecurityIdentifier) });
        PropertyInfo countProperty = rules.GetType().GetProperty("Count");
        PropertyInfo itemProperty = rules.GetType().GetProperty("Item");
        if (!protectedRules || currentUser == null || (int)countProperty.GetValue(rules, null) != 1) return false;
        object rule = itemProperty.GetValue(rules, new object[] { 0 });
        Type ruleType = rule.GetType();
        bool inherited = (bool)ruleType.GetProperty("IsInherited").GetValue(rule, null);
        System.Security.AccessControl.AccessControlType accessType =
            (System.Security.AccessControl.AccessControlType)ruleType.GetProperty("AccessControlType").GetValue(rule, null);
        string rights = ruleType.GetProperty("PipeAccessRights").GetValue(rule, null).ToString();
        IdentityReference identity = (IdentityReference)ruleType.GetProperty("IdentityReference").GetValue(rule, null);
        IdentityReference owner = (IdentityReference)securityType.GetMethod("GetOwner", new Type[] { typeof(Type) })
            .Invoke(security, new object[] { typeof(SecurityIdentifier) });
        return !inherited && accessType == System.Security.AccessControl.AccessControlType.Allow && rights == "FullControl" &&
            identity != null && owner != null &&
            String.Equals(identity.Value, currentUser.Value, StringComparison.OrdinalIgnoreCase) &&
            String.Equals(owner.Value, currentUser.Value, StringComparison.OrdinalIgnoreCase);
    }

    private static S3T03RunnerProcess StartInternal(string applicationName, string commandLine,
        string currentDirectory, DateTime deadlineUtc, Func<DateTime> clock, string expectedPrepareRunId,
        string expectedPrepareTclExecutable, NamedPipeServerStream digestPipe, IAsyncResult digestPipeWait)
    {
        if (deadlineUtc != DateTime.MaxValue && deadlineUtc.Kind != DateTimeKind.Utc)
            throw new ArgumentException("SUPERVISED_DEADLINE_MUST_BE_UTC", "deadlineUtc");
        if (deadlineUtc != DateTime.MaxValue && ReadUtcNow(clock) >= deadlineUtc)
            throw new S3T03DeadlineExceededException(0, -1, "BEFORE_CREATE_PROCESS");

        IntPtr job = CreateJobObjectW(IntPtr.Zero, null);
        if (job == IntPtr.Zero) throw new Win32Exception(Marshal.GetLastWin32Error(), "CREATE_JOB_OBJECT_FAILED");
        PROCESS_INFORMATION process = new PROCESS_INFORMATION();
        IntPtr outputRead = IntPtr.Zero, outputWrite = IntPtr.Zero;
        IntPtr attributeListMemory = IntPtr.Zero, inheritedHandleList = IntPtr.Zero;
        bool attributeListInitialized = false;
        SafeFileHandle nullInput = null;
        try
        {
            EXTENDED_LIMIT_INFORMATION limits = new EXTENDED_LIMIT_INFORMATION();
            limits.BasicLimitInformation.LimitFlags = 0x00002000;
            if (!SetInformationJobObject(job, 9, ref limits, (uint)Marshal.SizeOf(typeof(EXTENDED_LIMIT_INFORMATION))))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "SET_JOB_KILL_ON_CLOSE_FAILED");

            SECURITY_ATTRIBUTES pipeAttributes = new SECURITY_ATTRIBUTES();
            pipeAttributes.nLength = Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES));
            pipeAttributes.bInheritHandle = true;
            if (!CreatePipe(out outputRead, out outputWrite, ref pipeAttributes, 65536))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "CREATE_SUPERVISED_OUTPUT_PIPE_FAILED");
            if (!SetHandleInformation(outputRead, 0x00000001, 0))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "MAKE_SUPERVISED_OUTPUT_READ_HANDLE_PRIVATE_FAILED");
            nullInput = CreateFileW("NUL", 0x80000000, 0x00000003, ref pipeAttributes, 3, 0x00000080, IntPtr.Zero);
            if (nullInput == null || nullInput.IsInvalid)
                throw new Win32Exception(Marshal.GetLastWin32Error(), "OPEN_SUPERVISED_NULL_INPUT_FAILED");

            IntPtr attributeListSize = IntPtr.Zero;
            bool initialAttributeQuery = InitializeProcThreadAttributeList(IntPtr.Zero, 1, 0, ref attributeListSize);
            int initialAttributeError = Marshal.GetLastWin32Error();
            if (initialAttributeQuery || attributeListSize == IntPtr.Zero ||
                (initialAttributeError != 122 && initialAttributeError != 0))
                throw new Win32Exception(initialAttributeError, "QUERY_PROCESS_ATTRIBUTE_LIST_SIZE_FAILED");
            if (attributeListSize.ToInt64() > Int32.MaxValue)
                throw new InvalidOperationException("PROCESS_ATTRIBUTE_LIST_SIZE_OUT_OF_RANGE");
            attributeListMemory = Marshal.AllocHGlobal(attributeListSize.ToInt32());
            if (!InitializeProcThreadAttributeList(attributeListMemory, 1, 0, ref attributeListSize))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "INITIALIZE_PROCESS_ATTRIBUTE_LIST_FAILED");
            attributeListInitialized = true;

            inheritedHandleList = Marshal.AllocHGlobal(IntPtr.Size * 2);
            Marshal.WriteIntPtr(inheritedHandleList, 0, nullInput.DangerousGetHandle());
            Marshal.WriteIntPtr(inheritedHandleList, IntPtr.Size, outputWrite);
            IntPtr handleListAttribute = new IntPtr(unchecked((int)0x00020002));
            if (!UpdateProcThreadAttribute(attributeListMemory, 0, handleListAttribute,
                inheritedHandleList, new UIntPtr((uint)(IntPtr.Size * 2)), IntPtr.Zero, IntPtr.Zero))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "SET_INHERITED_HANDLE_WHITELIST_FAILED");

            STARTUPINFOEX startup = new STARTUPINFOEX();
            startup.StartupInfo.cb = Marshal.SizeOf(typeof(STARTUPINFOEX));
            startup.StartupInfo.dwFlags = 0x00000101;
            startup.StartupInfo.wShowWindow = 0;
            startup.StartupInfo.hStdInput = nullInput.DangerousGetHandle();
            startup.StartupInfo.hStdOutput = outputWrite;
            startup.StartupInfo.hStdError = outputWrite;
            startup.lpAttributeList = attributeListMemory;
            StringBuilder mutableCommandLine = new StringBuilder(commandLine);
            const uint CREATE_SUSPENDED = 0x00000004;
            const uint CREATE_NO_WINDOW = 0x08000000;
            const uint CREATE_UNICODE_ENVIRONMENT = 0x00000400;
            const uint EXTENDED_STARTUPINFO_PRESENT = 0x00080000;
            if (!CreateProcessW(applicationName, mutableCommandLine, IntPtr.Zero, IntPtr.Zero, true,
                CREATE_SUSPENDED | CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT | EXTENDED_STARTUPINFO_PRESENT,
                IntPtr.Zero, currentDirectory, ref startup, out process))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "CREATE_SUSPENDED_PROCESS_FAILED");

            CloseHandle(outputWrite);
            outputWrite = IntPtr.Zero;
            nullInput.Dispose();
            nullInput = null;

            if (!AssignProcessToJobObject(job, process.hProcess))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "ASSIGN_PROCESS_TO_PRIVATE_JOB_FAILED");
            if (deadlineUtc != DateTime.MaxValue && ReadUtcNow(clock) >= deadlineUtc)
            {
                if (!TerminateProcess(process.hProcess, 124))
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "DEADLINE_SUSPENDED_PROCESS_TERMINATION_FAILED");
                uint waitResult = WaitForSingleObject(process.hProcess, 5000);
                if (waitResult != 0)
                    throw new InvalidOperationException("DEADLINE_SUSPENDED_PROCESS_TERMINATION_UNCONFIRMED");
                throw new S3T03DeadlineExceededException(process.dwProcessId, 124, "BEFORE_RESUME_THREAD");
            }
            if (ResumeThread(process.hThread) == 0xFFFFFFFF)
                throw new Win32Exception(Marshal.GetLastWin32Error(), "RESUME_SUPERVISED_PROCESS_FAILED");
            S3T03RunnerProcess supervised = new S3T03RunnerProcess(job, process, commandLine, outputRead,
                expectedPrepareRunId, expectedPrepareTclExecutable, digestPipe, digestPipeWait);
            outputRead = IntPtr.Zero;
            return supervised;
        }
        catch
        {
            if (process.hProcess != IntPtr.Zero) TerminateProcess(process.hProcess, 1);
            if (process.hThread != IntPtr.Zero) CloseHandle(process.hThread);
            if (process.hProcess != IntPtr.Zero) CloseHandle(process.hProcess);
            if (nullInput != null) nullInput.Dispose();
            if (outputWrite != IntPtr.Zero) CloseHandle(outputWrite);
            if (outputRead != IntPtr.Zero) CloseHandle(outputRead);
            if (digestPipe != null) digestPipe.Dispose();
            CloseHandle(job);
            throw;
        }
        finally
        {
            if (attributeListInitialized && attributeListMemory != IntPtr.Zero)
                DeleteProcThreadAttributeList(attributeListMemory);
            if (attributeListMemory != IntPtr.Zero) Marshal.FreeHGlobal(attributeListMemory);
            if (inheritedHandleList != IntPtr.Zero) Marshal.FreeHGlobal(inheritedHandleList);
        }
    }

    private void ReadChildOutput()
    {
        IntPtr readHandle = Interlocked.Exchange(ref outputReadHandle, IntPtr.Zero);
        try
        {
            using (SafeFileHandle handle = new SafeFileHandle(readHandle, true))
            using (FileStream stream = new FileStream(handle, FileAccess.Read))
            using (StreamReader reader = new StreamReader(stream, Encoding.UTF8, true, 4096, false))
            {
                string line;
                while ((line = reader.ReadLine()) != null)
                {
                    if (line.StartsWith("S3_PREP_METADATA_DIGEST=", StringComparison.Ordinal))
                    {
                        lock (prepareDigestSync) prepareDigestError = "PREPARE_DIGEST_UNTRUSTED_STDOUT_MARKER";
                    }
                }
            }
        }
        catch (Exception error)
        {
            lock (prepareDigestSync)
                if (expectedPrepareRunId != null && String.IsNullOrEmpty(prepareDigestError))
                    prepareDigestError = "PREPARE_DIGEST_OUTPUT_CHANNEL_FAILED:" + error.GetType().Name + ":" + error.Message;
        }
    }

    private void ReadPrepareDigestPipe()
    {
        try
        {
            prepareDigestPipe.EndWaitForConnection(prepareDigestPipeWait);
            uint digestClientProcessId;
            if (!GetNamedPipeClientProcessId(prepareDigestPipe.SafePipeHandle, out digestClientProcessId) || digestClientProcessId == 0)
                throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_PIPE_CLIENT_PID_QUERY_FAILED");
            uint digestClientParentProcessId = GetParentProcessIdFromSnapshot(digestClientProcessId);
            lock (prepareDigestSync)
            {
                observedPrepareDigestClientProcessId = digestClientProcessId;
                observedPrepareDigestClientParentProcessId = digestClientParentProcessId;
            }
            try { ValidatePrepareTclProcessIdentity(digestClientProcessId); }
            catch (Exception error)
            {
                lock (prepareDigestSync)
                    prepareDigestError = "PREPARE_DIGEST_TCL_PROCESS_IDENTITY_REJECTED:" + error.Message;
                try { prepareDigestPipe.Dispose(); } catch { }
                return;
            }

            using (MemoryStream message = new MemoryStream())
            {
                byte[] buffer = new byte[128];
                int read;
                while ((read = prepareDigestPipe.Read(buffer, 0, buffer.Length)) > 0)
                {
                    if (message.Length + read > 256) throw new InvalidDataException("PREPARE_DIGEST_PIPE_MESSAGE_TOO_LARGE");
                    message.Write(buffer, 0, read);
                }
                byte[] bytes = message.ToArray();
                for (int index = 0; index < bytes.Length; index++)
                    if (bytes[index] > 0x7F) throw new InvalidDataException("PREPARE_DIGEST_PIPE_MESSAGE_NOT_ASCII");
                string payload = Encoding.ASCII.GetString(bytes);
                if (!payload.EndsWith("\n", StringComparison.Ordinal) || payload.IndexOf('\n') != payload.Length - 1)
                    throw new InvalidDataException("PREPARE_DIGEST_PIPE_MESSAGE_LINE_FORMAT_INVALID");
                string line = payload.Substring(0, payload.Length - 1);
                if (line.EndsWith("\r", StringComparison.Ordinal)) line = line.Substring(0, line.Length - 1);
                if (line.IndexOf('\r') >= 0) throw new InvalidDataException("PREPARE_DIGEST_PIPE_MESSAGE_LINE_FORMAT_INVALID");
                RecordPrepareDigestLine(line, digestClientProcessId);
                bool rejectConnection;
                lock (prepareDigestSync) rejectConnection = !String.IsNullOrEmpty(prepareDigestError);
                if (rejectConnection) prepareDigestPipe.Dispose();
            }
        }
        catch (Exception error)
        {
            lock (prepareDigestSync)
                if (expectedPrepareRunId != null && String.IsNullOrEmpty(prepareDigestError))
                    prepareDigestError = "PREPARE_DIGEST_PIPE_FAILED:" + error.GetType().Name + ":" + error.Message;
            try { prepareDigestPipe.Dispose(); } catch { }
        }
    }

    private void RecordPrepareDigestLine(string line, uint actualClientProcessId)
    {
        const string prefix = "S3_PREP_METADATA_DIGEST=";
        if (!line.StartsWith(prefix, StringComparison.Ordinal)) return;
        lock (prepareDigestSync)
        {
            prepareDigestMessageCount++;
            if (expectedPrepareRunId == null)
            {
                prepareDigestError = "UNEXPECTED_PREPARE_DIGEST_ON_NON_PREPARE_PROCESS";
                return;
            }
            if (prepareDigestMessageCount != 1)
            {
                prepareDigestError = "PREPARE_DIGEST_MESSAGE_DUPLICATED";
                return;
            }
            string[] fields = line.Substring(prefix.Length).Split('|');
            uint processId;
            int fileCount;
            if (fields.Length != 4 || fields[0] != expectedPrepareRunId ||
                !UInt32.TryParse(fields[1], out processId) || processId == 0 ||
                !Int32.TryParse(fields[2], out fileCount) || fileCount < 1 ||
                !System.Text.RegularExpressions.Regex.IsMatch(fields[3], "^[A-Fa-f0-9]{64}$"))
            {
                prepareDigestError = "PREPARE_DIGEST_MESSAGE_FORMAT_OR_RUN_ID_INVALID";
                return;
            }
            if (processId != actualClientProcessId)
            {
                prepareDigestError = "PREPARE_DIGEST_PIPE_CLIENT_PID_MISMATCH";
                return;
            }
            prepareDigestRunId = fields[0];
            prepareDigestTclProcessId = processId;
            prepareDigestFileCount = fileCount;
            prepareDigestSha256 = fields[3].ToUpperInvariant();
        }
    }

    private void ValidatePrepareTclProcessIdentity(uint processId)
    {
        if (jobHandle == IntPtr.Zero || String.IsNullOrWhiteSpace(expectedPrepareTclExecutable))
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_IDENTITY_CONTEXT_MISSING");
        const uint WAIT_TIMEOUT = 0x00000102;
        BindExpectedPrepareTclProcess();
        IntPtr process = boundPrepareTclProcessHandle;
        if (process == IntPtr.Zero || boundPrepareTclProcessId == 0)
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_BOUND_PROCESS_HANDLE_MISSING");
        if (processId != boundPrepareTclProcessId)
            throw new InvalidOperationException("PREPARE_DIGEST_PIPE_CLIENT_PID_NOT_EXACT_LAUNCH_TARGET");
        if (GetProcessId(process) != boundPrepareTclProcessId)
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_BOUND_HANDLE_PID_MISMATCH");
        if (WaitForSingleObject(process, 0) != WAIT_TIMEOUT)
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_LAUNCH_TARGET_EXITED_AFTER_BIND");
        bool belongsToPrivateJob;
        if (!IsProcessInJob(process, jobHandle, out belongsToPrivateJob))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_TCL_JOB_MEMBERSHIP_QUERY_FAILED");
        if (!belongsToPrivateJob)
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_PROCESS_NOT_IN_JOB");
        string actualImage = NormalizeImagePath(QueryImagePath(process));
        string expectedImage = NormalizeImagePath(expectedPrepareTclExecutable);
        if (!String.Equals(actualImage, expectedImage, StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_IMAGE_PATH_MISMATCH");
        uint actualParent = processId == ProcessId ? 0 : GetParentProcessIdFromSnapshot(boundPrepareTclProcessId);
        if (actualParent != boundPrepareTclParentProcessId)
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_PARENT_PROCESS_ID_MISMATCH");
        if (GetProcessId(process) != boundPrepareTclProcessId || WaitForSingleObject(process, 0) != WAIT_TIMEOUT)
            throw new InvalidOperationException("PREPARE_DIGEST_TCL_PROCESS_EXITED_DURING_IDENTITY_QUERY");
    }

    public string ValidateBoundPrepareTclProcessForSelfTest(uint reportedProcessId)
    {
        try
        {
            ValidatePrepareTclProcessIdentity(reportedProcessId);
            return "PASS";
        }
        catch (Exception error) { return error.Message; }
    }

    private void BindExpectedPrepareTclProcess()
    {
        const uint WAIT_TIMEOUT = 0x00000102;
        if (boundPrepareTclProcessId != 0)
        {
            if (boundPrepareTclProcessHandle == IntPtr.Zero ||
                WaitForSingleObject(boundPrepareTclProcessHandle, 0) != WAIT_TIMEOUT)
                throw new InvalidOperationException("PREPARE_DIGEST_TCL_LAUNCH_TARGET_EXITED_AFTER_BIND");
            return;
        }
        const uint PROCESS_QUERY_LIMITED_INFORMATION = 0x00001000;
        const uint SYNCHRONIZE = 0x00100000;
        string launcherImage = QueryImagePath(processHandle);
        string expectedImage = NormalizeImagePath(expectedPrepareTclExecutable);
        if (String.Equals(NormalizeImagePath(launcherImage), expectedImage, StringComparison.OrdinalIgnoreCase))
        {
            bool launcherInJob;
            if (!IsProcessInJob(processHandle, jobHandle, out launcherInJob) || !launcherInJob)
                throw new InvalidOperationException("PREPARE_DIGEST_LAUNCHED_PROCESS_NOT_IN_PRIVATE_JOB");
            IntPtr exactLauncher;
            if (!DuplicateHandle(GetCurrentProcess(), processHandle, GetCurrentProcess(), out exactLauncher,
                PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, false, 0))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_LAUNCHED_PROCESS_HANDLE_DUPLICATION_FAILED");
            if (GetProcessId(exactLauncher) != ProcessId || WaitForSingleObject(exactLauncher, 0) != WAIT_TIMEOUT)
            {
                CloseHandle(exactLauncher);
                throw new InvalidOperationException("PREPARE_DIGEST_LAUNCHED_PROCESS_EXITED_BEFORE_BIND");
            }
            boundPrepareTclProcessId = ProcessId;
            boundPrepareTclParentProcessId = 0;
            boundPrepareTclProcessHandle = exactLauncher;
            return;
        }

        DateTime deadline = DateTime.UtcNow.AddSeconds(30);
        while (DateTime.UtcNow < deadline)
        {
            uint candidateProcessId;
            uint candidateParentProcessId;
            IntPtr candidateHandle;
            if (TryFindUniqueDirectJobChild(expectedImage, out candidateProcessId,
                out candidateParentProcessId, out candidateHandle))
            {
                uint confirmProcessId = 0;
                uint confirmParentProcessId = 0;
                IntPtr confirmHandle = IntPtr.Zero;
                try
                {
                    if (!TryFindUniqueDirectJobChild(expectedImage, out confirmProcessId,
                        out confirmParentProcessId, out confirmHandle) ||
                        confirmProcessId != candidateProcessId || confirmParentProcessId != ProcessId)
                        throw new InvalidOperationException("PREPARE_DIGEST_TCL_LAUNCH_TARGET_AMBIGUOUS_OR_CHANGED");
                }
                finally { if (confirmHandle != IntPtr.Zero) CloseHandle(confirmHandle); }
                if (candidateParentProcessId != ProcessId || WaitForSingleObject(candidateHandle, 0) != WAIT_TIMEOUT)
                {
                    CloseHandle(candidateHandle);
                    throw new InvalidOperationException("PREPARE_DIGEST_TCL_LAUNCH_TARGET_PARENT_OR_LIFETIME_INVALID");
                }
                boundPrepareTclProcessId = candidateProcessId;
                boundPrepareTclParentProcessId = candidateParentProcessId;
                boundPrepareTclProcessHandle = candidateHandle;
                return;
            }
            if (WaitForSingleObject(processHandle, 0) != WAIT_TIMEOUT)
                throw new InvalidOperationException("PREPARE_DIGEST_LAUNCHER_EXITED_BEFORE_TCL_PROCESS_DISCOVERY");
            Thread.Sleep(25);
        }
        throw new TimeoutException("PREPARE_DIGEST_TCL_LAUNCH_TARGET_NOT_FOUND_UNDER_CONTROLLED_CMD");
    }

    private bool TryFindUniqueDirectJobChild(string expectedImage, out uint processId,
        out uint parentProcessId, out IntPtr processHandleForTarget)
    {
        const uint TH32CS_SNAPPROCESS = 0x00000002;
        const uint PROCESS_QUERY_LIMITED_INFORMATION = 0x00001000;
        const uint SYNCHRONIZE = 0x00100000;
        const uint WAIT_TIMEOUT = 0x00000102;
        IntPtr snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (snapshot == IntPtr.Zero || snapshot == new IntPtr(-1))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_PROCESS_SNAPSHOT_FAILED");
        processId = 0;
        parentProcessId = 0;
        processHandleForTarget = IntPtr.Zero;
        try
        {
            PROCESSENTRY32W entry = new PROCESSENTRY32W();
            entry.dwSize = (uint)Marshal.SizeOf(typeof(PROCESSENTRY32W));
            if (!Process32FirstW(snapshot, ref entry))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_PROCESS_SNAPSHOT_ENUMERATION_FAILED");
            do
            {
                if (entry.th32ParentProcessID != ProcessId || entry.th32ProcessID == 0) continue;
                IntPtr candidate = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, false, entry.th32ProcessID);
                if (candidate == IntPtr.Zero)
                {
                    int openError = Marshal.GetLastWin32Error();
                    if (openError == 87) continue;
                    throw new Win32Exception(openError, "PREPARE_DIGEST_DIRECT_CHILD_OPEN_FAILED");
                }
                bool keepCandidate = false;
                try
                {
                    if (WaitForSingleObject(candidate, 0) != WAIT_TIMEOUT) continue;
                    if (GetProcessId(candidate) != entry.th32ProcessID) continue;
                    string candidateImage = NormalizeImagePath(QueryImagePath(candidate));
                    if (!String.Equals(candidateImage, expectedImage, StringComparison.OrdinalIgnoreCase)) continue;
                    bool candidateInJob;
                    if (!IsProcessInJob(candidate, jobHandle, out candidateInJob))
                        throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_DIRECT_CHILD_JOB_QUERY_FAILED");
                    if (!candidateInJob)
                        throw new InvalidOperationException("PREPARE_DIGEST_TCL_DIRECT_CHILD_NOT_IN_PRIVATE_JOB");
                    uint verifiedParentProcessId = GetParentProcessIdFromSnapshot(GetProcessId(candidate));
                    if (verifiedParentProcessId != entry.th32ParentProcessID || verifiedParentProcessId != ProcessId ||
                        WaitForSingleObject(processHandle, 0) != WAIT_TIMEOUT)
                        throw new InvalidOperationException("PREPARE_DIGEST_TCL_DIRECT_CHILD_PARENT_IDENTITY_CHANGED");
                    if (processHandleForTarget != IntPtr.Zero)
                        throw new InvalidOperationException("PREPARE_DIGEST_TCL_LAUNCH_TARGET_MULTIPLE_MATCHES");
                    processId = entry.th32ProcessID;
                    parentProcessId = entry.th32ParentProcessID;
                    processHandleForTarget = candidate;
                    keepCandidate = true;
                }
                finally { if (!keepCandidate) CloseHandle(candidate); }
            }
            while (Process32NextW(snapshot, ref entry));
            int enumerationError = Marshal.GetLastWin32Error();
            if (enumerationError != 18)
                throw new Win32Exception(enumerationError, "PREPARE_DIGEST_PROCESS_SNAPSHOT_ENUMERATION_FAILED");
            return processHandleForTarget != IntPtr.Zero;
        }
        catch
        {
            if (processHandleForTarget != IntPtr.Zero)
            {
                CloseHandle(processHandleForTarget);
                processHandleForTarget = IntPtr.Zero;
            }
            throw;
        }
        finally { CloseHandle(snapshot); }
    }

    private static string QueryImagePath(IntPtr process)
    {
        StringBuilder imageName = new StringBuilder(32768);
        uint imageNameLength = (uint)imageName.Capacity;
        if (!QueryFullProcessImageNameW(process, 0, imageName, ref imageNameLength) || imageNameLength == 0)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_PROCESS_IMAGE_QUERY_FAILED");
        return imageName.ToString();
    }

    private static uint GetParentProcessIdFromSnapshot(uint childProcessId)
    {
        const uint TH32CS_SNAPPROCESS = 0x00000002;
        IntPtr snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (snapshot == IntPtr.Zero || snapshot == new IntPtr(-1))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_PARENT_SNAPSHOT_FAILED");
        try
        {
            PROCESSENTRY32W entry = new PROCESSENTRY32W();
            entry.dwSize = (uint)Marshal.SizeOf(typeof(PROCESSENTRY32W));
            if (!Process32FirstW(snapshot, ref entry))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "PREPARE_DIGEST_PARENT_ENUMERATION_FAILED");
            do
            {
                if (entry.th32ProcessID == childProcessId) return entry.th32ParentProcessID;
            }
            while (Process32NextW(snapshot, ref entry));
            throw new InvalidOperationException("PREPARE_DIGEST_CLIENT_PROCESS_NOT_IN_SNAPSHOT");
        }
        finally { CloseHandle(snapshot); }
    }

    private static string NormalizeImagePath(string path)
    {
        string value = path;
        if (value.StartsWith("\\\\?\\UNC\\", StringComparison.OrdinalIgnoreCase)) value = "\\\\" + value.Substring(8);
        else if (value.StartsWith("\\\\?\\", StringComparison.OrdinalIgnoreCase)) value = value.Substring(4);
        return Path.GetFullPath(value);
    }

    public static IntPtr CreateInheritableEventForSelfTest()
    {
        SECURITY_ATTRIBUTES attributes = new SECURITY_ATTRIBUTES();
        attributes.nLength = Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES));
        attributes.bInheritHandle = true;
        IntPtr handle = CreateEventW(ref attributes, false, false, null);
        if (handle == IntPtr.Zero) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_CREATE_INHERITABLE_EVENT_FAILED");
        return handle;
    }

    public static void CloseSelfTestHandle(IntPtr handle)
    {
        if (handle != IntPtr.Zero && !CloseHandle(handle))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_CLOSE_INHERITABLE_EVENT_FAILED");
    }

    public static bool IsSelfTestEventSignaled(IntPtr handle)
    {
        uint result = WaitForSingleObject(handle, 0);
        if (result == 0) return true;
        if (result == 0x00000102) return false;
        throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_EVENT_STATE_QUERY_FAILED");
    }

    public static void SignalSelfTestHandle(IntPtr handle)
    {
        if (!SetEvent(handle)) throw new Win32Exception(Marshal.GetLastWin32Error(), "SELFTEST_CHILD_EVENT_SIGNAL_FAILED");
    }

    public void RequirePreparedMetadataDigest(string expectedRunId)
    {
        if (expectedPrepareRunId == null || expectedRunId != expectedPrepareRunId)
            throw new InvalidOperationException("PREPARE_DIGEST_EXPECTED_RUN_ID_MISMATCH");
        Thread pipeReader = prepareDigestPipeReaderThread;
        if (pipeReader == null || !pipeReader.Join(10000)) throw new TimeoutException("PREPARE_DIGEST_PIPE_READ_TIMEOUT");
        Thread reader = outputReaderThread;
        if (reader != null && !reader.Join(10000)) throw new TimeoutException("PREPARE_DIGEST_OUTPUT_DRAIN_TIMEOUT");
        lock (prepareDigestSync)
        {
            if (!String.IsNullOrEmpty(prepareDigestError)) throw new InvalidOperationException(prepareDigestError);
            if (prepareDigestMessageCount != 1 || prepareDigestRunId != expectedRunId ||
                prepareDigestTclProcessId == 0 || prepareDigestFileCount < 1 ||
                !System.Text.RegularExpressions.Regex.IsMatch(prepareDigestSha256 ?? "", "^[A-F0-9]{64}$"))
                throw new InvalidOperationException("PREPARE_DIGEST_TRUSTED_CHANNEL_MESSAGE_MISSING_OR_INVALID");
        }
    }

    public int PreparedMetadataFileCount
    {
        get { lock (prepareDigestSync) return prepareDigestFileCount; }
    }

    public string PreparedMetadataTreeSha256
    {
        get { lock (prepareDigestSync) return prepareDigestSha256; }
    }

    public uint PreparedMetadataTclProcessId
    {
        get { lock (prepareDigestSync) return prepareDigestTclProcessId; }
    }

    public uint PreparedMetadataTclParentProcessId
    {
        get { lock (prepareDigestSync) return boundPrepareTclParentProcessId; }
    }

    public uint BoundPrepareTclProcessId
    {
        get { lock (prepareDigestSync) return boundPrepareTclProcessId; }
    }

    public uint ObservedPrepareDigestClientProcessId
    {
        get { lock (prepareDigestSync) return observedPrepareDigestClientProcessId; }
    }

    public uint ObservedPrepareDigestClientParentProcessId
    {
        get { lock (prepareDigestSync) return observedPrepareDigestClientParentProcessId; }
    }

    public bool HasExited
    {
        get
        {
            uint result = WaitForSingleObject(processHandle, 0);
            if (result == 0) return true;
            if (result == 0x00000102) return false;
            throw new Win32Exception(Marshal.GetLastWin32Error(), "WAIT_FOR_SUPERVISED_PROCESS_FAILED");
        }
    }

    public int ExitCode
    {
        get
        {
            uint result;
            if (!GetExitCodeProcess(processHandle, out result)) throw new Win32Exception(Marshal.GetLastWin32Error(), "READ_SUPERVISED_EXIT_CODE_FAILED");
            return unchecked((int)result);
        }
    }

    public void TerminateTree(uint exitCode)
    {
        if (jobHandle != IntPtr.Zero && !TerminateJobObject(jobHandle, exitCode))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "TERMINATE_PRIVATE_JOB_TREE_FAILED");
    }

    public bool WaitForTreeExit(int timeoutMilliseconds)
    {
        if (jobHandle == IntPtr.Zero) throw new InvalidOperationException("SUPERVISED_JOB_HANDLE_CLOSED");
        DateTime deadline = DateTime.UtcNow.AddMilliseconds(Math.Max(0, timeoutMilliseconds));
        while (true)
        {
            BASIC_ACCOUNTING_INFORMATION info;
            uint returned;
            if (!QueryInformationJobObject(jobHandle, 1, out info, (uint)Marshal.SizeOf(typeof(BASIC_ACCOUNTING_INFORMATION)), out returned))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "QUERY_SUPERVISED_JOB_PROCESS_COUNT_FAILED");
            if (info.ActiveProcesses == 0) return true;
            if (DateTime.UtcNow >= deadline) return false;
            Thread.Sleep(25);
        }
    }

    public void Dispose()
    {
        if (jobHandle != IntPtr.Zero) { CloseHandle(jobHandle); jobHandle = IntPtr.Zero; }
        if (prepareDigestPipe != null) { prepareDigestPipe.Dispose(); prepareDigestPipe = null; }
        if (prepareDigestPipeReaderThread != null) prepareDigestPipeReaderThread.Join(5000);
        if (outputReaderThread != null) outputReaderThread.Join(5000);
        if (outputReadHandle != IntPtr.Zero)
        {
            IntPtr readHandle = Interlocked.Exchange(ref outputReadHandle, IntPtr.Zero);
            if (readHandle != IntPtr.Zero) CloseHandle(readHandle);
        }
        if (threadHandle != IntPtr.Zero) { CloseHandle(threadHandle); threadHandle = IntPtr.Zero; }
        if (processHandle != IntPtr.Zero) { CloseHandle(processHandle); processHandle = IntPtr.Zero; }
        if (boundPrepareTclProcessHandle != IntPtr.Zero)
        {
            CloseHandle(boundPrepareTclProcessHandle);
            boundPrepareTclProcessHandle = IntPtr.Zero;
        }
    }
}
