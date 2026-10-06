param(
    [string]$VendorRoot,
    [string]$OutputDir,
    [switch]$SupervisorSelfTest,
    [switch]$SecureHelper,
    [switch]$SecureHashOnWrite,
    [switch]$SecureReadHelper,
    [switch]$SecureTreeHashHelper,
    [switch]$SecureLeaseServer,
    [string]$SecurePath,
    [string]$SecureRoot,
    [string]$SecureTreeRoot,
    [ValidateSet('CreateNew','OpenExisting')][string]$SecureMode
)

Set-StrictMode -Version 2
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$vivadoBin = 'D:\Xilinx\2026.1\Vivado\bin'
$vivadoBat = Join-Path $vivadoBin 'vivado.bat'
$vivadoExe = Join-Path $vivadoBin 'unwrapped\win64.o\vivado.exe'
$comSpec = $env:ComSpec
$defaultMaxRuntime = [TimeSpan]::FromMinutes(60)
$defaultNoProgress = [TimeSpan]::FromMinutes(15)
$pollIntervalMs = 1000

$nativeSource = @'
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.IO.Pipes;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Text;
using System.Threading;
using Microsoft.Win32.SafeHandles;

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
'@

if (-not ('S3T03RunnerProcess' -as [type])) {
    Add-Type -TypeDefinition $nativeSource -Language CSharp
}

$safeFileSource = @'
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Win32.SafeHandles;

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
'@

if (-not ('S3T03SafeFile' -as [type])) {
    Add-Type -TypeDefinition $safeFileSource -Language CSharp
}

function Get-SecureTreeSha256Manifest([string]$Root, [object]$LeaseSet = $null) {
    if ([string]::IsNullOrWhiteSpace($Root) -or -not [IO.Path]::IsPathRooted($Root) -or $Root -match '(^|[\\/])\.\.([\\/]|$)') {
        throw 'SECURE_TREE_ROOT_NOT_ABSOLUTE_OR_TRAVERSAL_FREE'
    }
    $treeRootFull = [IO.Path]::GetFullPath($Root).TrimEnd([char[]]@([char]92,[char]47))
    $treeRelativePrefix = $treeRootFull + [IO.Path]::DirectorySeparatorChar
    $treePendingDirectories = New-Object 'System.Collections.Generic.Stack[string]'
    $treePendingDirectories.Push($treeRootFull)
    $treeRecords = New-Object 'System.Collections.Generic.List[object]'
    while ($treePendingDirectories.Count -gt 0) {
        $treeDirectory = $treePendingDirectories.Pop()
        if ($null -ne $LeaseSet) {
            if (-not $LeaseSet.HasDirectoryLease($treeDirectory)) { $LeaseSet.LockDirectory($treeDirectory) }
            $treeEntries = [IO.Directory]::GetFileSystemEntries($treeDirectory)
        } else {
            $treeDirectoryHandle = [S3T03SafeFile]::OpenDirectory($treeDirectory)
            try { $treeEntries = [IO.Directory]::GetFileSystemEntries($treeDirectory) }
            finally { $treeDirectoryHandle.Dispose() }
        }
        foreach ($treeEntry in $treeEntries) {
            $treeEntryFull = [IO.Path]::GetFullPath($treeEntry)
            if (-not $treeEntryFull.StartsWith($treeRelativePrefix, [StringComparison]::OrdinalIgnoreCase)) {
                throw ('SECURE_TREE_ENTRY_OUTSIDE_ROOT:' + $treeEntryFull)
            }
            $treeAttributes = [IO.File]::GetAttributes($treeEntryFull)
            if (($treeAttributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw ('SECURE_TREE_REPARSE_POINT_REJECTED:' + $treeEntryFull)
            }
            if (($treeAttributes -band [IO.FileAttributes]::Directory) -ne 0) {
                if ($null -ne $LeaseSet) {
                    if (-not $LeaseSet.HasDirectoryLease($treeEntryFull)) { $LeaseSet.LockDirectory($treeEntryFull) }
                } else {
                    $treeChildHandle = [S3T03SafeFile]::OpenDirectory($treeEntryFull)
                    $treeChildHandle.Dispose()
                }
                $treePendingDirectories.Push($treeEntryFull)
                continue
            }
            if ($null -ne $LeaseSet) {
                if (-not $LeaseSet.HasFileLease($treeEntryFull)) { $LeaseSet.LockExistingReadOnly($treeEntryFull) }
                $treeBytes = $LeaseSet.ReadHeld($treeEntryFull)
            } else {
                $treeFileHandle = [S3T03SafeFile]::OpenReadLease($treeEntryFull)
                try { $treeBytes = [S3T03SafeFile]::ReadHandle($treeFileHandle) }
                finally { $treeFileHandle.Dispose() }
            }
            $treeSha = [Security.Cryptography.SHA256]::Create()
            try { $treeDigest = [BitConverter]::ToString($treeSha.ComputeHash($treeBytes)).Replace('-','') }
            finally { $treeSha.Dispose() }
            $treeRelativePath = $treeEntryFull.Substring($treeRelativePrefix.Length).Replace('\','/')
            if ([string]::IsNullOrWhiteSpace($treeRelativePath)) { throw 'SECURE_TREE_RELATIVE_PATH_EMPTY' }
            $treeRecords.Add([pscustomobject]@{ RelativePath=$treeRelativePath; Digest=$treeDigest })
        }
    }
    if ($treeRecords.Count -eq 0) { throw 'SECURE_TREE_EMPTY' }
    foreach ($treeRecord in ($treeRecords | Sort-Object -Property RelativePath)) {
        Write-Output ($treeRecord.Digest + [char]9 + $treeRecord.RelativePath)
    }
}

function Format-SecureTreeSha256Manifest([string]$Root, [string[]]$Records) {
    if ($null -eq $Records -or $Records.Count -eq 0) { throw 'SECURE_TREE_FORMAT_EMPTY_RECORDS' }
    $treeRootFull = [IO.Path]::GetFullPath($Root).TrimEnd([char[]]@([char]92,[char]47))
    $treeLines = New-Object 'System.Collections.Generic.List[string]'
    $treeLines.Add('ROOT=' + $treeRootFull)
    $treeLines.Add('FILE_COUNT=' + $Records.Count)
    foreach ($treeRecord in $Records) {
        if ($treeRecord -notmatch '^([A-Fa-f0-9]{64})\t(.+)$') { throw 'SECURE_TREE_FORMAT_INVALID_RECORD' }
        $treeLines.Add($Matches[1].ToUpperInvariant() + '  ' + $Matches[2])
    }
    return ($treeLines -join "`n") + "`n"
}

function Get-SecureTreeRecordsSha256([string[]]$Records) {
    if ($null -eq $Records -or $Records.Count -lt 1) { throw 'SECURE_TREE_RECORD_DIGEST_EMPTY' }
    $sorted = [System.Collections.Generic.SortedDictionary[string,string]]::new([System.StringComparer]::Ordinal)
    foreach ($record in $Records) {
        if ($record -notmatch '^([A-Fa-f0-9]{64})\t(.+)$') { throw 'SECURE_TREE_RECORD_DIGEST_INVALID_RECORD' }
        $digest = $Matches[1].ToUpperInvariant()
        $relative = $Matches[2]
        if ($relative.Contains('\') -or $relative.Contains(':') -or $relative.StartsWith('/') -or
            $relative.EndsWith('/') -or $relative.Contains('//') -or $relative -match '(^|/)\.\.?(/|$)') {
            throw ('SECURE_TREE_RECORD_DIGEST_INVALID_PATH:' + $relative)
        }
        $sorted.Add($relative, $digest)
    }
    $canonicalLines = New-Object 'System.Collections.Generic.List[string]'
    $canonicalLines.Add('FILE_COUNT=' + $sorted.Count)
    foreach ($entry in $sorted.GetEnumerator()) {
        $canonicalLines.Add($entry.Value + '  ' + $entry.Key)
    }
    return Get-Sha256Hex ([Text.Encoding]::UTF8.GetBytes(($canonicalLines -join "`n") + "`n"))
}

function Assert-PreparedMetadataTreeSha256([string[]]$Records, [int]$ExpectedCount, [string]$ExpectedSha256) {
    if ($ExpectedCount -lt 1 -or $null -eq $Records -or $Records.Count -ne $ExpectedCount) {
        throw ('PREPARED_METADATA_FILE_COUNT_MISMATCH: EXPECTED=' + $ExpectedCount + '; ACTUAL=' + $(if ($null -eq $Records) { 0 } else { $Records.Count }))
    }
    if ($ExpectedSha256 -notmatch '^[A-Fa-f0-9]{64}$') { throw 'PREPARED_METADATA_TREE_SHA256_INVALID' }
    $observedSha256 = Get-SecureTreeRecordsSha256 -Records $Records
    if ($observedSha256 -cne $ExpectedSha256.ToUpperInvariant()) {
        throw ('PREPARED_METADATA_TREE_SHA256_MISMATCH: EXPECTED=' + $ExpectedSha256.ToUpperInvariant() + '; ACTUAL=' + $observedSha256)
    }
    return $observedSha256
}

function Assert-PrepareResultMatchesTrustedDigest([string]$PrepareText, [string]$ExpectedRunId,
    [int]$ExpectedCount, [string]$ExpectedSha256) {
    if ($ExpectedCount -lt 1 -or $ExpectedSha256 -notmatch '^[A-Fa-f0-9]{64}$') {
        throw 'TRUSTED_PREPARE_DIGEST_ARGUMENTS_INVALID'
    }
    if ([regex]::Matches($PrepareText, '(?m)^RUN_ID=' + [regex]::Escape($ExpectedRunId) + '$').Count -ne 1) {
        throw 'PREPARATION_RESULT_OR_RUN_ID_MISMATCH'
    }
    if ([regex]::Matches($PrepareText, '(?m)^METADATA_COUNT=([1-9][0-9]*)$').Count -ne 1 -or
        $PrepareText -notmatch '(?m)^METADATA_COUNT=([1-9][0-9]*)$' -or [int]$Matches[1] -ne $ExpectedCount) {
        throw 'TRUSTED_PREPARE_METADATA_COUNT_MISMATCH'
    }
    if ([regex]::Matches($PrepareText, '(?m)^METADATA_TREE_SHA256=([A-Fa-f0-9]{64})$').Count -ne 1 -or
        $PrepareText -notmatch '(?m)^METADATA_TREE_SHA256=([A-Fa-f0-9]{64})$' -or
        $Matches[1].ToUpperInvariant() -cne $ExpectedSha256.ToUpperInvariant()) {
        throw 'TRUSTED_PREPARE_METADATA_DIGEST_MISMATCH'
    }
    return [pscustomobject]@{ FileCount=$ExpectedCount; Sha256=$ExpectedSha256.ToUpperInvariant() }
}

function Get-SecureMetadataTreeNodes([string]$Root, [object]$LeaseSet = $null) {
    if ([string]::IsNullOrWhiteSpace($Root) -or -not [IO.Path]::IsPathRooted($Root) -or $Root -match '(^|[\\/])\.\.([\\/]|$)') {
        throw 'SECURE_METADATA_ROOT_NOT_ABSOLUTE_OR_TRAVERSAL_FREE'
    }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd([char[]]@([char]92,[char]47))
    $rootPrefix = $rootFull + [IO.Path]::DirectorySeparatorChar
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $nodes = New-Object 'System.Collections.Generic.List[object]'
    $pending.Push($rootFull)
    while ($pending.Count -gt 0) {
        $path = $pending.Pop()
        $attributes = [IO.File]::GetAttributes($path)
        $isDirectory = (($attributes -band [IO.FileAttributes]::Directory) -ne 0)
        if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw ('SECURE_METADATA_REPARSE_POINT_REJECTED:' + $path) }
        if ($isDirectory) {
            if ($null -ne $LeaseSet) {
                if (-not $LeaseSet.HasDirectoryLease($path)) { $LeaseSet.LockDirectory($path) }
            } else {
                $directoryHandle = [S3T03SafeFile]::OpenDirectory($path)
                $directoryHandle.Dispose()
            }
        } else {
            $fileHandle = [S3T03SafeFile]::OpenReadLeaf($path)
            $fileHandle.Dispose()
        }
        $nodes.Add([pscustomobject]@{ Path=$path; IsDirectory=$isDirectory })
        if (-not $isDirectory) { continue }
        foreach ($entry in [IO.Directory]::GetFileSystemEntries($path)) {
            $entryFull = [IO.Path]::GetFullPath($entry)
            if (-not $entryFull.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                throw ('SECURE_METADATA_ENTRY_OUTSIDE_ROOT:' + $entryFull)
            }
            $pending.Push($entryFull)
        }
    }
    return $nodes.ToArray()
}

function Test-SecureMetadataDenyAce([object]$Acl, [Security.Principal.SecurityIdentifier]$Sid,
    [Security.AccessControl.FileSystemRights]$RequiredRights, [bool]$RequireInherited) {
    foreach ($rule in $Acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])) {
        if ($rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Deny -or
            $rule.IsInherited -ne $RequireInherited -or
            -not [string]::Equals($rule.IdentityReference.Value, $Sid.Value, [StringComparison]::OrdinalIgnoreCase)) { continue }
        $observedRights = [int64]$rule.FileSystemRights
        $requiredMask = [int64]$RequiredRights
        if (($observedRights -band $requiredMask) -eq $requiredMask) { return $true }
    }
    return $false
}

function Protect-SecureMetadataTree([string]$Root, [object]$LeaseSet,
    [ref]$OriginalSnapshots, [ref]$OriginalRootDaclSddl) {
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd([char[]]@([char]92,[char]47))
    $null = $LeaseSet.HasDirectoryLease($rootFull)
    $rootNodes = @(Get-SecureMetadataTreeNodes -Root $rootFull -LeaseSet $LeaseSet)
    if ($rootNodes.Count -lt 1 -or -not $rootNodes[0].IsDirectory -or
        -not [string]::Equals($rootNodes[0].Path, $rootFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'SECURE_METADATA_ROOT_NODE_INVALID'
    }
    $snapshots = @{}
    foreach ($node in $rootNodes) {
        $acl = Get-Acl -LiteralPath $node.Path -ErrorAction Stop
        $sddl = $acl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)
        $snapshots[$node.Path] = [pscustomobject]@{ Path=$node.Path; IsDirectory=$node.IsDirectory; Acl=$acl; Sddl=$sddl }
    }
    $OriginalSnapshots.Value = $snapshots
    $OriginalRootDaclSddl.Value = $snapshots[$rootFull].Sddl

    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    if ($null -eq $identity.User) { throw 'SECURE_METADATA_CURRENT_USER_SID_MISSING' }
    $sid = $identity.User
    $denyRights = [Security.AccessControl.FileSystemRights]([int64]([Security.AccessControl.FileSystemRights]::WriteData -bor
        [Security.AccessControl.FileSystemRights]::AppendData -bor
        [Security.AccessControl.FileSystemRights]::WriteAttributes -bor
        [Security.AccessControl.FileSystemRights]::WriteExtendedAttributes -bor
        [Security.AccessControl.FileSystemRights]::Delete -bor
        [Security.AccessControl.FileSystemRights]::DeleteSubdirectoriesAndFiles))
    $denyRule = [Security.AccessControl.FileSystemAccessRule]::new($sid, $denyRights,
        [Security.AccessControl.InheritanceFlags]::None, [Security.AccessControl.PropagationFlags]::None,
        [Security.AccessControl.AccessControlType]::Deny)

    $orderedNodes = @($rootNodes | Sort-Object -Property @{ Expression={ $_.Path.Split([char[]]@([char]92)).Length } }, @{ Expression={ $_.Path }; Ascending=$true })
    foreach ($node in $orderedNodes) {
        $acl = Get-Acl -LiteralPath $node.Path -ErrorAction Stop
        $acl.AddAccessRule($denyRule)
        Set-Acl -LiteralPath $node.Path -AclObject $acl -ErrorAction Stop
        $verifiedAcl = Get-Acl -LiteralPath $node.Path -ErrorAction Stop
        if (-not (Test-SecureMetadataDenyAce -Acl $verifiedAcl -Sid $sid -RequiredRights $denyRights -RequireInherited $false)) {
            throw ('SECURE_METADATA_EXPLICIT_DENY_ACE_MISSING:' + $node.Path)
        }
        if (-not $node.IsDirectory -and -not $LeaseSet.HasFileLease($node.Path)) {
            $LeaseSet.LockExistingReadOnly($node.Path)
        }
    }

    $afterNodes = @(Get-SecureMetadataTreeNodes -Root $rootFull -LeaseSet $LeaseSet)
    if ($afterNodes.Count -ne $rootNodes.Count) { throw 'SECURE_METADATA_TREE_CARDINALITY_CHANGED_DURING_FREEZE' }
    foreach ($node in $afterNodes) {
        if (-not $snapshots.ContainsKey($node.Path)) { throw ('SECURE_METADATA_TREE_ENTRY_ADDED_DURING_FREEZE:' + $node.Path) }
        $acl = Get-Acl -LiteralPath $node.Path -ErrorAction Stop
        if (-not (Test-SecureMetadataDenyAce -Acl $acl -Sid $sid -RequiredRights $denyRights -RequireInherited $false)) {
            throw ('SECURE_METADATA_TREE_ENTRY_NOT_FROZEN:' + $node.Path)
        }
    }
}

function Restore-SecureMetadataTree([string]$Root, [object]$LeaseSet,
    [hashtable]$OriginalSnapshots, [string]$OriginalRootDaclSddl) {
    if ($null -eq $OriginalSnapshots -or $OriginalSnapshots.Count -lt 1 -or [string]::IsNullOrWhiteSpace($OriginalRootDaclSddl)) {
        throw 'SECURE_METADATA_ACL_RESTORE_SNAPSHOT_MISSING'
    }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd([char[]]@([char]92,[char]47))
    if (-not $OriginalSnapshots.ContainsKey($rootFull) -or
        -not [string]::Equals($OriginalSnapshots[$rootFull].Sddl, $OriginalRootDaclSddl, [StringComparison]::Ordinal)) {
        throw 'SECURE_METADATA_ROOT_ACL_SNAPSHOT_MISMATCH'
    }
    $LeaseSet.ReleaseLeasesUnder($rootFull)
    $orderedSnapshots = @($OriginalSnapshots.Values | Sort-Object -Property @{ Expression={ $_.Path.Split([char[]]@([char]92)).Length }; Descending=$true }, @{ Expression={ $_.Path }; Descending=$true })
    foreach ($snapshot in $orderedSnapshots) {
        Set-Acl -LiteralPath $snapshot.Path -AclObject $snapshot.Acl -ErrorAction Stop
    }
    foreach ($snapshot in $OriginalSnapshots.Values) {
        $actualAcl = Get-Acl -LiteralPath $snapshot.Path -ErrorAction Stop
        $actualSddl = $actualAcl.GetSecurityDescriptorSddlForm([Security.AccessControl.AccessControlSections]::Access)
        if (-not [string]::Equals($actualSddl, $snapshot.Sddl, [StringComparison]::Ordinal)) {
            throw ('SECURE_METADATA_ACL_RESTORE_MISMATCH:' + $snapshot.Path)
        }
    }
    $restoredNodes = @(Get-SecureMetadataTreeNodes -Root $rootFull)
    if ($restoredNodes.Count -ne $OriginalSnapshots.Count) { throw 'SECURE_METADATA_TREE_SHAPE_CHANGED_AFTER_ACL_RESTORE' }
    foreach ($node in $restoredNodes) {
        if (-not $OriginalSnapshots.ContainsKey($node.Path)) { throw ('SECURE_METADATA_UNTRACKED_NODE_AFTER_ACL_RESTORE:' + $node.Path) }
    }
}

if ($SecureTreeHashHelper) {
    try {
        if ([string]::IsNullOrWhiteSpace($SecureRoot) -or [string]::IsNullOrWhiteSpace($SecureTreeRoot) -or
            -not [IO.Path]::IsPathRooted($SecureRoot) -or -not [IO.Path]::IsPathRooted($SecureTreeRoot) -or
            $SecureRoot -match '(^|[\\/])\.\.([\\/]|$)' -or $SecureTreeRoot -match '(^|[\\/])\.\.([\\/]|$)') {
            throw 'SECURE_TREE_HASH_ROOTS_INVALID'
        }
        $secureTreeBoundary = [IO.Path]::GetFullPath($SecureRoot).TrimEnd([char[]]@([char]92,[char]47))
        $secureTreeRootFull = [IO.Path]::GetFullPath($SecureTreeRoot).TrimEnd([char[]]@([char]92,[char]47))
        $secureTreeRepoTmp = [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp')).TrimEnd([char[]]@([char]92,[char]47))
        if (-not $secureTreeBoundary.StartsWith(($secureTreeRepoTmp + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
            throw 'SECURE_TREE_HASH_BOUNDARY_OUTSIDE_REPOSITORY_TMP'
        }
        if (-not $secureTreeRootFull.StartsWith(($secureTreeBoundary + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
            throw 'SECURE_TREE_HASH_ROOT_OUTSIDE_OUTPUT_BOUNDARY'
        }
        foreach ($treeRecord in (Get-SecureTreeSha256Manifest -Root $secureTreeRootFull)) {
            [Console]::Out.WriteLine('S3_SECURE_TREE_SHA256=' + $treeRecord)
        }
        exit 0
    } catch {
        [Console]::Error.WriteLine('S3_SECURE_TREE_SHA256=FAIL:' + $_.Exception.Message)
        exit 3
    }
}

if ($SecureLeaseServer) {
    $leaseSet = $null
    $leaseServerExit = 3
    try {
        if ([string]::IsNullOrWhiteSpace($SecurePath) -or [string]::IsNullOrWhiteSpace($SecureRoot)) { throw 'SECURE_LEASE_ARGUMENTS_MISSING' }
        $target = [IO.Path]::GetFullPath($SecurePath)
        $rootFull = [IO.Path]::GetFullPath($SecureRoot).TrimEnd('\')
        $repoTmp = [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp')).TrimEnd('\')
        if (-not $rootFull.StartsWith(($repoTmp + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'SECURE_LEASE_ROOT_OUTSIDE_REPOSITORY_TMP' }
        if (-not $target.StartsWith(($rootFull + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'SECURE_LEASE_TARGET_OUTSIDE_OUTPUT_ROOT' }
        $leaseSet = New-Object S3T03OutputLeaseSet($rootFull)
        $leaseSet.LockParentDirectory($repoRoot)
        $leaseSet.LockParentDirectory($repoTmp)
        $parent = [IO.Path]::GetDirectoryName($target)
        $leaseSet.LockDirectoryChain($parent)
        $leaseSet.LockExistingReadOnly($target)
        $bytes = $leaseSet.ReadHeld($target)
        $sha = [Security.Cryptography.SHA256]::Create()
        try { $digest = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-','') }
        finally { $sha.Dispose() }
        [Console]::Out.WriteLine('S3_SECURE_LEASE=READY:' + $digest)
        [Console]::Out.Flush()
        $release = [Console]::In.ReadLine()
        if ($release -cne 'RELEASE') { throw 'SECURE_LEASE_RELEASE_COMMAND_MISSING' }
        [Console]::Out.WriteLine('S3_SECURE_LEASE=RELEASED')
        [Console]::Out.Flush()
        $leaseServerExit = 0
    } catch {
        [Console]::Error.WriteLine('S3_SECURE_LEASE=FAIL:' + $_.Exception.Message)
        $leaseServerExit = 3
    } finally {
        if ($leaseSet) { $leaseSet.Dispose() }
    }
    exit $leaseServerExit
}

if ($SecureHelper) {
    try {
        if ([string]::IsNullOrWhiteSpace($SecurePath) -or [string]::IsNullOrWhiteSpace($SecureRoot) -or [string]::IsNullOrWhiteSpace($SecureMode)) { throw 'SECURE_HELPER_ARGUMENTS_MISSING' }
        $target = [IO.Path]::GetFullPath($SecurePath)
        $secureRootFull = [IO.Path]::GetFullPath($SecureRoot).TrimEnd('\')
        $securePrefix = $secureRootFull + '\'
        if (-not $target.StartsWith($securePrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'SECURE_HELPER_TARGET_OUTSIDE_GUARDED_OUTPUT_TREE' }
        $encodedInput = [Console]::In.ReadToEnd().Trim()
        if ($encodedInput.Length -gt 90000000) { throw 'SECURE_HELPER_INPUT_TOO_LARGE' }
        $inputBytes = [Convert]::FromBase64String($encodedInput)
        if ($SecureHashOnWrite) {
            if ($SecureMode -ne 'OpenExisting') { throw 'HASH_WRITE_REQUIRES_EXISTING_LEAF' }
            $digest = [S3T03SafeFile]::WriteWithinRootAndHash($target, $secureRootFull, $inputBytes)
            [Console]::Out.WriteLine('S3_SECURE_WRITE=PASS:' + $digest)
        } else {
            [S3T03SafeFile]::WriteWithinRoot($target, $secureRootFull, ($SecureMode -eq 'CreateNew'), $inputBytes)
            [Console]::Out.WriteLine('S3_SECURE_WRITE=PASS')
        }
        exit 0
    } catch {
        [Console]::Error.WriteLine('S3_SECURE_WRITE=FAIL:' + $_.Exception.Message)
        exit 3
    }
}

if ($SecureReadHelper) {
    try {
        if ([string]::IsNullOrWhiteSpace($SecurePath) -or [string]::IsNullOrWhiteSpace($SecureRoot)) { throw 'SECURE_READ_ARGUMENTS_MISSING' }
        $target = [IO.Path]::GetFullPath($SecurePath)
        $secureRootFull = [IO.Path]::GetFullPath($SecureRoot).TrimEnd('\')
        if (-not $target.StartsWith(($secureRootFull + '\'), [StringComparison]::OrdinalIgnoreCase)) { throw 'SECURE_READ_TARGET_OUTSIDE_GUARDED_OUTPUT_TREE' }
        $handle = [S3T03SafeFile]::OpenReadLease($target)
        try { $bytes = [S3T03SafeFile]::ReadHandle($handle) }
        finally { $handle.Dispose() }
        $sha = [Security.Cryptography.SHA256]::Create()
        try { $digest = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-','') }
        finally { $sha.Dispose() }
        [Console]::Out.WriteLine('S3_SECURE_READ=' + $digest + ':' + [Convert]::ToBase64String($bytes))
        exit 0
    } catch {
        [Console]::Error.WriteLine('S3_SECURE_READ=FAIL:' + $_.Exception.Message)
        exit 3
    }
}

function ConvertTo-WindowsArgument([string]$Value) {
    $builder = New-Object Text.StringBuilder
    [void]$builder.Append('"')
    $slashes = 0
    foreach ($character in $Value.ToCharArray()) {
        if ($character -eq '\') { $slashes++; continue }
        if ($character -eq '"') {
            if ($slashes -gt 0) { [void]$builder.Append(('\' * (2 * $slashes))) }
            [void]$builder.Append('\"')
            $slashes = 0
            continue
        }
        if ($slashes -gt 0) { [void]$builder.Append(('\' * $slashes)); $slashes = 0 }
        [void]$builder.Append($character)
    }
    if ($slashes -gt 0) { [void]$builder.Append(('\' * (2 * $slashes))) }
    [void]$builder.Append('"')
    return $builder.ToString()
}

function ConvertTo-CmdArgument([string]$Value) {
    if ($Value.Contains('"') -or $Value.Contains('%') -or $Value.Contains('!') -or $Value.Contains("`r") -or $Value.Contains("`n")) {
        throw '命令行参数包含不允许的 cmd 元字符。'
    }
    if ($Value -match '[\s&|<>^()]') { return '"' + $Value + '"' }
    return $Value
}

function New-BatchCommandLine([string]$BatchPath, [string[]]$Arguments) {
    $payload = '"' + $BatchPath + '" ' + (($Arguments | ForEach-Object { ConvertTo-CmdArgument $_ }) -join ' ')
    return (ConvertTo-WindowsArgument $comSpec) + ' /d /s /c "' + $payload + '"'
}

function New-DirectCommandLine([string]$Executable, [string[]]$Arguments) {
    return ((@($Executable) + $Arguments | ForEach-Object { ConvertTo-WindowsArgument $_ }) -join ' ')
}

function ConvertTo-PowerShellLiteral([string]$Value) {
    return "'" + $Value.Replace("'", "''") + "'"
}

function New-PrepareDigestPipeClientCode([string]$PipeName, [string]$RunId,
    [string]$ClaimedProcessIdExpression, [int]$FileCount, [string]$Digest) {
    if ($Digest -notmatch '^[A-Fa-f0-9]{64}$' -or $FileCount -lt 1) { throw 'SELFTEST_DIGEST_ARGUMENTS_INVALID' }
    $prefix = ConvertTo-PowerShellLiteral ('S3_PREP_METADATA_DIGEST=' + $RunId + '|')
    $suffix = ConvertTo-PowerShellLiteral ('|' + $FileCount.ToString([Globalization.CultureInfo]::InvariantCulture) + '|' + $Digest.ToUpperInvariant())
    return '$pipeName=' + (ConvertTo-PowerShellLiteral $PipeName) +
        ';$claimedPid=' + $ClaimedProcessIdExpression +
        ';$pipe=[IO.Pipes.NamedPipeClientStream]::new(''.'',$pipeName,[IO.Pipes.PipeDirection]::Out);$pipe.Connect(5000);' +
        'try{$bytes=[Text.Encoding]::ASCII.GetBytes(' + $prefix + '+[string]$claimedPid+' + $suffix + '+[char]10);' +
        '$pipe.Write($bytes,0,$bytes.Length);$pipe.Flush()}finally{$pipe.Dispose()}'
}

function New-PrepareDigestRawPipeClientCode([string]$PipeName, [string]$PayloadText,
    [int]$HoldSeconds = 1, [string]$StdoutMarker = '') {
    $code = '$ErrorActionPreference=''Stop'';$pipeName=' + (ConvertTo-PowerShellLiteral $PipeName) +
        ';$payloadText=' + (ConvertTo-PowerShellLiteral $PayloadText) +
        ';$payloadText=$payloadText.Replace(''__PID__'',[string]$PID);' +
        '$bytes=[Text.Encoding]::UTF8.GetBytes($payloadText);' +
        '$pipe=[IO.Pipes.NamedPipeClientStream]::new(''.'',$pipeName,[IO.Pipes.PipeDirection]::Out);' +
        'try{$pipe.Connect(5000);try{$pipe.Write($bytes,0,$bytes.Length);$pipe.Flush()}catch{}}finally{$pipe.Dispose()}'
    if (-not [string]::IsNullOrEmpty($StdoutMarker)) {
        $code += ';[Console]::Out.WriteLine(' + (ConvertTo-PowerShellLiteral $StdoutMarker) + ')'
    }
    if ($HoldSeconds -gt 0) { $code += ';Start-Sleep -Seconds ' + $HoldSeconds.ToString([Globalization.CultureInfo]::InvariantCulture) }
    return $code
}

function Get-WindowsPowerShellExecutable {
    $command = Get-Command -Name 'powershell.exe' -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $command) { throw 'WINDOWS_POWERSHELL_EXECUTABLE_NOT_FOUND' }
    $path = $command.Source
    if ([string]::IsNullOrWhiteSpace($path)) { $path = $command.Definition }
    if ([string]::IsNullOrWhiteSpace($path)) { throw 'WINDOWS_POWERSHELL_EXECUTABLE_PATH_MISSING' }
    $fullPath = [IO.Path]::GetFullPath($path)
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { throw ('WINDOWS_POWERSHELL_EXECUTABLE_NOT_FOUND: ' + $fullPath) }
    return $fullPath
}

function Try-ReadSafeBytes([string]$Path) {
    try {
        $handle = [S3T03SafeFile]::OpenReadLeaf($Path)
        try { return [pscustomobject]@{ Found=$true; Bytes=[S3T03SafeFile]::ReadHandle($handle) } }
        finally { $handle.Dispose() }
    } catch [ComponentModel.Win32Exception] {
        if ($_.Exception.NativeErrorCode -eq 2 -or $_.Exception.NativeErrorCode -eq 3) {
            return [pscustomobject]@{ Found=$false; Bytes=[byte[]]@() }
        }
        throw
    }
}

function Get-ProgressFingerprint([string]$Directory) {
    $parts = [Collections.Generic.List[string]]::new()
    $statusPath = Join-Path $Directory 'run_status.txt'
    $statusRead = Try-ReadSafeBytes $statusPath
    if ($statusRead.Found) {
        $status = [Text.Encoding]::UTF8.GetString($statusRead.Bytes)
        foreach ($name in @('STAGE','RESULT','TCL_RESULT','SYNTH_STATE','OPT_STATE','PLACE_STATE','ROUTE_STATE')) {
            $match = [regex]::Match($status, '(?m)^' + [regex]::Escape($name) + '=(.*)$')
            if ($match.Success) { $parts.Add($name + '=' + $match.Groups[1].Value) }
        }
    }
    foreach ($name in @('vivado.log','vivado.jou')) {
        $path = Join-Path $Directory $name
        $read = Try-ReadSafeBytes $path
        if ($read.Found) { $parts.Add($name + '=' + $read.Bytes.Length) }
        else {
            $parts.Add($name + '=MISSING')
        }
    }
    return ($parts -join "`n")
}

function Get-ResultMarker([string]$Directory, [ValidateSet('prepare','run')] [string]$Phase) {
    $files = if ($Phase -eq 'prepare') {
        @((Join-Path $Directory 'prepare.result'), (Join-Path $Directory 'failure.result'), (Join-Path $Directory 'run_status.txt'))
    } else {
        @((Join-Path $Directory 'run_status.txt'), (Join-Path $Directory 'failure.result'), (Join-Path $Directory 'vivado.log'), (Join-Path $Directory 'vivado.jou'))
    }
    $found = $null
    foreach ($path in $files) {
        $read = Try-ReadSafeBytes $path
        if (-not $read.Found) { continue }
        $content = [Text.Encoding]::UTF8.GetString($read.Bytes)
        foreach ($line in ($content -split "`r?`n")) {
            $match = [regex]::Match($line, '^(?:S3_TCL_RESULT|TCL_RESULT)=(PASS|FAIL):([A-Z_]+)\s*$')
            if ($match.Success) {
                $found = [pscustomobject]@{ Kind=$match.Groups[1].Value; Code=$match.Groups[2].Value; Line=$line; Path=$path }
            }
        }
    }
    return $found
}

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash($Bytes)).Replace('-','') }
    finally { $sha.Dispose() }
}

function Get-ExpectedGeneratedClockXdcPath([string]$Directory) {
    $relative = 'project\s3_hdmi_only.gen\sources_1\bd\s3_hdmi_only\ip\s3_hdmi_only_rgb2dvi_0_0\rgb2dvi_0_0\src\rgb2dvi_clocks.xdc'
    return [IO.Path]::GetFullPath((Join-Path $Directory $relative))
}

function New-GeneratedClockXdcBrokerState([int]$BarrierTimeoutSeconds = 105) {
    return [pscustomobject]@{
        RequestPath=$null; Sha256=$null; Completed=$false; Error=$null
        BarrierStartedAt=$null; BarrierTimeout=[TimeSpan]::FromSeconds($BarrierTimeoutSeconds)
        ExpectedPath=$null
    }
}

function Write-GeneratedClockXdcBrokerError([string]$Directory, $Broker, $Leases, [string]$Code) {
    $Broker.Error = $Code
    $errorPath = Join-Path $Directory 'reports\generated_clock_xdc.lease_error'
    $message = "S3_GENERATED_CLOCK_LEASE=FAIL`nERROR=$Code`n"
    $Leases.WriteHeld($errorPath, [Text.Encoding]::UTF8.GetBytes($message))
}

function Invoke-GeneratedClockXdcLeaseBroker([string]$Directory, $Broker, $Leases) {
    $errorPath = Join-Path $Directory 'reports\generated_clock_xdc.lease_error'
    $errorBytes = $Leases.ReadHeld($errorPath)
    if ($errorBytes.Length -gt 0) {
        $errorText = [Text.Encoding]::UTF8.GetString($errorBytes)
        if (-not $errorText.EndsWith("`n", [StringComparison]::Ordinal)) { return }
        $errorMatch = [regex]::Match($errorText, '(?m)^ERROR=([A-Z0-9_]+)\s*$')
        $Broker.Error = if ($errorMatch.Success) { $errorMatch.Groups[1].Value } else { 'TCL_ERROR_CHANNEL_MALFORMED' }
        throw ('TCL_REPORTED_GENERATED_XDC_BROKER_ERROR: ' + $Broker.Error)
    }
    $statusBytes = $Leases.ReadHeld((Join-Path $Directory 'run_status.txt'))
    $status = [Text.Encoding]::UTF8.GetString($statusBytes)
    if ($status -match '(?m)^STAGE=GENERATED_CLOCK_XDC_LEASE_BARRIER\s*$') {
        if (-not $Broker.BarrierStartedAt) { $Broker.BarrierStartedAt = [DateTime]::UtcNow }
        if (([DateTime]::UtcNow - $Broker.BarrierStartedAt) -ge $Broker.BarrierTimeout) {
            Write-GeneratedClockXdcBrokerError $Directory $Broker $Leases 'BROKER_WAIT_TIMEOUT'
            throw 'GENERATED_CLOCK_XDC_BROKER_WAIT_TIMEOUT'
        }
    }

    $requestPath = Join-Path $Directory 'reports\generated_clock_xdc.lease_request'
    $requestBytes = $Leases.ReadHeld($requestPath)
    if ($requestBytes.Length -eq 0) { return }
    $requestText = [Text.Encoding]::UTF8.GetString($requestBytes)
    if (-not $requestText.EndsWith("`n", [StringComparison]::Ordinal)) { return }
    if ($Broker.Completed) {
        $expectedRequest = "S3_GENERATED_CLOCK_LEASE=1`nPATH_B64=" + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Broker.RequestPath)) + "`nSHA256=$($Broker.Sha256)`n"
        if ($requestText -cne $expectedRequest) {
            Write-GeneratedClockXdcBrokerError $Directory $Broker $Leases 'DUPLICATE_OR_MUTATED_REQUEST'
            throw 'GENERATED_CLOCK_XDC_BROKER_DUPLICATE_REQUEST'
        }
        return
    }

    try {
        $lines = $requestText.TrimEnd([char[]]@([char]13,[char]10)) -split "`r?`n"
        if ($lines.Count -ne 3 -or $lines[0] -cne 'S3_GENERATED_CLOCK_LEASE=1') { throw 'REQUEST_FORMAT_INVALID' }
        $pathMatch = [regex]::Match($lines[1], '^PATH_B64=([A-Za-z0-9+/]*={0,2})$')
        $hashMatch = [regex]::Match($lines[2], '^SHA256=([A-Fa-f0-9]{64})$')
        if (-not $pathMatch.Success -or -not $hashMatch.Success) { throw 'REQUEST_FORMAT_INVALID' }
        $target = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($pathMatch.Groups[1].Value))
        $requestedHash = $hashMatch.Groups[1].Value.ToUpperInvariant()
        $expected = Get-ExpectedGeneratedClockXdcPath $Directory
        if (-not [string]::Equals($target, $expected, [StringComparison]::OrdinalIgnoreCase) -or
            -not [string]::Equals($target, [IO.Path]::GetFullPath($target), [StringComparison]::OrdinalIgnoreCase)) {
            throw 'REQUEST_PATH_NOT_EXACT_EXPECTED_GENERATED_XDC'
        }
        $projectRoot = [IO.Path]::GetFullPath((Join-Path $Directory 'project')).TrimEnd('\') + '\'
        if (-not $target.StartsWith($projectRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'REQUEST_PATH_ESCAPES_PROJECT' }
        $Leases.LockDirectoryChain([IO.Path]::GetDirectoryName($target))
        $Leases.LockExistingReadOnly($target)
        $actualHash = Get-Sha256Hex ($Leases.ReadHeld($target))
        if ($actualHash -cne $requestedHash) { throw 'REQUEST_SHA256_MISMATCH' }

        $Broker.RequestPath = $target
        $Broker.Sha256 = $actualHash
        $Broker.ExpectedPath = $expected
        $ackPath = Join-Path $Directory 'reports\generated_clock_xdc.lease_ack'
        $ackText = "S3_GENERATED_CLOCK_LEASE=READY`nPATH_B64=" + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($target)) + "`nSHA256=$actualHash`n"
        $Leases.WriteHeld($ackPath, [Text.Encoding]::UTF8.GetBytes($ackText))
        $Broker.Completed = $true
    } catch {
        $message = $_.Exception.Message -replace '[\r\n=]', '_'
        Write-GeneratedClockXdcBrokerError $Directory $Broker $Leases $message
        throw ('GENERATED_CLOCK_XDC_BROKER_REJECTED: ' + $message)
    }
}

function Resolve-SupervisedResult($Process, [string]$Directory, [string]$Phase, [DateTime]$StartedAt,
    [TimeSpan]$MaxRuntime, [TimeSpan]$NoProgressLimit, [int]$PollMs, $LeaseBroker = $null, $Leases = $null) {
    $lastFingerprint = Get-ProgressFingerprint $Directory
    $lastProgressAt = [DateTime]::UtcNow
    $stopReason = 'PROCESS_EXITED'
    $brokerFailure = $null
    $firstLinkFailure = $null
    $linkCheckDiagnostic = if ($Leases) { 'NOT_RUN' } else { 'LEASES_NOT_SUPPLIED' }
    $linkCheckPhase = 'NOT_RUN'
    while (-not $Process.HasExited) {
        $now = [DateTime]::UtcNow
        if ($Leases) {
            $linkCheckDiagnostic = $Leases.AuditFileLinkCounts()
            $linkCheckPhase = 'SUPERVISION_POLL'
            if (-not $linkCheckDiagnostic.StartsWith('PASS;', [StringComparison]::Ordinal)) {
                $firstLinkFailure = $linkCheckDiagnostic
                $stopReason = $linkCheckDiagnostic.Split(';')[0]
                break
            }
        }
        if (($now - $StartedAt) -ge $MaxRuntime) { $stopReason = 'HARD_TIMEOUT_60_MIN'; break }
        if ($Phase -eq 'run' -and $LeaseBroker) {
            try { Invoke-GeneratedClockXdcLeaseBroker $Directory $LeaseBroker $Leases }
            catch { $brokerFailure = $_.Exception.Message; $stopReason = 'GENERATED_CLOCK_XDC_BROKER_FAILED'; break }
        }
        $fingerprint = Get-ProgressFingerprint $Directory
        if ($fingerprint -cne $lastFingerprint) {
            $lastFingerprint = $fingerprint
            $lastProgressAt = $now
        }
        if (($now - $lastProgressAt) -ge $NoProgressLimit) { $stopReason = 'NO_PROGRESS_15_MIN'; break }
        Start-Sleep -Milliseconds $PollMs
    }
    if ($stopReason -eq 'PROCESS_EXITED' -and ([DateTime]::UtcNow - $StartedAt) -ge $MaxRuntime) {
        $stopReason = 'HARD_TIMEOUT_60_MIN'
    }
    if ($stopReason -ne 'PROCESS_EXITED') {
        try {
            if (-not $Process.WaitForTreeExit(0)) { $Process.TerminateTree(124) }
        } catch {
            try { $Process.TerminateTree(124) }
            catch { $stopReason += '_TREE_TERMINATION_FAILED' }
        }
        $stopAt = [DateTime]::UtcNow.AddSeconds(8)
        while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $stopAt) { Start-Sleep -Milliseconds 100 }
        if (-not $Process.HasExited) { $stopReason += '_TREE_TERMINATION_UNCONFIRMED' }
    }

    $treeExitConfirmed = $false
    $treeExitDiagnostic = 'NOT_CHECKED'
    try {
        $treeExitConfirmed = $Process.WaitForTreeExit(8000)
        if ($treeExitConfirmed) {
            $treeExitDiagnostic = 'TREE_EMPTY'
        } else {
            $treeExitDiagnostic = 'TREE_EXIT_TIMEOUT_TERMINATING_JOB'
            $Process.TerminateTree(124)
            $treeExitConfirmed = $Process.WaitForTreeExit(8000)
            if ($treeExitConfirmed) {
                if ($stopReason -eq 'PROCESS_EXITED') { $stopReason = 'PROCESS_TREE_EXIT_TIMEOUT_TERMINATED' }
                $treeExitDiagnostic = 'TREE_TERMINATED_AFTER_TIMEOUT'
            } else {
                $treeExitDiagnostic = 'TREE_TERMINATION_UNCONFIRMED'
                if ($stopReason -eq 'PROCESS_EXITED') { $stopReason = 'PROCESS_TREE_TERMINATION_UNCONFIRMED' }
            }
        }
    } catch {
        $treeExitDiagnostic = 'TREE_EXIT_AUDIT_FAILED:' + ($_.Exception.Message -replace '[\r\n;=]', '_')
        $treeExitConfirmed = $false
        if ($stopReason -eq 'PROCESS_EXITED') { $stopReason = 'PROCESS_TREE_EXIT_AUDIT_FAILED' }
        try { $Process.TerminateTree(124) } catch { $treeExitDiagnostic += ';TERMINATION_FAILED' }
    }

    $finalLinkCheck = 'LEASES_NOT_SUPPLIED'
    if ($Leases) {
        try { $finalLinkCheck = $Leases.AuditFileLinkCounts() }
        catch { $finalLinkCheck = 'OUTPUT_LINK_AUDIT_FAILED;ERROR_B64=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($_.Exception.Message)) }
        if (-not $finalLinkCheck.StartsWith('PASS;', [StringComparison]::Ordinal) -and -not $firstLinkFailure) {
            $firstLinkFailure = $finalLinkCheck
        }
        if ($firstLinkFailure) { $linkCheckPhase = 'SUPERVISION_POLL_AND_FINAL' }
        else { $linkCheckPhase = 'FINAL_AFTER_TREE_EXIT' }
        $linkCheckDiagnostic = if ($firstLinkFailure) { $firstLinkFailure + ';FINAL=' + $finalLinkCheck } else { $finalLinkCheck }
    }

    $exitCode = $Process.ExitCode
    $marker = Get-ResultMarker $Directory $Phase
    if ($firstLinkFailure) { $result = $firstLinkFailure.Split(';')[0]; $stopReason = $result }
    elseif (-not $treeExitConfirmed) { $result = 'PROCESS_TREE_TERMINATION_UNCONFIRMED'; $stopReason = $result }
    elseif ($stopReason -ne 'PROCESS_EXITED') { $result = $stopReason }
    elseif ($marker -and $marker.Kind -eq 'FAIL') { $result = 'TCL_FAILURE_MARKER' }
    elseif ($exitCode -ne 0) { $result = 'NONZERO_PROCESS_EXIT' }
    elseif (-not $marker) { $result = 'MISSING_RESULT_MARKER' }
    elseif (($Phase -eq 'prepare' -and $marker.Kind -eq 'PASS' -and $marker.Code -eq 'PREPARED') -or
            ($Phase -eq 'run' -and $marker.Kind -eq 'PASS' -and $marker.Code -eq 'ROUTE_COMPLETE')) { $result = 'SUCCESS' }
    else { $result = 'UNEXPECTED_RESULT_MARKER' }
    if ($Phase -eq 'run' -and $result -eq 'SUCCESS' -and $LeaseBroker -and -not $LeaseBroker.Completed) {
        $result = 'MISSING_GENERATED_CLOCK_XDC_LEASE_ACK'
    }
    return [pscustomobject]@{
        Result=$result; StopReason=$stopReason; ExitCode=$exitCode; Marker=$marker
        ProcessId=$Process.ProcessId; Elapsed=([DateTime]::UtcNow - $StartedAt); BrokerError=$brokerFailure; Broker=$LeaseBroker
        LinkCheckDiagnostic=$linkCheckDiagnostic; LinkCheckPhase=$linkCheckPhase
        TreeExitConfirmed=$treeExitConfirmed; TreeExitDiagnostic=$treeExitDiagnostic
    }
}

function Write-SafeOutputText([string]$Path, [string]$Text, $Leases = $null) {
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text + "`n")
    if ($Leases) { $Leases.WriteHeld($Path, $bytes) }
    else { [S3T03SafeFile]::WriteCreateOrExisting($Path, [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path)), $bytes) }
}

function Write-RunnerStatus([string]$Directory, [string]$RunId, $Result, [string]$RunnerSha, $Leases) {
    if (-not $Leases) { throw 'RUNNER_STATUS_REQUIRES_HELD_OUTPUT_LEASES' }
    $logPath = Join-Path $Directory 'vivado.log'
    $journalPath = Join-Path $Directory 'vivado.jou'
    $logData = $Leases.ReadHeld($logPath)
    $journalData = $Leases.ReadHeld($journalPath)
    $logHash = Get-Sha256Hex $logData
    $journalHash = Get-Sha256Hex $journalData
    $logBytes = $logData.Length
    $journalBytes = $journalData.Length
    $markerLine = if ($Result.Marker) { $Result.Marker.Line } else { 'MISSING' }
    $prepareMarkerProperty = $Result.PSObject.Properties['PrepareMarker']
    $prepareMarker = if ($prepareMarkerProperty -and $prepareMarkerProperty.Value) { $prepareMarkerProperty.Value.Line } elseif ($prepareMarkerProperty) { 'MISSING' } else { 'NOT_APPLICABLE' }
    $brokerProperty = $Result.PSObject.Properties['Broker']
    $xdcBroker = if ($brokerProperty) { $brokerProperty.Value } else { $null }
    $linkDiagnosticProperty = $Result.PSObject.Properties['LinkCheckDiagnostic']
    $linkDiagnostic = if ($linkDiagnosticProperty) { [string]$linkDiagnosticProperty.Value } else { 'NOT_RUN' }
    $linkPhaseProperty = $Result.PSObject.Properties['LinkCheckPhase']
    $linkPhase = if ($linkPhaseProperty) { [string]$linkPhaseProperty.Value } else { 'NOT_RUN' }
    $treeConfirmedProperty = $Result.PSObject.Properties['TreeExitConfirmed']
    $treeConfirmed = if ($treeConfirmedProperty) { [string]$treeConfirmedProperty.Value } else { 'NOT_RUN' }
    $treeDiagnosticProperty = $Result.PSObject.Properties['TreeExitDiagnostic']
    $treeDiagnostic = if ($treeDiagnosticProperty) { [string]$treeDiagnosticProperty.Value } else { 'NOT_RUN' }
    $routeAbortPidProperty = $Result.PSObject.Properties['RouteStartAbortProcessId']
    $routeAbortPid = if ($routeAbortPidProperty) { [string]$routeAbortPidProperty.Value } else { 'NOT_APPLICABLE' }
    $routeAbortExitProperty = $Result.PSObject.Properties['RouteStartAbortExitCode']
    $routeAbortExit = if ($routeAbortExitProperty) { [string]$routeAbortExitProperty.Value } else { 'NOT_APPLICABLE' }
    $routeAbortPhaseProperty = $Result.PSObject.Properties['RouteStartAbortPhase']
    $routeAbortPhase = if ($routeAbortPhaseProperty) { [string]$routeAbortPhaseProperty.Value } else { 'NOT_APPLICABLE' }
    $text = @(
        'S3_RUNNER_RESULT=' + $Result.Result
        'RUN_ID=' + $RunId
        'STOP_REASON=' + $Result.StopReason
        'PROCESS_EXIT_CODE=' + $Result.ExitCode
        'OWNED_ROOT_PROCESS_ID=' + $Result.ProcessId
        'TCL_RESULT_MARKER=' + $markerLine
        'PREPARE_RESULT_MARKER=' + $prepareMarker
        'ELAPSED_SECONDS=' + [Math]::Round($Result.Elapsed.TotalSeconds, 3)
        'MAX_RUNTIME=60 minutes'
        'NO_PROGRESS_STOP=15 minutes'
        'EXECUTION_TCL_SHA256=' + (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $PSScriptRoot 's3_implement_hdmi_only_diag.tcl')).Hash
        'RUNNER_SCRIPT_SHA256=' + $RunnerSha
        'VIVADO_LOG=' + $logPath
        'VIVADO_LOG_BYTES=' + $logBytes
        'VIVADO_LOG_SHA256=' + $logHash
        'VIVADO_JOURNAL=' + $journalPath
        'VIVADO_JOURNAL_BYTES=' + $journalBytes
        'VIVADO_JOURNAL_SHA256=' + $journalHash
        'GENERATED_CLOCK_XDC_PATH=' + $(if ($xdcBroker -and $xdcBroker.Completed) { $xdcBroker.RequestPath } else { 'NOT_LEASED' })
        'GENERATED_CLOCK_XDC_SHA256=' + $(if ($xdcBroker -and $xdcBroker.Completed) { $xdcBroker.Sha256 } else { 'NOT_LEASED' })
        'GENERATED_CLOCK_XDC_BROKER_ERROR=' + $(if ($xdcBroker -and $xdcBroker.Error) { $xdcBroker.Error } else { 'NONE' })
        'OUTPUT_LINK_CHECK=' + $(if ($linkDiagnostic.StartsWith('PASS;', [StringComparison]::Ordinal)) { 'PASS' } elseif ($linkDiagnostic -eq 'NOT_RUN') { 'NOT_RUN' } else { 'FAIL' })
        'OUTPUT_LINK_CHECK_PHASE=' + $linkPhase
        'OUTPUT_LINK_CHECK_DIAGNOSTIC=' + $linkDiagnostic
        'PROCESS_TREE_EXIT_CONFIRMED=' + $treeConfirmed
        'PROCESS_TREE_EXIT_DIAGNOSTIC=' + $treeDiagnostic
        'ROUTE_START_ABORT_PROCESS_ID=' + $routeAbortPid
        'ROUTE_START_ABORT_EXIT_CODE=' + $routeAbortExit
        'ROUTE_START_ABORT_PHASE=' + $routeAbortPhase
    ) -join "`n"
    Write-SafeOutputText (Join-Path $Directory 'runner_status.txt') $text $Leases
}

function Invoke-RunnerCatchStatusHandler([string]$Directory, [string]$RunId, [string]$RunnerSha,
    [TimeSpan]$Elapsed, $Leases, $CapturedFailureStatus, $Broker = $null) {
    if ($CapturedFailureStatus -and $CapturedFailureStatus.Written) { return 'CAPTURED_FAILURE_PRESERVED' }
    if (-not $Leases -or -not $RunId -or -not $RunnerSha) { return 'RUNNER_EXCEPTION_STATUS_NOT_WRITTEN' }
    $failureResult = [pscustomobject]@{
        Result='RUNNER_EXCEPTION'; StopReason='RUNNER_EXCEPTION'; ExitCode='NOT_STARTED_OR_ABORTED'
        Marker=$null; ProcessId=0; Elapsed=$Elapsed; Broker=$Broker
        LinkCheckDiagnostic='NOT_RUN'; LinkCheckPhase='NOT_RUN'
        TreeExitConfirmed='NOT_RUN'; TreeExitDiagnostic='NOT_RUN'
    }
    Write-RunnerStatus $Directory $RunId $failureResult $RunnerSha $Leases
    return 'RUNNER_EXCEPTION_WRITTEN'
}

function Complete-PrepareFailureStatus([string]$Directory, [string]$RunId, $Result, [string]$RunnerSha, $Leases) {
    if (-not $Leases) { throw 'PREPARE_FAILURE_STATUS_REQUIRES_HELD_OUTPUT_LEASES' }
    Write-RunnerStatus $Directory $RunId $Result $RunnerSha $Leases
}

function New-DeadlineFailureResult($PrepareResult, [TimeSpan]$Elapsed, $RouteStartFailure = $null) {
    $routeStartAbortProcessId = 0
    $routeStartAbortExitCode = 'NOT_STARTED_OR_ABORTED'
    $routeStartAbortPhase = 'NOT_ATTEMPTED'
    if ($RouteStartFailure) {
        $routeStartAbortProcessId = $RouteStartFailure.ProcessId
        $routeStartAbortExitCode = $RouteStartFailure.ExitCode
        $routeStartAbortPhase = $RouteStartFailure.AbortPhase
    }
    return [pscustomobject]@{
        Result='HARD_TIMEOUT_60_MIN'; StopReason='HARD_TIMEOUT_60_MIN'; ExitCode=$PrepareResult.ExitCode
        Marker=$null; PrepareMarker=$PrepareResult.Marker; ProcessId=$PrepareResult.ProcessId; Elapsed=$Elapsed
        LinkCheckDiagnostic=$PrepareResult.LinkCheckDiagnostic; LinkCheckPhase=$PrepareResult.LinkCheckPhase
        TreeExitConfirmed=$PrepareResult.TreeExitConfirmed; TreeExitDiagnostic=$PrepareResult.TreeExitDiagnostic
        RouteStartAbortProcessId=$routeStartAbortProcessId; RouteStartAbortExitCode=$routeStartAbortExitCode
        RouteStartAbortPhase=$routeStartAbortPhase
    }
}

function Invoke-CapturedFailureAndThrow([string]$Directory, [string]$RunId, $Result, [string]$RunnerSha,
    $Leases, [ValidateSet('prepare','prepare-deadline','run')][string]$Source,
    [ref]$CapturedFailureStatus, [string]$FailureMessage, [scriptblock]$StatusWriter = $null) {
    if (-not $CapturedFailureStatus) { throw 'CAPTURED_FAILURE_STATUS_REFERENCE_REQUIRED' }
    if ($Source -eq 'prepare' -and -not $Leases) { throw 'PREPARE_FAILURE_STATUS_REQUIRES_HELD_OUTPUT_LEASES' }
    if ($Source -eq 'prepare-deadline' -and $Result.Result -cne 'HARD_TIMEOUT_60_MIN') { throw 'DEADLINE_FAILURE_RESULT_MISMATCH' }
    if ($Source -ne 'prepare-deadline' -and $Result.Result -ceq 'SUCCESS') { throw 'SUCCESS_RESULT_CANNOT_BE_CAPTURED_AS_FAILURE' }

    if ($StatusWriter) {
        & $StatusWriter $Directory $RunId $Result $RunnerSha $Leases
    } elseif ($Source -eq 'prepare') {
        Complete-PrepareFailureStatus $Directory $RunId $Result $RunnerSha $Leases
    } else {
        Write-RunnerStatus $Directory $RunId $Result $RunnerSha $Leases
    }

    $CapturedFailureStatus.Value = [pscustomobject]@{ Written=$true; Result=$Result; Source=$Source }
    throw $FailureMessage
}

function Invoke-PrepareDigestAuthenticationGate {
    param(
        [S3T03RunnerProcess]$PrepareProcess,
        [string]$ExpectedRunId,
        [string]$Directory,
        [string]$RunId,
        [string]$RunnerSha,
        $Leases,
        [ref]$CapturedFailureStatus,
        [TimeSpan]$Elapsed,
        $PrepareResult
    )
    if (-not $PrepareProcess) { throw 'PREPARE_DIGEST_PROCESS_REQUIRED' }
    try {
        $PrepareProcess.RequirePreparedMetadataDigest($ExpectedRunId)
        return [pscustomobject]@{
            Authenticated=$true
            FileCount=$PrepareProcess.PreparedMetadataFileCount
            Sha256=$PrepareProcess.PreparedMetadataTreeSha256
            ProcessId=$PrepareProcess.PreparedMetadataTclProcessId
            ParentProcessId=$PrepareProcess.PreparedMetadataTclParentProcessId
        }
    } catch {
        $failure = [pscustomobject]@{
            Result='PREPARE_DIGEST_AUTHENTICATION_FAILED'
            StopReason='PREPARE_DIGEST_AUTHENTICATION_FAILED'
            ExitCode=$PrepareProcess.ExitCode
            Marker=$null
            PrepareMarker=$(if ($PrepareResult) { $PrepareResult.Marker } else { $null })
            ProcessId=$PrepareProcess.ProcessId
            Elapsed=$Elapsed
            LinkCheckDiagnostic='NOT_RUN'
            LinkCheckPhase='NOT_RUN'
            TreeExitConfirmed='TRUE'
            TreeExitDiagnostic='PREPARE_PROCESS_EXIT_CONFIRMED'
        }
        Invoke-CapturedFailureAndThrow $Directory $RunId $failure $RunnerSha $Leases 'prepare' `
            $CapturedFailureStatus ('受控准备阶段摘要认证失败：' + $_.Exception.Message)
    }
}

function Invoke-RouteStartGate {
    param(
        $PrepareResult,
        [DateTime]$StartedAt,
        [TimeSpan]$MaxRuntime,
        [string]$Directory,
        [string]$RunId,
        [string]$RunnerSha,
        $Leases,
        [ref]$CapturedFailureStatus,
        [string]$FailureMessage,
        [scriptblock]$RouteStartAction,
        [scriptblock]$Clock = $null
    )
    if (-not $RouteStartAction) { throw 'ROUTE_START_ACTION_REQUIRED' }
    $deadlineUtc = $StartedAt.Add($MaxRuntime)
    if ($Clock) {
        $now = & $Clock
        if ($now -isnot [DateTime]) { throw 'ROUTE_START_CLOCK_MUST_RETURN_DATETIME' }
    } else {
        $now = [DateTime]::UtcNow
    }
    $elapsed = $now - $StartedAt
    if ($elapsed -ge $MaxRuntime) {
        $deadlineResult = New-DeadlineFailureResult $PrepareResult $elapsed
        Invoke-CapturedFailureAndThrow $Directory $RunId $deadlineResult $RunnerSha $Leases 'prepare-deadline' $CapturedFailureStatus $FailureMessage
    }

    # 最终时钟采样是 route 启动授权点；原生启动器还会在创建与恢复挂起进程前复查截止线。
    if ($Clock) {
        $now = & $Clock
        if ($now -isnot [DateTime]) { throw 'ROUTE_START_CLOCK_MUST_RETURN_DATETIME' }
    } else {
        $now = [DateTime]::UtcNow
    }
    $elapsed = $now - $StartedAt
    if ($elapsed -ge $MaxRuntime) {
        $deadlineResult = New-DeadlineFailureResult $PrepareResult $elapsed
        Invoke-CapturedFailureAndThrow $Directory $RunId $deadlineResult $RunnerSha $Leases 'prepare-deadline' $CapturedFailureStatus $FailureMessage
    }
    try {
        return (& $RouteStartAction $deadlineUtc)
    } catch {
        $startFailure = $_.Exception
        if ($startFailure -is [System.Management.Automation.MethodInvocationException]) {
            $startFailure = $startFailure.InnerException
        }
        if ($startFailure -isnot [S3T03DeadlineExceededException]) { throw }
        $deadlineResult = New-DeadlineFailureResult $PrepareResult $MaxRuntime $startFailure
        Invoke-CapturedFailureAndThrow $Directory $RunId $deadlineResult $RunnerSha $Leases 'prepare-deadline' `
            $CapturedFailureStatus $FailureMessage
    }
}

function Get-ExactNamedProcesses([string]$Name) {
    try {
        return @(Get-Process -Name $Name -ErrorAction Stop)
    } catch {
        if ($_.CategoryInfo.Category -eq [Management.Automation.ErrorCategory]::ObjectNotFound -and
            $_.FullyQualifiedErrorId -like 'NoProcessFoundForGivenName,*') {
            return @()
        }
        throw
    }
}

function Assert-NoVivadoAlreadyRunning([scriptblock]$ProcessQuery = { Get-ExactNamedProcesses -Name 'vivado' }) {
    try {
        $active = @(& $ProcessQuery)
    } catch {
        throw ('无法安全枚举 Vivado 进程，拒绝启动：' + $_.Exception.Message)
    }
    if ($active.Count -gt 0) {
        $ids = ($active | ForEach-Object { [string]$_.Id }) -join ','
        throw ('发现已有 vivado 进程，拒绝启动；PID=' + $ids)
    }
}

function Invoke-GuardedVivadoStart {
    param(
        [Parameter(Mandatory=$true)][scriptblock]$ProcessStartAction,
        [scriptblock]$ProcessQuery = { Get-ExactNamedProcesses -Name 'vivado' }
    )
    Assert-NoVivadoAlreadyRunning -ProcessQuery $ProcessQuery
    return (& $ProcessStartAction)
}

function Assert-Test([bool]$Condition, [string]$Name) {
    if (-not $Condition) { throw ('SUPERVISOR_SELFTEST_FAILED: ' + $Name) }
    [Console]::Out.WriteLine('SUPERVISOR_TEST=PASS:' + $Name)
}

function Complete-PrepareDigestSelfTestProcess([S3T03RunnerProcess]$Process, [string]$CaseName, [int]$TimeoutSeconds = 12) {
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    while (-not $Process.HasExited -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Milliseconds 25 }
    if (-not $Process.HasExited -or -not $Process.WaitForTreeExit(5000)) {
        $Process.TerminateTree(124)
        throw ('PREPARE_DIGEST_SELFTEST_CHILD_TIMEOUT:' + $CaseName)
    }
    return $Process.ExitCode
}

function Assert-S3T03SelfTestAttributes([uint32]$Attributes, [bool]$Directory, [string]$Path) {
    try { [S3T03SafeFile]::ValidateAttributesForTest($Attributes, $Directory) }
    catch { throw ('SELFTEST_REPARSE_POINT_REJECTED:' + $Path + ':' + $_.Exception.Message) }
}

function Assert-S3T03OrdinarySelfTestNode([string]$Path) {
    $attributes = [uint32][IO.File]::GetAttributes($Path)
    $isDirectory = (($attributes -band [uint32][S3T03SafeFile]::AttributeDirectory) -ne 0)
    Assert-S3T03SelfTestAttributes $attributes $isDirectory $Path
    if ($isDirectory) {
        $handle = [S3T03SafeFile]::OpenDirectory($Path)
        try {
            foreach ($child in [IO.Directory]::GetFileSystemEntries($Path)) {
                Assert-S3T03OrdinarySelfTestNode $child
            }
        } finally { $handle.Dispose() }
    } else {
        $handle = [S3T03SafeFile]::OpenReadLeaf($Path)
        $handle.Dispose()
    }
}

function Remove-S3T03OrdinarySelfTestNode([string]$Path) {
    $attributes = [uint32][IO.File]::GetAttributes($Path)
    $isDirectory = (($attributes -band [uint32][S3T03SafeFile]::AttributeDirectory) -ne 0)
    Assert-S3T03SelfTestAttributes $attributes $isDirectory $Path
    if ($isDirectory) {
        $handle = [S3T03SafeFile]::OpenDirectory($Path)
        try { $children = @([IO.Directory]::GetFileSystemEntries($Path)) }
        finally { $handle.Dispose() }
        foreach ($child in $children) { Remove-S3T03OrdinarySelfTestNode $child }
        [S3T03SafeFile]::DeleteEmptyDirectory($Path)
    } else {
        [S3T03SafeFile]::DeleteRegularFile($Path)
    }
}

function Remove-S3T03OwnedSelfTestTree([string]$Root, [string]$AllowedParent, [string]$NamePrefix, [string]$OwnerText) {
    $resolvedRoot = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $resolvedParent = [IO.Path]::GetFullPath($AllowedParent).TrimEnd('\')
    $actualParent = [IO.Path]::GetDirectoryName($resolvedRoot).TrimEnd('\')
    $leaf = [IO.Path]::GetFileName($resolvedRoot)
    $namePattern = '^' + [regex]::Escape($NamePrefix) + '[0-9a-f]{32}$'
    if (-not [string]::Equals($actualParent, $resolvedParent, [StringComparison]::OrdinalIgnoreCase) -or
        $leaf -notmatch $namePattern) {
        throw ('SELFTEST_CLEANUP_ROOT_NOT_OWNED:' + $resolvedRoot)
    }

    $parentHandle = [S3T03SafeFile]::OpenDirectory($resolvedParent)
    try {
        $rootHandle = [S3T03SafeFile]::OpenDirectory($resolvedRoot)
        $rootHandle.Dispose()
        $ownerPath = Join-Path $resolvedRoot '.s3_t03_runner_selftest_owned'
        $ownerHandle = [S3T03SafeFile]::OpenReadLeaf($ownerPath)
        try { $ownerActual = [Text.Encoding]::UTF8.GetString([S3T03SafeFile]::ReadHandle($ownerHandle)) }
        finally { $ownerHandle.Dispose() }
        if (-not [string]::Equals($ownerActual, $OwnerText, [StringComparison]::Ordinal)) {
            throw ('SELFTEST_CLEANUP_OWNER_MARKER_MISMATCH:' + $resolvedRoot)
        }

        Assert-S3T03OrdinarySelfTestNode $resolvedRoot
        Remove-S3T03OrdinarySelfTestNode $resolvedRoot
    } finally { $parentHandle.Dispose() }
}

function Get-S3T03SafeFileHash([string]$Path) {
    $handle = [S3T03SafeFile]::OpenReadLeaf($Path)
    try {
        $sha = [Security.Cryptography.SHA256]::Create()
        try { return [BitConverter]::ToString($sha.ComputeHash([S3T03SafeFile]::ReadHandle($handle))).Replace('-', '') }
        finally { $sha.Dispose() }
    } finally { $handle.Dispose() }
}

function Get-FixedVivadoInstallStatus {
    $batchExists = Test-Path -LiteralPath $vivadoBat -PathType Leaf
    $executableExists = Test-Path -LiteralPath $vivadoExe -PathType Leaf
    return [pscustomobject]@{
        BatchPath=$vivadoBat; ExecutablePath=$vivadoExe
        BatchExists=$batchExists; ExecutableExists=$executableExists
        IsValid=($batchExists -and $executableExists)
    }
}

function Assert-FixedVivadoInstall {
    $status = Get-FixedVivadoInstallStatus
    if (-not $status.IsValid) {
        throw ('固定 Vivado 安装缺失：BATCH=' + $status.BatchPath + '; EXECUTABLE=' + $status.ExecutablePath)
    }
    return $status
}

function New-FakeChild([string]$Directory, [string]$Code, [string]$Name) {
    $caseDir = Join-Path $Directory $Name
    [void][IO.Directory]::CreateDirectory($caseDir)
    $errorPath = ConvertTo-PowerShellLiteral (Join-Path $caseDir 'fake_error.txt')
    $fakeWriter = 'function Set-FakeFile([string]$p,[string]$v){$b=[Text.Encoding]::UTF8.GetBytes($v);$f=[IO.File]::Open($p,[IO.FileMode]::Create,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);try{$f.Write($b,0,$b.Length)}finally{$f.Dispose()}}'
    $fakeReader = 'function Read-FakeFile([string]$p){$f=[IO.File]::Open($p,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite);try{$b=New-Object IO.MemoryStream;$f.CopyTo($b);return [Text.Encoding]::UTF8.GetString($b.ToArray())}finally{$f.Dispose()}}'
    $fakeError = '$b=[Text.Encoding]::UTF8.GetBytes(($_|Out-String));$f=[IO.File]::Open(' + $errorPath + ',[IO.FileMode]::Create,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);try{$f.Write($b,0,$b.Length)}finally{$f.Dispose()};exit 91'
    $fakeScript = '$d=' + (ConvertTo-PowerShellLiteral $caseDir) + ';$ErrorActionPreference=''Stop'';' + $fakeWriter + ';' + $fakeReader + ';try{' + $Code + '}catch{' + $fakeError + '}'
    [void][ScriptBlock]::Create($fakeScript)
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($fakeScript))
    $exe = Get-WindowsPowerShellExecutable
    $line = New-DirectCommandLine $exe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$encoded)
    return [pscustomobject]@{ Directory=$caseDir; Process=[S3T03RunnerProcess]::Start($exe,$line,$repoRoot) }
}

function Invoke-SupervisorSelfTests {
    $tmpRoot = Join-Path $repoRoot 'tmp'
    if (-not (Test-Path -LiteralPath $tmpRoot -PathType Container)) { throw 'REPOSITORY_TMP_MISSING_FOR_SELFTEST' }
    Assert-Test (Test-OutputParentMatchesRepoTmp $tmpRoot $tmpRoot) 'direct-repository-tmp-output-parent-accepted'
    Assert-Test (Test-OutputParentMatchesRepoTmp (Join-Path $tmpRoot 'nested') $tmpRoot) 'nested-repository-tmp-output-parent-accepted'
    $outsideTmp = Join-Path (Split-Path -Parent $tmpRoot) 'tmp_outside'
    Assert-Test (-not (Test-OutputParentMatchesRepoTmp $outsideTmp $tmpRoot)) 'output-parent-outside-repository-tmp-rejected'
    $powershellExe = Get-WindowsPowerShellExecutable
    $testRoot = Join-Path $tmpRoot ('s3_t03_runner_selftest_' + [Guid]::NewGuid().ToString('N'))
    if (Test-Path -LiteralPath $testRoot) { throw 'SELFTEST_TEMP_COLLISION' }
    $tmpHandle = [S3T03SafeFile]::OpenDirectory($tmpRoot)
    try {
        $testRootHandle = [S3T03SafeFile]::CreateDirectoryWithinRoot($testRoot, $tmpRoot)
        $testRootHandle.Dispose()
    } finally { $tmpHandle.Dispose() }
    $ownerMarker = Join-Path $testRoot '.s3_t03_runner_selftest_owned'
    $ownerText = 'owned by supervised-runner selftest'
    [S3T03SafeFile]::WriteSingle($ownerMarker, $true, [Text.Encoding]::UTF8.GetBytes($ownerText))
    $unrelated = $null
    $secureLeases = $null
    $treeMonitor = $null
    $aclTreeRoot = $null
    $aclTreeSnapshots = $null
    $aclTreeOriginalSddl = $null
    $testExitCode = 1
    $testFailureMessage = $null
    $cleanupFailureMessage = $null
    try {
        $vivadoInstall = Get-FixedVivadoInstallStatus
        $expectedVivadoExe = Join-Path $vivadoBin 'unwrapped\win64.o\vivado.exe'
        Assert-Test ([string]::Equals($vivadoInstall.BatchPath, (Join-Path $vivadoBin 'vivado.bat'), [StringComparison]::OrdinalIgnoreCase) -and
            [string]::Equals($vivadoInstall.ExecutablePath, $expectedVivadoExe, [StringComparison]::OrdinalIgnoreCase)) `
            'fixed-vivado-install-paths-match-host-layout'
        Assert-Test ($vivadoInstall.IsValid -and $vivadoInstall.BatchExists -and $vivadoInstall.ExecutableExists) `
            'fixed-vivado-install-files-exist-without-launch'

        $secureTreeRoot = Join-Path $testRoot 'secure-tree'
        [void][IO.Directory]::CreateDirectory($secureTreeRoot)
        $secureTreeFile = Join-Path $secureTreeRoot 'ordinary.txt'
        [S3T03SafeFile]::WriteSingle($secureTreeFile, $true, [Text.Encoding]::UTF8.GetBytes('tree-content'))
        $treeFileSha = [Security.Cryptography.SHA256]::Create()
        try { $expectedTreeDigest = [BitConverter]::ToString($treeFileSha.ComputeHash([IO.File]::ReadAllBytes($secureTreeFile))).Replace('-','') }
        finally { $treeFileSha.Dispose() }
        $ordinaryTreeManifest = @(Get-SecureTreeSha256Manifest -Root $secureTreeRoot)
        Assert-Test ($ordinaryTreeManifest.Count -eq 1 -and $ordinaryTreeManifest[0] -eq ($expectedTreeDigest + [char]9 + 'ordinary.txt')) `
            'secure-tree-hash-manifest-matches-file'

        $secureTreeOutsideFile = Join-Path $testRoot 'secure-tree-outside-target.txt'
        $secureTreeOutsideLink = Join-Path $secureTreeRoot 'outside-target-link.txt'
        [S3T03SafeFile]::WriteSingle($secureTreeOutsideFile, $true, [Text.Encoding]::UTF8.GetBytes('outside-tree-target'))
        $outsideBefore = [Convert]::ToBase64String([IO.File]::ReadAllBytes($secureTreeOutsideFile))
        $outsideLinkRejected = $false
        try {
            [S3T03SafeFile]::CreateHardLink($secureTreeOutsideLink, $secureTreeOutsideFile)
            try { $null = @(Get-SecureTreeSha256Manifest -Root $secureTreeRoot) }
            catch { $outsideLinkRejected = $_.Exception.ToString().Contains('OUTPUT_LINK_COUNT_NOT_ONE') }
        } finally {
            if (Test-Path -LiteralPath $secureTreeOutsideLink -PathType Leaf) { [IO.File]::Delete($secureTreeOutsideLink) }
        }
        $outsideAfter = [Convert]::ToBase64String([IO.File]::ReadAllBytes($secureTreeOutsideFile))
        Assert-Test ($outsideLinkRejected -and $outsideBefore -ceq $outsideAfter) `
            'secure-tree-hash-rejects-outside-hardlink-without-modification'

        $secureTreeBusyRoot = Join-Path $testRoot 'secure-tree-busy-writer'
        [void][IO.Directory]::CreateDirectory($secureTreeBusyRoot)
        $secureTreeBusyFile = Join-Path $secureTreeBusyRoot 'writer-held.txt'
        [S3T03SafeFile]::WriteSingle($secureTreeBusyFile, $true, [Text.Encoding]::UTF8.GetBytes('writer-held'))
        $secureTreeWriter = [IO.File]::Open($secureTreeBusyFile, [IO.FileMode]::Open, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
        $concurrentWriterRejected = $false
        try {
            try { $null = @(Get-SecureTreeSha256Manifest -Root $secureTreeBusyRoot) }
            catch { $concurrentWriterRejected = $_.Exception.ToString().Contains('SECURE_READ_LEASE_OPEN_FAILED') }
        } finally { $secureTreeWriter.Dispose() }
        Assert-Test $concurrentWriterRejected 'secure-tree-hash-blocks-concurrent-writer'

        $secureRoot = Join-Path $testRoot 'secure-files'
        [void][IO.Directory]::CreateDirectory($secureRoot)
        $secureLeases = New-Object S3T03OutputLeaseSet($secureRoot)
        $secureLeases.LockParentDirectory($repoRoot)
        $secureLeases.LockParentDirectory((Join-Path $repoRoot 'tmp'))
        $secureLeases.LockParentDirectory($testRoot)
        $secureLeases.LockDirectory($secureRoot)
        $normalPath = Join-Path $secureRoot 'ordinary.txt'
        $secureLeases.ReserveNew($normalPath)
        $secureLeases.WriteHeld($normalPath, [Text.Encoding]::UTF8.GetBytes('first'))
        $secureLeases.WriteHeld($normalPath, [Text.Encoding]::UTF8.GetBytes('updated-twice'))
        $normalText = [Text.Encoding]::UTF8.GetString($secureLeases.ReadHeld($normalPath))
        Assert-Test ($normalText -eq 'updated-twice') 'secure-create-and-repeated-update'
        $sealedManifestPath = Join-Path $secureRoot 'sealed_manifest.txt'
        $sealedManifestBytes = [Text.Encoding]::UTF8.GetBytes("snapshot`n")
        $secureLeases.ReserveNew($sealedManifestPath)
        $secureLeases.WriteHeld($sealedManifestPath, $sealedManifestBytes)
        $sealedManifestSha = Get-Sha256Hex $sealedManifestBytes
        $secureLeases.SealExistingReadOnly($sealedManifestPath)
        $sealedManifestReadback = $secureLeases.ReadHeld($sealedManifestPath)
        $sealedManifestWriteRejected = $false
        try { $secureLeases.WriteHeld($sealedManifestPath, [Text.Encoding]::UTF8.GetBytes('changed')) }
        catch { $sealedManifestWriteRejected = $true }
        Assert-Test ((Get-Sha256Hex $sealedManifestReadback) -ceq $sealedManifestSha -and $sealedManifestWriteRejected) `
            'manifest-lease-seals-verified-content-read-only'

        $pinnedTreeRoot = Join-Path $secureRoot 'pinned-tree'
        $secureLeases.CreateDirectory($pinnedTreeRoot)
        $pinnedTreeFile = Join-Path $pinnedTreeRoot 'metadata.xml'
        [S3T03SafeFile]::WriteWithinRoot($pinnedTreeFile, $secureRoot, $true, [Text.Encoding]::UTF8.GetBytes('pinned-metadata'))
        $pinnedTreeRecords = @(Get-SecureTreeSha256Manifest -Root $pinnedTreeRoot -LeaseSet $secureLeases)
        $pinnedTreeManifest = Format-SecureTreeSha256Manifest -Root $pinnedTreeRoot -Records $pinnedTreeRecords
        Assert-Test ($pinnedTreeRecords.Count -eq 1 -and
            $pinnedTreeManifest.Contains('FILE_COUNT=1') -and
            $pinnedTreeManifest.Contains('  metadata.xml' + "`n")) 'supervisor-pins-and-formats-metadata-tree-after-prepare'
        $pinnedTreeSha256 = Get-SecureTreeRecordsSha256 -Records $pinnedTreeRecords
        $prepareChannelRunId = 'S3T03_DIGEST_SELFTEST'
        $prepareChannelPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $inheritableProbeHandle = [S3T03RunnerProcess]::CreateInheritableEventForSelfTest()
        $prepareChannelProcess = $null
        $staleBoundTargetFailure = ''
        try {
            $handleProbeSource = 'using System;using System.Runtime.InteropServices;public static class S3T03HandleProbe{[DllImport("kernel32.dll",SetLastError=true)]public static extern bool GetHandleInformation(IntPtr h,out uint f);[DllImport("kernel32.dll",SetLastError=true)]public static extern bool SetEvent(IntPtr h);}'
            $prepareChannelCode = '$ErrorActionPreference=''Stop'';$source=' + (ConvertTo-PowerShellLiteral $handleProbeSource) +
                ';Add-Type -TypeDefinition $source;$flags=[uint32]0;if([S3T03HandleProbe]::GetHandleInformation([IntPtr]' +
                $inheritableProbeHandle.ToInt64().ToString([Globalization.CultureInfo]::InvariantCulture) + ',[ref]$flags)){[void][S3T03HandleProbe]::SetEvent([IntPtr]' +
                $inheritableProbeHandle.ToInt64().ToString([Globalization.CultureInfo]::InvariantCulture) + ')};' +
                (New-PrepareDigestPipeClientCode $prepareChannelPipeName $prepareChannelRunId '$PID' 1 $pinnedTreeSha256) +
                ';Start-Sleep -Seconds 2'
            $prepareChannelEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($prepareChannelCode))
            $prepareChannelCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$prepareChannelEncoded)
            $prepareChannelProcess = [S3T03RunnerProcess]::StartForPrepare($powershellExe,$prepareChannelCommand,$repoRoot,$prepareChannelRunId,$powershellExe,$prepareChannelPipeName)
            $channelExitCode = Complete-PrepareDigestSelfTestProcess $prepareChannelProcess 'trusted-channel-and-handle-whitelist'
            if ($channelExitCode -ne 0) { throw ('PREPARE_DIGEST_HANDLE_WHITELIST_CHILD_EXITED:' + $channelExitCode) }
            $prepareChannelProcess.RequirePreparedMetadataDigest($prepareChannelRunId)
            $channelReportedCount = $prepareChannelProcess.PreparedMetadataFileCount
            $channelReportedSha256 = $prepareChannelProcess.PreparedMetadataTreeSha256
            $staleBoundTargetFailure = $prepareChannelProcess.ValidateBoundPrepareTclProcessForSelfTest(
                $prepareChannelProcess.BoundPrepareTclProcessId)
            $unlistedHandleSignaledParentEvent = [S3T03RunnerProcess]::IsSelfTestEventSignaled($inheritableProbeHandle)
        } finally {
            if ($prepareChannelProcess) { $prepareChannelProcess.Dispose() }
            [S3T03RunnerProcess]::CloseSelfTestHandle($inheritableProbeHandle)
        }
        Assert-Test ($channelReportedCount -eq 1 -and $channelReportedSha256 -ceq $pinnedTreeSha256 -and
            -not $unlistedHandleSignaledParentEvent) `
            'prepare-digest-authenticates-named-pipe-client-job-image-and-handle-whitelist'
        Assert-Test ($staleBoundTargetFailure -eq 'PREPARE_DIGEST_TCL_LAUNCH_TARGET_EXITED_AFTER_BIND') `
            ('prepare-digest-rejects-stale-bound-process-handle-with-same-reported-pid; OBSERVED=' + $staleBoundTargetFailure)
        Assert-Test ([S3T03RunnerProcess]::VerifyCurrentUserPipeAclForSelfTest()) `
            'prepare-digest-pipe-acl-allows-only-current-user'

        $nonJobRunId = 'S3T03_NON_JOB_PID_SELFTEST'
        $nonJobPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $nonJobCode = 'Start-Sleep -Seconds 2'
        $nonJobEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($nonJobCode))
        $nonJobCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$nonJobEncoded)
        $nonJobProcess = [S3T03RunnerProcess]::StartForPrepare($powershellExe,$nonJobCommand,$repoRoot,$nonJobRunId,$powershellExe,$nonJobPipeName)
        $nonJobFailure = ''
        $nonJobWriteRejected = $false
        try {
            $nonJobPipeClient = [IO.Pipes.NamedPipeClientStream]::new('.',$nonJobPipeName,[IO.Pipes.PipeDirection]::Out)
            try {
                $nonJobPipeClient.Connect(5000)
                $nonJobPayload = [Text.Encoding]::ASCII.GetBytes('S3_PREP_METADATA_DIGEST=' + $nonJobRunId + '|' +
                    ([uint32]$PID).ToString([Globalization.CultureInfo]::InvariantCulture) + '|1|' + $pinnedTreeSha256 + "`n")
                $nonJobPipeClient.Write($nonJobPayload,0,$nonJobPayload.Length)
                $nonJobPipeClient.Flush()
            } catch { $nonJobWriteRejected = $true
            } finally { $nonJobPipeClient.Dispose() }
            $nonJobExitCode = Complete-PrepareDigestSelfTestProcess $nonJobProcess 'non-job-pid-rejection'
            if ($nonJobExitCode -ne 0) { throw ('NON_JOB_PID_SELFTEST_CHILD_EXITED:' + $nonJobExitCode) }
            try { $nonJobProcess.RequirePreparedMetadataDigest($nonJobRunId) }
            catch { $nonJobFailure = $_.Exception.ToString() }
        } finally { $nonJobProcess.Dispose() }
        Assert-Test (($nonJobFailure.Contains('PREPARE_DIGEST_PIPE_CLIENT_PID_NOT_EXACT_LAUNCH_TARGET') -or
            $nonJobFailure.Contains('PREPARE_DIGEST_TCL_PROCESS_NOT_IN_JOB')) -and $nonJobWriteRejected) `
            ('prepare-digest-rejects-non-job-client; WRITE_REJECTED=' + $nonJobWriteRejected + '; OBSERVED=' + $nonJobFailure)

        $wrongImageRunId = 'S3T03_WRONG_IMAGE_SELFTEST'
        $wrongImagePipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $wrongImageCode = '$ErrorActionPreference=''Stop'';try{' +
            (New-PrepareDigestPipeClientCode $wrongImagePipeName $wrongImageRunId '$PID' 1 $pinnedTreeSha256) +
            '}catch{};Start-Sleep -Seconds 2'
        $wrongImageEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($wrongImageCode))
        $wrongImageCommand = New-BatchCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$wrongImageEncoded)
        $wrongImageProcess = [S3T03RunnerProcess]::StartForPrepare($comSpec,$wrongImageCommand,$repoRoot,$wrongImageRunId,$comSpec,$wrongImagePipeName)
        $wrongImageFailure = ''
        try {
            $wrongImageExitCode = Complete-PrepareDigestSelfTestProcess $wrongImageProcess 'wrong-image-rejection'
            if ($wrongImageExitCode -ne 0) { throw ('WRONG_IMAGE_SELFTEST_CHILD_EXITED:' + $wrongImageExitCode) }
            try { $wrongImageProcess.RequirePreparedMetadataDigest($wrongImageRunId) }
            catch { $wrongImageFailure = $_.Exception.ToString() }
        } finally { $wrongImageProcess.Dispose() }
        Assert-Test ($wrongImageFailure.Contains('PREPARE_DIGEST_PIPE_CLIENT_PID_NOT_EXACT_LAUNCH_TARGET')) `
            'prepare-digest-rejects-wrong-image-pipe-client-not-the-fixed-launch-target'

        $treeHelperRunId = 'S3T03_TREE_HELPER_PID_SELFTEST'
        $treeHelperPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $treeHelperChildCode = New-PrepareDigestPipeClientCode $treeHelperPipeName $treeHelperRunId '$PID' 1 $pinnedTreeSha256
        $treeHelperChildEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($treeHelperChildCode))
        $treeHelperChildArguments = (@('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$treeHelperChildEncoded) |
            ForEach-Object { ConvertTo-WindowsArgument $_ }) -join ' '
        $jobMembershipProbeSource = 'using System;using System.Runtime.InteropServices;public static class S3T03JobMembershipProbe{[DllImport("kernel32.dll",SetLastError=true)]public static extern bool IsProcessInJob(IntPtr process,IntPtr job,out bool result);}'
        $treeHelperParentCode = '$ErrorActionPreference=''Stop'';$source=' + (ConvertTo-PowerShellLiteral $jobMembershipProbeSource) +
            ';Add-Type -TypeDefinition $source;$psi=New-Object Diagnostics.ProcessStartInfo;' +
            '$psi.FileName=' + (ConvertTo-PowerShellLiteral $powershellExe) +
            ';$psi.Arguments=' + (ConvertTo-PowerShellLiteral $treeHelperChildArguments) +
            ';$psi.UseShellExecute=$false;$psi.CreateNoWindow=$true;$helper=[Diagnostics.Process]::Start($psi);' +
            '$inJob=$false;if(-not [S3T03JobMembershipProbe]::IsProcessInJob($helper.Handle,[IntPtr]::Zero,[ref]$inJob)-or-not $inJob){exit 91};' +
            'if(-not $helper.WaitForExit(10000)){exit 92};Write-Output (''SELFTEST_SIBLING_REAL_PID='' + $helper.Id + '';EXIT='' + $helper.ExitCode);Start-Sleep -Seconds 2'
        $treeHelperParentEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($treeHelperParentCode))
        $treeHelperCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$treeHelperParentEncoded)
        $treeHelperProcess = [S3T03RunnerProcess]::StartForPrepare($powershellExe,$treeHelperCommand,$repoRoot,$treeHelperRunId,$powershellExe,$treeHelperPipeName)
        $treeHelperFailure = ''
        try {
            $treeHelperExitCode = Complete-PrepareDigestSelfTestProcess $treeHelperProcess 'tree-helper-pid-rejection'
            if ($treeHelperExitCode -ne 0) { throw ('TREE_HELPER_PID_SELFTEST_CHILD_EXITED:' + $treeHelperExitCode) }
            try { $treeHelperProcess.RequirePreparedMetadataDigest($treeHelperRunId) }
            catch { $treeHelperFailure = $_.Exception.ToString() }
        } finally { $treeHelperProcess.Dispose() }
        Assert-Test ($treeHelperFailure.Contains('PREPARE_DIGEST_PIPE_CLIENT_PID_NOT_EXACT_LAUNCH_TARGET') -and
            $treeHelperProcess.ObservedPrepareDigestClientProcessId -gt 0 -and
            $treeHelperProcess.ObservedPrepareDigestClientProcessId -ne $treeHelperProcess.BoundPrepareTclProcessId) `
            ('prepare-digest-rejects-same-job-same-image-sibling-using-real-pid; LAUNCH_PID=' + $treeHelperProcess.ProcessId +
                '; BOUND_PID=' + $treeHelperProcess.BoundPrepareTclProcessId +
                '; PIPE_CLIENT_PID=' + $treeHelperProcess.ObservedPrepareDigestClientProcessId + '; OBSERVED=' + $treeHelperFailure)

        $negativeRunId = 'S3T03_PIPE_NEGATIVE_SELFTEST'
        $negativeDigestLine = 'S3_PREP_METADATA_DIGEST=' + $negativeRunId + '|__PID__|1|' + $pinnedTreeSha256 + "`n"
        $negativePipeCases = @(
            @{ Name='non-ascii'; Payload=($negativeDigestLine + '非ASCII'); Expected='PREPARE_DIGEST_PIPE_MESSAGE_NOT_ASCII' },
            @{ Name='oversized'; Payload=($negativeDigestLine + ('X' * 300)); Expected='PREPARE_DIGEST_PIPE_MESSAGE_TOO_LARGE' },
            @{ Name='multiline'; Payload=($negativeDigestLine + 'EXTRA=1' + "`n"); Expected='PREPARE_DIGEST_PIPE_MESSAGE_LINE_FORMAT_INVALID' },
            @{ Name='duplicate-lines'; Payload=($negativeDigestLine + $negativeDigestLine); Expected='PREPARE_DIGEST_PIPE_MESSAGE_LINE_FORMAT_INVALID' },
            @{ Name='wrong-run-id'; Payload=('S3_PREP_METADATA_DIGEST=OTHER_RUN|__PID__|1|' + $pinnedTreeSha256 + "`n"); Expected='PREPARE_DIGEST_MESSAGE_FORMAT_OR_RUN_ID_INVALID' }
        )
        foreach ($negativePipeCase in $negativePipeCases) {
            $negativePipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
            $negativePipeCode = New-PrepareDigestRawPipeClientCode $negativePipeName $negativePipeCase.Payload
            $negativePipeEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($negativePipeCode))
            $negativePipeCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$negativePipeEncoded)
            $negativePipeProcess = [S3T03RunnerProcess]::StartForPrepare($powershellExe,$negativePipeCommand,$repoRoot,
                $negativeRunId,$powershellExe,$negativePipeName)
            $negativePipeFailure = ''
            try {
                $negativePipeExitCode = Complete-PrepareDigestSelfTestProcess $negativePipeProcess ('pipe-' + $negativePipeCase.Name)
                if ($negativePipeExitCode -ne 0) { throw ('NEGATIVE_PIPE_SELFTEST_CHILD_EXITED:' + $negativePipeCase.Name + ':' + $negativePipeExitCode) }
                try { $negativePipeProcess.RequirePreparedMetadataDigest($negativeRunId) }
                catch { $negativePipeFailure = $_.Exception.ToString() }
            } finally { $negativePipeProcess.Dispose() }
            Assert-Test ($negativePipeFailure.Contains($negativePipeCase.Expected)) `
                ('prepare-digest-fails-closed-' + $negativePipeCase.Name + '; OBSERVED=' + $negativePipeFailure)
        }

        $stdoutForgeryRunId = 'S3T03_STDOUT_FORGERY_SELFTEST'
        $stdoutForgeryPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $stdoutForgeryPayload = 'S3_PREP_METADATA_DIGEST=' + $stdoutForgeryRunId + '|__PID__|1|' + $pinnedTreeSha256 + "`n"
        $stdoutForgeryMarker = 'S3_PREP_METADATA_DIGEST=' + $stdoutForgeryRunId + '|999999|1|' + $pinnedTreeSha256
        $stdoutForgeryCode = New-PrepareDigestRawPipeClientCode $stdoutForgeryPipeName $stdoutForgeryPayload 1 $stdoutForgeryMarker
        $stdoutForgeryEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($stdoutForgeryCode))
        $stdoutForgeryCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$stdoutForgeryEncoded)
        $stdoutForgeryProcess = [S3T03RunnerProcess]::StartForPrepare($powershellExe,$stdoutForgeryCommand,$repoRoot,
            $stdoutForgeryRunId,$powershellExe,$stdoutForgeryPipeName)
        $stdoutForgeryFailure = ''
        try {
            $stdoutForgeryExitCode = Complete-PrepareDigestSelfTestProcess $stdoutForgeryProcess 'pipe-with-stdout-forgery'
            if ($stdoutForgeryExitCode -ne 0) { throw ('STDOUT_FORGERY_SELFTEST_CHILD_EXITED:' + $stdoutForgeryExitCode) }
            try { $stdoutForgeryProcess.RequirePreparedMetadataDigest($stdoutForgeryRunId) }
            catch { $stdoutForgeryFailure = $_.Exception.ToString() }
        } finally { $stdoutForgeryProcess.Dispose() }
        Assert-Test ($stdoutForgeryFailure.Contains('PREPARE_DIGEST_UNTRUSTED_STDOUT_MARKER')) `
            ('valid-pipe-digest-plus-stdout-forgery-fails-as-a-whole; OBSERVED=' + $stdoutForgeryFailure)

        $noClientRunId = 'S3T03_NO_PIPE_CLIENT_SELFTEST'
        $noClientPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $noClientCode = 'Start-Sleep -Seconds 1'
        $noClientEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($noClientCode))
        $noClientCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$noClientEncoded)
        $noClientProcess = [S3T03RunnerProcess]::StartForPrepare($powershellExe,$noClientCommand,$repoRoot,
            $noClientRunId,$powershellExe,$noClientPipeName)
        $noClientFailure = ''
        try {
            $noClientExitCode = Complete-PrepareDigestSelfTestProcess $noClientProcess 'pipe-no-client-timeout'
            if ($noClientExitCode -ne 0) { throw ('NO_CLIENT_SELFTEST_CHILD_EXITED:' + $noClientExitCode) }
            try { $noClientProcess.RequirePreparedMetadataDigest($noClientRunId) }
            catch { $noClientFailure = $_.Exception.ToString() }
        } finally { $noClientProcess.Dispose() }
        Assert-Test ($noClientFailure.Contains('PREPARE_DIGEST_PIPE_READ_TIMEOUT')) `
            ('prepare-digest-no-client-times-out-fail-closed; OBSERVED=' + $noClientFailure)

        $realVivadoPipeRunId = 'SELFTEST_DIGEST_PIPE'
        $realVivadoSiblingPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $realVivadoSiblingLog = Join-Path $testRoot 'vivado_digest_sibling_selftest.log'
        $realVivadoSiblingJournal = Join-Path $testRoot 'vivado_digest_sibling_selftest.jou'
        $realVivadoTclScript = Join-Path $repoRoot 'scripts\s3_implement_hdmi_only_diag.tcl'
        $realVivadoSiblingArgs = @('-mode','batch','-log',(Join-Path $testRoot 'vivado_digest_sibling_parent.log'),
            '-journal',(Join-Path $testRoot 'vivado_digest_sibling_parent.jou'),'-source','scripts/s3_implement_hdmi_only_diag.tcl',
            '-tclargs','--selftest-launch-same-image-sibling',$realVivadoSiblingPipeName,
            $realVivadoSiblingLog,$realVivadoSiblingJournal,$realVivadoTclScript)
        $realVivadoSiblingCommand = New-BatchCommandLine $vivadoBat $realVivadoSiblingArgs
        $realVivadoSiblingProcess = Invoke-GuardedVivadoStart -ProcessStartAction {
            [S3T03RunnerProcess]::StartForPrepare($comSpec,$realVivadoSiblingCommand,$repoRoot,
                $realVivadoPipeRunId,$vivadoInstall.ExecutablePath,$realVivadoSiblingPipeName)
        }
        $realVivadoSiblingFailure = ''
        $realVivadoSiblingE2eRoot = Join-Path $testRoot 'real-vivado-sibling-prepare-e2e'
        $realVivadoSiblingE2eLeases = Initialize-SafeOutputLeases $realVivadoSiblingE2eRoot
        $realVivadoSiblingE2eCaptured = $null
        $realVivadoSiblingE2eCatchAction = ''
        $realVivadoSiblingE2eRouteActionState = [pscustomobject]@{ Count=0 }
        $realVivadoSiblingE2eStatus = ''
        try {
            $realVivadoSiblingExitCode = Complete-PrepareDigestSelfTestProcess $realVivadoSiblingProcess 'real-vivado-same-image-sibling' 120
            if ($realVivadoSiblingExitCode -ne 0) {
                $siblingLogTail = if (Test-Path -LiteralPath (Join-Path $testRoot 'vivado_digest_sibling_parent.log') -PathType Leaf) {
                    (Get-Content -LiteralPath (Join-Path $testRoot 'vivado_digest_sibling_parent.log') -Tail 30 -ErrorAction SilentlyContinue) -join ' | '
                } else { 'VIVADO_SIBLING_PARENT_LOG_MISSING' }
                throw ('REAL_VIVADO_SIBLING_SELFTEST_PARENT_EXITED:' + $realVivadoSiblingExitCode + '; LOG=' + $siblingLogTail)
            }
            $realVivadoSiblingE2ePrepareResult = [pscustomobject]@{
                Result='SUCCESS'; StopReason='PROCESS_EXITED'; ExitCode=$realVivadoSiblingExitCode
                Marker=[pscustomobject]@{ Kind='PASS'; Code='PREPARED'; Line='S3_TCL_RESULT=PASS:PREPARED' }
                ProcessId=$realVivadoSiblingProcess.ProcessId; Elapsed=[TimeSpan]::FromSeconds(1)
            }
            try {
                $realVivadoSiblingAuthorization = Invoke-PrepareDigestAuthenticationGate `
                    $realVivadoSiblingProcess $realVivadoPipeRunId $realVivadoSiblingE2eRoot $realVivadoPipeRunId `
                    'selftest-runner-sha' $realVivadoSiblingE2eLeases ([ref]$realVivadoSiblingE2eCaptured) `
                    ([TimeSpan]::FromSeconds(1)) $realVivadoSiblingE2ePrepareResult
                $realVivadoSiblingRouteAction = {
                    param([DateTime]$RouteDeadlineUtc)
                    $realVivadoSiblingE2eRouteActionState.Count++
                    'ROUTE_ACTION_INVOKED'
                }.GetNewClosure()
                [void](Invoke-RouteStartGate -PrepareResult $realVivadoSiblingE2ePrepareResult `
                    -StartedAt ([DateTime]::UtcNow) -MaxRuntime ([TimeSpan]::FromMinutes(1)) `
                    -Directory $realVivadoSiblingE2eRoot -RunId $realVivadoPipeRunId `
                    -RunnerSha 'selftest-runner-sha' -Leases $realVivadoSiblingE2eLeases `
                    -CapturedFailureStatus ([ref]$realVivadoSiblingE2eCaptured) `
                    -FailureMessage 'SELFTEST_SIBLING_AUTHENTICATION_FAILURE' -RouteStartAction $realVivadoSiblingRouteAction)
            } catch {
                $realVivadoSiblingFailure = $_.Exception.ToString()
                $realVivadoSiblingE2eCatchAction = Invoke-RunnerCatchStatusHandler `
                    $realVivadoSiblingE2eRoot $realVivadoPipeRunId 'selftest-runner-sha' `
                    ([TimeSpan]::FromSeconds(1)) $realVivadoSiblingE2eLeases $realVivadoSiblingE2eCaptured
            }
            $realVivadoSiblingE2eStatus = [Text.Encoding]::UTF8.GetString(
                $realVivadoSiblingE2eLeases.ReadHeld((Join-Path $realVivadoSiblingE2eRoot 'runner_status.txt')))
        } finally {
            $realVivadoSiblingProcess.Dispose()
            $realVivadoSiblingE2eLeases.Dispose()
        }
        $realVivadoSiblingLogTail = if (Test-Path -LiteralPath $realVivadoSiblingLog -PathType Leaf) {
            (Get-Content -LiteralPath $realVivadoSiblingLog -Tail 30 -ErrorAction SilentlyContinue) -join ' | '
        } else { 'VIVADO_SIBLING_LOG_MISSING' }
        $realVivadoSiblingParentLog = Join-Path $testRoot 'vivado_digest_sibling_parent.log'
        $realVivadoSiblingParentLogTail = if (Test-Path -LiteralPath $realVivadoSiblingParentLog -PathType Leaf) {
            (Get-Content -LiteralPath $realVivadoSiblingParentLog -Tail 30 -ErrorAction SilentlyContinue) -join ' | '
        } else { 'VIVADO_SIBLING_PARENT_LOG_MISSING' }
        Assert-Test ($realVivadoSiblingFailure.Contains('PREPARE_DIGEST_PIPE_CLIENT_PID_NOT_EXACT_LAUNCH_TARGET') -and
            $realVivadoSiblingProcess.BoundPrepareTclProcessId -gt 0 -and
            $realVivadoSiblingProcess.PreparedMetadataTclParentProcessId -eq $realVivadoSiblingProcess.ProcessId -and
            $realVivadoSiblingProcess.ObservedPrepareDigestClientProcessId -gt 0 -and
            $realVivadoSiblingProcess.ObservedPrepareDigestClientParentProcessId -eq $realVivadoSiblingProcess.BoundPrepareTclProcessId -and
            $realVivadoSiblingProcess.ObservedPrepareDigestClientProcessId -ne $realVivadoSiblingProcess.BoundPrepareTclProcessId -and
            $realVivadoSiblingE2eCaptured.Written -and
            $realVivadoSiblingE2eStatus.Contains('S3_RUNNER_RESULT=PREPARE_DIGEST_AUTHENTICATION_FAILED') -and
            -not $realVivadoSiblingE2eStatus.Contains('S3_RUNNER_RESULT=SUCCESS') -and
            $realVivadoSiblingE2eRouteActionState.Count -eq 0 -and
            $realVivadoSiblingE2eCatchAction -eq 'CAPTURED_FAILURE_PRESERVED') `
            ('real-vivado-same-image-sibling-fails-prepare-terminal-and-route-is-not-started; CMD_PID=' + $realVivadoSiblingProcess.ProcessId +
                '; BOUND_VIVADO_PID=' + $realVivadoSiblingProcess.BoundPrepareTclProcessId +
                '; PIPE_CLIENT_PID=' + $realVivadoSiblingProcess.ObservedPrepareDigestClientProcessId +
                '; PIPE_CLIENT_PARENT_PID=' + $realVivadoSiblingProcess.ObservedPrepareDigestClientParentProcessId +
                '; CAPTURED=' + $realVivadoSiblingE2eCaptured.Result +
                '; ROUTE_START_COUNT=' + $realVivadoSiblingE2eRouteActionState.Count +
                '; STATUS=' + $realVivadoSiblingE2eStatus.Replace("`n",'|') +
                '; OBSERVED=' + $realVivadoSiblingFailure +
                '; PARENT_LOG=' + $realVivadoSiblingParentLogTail + '; SIBLING_LOG=' + $realVivadoSiblingLogTail)

        $realVivadoPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
        $realVivadoLog = Join-Path $testRoot 'vivado_digest_pipe_selftest.log'
        $realVivadoJournal = Join-Path $testRoot 'vivado_digest_pipe_selftest.jou'
        $realVivadoArgs = @('-mode','batch','-log',$realVivadoLog,'-journal',$realVivadoJournal,
            '-source','scripts/s3_implement_hdmi_only_diag.tcl','-tclargs','--selftest-digest-pipe',$realVivadoPipeName)
        $realVivadoCommand = New-BatchCommandLine $vivadoBat $realVivadoArgs
        $realVivadoPipeProcess = Invoke-GuardedVivadoStart -ProcessStartAction {
            [S3T03RunnerProcess]::StartForPrepare($comSpec,$realVivadoCommand,$repoRoot,
                $realVivadoPipeRunId,$vivadoInstall.ExecutablePath,$realVivadoPipeName)
        }
        $realVivadoClientPid = [uint32]0
        try {
            $realVivadoExitCode = Complete-PrepareDigestSelfTestProcess $realVivadoPipeProcess 'real-vivado-digest-pipe' 120
            if ($realVivadoExitCode -ne 0) {
                $realVivadoLogTail = if (Test-Path -LiteralPath $realVivadoLog -PathType Leaf) { (Get-Content -LiteralPath $realVivadoLog -Tail 30 -ErrorAction SilentlyContinue) -join ' | ' } else { 'VIVADO_LOG_MISSING' }
                throw ('REAL_VIVADO_DIGEST_PIPE_CHILD_EXITED:' + $realVivadoExitCode + '; LOG=' + $realVivadoLogTail)
            }
            $realVivadoPipeProcess.RequirePreparedMetadataDigest($realVivadoPipeRunId)
            $realVivadoClientPid = $realVivadoPipeProcess.PreparedMetadataTclProcessId
        } finally { $realVivadoPipeProcess.Dispose() }
        Assert-Test ($realVivadoClientPid -gt 0) ('real-vivado-tcl-authenticated-named-pipe-client-pid=' + $realVivadoClientPid)

        $verifiedPreparedTreeSha256 = Assert-PreparedMetadataTreeSha256 -Records $pinnedTreeRecords `
            -ExpectedCount 1 -ExpectedSha256 $pinnedTreeSha256
        $tamperedTreeRecords = @(('A' * 64) + [char]9 + 'metadata.xml')
        $tamperedTreeRejected = $false
        try { Assert-PreparedMetadataTreeSha256 -Records $tamperedTreeRecords -ExpectedCount 1 -ExpectedSha256 $pinnedTreeSha256 }
        catch { $tamperedTreeRejected = $_.Exception.Message.Contains('PREPARED_METADATA_TREE_SHA256_MISMATCH') }
        $forgedTreeSha256 = Get-SecureTreeRecordsSha256 -Records $tamperedTreeRecords
        $forgedPrepareText = "S3_TCL_RESULT=PASS:PREPARED`nRUN_ID=$prepareChannelRunId`nMETADATA_COUNT=1`nMETADATA_TREE_SHA256=$forgedTreeSha256`n"
        $forgedMarkerRejected = $false
        try {
            Assert-PrepareResultMatchesTrustedDigest -PrepareText $forgedPrepareText -ExpectedRunId $prepareChannelRunId `
                -ExpectedCount $channelReportedCount -ExpectedSha256 $channelReportedSha256
        } catch { $forgedMarkerRejected = $_.Exception.Message.Contains('TRUSTED_PREPARE_METADATA_DIGEST_MISMATCH') }
        Assert-Test ($verifiedPreparedTreeSha256 -ceq $pinnedTreeSha256 -and $tamperedTreeRejected -and $forgedMarkerRejected) `
            'trusted-prepare-channel-rejects-same-count-metadata-and-marker-forgery'
        $treeMonitor = New-Object S3T03TreeMonitor($pinnedTreeRoot)
        $stableTreeStatus = $treeMonitor.Status()
        Assert-Test ($stableTreeStatus -eq 'EVENT_COUNT=0;ERROR_COUNT=0;ERROR=') 'metadata-tree-monitor-starts-clean'
        $pinnedTreeWriter = $null
        $pinnedTreeWriterRejected = $false
        try { $pinnedTreeWriter = [IO.File]::Open($pinnedTreeFile, [IO.FileMode]::Open, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite) }
        catch { $pinnedTreeWriterRejected = $true }
        finally { if ($pinnedTreeWriter) { $pinnedTreeWriter.Dispose() } }
        Assert-Test $pinnedTreeWriterRejected 'pinned-metadata-file-blocks-concurrent-writer'
        $lateMetadataPath = Join-Path $pinnedTreeRoot 'late-added.xml'
        [S3T03SafeFile]::WriteWithinRoot($lateMetadataPath, $secureRoot, $true, [Text.Encoding]::UTF8.GetBytes('late-metadata'))
        $lateTreeRecords = @(Get-SecureTreeSha256Manifest -Root $pinnedTreeRoot)
        $lateTreeManifest = Format-SecureTreeSha256Manifest -Root $pinnedTreeRoot -Records $lateTreeRecords
        Assert-Test (-not [string]::Equals($lateTreeManifest, $pinnedTreeManifest, [StringComparison]::Ordinal)) `
            'post-run-tree-recheck-detects-new-metadata-entry'
        [S3T03SafeFile]::DeleteRegularFile($lateMetadataPath)
        $treeMonitor.StopAndDrain()
        $changedTreeStatus = $treeMonitor.Status()
        $treeMonitor.Dispose()
        Assert-Test ($changedTreeStatus -match '^EVENT_COUNT=[1-9][0-9]*;ERROR_COUNT=0;ERROR=$') `
            'metadata-tree-monitor-detects-transient-create-and-delete'

        $aclTreeRoot = Join-Path $secureRoot 'acl-tree'
        $secureLeases.CreateDirectory($aclTreeRoot)
        $secureLeases.LockDirectoryChain($aclTreeRoot)
        $aclTreeNested = Join-Path $aclTreeRoot 'nested'
        $secureLeases.CreateDirectory($aclTreeNested)
        $aclTreeFile = Join-Path $aclTreeNested 'metadata.xml'
        [S3T03SafeFile]::WriteWithinRoot($aclTreeFile, $secureRoot, $true, [Text.Encoding]::UTF8.GetBytes('acl-original'))
        $aclTreeOriginalText = [Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($aclTreeFile))
        Protect-SecureMetadataTree -Root $aclTreeRoot -LeaseSet $secureLeases `
            -OriginalSnapshots ([ref]$aclTreeSnapshots) -OriginalRootDaclSddl ([ref]$aclTreeOriginalSddl)
        $aclWriteRejected = $false
        try { [IO.File]::WriteAllText($aclTreeFile, 'acl-mutated', [Text.Encoding]::UTF8) }
        catch { $aclWriteRejected = $true }
        $aclRootCreateRejected = $false
        $aclRootCreatePath = Join-Path $aclTreeRoot 'late.xml'
        try { [IO.File]::WriteAllText($aclRootCreatePath, 'late', [Text.Encoding]::UTF8) }
        catch { $aclRootCreateRejected = $true }
        $aclNestedCreateRejected = $false
        $aclNestedCreatePath = Join-Path $aclTreeNested 'late.xml'
        try { [IO.File]::WriteAllText($aclNestedCreatePath, 'late', [Text.Encoding]::UTF8) }
        catch { $aclNestedCreateRejected = $true }
        Assert-Test ($aclWriteRejected -and $aclRootCreateRejected -and $aclNestedCreateRejected -and
            -not [IO.File]::Exists($aclRootCreatePath) -and -not [IO.File]::Exists($aclNestedCreatePath)) `
            'metadata-acl-freeze-blocks-file-write-and-create-at-each-depth'
        Assert-Test ([string]::Equals([IO.File]::ReadAllText($aclTreeFile, [Text.Encoding]::UTF8), $aclTreeOriginalText, [StringComparison]::Ordinal)) `
            'metadata-acl-freeze-preserves-existing-read-access-and-content'
        Restore-SecureMetadataTree -Root $aclTreeRoot -LeaseSet $secureLeases `
            -OriginalSnapshots $aclTreeSnapshots -OriginalRootDaclSddl $aclTreeOriginalSddl
        $aclTreeSnapshots = $null
        $aclTreeOriginalSddl = $null
        $aclRestoreCreatePath = Join-Path $aclTreeRoot 'restored-write-probe.txt'
        [IO.File]::WriteAllText($aclRestoreCreatePath, 'restored', [Text.Encoding]::UTF8)
        $aclRestoreWriteSucceeded = [string]::Equals([IO.File]::ReadAllText($aclRestoreCreatePath, [Text.Encoding]::UTF8), 'restored', [StringComparison]::Ordinal)
        [IO.File]::Delete($aclRestoreCreatePath)
        Assert-Test $aclRestoreWriteSucceeded 'metadata-acl-restore-matches-snapshot-and-reenables-write'

        $openCheck = [S3T03SafeFile]::OpenLeaf($normalPath, $false)
        $openCheck.Dispose()
        Assert-Test $true 'secure-open-existing'
        $conflictRejected = $false
        try { $secureLeases.ReserveNew($normalPath) } catch { $conflictRejected = $true }
        Assert-Test $conflictRejected 'create-new-leaf-conflict-rejected'

        $reparseClosed = $false
        $fileLink = Join-Path $secureRoot 'symlink-leaf.txt'
        $fileLinkCreated = $false
        if ([S3T03SafeFile]::TryCreateSymbolicLink($fileLink, $normalPath, $false) -and (Test-Path -LiteralPath $fileLink)) {
            $fileLinkAttributes = [uint32][IO.File]::GetAttributes($fileLink)
            if (($fileLinkAttributes -band [uint32][S3T03SafeFile]::AttributeReparsePoint) -eq 0) {
                throw 'SELFTEST_FILE_SYMLINK_CREATED_ENTRY_NOT_REPARSE'
            }
            $fileLinkCreated = $true
            $reparseClosed = $true
            if ($reparseClosed) {
                try { $bad = [S3T03SafeFile]::OpenLeaf($fileLink, $false); $bad.Dispose(); $reparseClosed = $false }
                catch { $reparseClosed = $_.Exception.Message -match 'REPARSE_POINT' }
            }
            [Console]::Out.WriteLine('SECURE_IO_SYMLINK_TEST=REAL_FILE_SYMLINK')
        } else {
            try { [S3T03SafeFile]::ValidateAttributesForTest(0x400, $false) } catch { $reparseClosed = $true }
            [Console]::Out.WriteLine('SECURE_IO_SYMLINK_TEST=SYNTHETIC_ATTRIBUTE_GATE_ONLY; CREATE_RESULT_WITHOUT_ENTRY_OR_UNAVAILABLE')
        }
        Assert-Test $reparseClosed 'reparse-leaf-fails-closed'
        if ($fileLinkCreated) { [S3T03SafeFile]::DeleteKnownReparsePoint($fileLink, $false) }
        $syntheticLeafReparseRejected = $false
        try { [S3T03SafeFile]::ValidateAttributesForTest(0x400, $false) } catch { $syntheticLeafReparseRejected = $_.Exception.Message -match 'REPARSE_POINT' }
        Assert-Test $syntheticLeafReparseRejected 'reparse-attribute-gate-rejects-leaf'
        $directoryReparseClosed = $false
        $directoryLink = Join-Path $secureRoot 'directory-junction'
        $directoryLinkCreated = $false
        if ([S3T03SafeFile]::TryCreateSymbolicLink($directoryLink, $secureRoot, $true) -and (Test-Path -LiteralPath $directoryLink -PathType Container)) {
            $directoryLinkAttributes = [uint32][IO.File]::GetAttributes($directoryLink)
            if (($directoryLinkAttributes -band [uint32][S3T03SafeFile]::AttributeReparsePoint) -eq 0) {
                throw 'SELFTEST_DIRECTORY_SYMLINK_CREATED_ENTRY_NOT_REPARSE'
            }
            $directoryLinkCreated = $true
            try { $badDirectory = [S3T03SafeFile]::OpenDirectory($directoryLink); $badDirectory.Dispose() }
            catch { $directoryReparseClosed = $_.Exception.Message -match 'REPARSE_POINT' }
            [Console]::Out.WriteLine('SECURE_IO_DIRECTORY_REPARSE_TEST=REAL_DIRECTORY_SYMLINK')
        } else {
            try { [S3T03SafeFile]::ValidateAttributesForTest(0x410, $true) } catch { $directoryReparseClosed = $true }
            [Console]::Out.WriteLine('SECURE_IO_DIRECTORY_REPARSE_TEST=SYNTHETIC_ATTRIBUTE_GATE_ONLY; CREATE_RESULT_WITHOUT_ENTRY_OR_UNAVAILABLE')
        }
        Assert-Test $directoryReparseClosed 'directory-junction-attribute-gate-fails-closed'
        if ($directoryLinkCreated) { [S3T03SafeFile]::DeleteKnownReparsePoint($directoryLink, $true) }
        $syntheticDirectoryReparseRejected = $false
        try { [S3T03SafeFile]::ValidateAttributesForTest(0x410, $true) } catch { $syntheticDirectoryReparseRejected = $_.Exception.Message -match 'REPARSE_POINT' }
        Assert-Test $syntheticDirectoryReparseRejected 'reparse-attribute-gate-rejects-directory'

        $vivadoLog = Join-Path $secureRoot 'vivado.log'
        $vivadoJournal = Join-Path $secureRoot 'vivado.jou'
        $fakeResult = Join-Path $secureRoot 'fake-vivado-write-result.txt'
        $secureLeases.ReserveNew($vivadoLog)
        $secureLeases.ReserveNew($vivadoJournal)
        $secureLeases.ReserveNew($fakeResult)
        $fakeCode = '$log=' + (ConvertTo-PowerShellLiteral $vivadoLog) + ';$jou=' + (ConvertTo-PowerShellLiteral $vivadoJournal) + ';' +
            '$fs=[IO.File]::Open($log,[IO.FileMode]::Open,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);$b=[Text.Encoding]::UTF8.GetBytes(''vivado-compatible-log'');$fs.SetLength(0);$fs.Write($b,0,$b.Length);$fs.Dispose();' +
            '$fs=[IO.File]::Open($jou,[IO.FileMode]::Open,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);$b=[Text.Encoding]::UTF8.GetBytes(''vivado-compatible-journal'');$fs.SetLength(0);$fs.Write($b,0,$b.Length);$fs.Dispose();' +
            '$l=''BLOCKED'';$j=''BLOCKED'';try{[IO.File]::Move($log,$log+''.replacement'');$l=''MOVED''}catch{};try{[IO.File]::Move($jou,$jou+''.replacement'');$j=''MOVED''}catch{};' +
            '$res=[IO.File]::Open(' + (ConvertTo-PowerShellLiteral $fakeResult) + ',[IO.FileMode]::Open,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);$b=[Text.Encoding]::UTF8.GetBytes($l+'',''+$j);$res.SetLength(0);$res.Write($b,0,$b.Length);$res.Dispose()'
        $fakeEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($fakeCode))
        $fakeLine = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$fakeEncoded)
        $fakeWriter = [S3T03RunnerProcess]::Start($powershellExe, $fakeLine, $repoRoot)
        try {
            $fakeDeadline = [DateTime]::UtcNow.AddSeconds(8)
            while (-not $fakeWriter.HasExited -and [DateTime]::UtcNow -lt $fakeDeadline) { Start-Sleep -Milliseconds 50 }
            Assert-Test ($fakeWriter.HasExited -and $fakeWriter.ExitCode -eq 0) 'fake-vivado-writer-exits-cleanly'
        } finally { $fakeWriter.Dispose() }
        $replaceResults = [Text.Encoding]::UTF8.GetString($secureLeases.ReadHeld($fakeResult))
        Assert-Test ($replaceResults -eq 'BLOCKED,BLOCKED') 'fake-vivado-path-write-compatible-and-replacement-blocked'
        $logText = [Text.Encoding]::UTF8.GetString($secureLeases.ReadHeld($vivadoLog))
        $journalText = [Text.Encoding]::UTF8.GetString($secureLeases.ReadHeld($vivadoJournal))
        Assert-Test ($logText -eq 'vivado-compatible-log' -and $journalText -eq 'vivado-compatible-journal') 'held-vivado-log-journal-content-stable'

        $layoutRoot = Join-Path $testRoot 'output-layout'
        $layoutLeases = Initialize-SafeOutputLeases $layoutRoot
        try {
            $runStatusPath = Join-Path $layoutRoot 'run_status.txt'
            $prepareCode = 'Set-FakeFile (Join-Path $d ''run_status.txt'') ''S3_TCL_RESULT=FAIL:IMPLEMENTATION_ERROR''; exit 2'
            $fakePrepare = New-FakeChild $testRoot $prepareCode 'prepare-failure'
            try {
                $fakePrepareResult = Resolve-SupervisedResult $fakePrepare.Process $fakePrepare.Directory 'prepare' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromSeconds(4)) 50 $null $layoutLeases
            } finally { $fakePrepare.Process.Dispose() }
            Assert-Test ($fakePrepareResult.Result -eq 'TCL_FAILURE_MARKER' -and $fakePrepareResult.ExitCode -eq 2) 'fake-prepare-failure-observed-before-status-write'
            $layoutLeases.WriteHeld($runStatusPath, [Text.Encoding]::UTF8.GetBytes("RUN_ID=S3T03_PREP_FAIL`nSTAGE=FAILED`nS3_TCL_RESULT=FAIL:IMPLEMENTATION_ERROR`n"))
            Write-SafeOutputText (Join-Path $layoutRoot 'reports\runner_manifest.txt') 'manifest-test' $layoutLeases
            Complete-PrepareFailureStatus $layoutRoot 'S3T03_PREP_FAIL' $fakePrepareResult 'selftest-runner-sha' $layoutLeases
            $layoutManifest = [Text.Encoding]::UTF8.GetString($layoutLeases.ReadHeld((Join-Path $layoutRoot 'reports\runner_manifest.txt')))
            $layoutStatus = [Text.Encoding]::UTF8.GetString($layoutLeases.ReadHeld((Join-Path $layoutRoot 'runner_status.txt')))
            Assert-Test ($layoutManifest -eq "manifest-test`n" -and $layoutStatus.Contains('S3_RUNNER_RESULT=TCL_FAILURE_MARKER') -and $layoutStatus.Contains('PROCESS_EXIT_CODE=2')) 'prepare-failure-status-written-through-preheld-lease'

            $prepareCaptured = $null
            $prepareCatchAction = $null
            try {
                Invoke-CapturedFailureAndThrow $layoutRoot 'S3T03_PREP_FAIL' $fakePrepareResult 'selftest-runner-sha' $layoutLeases 'prepare' ([ref]$prepareCaptured) 'SELFTEST_PREPARE_FAILURE'
            } catch {
                $prepareCatchAction = Invoke-RunnerCatchStatusHandler $layoutRoot 'S3T03_PREP_FAIL' 'selftest-runner-sha' ([TimeSpan]::FromSeconds(1)) $layoutLeases $prepareCaptured
            }
            $layoutStatus = [Text.Encoding]::UTF8.GetString($layoutLeases.ReadHeld((Join-Path $layoutRoot 'runner_status.txt')))
            $prepareStatusPreserved = $layoutStatus.Contains('S3_RUNNER_RESULT=TCL_FAILURE_MARKER') -and
                $layoutStatus.Contains('STOP_REASON=PROCESS_EXITED') -and $layoutStatus.Contains('PROCESS_EXIT_CODE=2') -and
                $layoutStatus.Contains('OWNED_ROOT_PROCESS_ID=' + $fakePrepare.Process.ProcessId) -and
                -not $layoutStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                -not $layoutStatus.Contains('PROCESS_EXIT_CODE=NOT_STARTED_OR_ABORTED') -and
                -not $layoutStatus.Contains('OWNED_ROOT_PROCESS_ID=0')
            Assert-Test ($prepareCatchAction -eq 'CAPTURED_FAILURE_PRESERVED' -and $prepareCaptured.Written -and
                $prepareCaptured.Source -eq 'prepare' -and $prepareStatusPreserved) 'prepare-failure-write-mark-throw-common-catch-preserves-final-status'

            $runCatchRoot = Join-Path $testRoot 'run-catch-output'
            $runCatchLeases = Initialize-SafeOutputLeases $runCatchRoot
            try {
                $runFailureCode = 'Set-FakeFile (Join-Path $d ''run_status.txt'') ''S3_TCL_RESULT=PASS:ROUTE_COMPLETE''; exit 7'
                $fakeRunFailure = New-FakeChild $testRoot $runFailureCode 'run-failure-catch'
                try {
                    $runFailureResult = Resolve-SupervisedResult $fakeRunFailure.Process $fakeRunFailure.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromSeconds(4)) 50 $null $runCatchLeases
                } finally { $fakeRunFailure.Process.Dispose() }
                $runCaptured = $null
                $runCatchAction = $null
                try {
                    Invoke-CapturedFailureAndThrow $runCatchRoot 'S3T03_RUN_FAIL' $runFailureResult 'selftest-runner-sha' $runCatchLeases 'run' ([ref]$runCaptured) 'SELFTEST_RUN_FAILURE'
                } catch {
                    $runCatchAction = Invoke-RunnerCatchStatusHandler $runCatchRoot 'S3T03_RUN_FAIL' 'selftest-runner-sha' ([TimeSpan]::FromSeconds(1)) $runCatchLeases $runCaptured
                }
                $runFailureStatus = [Text.Encoding]::UTF8.GetString($runCatchLeases.ReadHeld((Join-Path $runCatchRoot 'runner_status.txt')))
                $runStatusPreserved = $runFailureResult.Result -eq 'NONZERO_PROCESS_EXIT' -and
                    $runFailureStatus.Contains('S3_RUNNER_RESULT=NONZERO_PROCESS_EXIT') -and
                    $runFailureStatus.Contains('STOP_REASON=PROCESS_EXITED') -and $runFailureStatus.Contains('PROCESS_EXIT_CODE=7') -and
                    $runFailureStatus.Contains('OWNED_ROOT_PROCESS_ID=' + $fakeRunFailure.Process.ProcessId) -and
                    -not $runFailureStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                    -not $runFailureStatus.Contains('PROCESS_EXIT_CODE=NOT_STARTED_OR_ABORTED') -and
                    -not $runFailureStatus.Contains('OWNED_ROOT_PROCESS_ID=0')
                Assert-Test ($runCatchAction -eq 'CAPTURED_FAILURE_PRESERVED' -and $runCaptured.Written -and
                    $runCaptured.Source -eq 'run' -and $runStatusPreserved) 'run-failure-write-mark-throw-common-catch-preserves-final-status'

                $deadlineRoot = Join-Path $testRoot 'deadline-catch-output'
                $deadlineLeases = Initialize-SafeOutputLeases $deadlineRoot
                try {
                    $deadlineCode = 'Set-FakeFile (Join-Path $d ''run_status.txt'') ''S3_TCL_RESULT=PASS:PREPARED''; exit 0'
                    $fakeDeadlinePrepare = New-FakeChild $testRoot $deadlineCode 'deadline-prepare-success'
                    try {
                        $deadlinePrepareResult = Resolve-SupervisedResult $fakeDeadlinePrepare.Process $fakeDeadlinePrepare.Directory 'prepare' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromSeconds(4)) 50 $null $deadlineLeases
                    } finally { $fakeDeadlinePrepare.Process.Dispose() }
                    Assert-Test ($deadlinePrepareResult.Result -eq 'SUCCESS' -and $deadlinePrepareResult.ExitCode -eq 0) 'deadline-prepare-baseline-success'
                    $deadlineMaxRuntime = [TimeSpan]::FromMinutes(60)
                    $preDeadlineStart = [DateTime]::UtcNow
                    $preDeadlineNow = $preDeadlineStart.AddMinutes(59).AddSeconds(59)
                    $preDeadlineClockState = [pscustomobject]@{ Count=0 }
                    $preDeadlineClock = { $preDeadlineClockState.Count++; $preDeadlineNow }.GetNewClosure()
                    $preDeadlineActionState = [pscustomobject]@{ Count=0 }
                    $preDeadlineAction = { $preDeadlineActionState.Count++; 'ROUTE_START_ACTION_INVOKED' }.GetNewClosure()
                    $preDeadlineCaptured = $null
                    $preDeadlineActionResult = Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                        -StartedAt $preDeadlineStart -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                        -RunId 'S3T03_PRE_DEADLINE' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                        -CapturedFailureStatus ([ref]$preDeadlineCaptured) -FailureMessage 'SELFTEST_PRE_DEADLINE' `
                        -RouteStartAction $preDeadlineAction -Clock $preDeadlineClock
                    Assert-Test ($preDeadlineActionResult -eq 'ROUTE_START_ACTION_INVOKED' -and
                        $preDeadlineActionState.Count -eq 1 -and $preDeadlineClockState.Count -eq 2 -and
                        $null -eq $preDeadlineCaptured) 'route-start-gate-before-deadline-samples-twice-and-invokes-action-once'

                    $routeScopeState = [pscustomobject]@{ Count=0; Deadline=[DateTime]::MinValue }
                    $routeScopeProcessQuery = { @() }
                    $routeScopeAction = {
                        param([DateTime]$RouteDeadlineUtc)
                        Invoke-GuardedVivadoStart -ProcessStartAction {
                            $routeScopeState.Count++
                            $routeScopeState.Deadline = $RouteDeadlineUtc
                            'ROUTE_DEADLINE_SCOPE_REACHED'
                        } -ProcessQuery $routeScopeProcessQuery
                    }
                    $routeScopeNow = $preDeadlineStart.AddMinutes(1)
                    $routeScopeClockState = [pscustomobject]@{ Count=0 }
                    $routeScopeClock = { $routeScopeClockState.Count++; $routeScopeNow }.GetNewClosure()
                    $routeScopeCaptured = $null
                    $routeScopeResult = Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                        -StartedAt $preDeadlineStart -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                        -RunId 'S3T03_ROUTE_DEADLINE_SCOPE' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                        -CapturedFailureStatus ([ref]$routeScopeCaptured) -FailureMessage 'SELFTEST_ROUTE_DEADLINE_SCOPE' `
                        -RouteStartAction $routeScopeAction -Clock $routeScopeClock
                    Assert-Test ($routeScopeResult -eq 'ROUTE_DEADLINE_SCOPE_REACHED' -and $routeScopeState.Count -eq 1 -and
                        $routeScopeState.Deadline -eq $preDeadlineStart.Add($deadlineMaxRuntime) -and
                        $routeScopeClockState.Count -eq 2 -and $null -eq $routeScopeCaptured) `
                        'guarded-route-start-inherits-deadline-without-closure-copy'

                    $deadlineStartAt = [DateTime]::UtcNow
                    $deadlineBoundary = $deadlineStartAt.Add($deadlineMaxRuntime)
                    $deadlineClockState = [pscustomobject]@{ Count=0 }
                    $deadlineClock = { $deadlineClockState.Count++; $deadlineBoundary }.GetNewClosure()
                    $deadlineActionState = [pscustomobject]@{ Count=0 }
                    $deadlineRouteStartAction = { $deadlineActionState.Count++; 'ROUTE_START_ACTION_MUST_NOT_RUN' }.GetNewClosure()
                    $deadlineCaptured = $null
                    $deadlineCatchAction = $null
                    $deadlineThrownMessage = $null
                    try {
                        $deadlineActionResult = Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                            -StartedAt $deadlineStartAt -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                            -RunId 'S3T03_DEADLINE' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                            -CapturedFailureStatus ([ref]$deadlineCaptured) -FailureMessage 'SELFTEST_60_MINUTE_DEADLINE' `
                            -RouteStartAction $deadlineRouteStartAction -Clock $deadlineClock
                    } catch {
                        $deadlineThrownMessage = $_.Exception.Message
                        $deadlineCatchAction = Invoke-RunnerCatchStatusHandler $deadlineRoot 'S3T03_DEADLINE' 'selftest-runner-sha' $deadlineMaxRuntime $deadlineLeases $deadlineCaptured
                    }
                    $deadlineStatus = [Text.Encoding]::UTF8.GetString($deadlineLeases.ReadHeld((Join-Path $deadlineRoot 'runner_status.txt')))
                    $deadlineStatusPreserved = $deadlineStatus.Contains('S3_RUNNER_RESULT=HARD_TIMEOUT_60_MIN') -and
                        $deadlineStatus.Contains('STOP_REASON=HARD_TIMEOUT_60_MIN') -and $deadlineStatus.Contains('PROCESS_EXIT_CODE=0') -and
                        $deadlineStatus.Contains('OWNED_ROOT_PROCESS_ID=' + $fakeDeadlinePrepare.Process.ProcessId) -and
                        -not $deadlineStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                        -not $deadlineStatus.Contains('PROCESS_EXIT_CODE=NOT_STARTED_OR_ABORTED') -and
                        -not $deadlineStatus.Contains('OWNED_ROOT_PROCESS_ID=0')
                    Assert-Test ($deadlineThrownMessage -eq 'SELFTEST_60_MINUTE_DEADLINE' -and $deadlineActionState.Count -eq 0 -and
                        $deadlineClockState.Count -eq 1 -and
                        $deadlineCatchAction -eq 'CAPTURED_FAILURE_PRESERVED' -and $deadlineCaptured.Written -and
                        $deadlineCaptured.Source -eq 'prepare-deadline' -and
                        $deadlineCaptured.Result.Result -eq 'HARD_TIMEOUT_60_MIN' -and
                        $deadlineCaptured.Result.StopReason -eq 'HARD_TIMEOUT_60_MIN' -and
                        $deadlineCaptured.Result.ExitCode -eq $deadlinePrepareResult.ExitCode -and
                        $deadlineCaptured.Result.ProcessId -eq $deadlinePrepareResult.ProcessId -and
                        $deadlineStatusPreserved) 'route-start-gate-at-60-minute-boundary-stops-on-first-sample-and-never-starts-route'

                    $sequencedStartAt = [DateTime]::UtcNow
                    $sequencedBoundary = $sequencedStartAt.Add($deadlineMaxRuntime)
                    $sequencedClockState = [pscustomobject]@{
                        Count=0; First=$sequencedBoundary.AddTicks(-1); Final=$sequencedBoundary
                    }
                    $sequencedClock = {
                        $sequencedClockState.Count++
                        if ($sequencedClockState.Count -eq 1) { $sequencedClockState.First }
                        else { $sequencedClockState.Final }
                    }.GetNewClosure()
                    $sequencedActionState = [pscustomobject]@{ Count=0 }
                    $sequencedRouteStartAction = { $sequencedActionState.Count++; 'SEQUENCED_ROUTE_START_MUST_NOT_RUN' }.GetNewClosure()
                    $sequencedCaptured = $null
                    $sequencedCatchAction = $null
                    $sequencedThrownMessage = $null
                    try {
                        $sequencedActionResult = Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                            -StartedAt $sequencedStartAt -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                            -RunId 'S3T03_FINAL_CHECK_DEADLINE' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                            -CapturedFailureStatus ([ref]$sequencedCaptured) -FailureMessage 'SELFTEST_FINAL_CHECK_DEADLINE' `
                            -RouteStartAction $sequencedRouteStartAction -Clock $sequencedClock
                    } catch {
                        $sequencedThrownMessage = $_.Exception.Message
                        $sequencedCatchAction = Invoke-RunnerCatchStatusHandler $deadlineRoot 'S3T03_FINAL_CHECK_DEADLINE' 'selftest-runner-sha' $deadlineMaxRuntime $deadlineLeases $sequencedCaptured
                    }
                    $sequencedStatus = [Text.Encoding]::UTF8.GetString($deadlineLeases.ReadHeld((Join-Path $deadlineRoot 'runner_status.txt')))
                    $sequencedStatusPreserved = $sequencedStatus.Contains('S3_RUNNER_RESULT=HARD_TIMEOUT_60_MIN') -and
                        $sequencedStatus.Contains('STOP_REASON=HARD_TIMEOUT_60_MIN') -and $sequencedStatus.Contains('PROCESS_EXIT_CODE=0') -and
                        $sequencedStatus.Contains('OWNED_ROOT_PROCESS_ID=' + $deadlinePrepareResult.ProcessId) -and
                        -not $sequencedStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                        -not $sequencedStatus.Contains('PROCESS_EXIT_CODE=NOT_STARTED_OR_ABORTED') -and
                        -not $sequencedStatus.Contains('OWNED_ROOT_PROCESS_ID=0')
                    Assert-Test ($sequencedThrownMessage -eq 'SELFTEST_FINAL_CHECK_DEADLINE' -and
                        $sequencedClockState.Count -eq 2 -and $sequencedActionState.Count -eq 0 -and
                        $sequencedCatchAction -eq 'CAPTURED_FAILURE_PRESERVED' -and $sequencedCaptured.Written -and
                        $sequencedCaptured.Source -eq 'prepare-deadline' -and
                        $sequencedCaptured.Result.Result -eq 'HARD_TIMEOUT_60_MIN' -and
                        $sequencedCaptured.Result.StopReason -eq 'HARD_TIMEOUT_60_MIN' -and
                        $sequencedCaptured.Result.ExitCode -eq $deadlinePrepareResult.ExitCode -and
                        $sequencedCaptured.Result.ProcessId -eq $deadlinePrepareResult.ProcessId -and
                        $sequencedStatusPreserved) 'route-start-gate-final-sample-at-deadline-preserves-timeout-and-never-starts-route'

                    $clockErrorState = [pscustomobject]@{ Count=0 }
                    $clockErrorClock = {
                        $clockErrorState.Count++
                        if ($clockErrorState.Count -eq 1) { $sequencedBoundary.AddMinutes(-1) }
                        else { throw 'SELFTEST_FINAL_CLOCK_SAMPLE_FAILURE' }
                    }.GetNewClosure()
                    $clockErrorActionState = [pscustomobject]@{ Count=0 }
                    $clockErrorRouteStartAction = { $clockErrorActionState.Count++; 'CLOCK_ERROR_ROUTE_START_MUST_NOT_RUN' }.GetNewClosure()
                    $clockErrorCaptured = $null
                    $clockErrorCatchAction = $null
                    $clockErrorThrownMessage = $null
                    try {
                        $clockErrorActionResult = Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                            -StartedAt $sequencedStartAt -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                            -RunId 'S3T03_FINAL_CLOCK_ERROR' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                            -CapturedFailureStatus ([ref]$clockErrorCaptured) -FailureMessage 'SELFTEST_FINAL_CLOCK_ERROR' `
                            -RouteStartAction $clockErrorRouteStartAction -Clock $clockErrorClock
                    } catch {
                        $clockErrorThrownMessage = $_.Exception.Message
                        $clockErrorCatchAction = Invoke-RunnerCatchStatusHandler $deadlineRoot 'S3T03_FINAL_CLOCK_ERROR' 'selftest-runner-sha' $deadlineMaxRuntime $deadlineLeases $clockErrorCaptured
                    }
                    $clockErrorStatus = [Text.Encoding]::UTF8.GetString($deadlineLeases.ReadHeld((Join-Path $deadlineRoot 'runner_status.txt')))
                    Assert-Test ($clockErrorThrownMessage -eq 'SELFTEST_FINAL_CLOCK_SAMPLE_FAILURE' -and
                        $clockErrorState.Count -eq 2 -and $clockErrorActionState.Count -eq 0 -and
                        $null -eq $clockErrorCaptured -and $clockErrorCatchAction -eq 'RUNNER_EXCEPTION_WRITTEN' -and
                        $clockErrorStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                        $clockErrorStatus.Contains('STOP_REASON=RUNNER_EXCEPTION')) 'route-start-gate-final-clock-error-fails-closed-before-action'

                    $nativeStartAt = [DateTime]::UtcNow
                    $nativeDeadline = $nativeStartAt.Add($deadlineMaxRuntime)
                    $nativeGateNow = $nativeStartAt.AddMinutes(59).AddSeconds(59)
                    $nativeGateClock = { $nativeGateNow }.GetNewClosure()
                    $nativeRouteCodePath = Join-Path $testRoot 'route-command-executed.txt'
                    $nativeRouteCode = '[IO.File]::WriteAllText(' + (ConvertTo-PowerShellLiteral $nativeRouteCodePath) + ', ''ROUTE_COMMAND_EXECUTED'')'
                    $nativeRouteEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($nativeRouteCode))
                    $nativeRouteCommand = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand',$nativeRouteEncoded)

                    $beforeCreateState = [pscustomobject]@{ Count=0; Deadline=$nativeDeadline }
                    $beforeCreateClockScript = {
                        $beforeCreateState.Count++
                        return $beforeCreateState.Deadline
                    }.GetNewClosure()
                    $beforeCreateClock = [Func[DateTime]]$beforeCreateClockScript
                    $beforeCreateActionState = [pscustomobject]@{ Count=0 }
                    $beforeCreateAction = {
                        param([DateTime]$RouteDeadlineUtc)
                        $beforeCreateActionState.Count++
                        [S3T03RunnerProcess]::Start($powershellExe,$nativeRouteCommand,$repoRoot,$RouteDeadlineUtc,$beforeCreateClock)
                    }.GetNewClosure()
                    $beforeCreateCaptured = $null
                    $beforeCreateCatchAction = $null
                    $beforeCreateThrownMessage = $null
                    try {
                        [void](Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                            -StartedAt $nativeStartAt -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                            -RunId 'S3T03_NATIVE_BEFORE_CREATE' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                            -CapturedFailureStatus ([ref]$beforeCreateCaptured) -FailureMessage 'SELFTEST_NATIVE_BEFORE_CREATE_TIMEOUT' `
                            -RouteStartAction $beforeCreateAction -Clock $nativeGateClock)
                    } catch {
                        $beforeCreateThrownMessage = $_.Exception.Message
                        $beforeCreateCatchAction = Invoke-RunnerCatchStatusHandler $deadlineRoot 'S3T03_NATIVE_BEFORE_CREATE' `
                            'selftest-runner-sha' $deadlineMaxRuntime $deadlineLeases $beforeCreateCaptured
                    }
                    $beforeCreateStatus = [Text.Encoding]::UTF8.GetString($deadlineLeases.ReadHeld((Join-Path $deadlineRoot 'runner_status.txt')))
                    Assert-Test ($beforeCreateThrownMessage -eq 'SELFTEST_NATIVE_BEFORE_CREATE_TIMEOUT' -and
                        $beforeCreateState.Count -eq 1 -and $beforeCreateActionState.Count -eq 1 -and
                        $beforeCreateCatchAction -eq 'CAPTURED_FAILURE_PRESERVED' -and $beforeCreateCaptured.Written -and
                        $beforeCreateCaptured.Result.Result -eq 'HARD_TIMEOUT_60_MIN' -and
                        $beforeCreateCaptured.Result.RouteStartAbortProcessId -eq 0 -and
                        $beforeCreateCaptured.Result.RouteStartAbortPhase -eq 'BEFORE_CREATE_PROCESS' -and
                        $beforeCreateStatus.Contains('S3_RUNNER_RESULT=HARD_TIMEOUT_60_MIN') -and
                        $beforeCreateStatus.Contains('ROUTE_START_ABORT_PROCESS_ID=0') -and
                        $beforeCreateStatus.Contains('ROUTE_START_ABORT_EXIT_CODE=-1') -and
                        $beforeCreateStatus.Contains('ROUTE_START_ABORT_PHASE=BEFORE_CREATE_PROCESS') -and
                        $beforeCreateStatus.Contains('TCL_RESULT_MARKER=MISSING') -and
                        $beforeCreateStatus.Contains('PREPARE_RESULT_MARKER=S3_TCL_RESULT=PASS:PREPARED') -and
                        -not (Test-Path -LiteralPath $nativeRouteCodePath -PathType Leaf)) `
                        'native-start-deadline-before-create-records-timeout-without-running-route-command'

                    $beforeResumeState = [pscustomobject]@{ Count=0; BeforeCreate=$nativeDeadline.AddTicks(-1); AtResume=$nativeDeadline }
                    $beforeResumeClockScript = {
                        $beforeResumeState.Count++
                        if ($beforeResumeState.Count -eq 1) { return $beforeResumeState.BeforeCreate }
                        return $beforeResumeState.AtResume
                    }.GetNewClosure()
                    $beforeResumeClock = [Func[DateTime]]$beforeResumeClockScript
                    $beforeResumeActionState = [pscustomobject]@{ Count=0 }
                    $beforeResumeAction = {
                        param([DateTime]$RouteDeadlineUtc)
                        $beforeResumeActionState.Count++
                        [S3T03RunnerProcess]::Start($powershellExe,$nativeRouteCommand,$testRoot,$RouteDeadlineUtc,$beforeResumeClock)
                    }.GetNewClosure()
                    $beforeResumeCaptured = $null
                    $beforeResumeCatchAction = $null
                    $beforeResumeThrownMessage = $null
                    try {
                        [void](Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult `
                            -StartedAt $nativeStartAt -MaxRuntime $deadlineMaxRuntime -Directory $deadlineRoot `
                            -RunId 'S3T03_NATIVE_BEFORE_RESUME' -RunnerSha 'selftest-runner-sha' -Leases $deadlineLeases `
                            -CapturedFailureStatus ([ref]$beforeResumeCaptured) -FailureMessage 'SELFTEST_NATIVE_BEFORE_RESUME_TIMEOUT' `
                            -RouteStartAction $beforeResumeAction -Clock $nativeGateClock)
                    } catch {
                        $beforeResumeThrownMessage = $_.Exception.Message
                        $beforeResumeCatchAction = Invoke-RunnerCatchStatusHandler $deadlineRoot 'S3T03_NATIVE_BEFORE_RESUME' `
                            'selftest-runner-sha' $deadlineMaxRuntime $deadlineLeases $beforeResumeCaptured
                    }
                    $beforeResumeStatus = [Text.Encoding]::UTF8.GetString($deadlineLeases.ReadHeld((Join-Path $deadlineRoot 'runner_status.txt')))
                    Assert-Test ($beforeResumeThrownMessage -eq 'SELFTEST_NATIVE_BEFORE_RESUME_TIMEOUT' -and
                        $beforeResumeState.Count -eq 2 -and $beforeResumeActionState.Count -eq 1 -and
                        $beforeResumeCatchAction -eq 'CAPTURED_FAILURE_PRESERVED' -and $beforeResumeCaptured.Written -and
                        $beforeResumeCaptured.Result.Result -eq 'HARD_TIMEOUT_60_MIN' -and
                        $beforeResumeCaptured.Result.RouteStartAbortProcessId -gt 0 -and
                        $beforeResumeCaptured.Result.RouteStartAbortExitCode -eq 124 -and
                        $beforeResumeCaptured.Result.RouteStartAbortPhase -eq 'BEFORE_RESUME_THREAD' -and
                        $beforeResumeStatus.Contains('S3_RUNNER_RESULT=HARD_TIMEOUT_60_MIN') -and
                        $beforeResumeStatus.Contains('ROUTE_START_ABORT_EXIT_CODE=124') -and
                        $beforeResumeStatus.Contains('ROUTE_START_ABORT_PHASE=BEFORE_RESUME_THREAD') -and
                        $beforeResumeStatus.Contains('TCL_RESULT_MARKER=MISSING') -and
                        -not (Test-Path -LiteralPath $nativeRouteCodePath -PathType Leaf)) `
                        'native-start-deadline-before-resume-terminates-suspended-child-without-running-route-command'
                } finally { $deadlineLeases.Dispose() }

                $unexpectedCaptured = $null
                $unexpectedAction = $null
                try { throw 'SELFTEST_UNEXPECTED_RUNNER_EXCEPTION' } catch {
                    $unexpectedAction = Invoke-RunnerCatchStatusHandler $runCatchRoot 'S3T03_RUN_FAIL' 'selftest-runner-sha' ([TimeSpan]::FromSeconds(1)) $runCatchLeases $unexpectedCaptured
                }
                $unexpectedStatus = [Text.Encoding]::UTF8.GetString($runCatchLeases.ReadHeld((Join-Path $runCatchRoot 'runner_status.txt')))
                Assert-Test ($unexpectedAction -eq 'RUNNER_EXCEPTION_WRITTEN' -and $unexpectedStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                    $unexpectedStatus.Contains('STOP_REASON=RUNNER_EXCEPTION') -and $unexpectedStatus.Contains('PROCESS_EXIT_CODE=NOT_STARTED_OR_ABORTED') -and
                    $unexpectedStatus.Contains('OWNED_ROOT_PROCESS_ID=0')) 'unexpected-exception-common-catch-writes-final-runner-exception-status'

                $writeFailureCaptured = $null
                $writeFailureAction = $null
                $writeFailureMessage = $null
                $injectedStatusWriter = { param($Directory,$RunId,$Result,$RunnerSha,$Leases) throw 'INJECTED_RUNNER_STATUS_WRITE_FAILURE' }
                try {
                    Invoke-CapturedFailureAndThrow $runCatchRoot 'S3T03_WRITE_FAILURE' $runFailureResult 'selftest-runner-sha' $runCatchLeases 'run' ([ref]$writeFailureCaptured) 'SELFTEST_STATUS_WRITE_FAILURE' $injectedStatusWriter
                } catch {
                    $writeFailureMessage = $_.Exception.Message
                    $writeFailureAction = Invoke-RunnerCatchStatusHandler $runCatchRoot 'S3T03_WRITE_FAILURE' 'selftest-runner-sha' ([TimeSpan]::FromSeconds(1)) $runCatchLeases $writeFailureCaptured
                }
                $writeFailureStatus = [Text.Encoding]::UTF8.GetString($runCatchLeases.ReadHeld((Join-Path $runCatchRoot 'runner_status.txt')))
                Assert-Test ($null -eq $writeFailureCaptured -and $writeFailureMessage -eq 'INJECTED_RUNNER_STATUS_WRITE_FAILURE' -and
                    $writeFailureAction -eq 'RUNNER_EXCEPTION_WRITTEN' -and $writeFailureStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
                    $writeFailureStatus.Contains('STOP_REASON=RUNNER_EXCEPTION') -and
                    $writeFailureStatus.Contains('PROCESS_EXIT_CODE=NOT_STARTED_OR_ABORTED') -and
                    $writeFailureStatus.Contains('OWNED_ROOT_PROCESS_ID=0')) 'status-write-failure-keeps-capture-null-and-common-catch-writes-exception-status'
            } finally { $runCatchLeases.Dispose() }

            $hardlinkRoot = Join-Path $testRoot 'hardlink-output'
            $hardlinkLeases = Initialize-SafeOutputLeases $hardlinkRoot
            $hardlinkFake = $null
            $hardlinkAlias = Join-Path $hardlinkRoot 'reports\final-summary-alias.txt'
            $hardlinkTarget = Join-Path $hardlinkRoot 'reports\final_summary.txt'
            try {
                $hardlinkLeases.WriteHeld($hardlinkTarget, [Text.Encoding]::UTF8.GetBytes('original-summary'))
                $hardlinkCode = @'
Set-FakeFile (Join-Path $d 'run_status.txt') 'STAGE=ROUTE_DESIGN'
Start-Sleep -Seconds 30
'@
                $hardlinkFake = New-FakeChild $testRoot $hardlinkCode 'hardlink-supervisor'
                $readyDeadline = [DateTime]::UtcNow.AddSeconds(5)
                while ($hardlinkFake.Process.HasExited -and [DateTime]::UtcNow -lt $readyDeadline) { Start-Sleep -Milliseconds 25 }
                Assert-Test (-not $hardlinkFake.Process.HasExited) 'hardlink-supervisor-fake-child-running'
                [S3T03SafeFile]::CreateHardLink($hardlinkAlias, $hardlinkTarget)
                $beforeWriteDiagnostic = $hardlinkLeases.AuditFileLinkCounts()
                $aliasStream = [IO.File]::Open($hardlinkAlias, [IO.FileMode]::Open, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
                try {
                    $aliasBytes = [Text.UTF8Encoding]::new($false).GetBytes('alias-rewrote-original')
                    $aliasStream.SetLength(0)
                    $aliasStream.Write($aliasBytes, 0, $aliasBytes.Length)
                } finally { $aliasStream.Dispose() }
                $rewrittenOriginal = [Text.Encoding]::UTF8.GetString($hardlinkLeases.ReadHeld($hardlinkTarget))
                Assert-Test ($beforeWriteDiagnostic -like 'OUTPUT_HARDLINK_DETECTED;*LINK_COUNT=2*' -and $rewrittenOriginal -eq 'alias-rewrote-original') 'hardlink-alias-write-changes-leased-original'

                try {
                    $hardlinkResult = Resolve-SupervisedResult $hardlinkFake.Process $hardlinkFake.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromSeconds(5)) 25 $null $hardlinkLeases
                } finally { $hardlinkFake.Process.Dispose() }
                Write-RunnerStatus $hardlinkRoot 'S3T03_HARDLINK' $hardlinkResult 'selftest-runner-sha' $hardlinkLeases
                $hardlinkStatus = [Text.Encoding]::UTF8.GetString($hardlinkLeases.ReadHeld((Join-Path $hardlinkRoot 'runner_status.txt')))
                Assert-Test ($hardlinkResult.Result -eq 'OUTPUT_HARDLINK_DETECTED' -and $hardlinkResult.StopReason -eq 'OUTPUT_HARDLINK_DETECTED' -and
                    $hardlinkResult.TreeExitConfirmed -and $hardlinkStatus.Contains('OUTPUT_LINK_CHECK=FAIL') -and
                    $hardlinkStatus.Contains('OUTPUT_HARDLINK_DETECTED;') -and $hardlinkStatus.Contains('PROCESS_TREE_EXIT_CONFIRMED=True')) 'hardlink-detection-terminates-tree-and-fails-closed'

                $hardlinkLeases.Dispose()
                $hardlinkLeases = $null
                [IO.File]::Delete($hardlinkAlias)
                $postCleanupHandle = [S3T03SafeFile]::OpenReadLeaf($hardlinkTarget)
                try { $postCleanupLinks = [S3T03SafeFile]::GetLinkCount($postCleanupHandle) }
                finally { $postCleanupHandle.Dispose() }
                Assert-Test ($postCleanupLinks -eq 1) 'hardlink-cleanup-restores-single-link-count'
            } finally {
                if ($hardlinkFake) { $hardlinkFake.Process.Dispose() }
                if ($hardlinkLeases) { $hardlinkLeases.Dispose() }
                if (Test-Path -LiteralPath $hardlinkAlias -PathType Leaf) { [IO.File]::Delete($hardlinkAlias) }
            }

            $missingLeaseRejected = $false
            try { Complete-PrepareFailureStatus $layoutRoot 'S3T03_PREP_FAIL' $fakePrepareResult 'selftest-runner-sha' $null } catch { $missingLeaseRejected = $_.Exception.Message -match 'REQUIRES_HELD_OUTPUT_LEASES' }
            Assert-Test $missingLeaseRejected 'prepare-failure-status-without-lease-fails-closed'
            $requiredLeaves = @('run_status.txt','prepare.result','runner_status.txt','vivado.log','vivado.jou','failure_details.txt','failure.result',
                'reports\runner_manifest.txt','reports\input_sha256.txt','reports\hdmi_xdc_audit.txt','reports\metadata_copy_sha256.txt',
                'reports\clock_constraint_change.txt','reports\synth_utilization.rpt','reports\synth_clocks.rpt','reports\synth_timing_summary.rpt',
                'reports\placed_utilization.rpt','reports\placed_timing_summary.rpt','reports\routed_timing_summary.rpt','reports\routed_clocks.rpt',
                'reports\routed_clock_interaction.rpt','reports\routed_check_timing.rpt','reports\routed_drc.rpt','reports\final_summary.txt',
            'reports\generated_clock_xdc.lease_request','reports\generated_clock_xdc.lease_ack','reports\generated_clock_xdc.lease_error',
                'checkpoints\synth.dcp','checkpoints\opt.dcp','checkpoints\placed.dcp','checkpoints\routed.dcp',
                'sentinels\preflight.complete','sentinels\synth.complete','sentinels\opt.complete','sentinels\place.complete',
                'sentinels\route.complete','sentinels\final_reports.complete','sentinels\failed.sentinel','inputs\hdmi_out.xdc')
            foreach ($relative in $requiredLeaves) { [void]$layoutLeases.ReadHeld((Join-Path $layoutRoot $relative)) }
            Assert-Test $true 'prepare-start-holds-all-known-output-leaves'

            $brokerXdc = Get-ExpectedGeneratedClockXdcPath $layoutRoot
            [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($brokerXdc))
            $brokerXdcBytes = [Text.Encoding]::UTF8.GetBytes('# broker-fake-generated-clock-xdc')
            [S3T03SafeFile]::WriteWithinRoot($brokerXdc, $layoutRoot, $true, $brokerXdcBytes)
            $brokerSha = Get-Sha256Hex $brokerXdcBytes
            $brokerPathB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($brokerXdc))
            $requestPath = Join-Path $layoutRoot 'reports\generated_clock_xdc.lease_request'
            $ackPath = Join-Path $layoutRoot 'reports\generated_clock_xdc.lease_ack'
            $errorPath = Join-Path $layoutRoot 'reports\generated_clock_xdc.lease_error'
            $brokerFakeCode = @'
$root=@ROOT@;$xdc=@XDC@;$request=@REQUEST@;$ack=@ACK@;$errorPath=@ERROR@
Set-FakeFile (Join-Path $root 'run_status.txt') "STAGE=GENERATED_CLOCK_XDC_LEASE_BARRIER`nRESULT=RUNNING"
$hash=[BitConverter]::ToString(([Security.Cryptography.SHA256]::Create()).ComputeHash([IO.File]::ReadAllBytes($xdc))).Replace('-','')
$pathB64=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($xdc))
Set-FakeFile $request "S3_GENERATED_CLOCK_LEASE=1`nPATH_B64=$pathB64`nSHA256=$hash`n"
$until=[DateTime]::UtcNow.AddSeconds(8)
while([DateTime]::UtcNow -lt $until){
  $e=Read-FakeFile $errorPath;if($e.Contains('S3_GENERATED_CLOCK_LEASE=FAIL')){exit 9}
  $a=Read-FakeFile $ack;if($a.Contains('S3_GENERATED_CLOCK_LEASE=READY')){
    $reader=[IO.File]::Open($xdc,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::ReadWrite);$reader.Dispose()
    $writeBlocked=$false;try{$w=[IO.File]::Open($xdc,[IO.FileMode]::Open,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);$w.Dispose()}catch{$writeBlocked=$true}
    $moveBlocked=$false;try{[IO.File]::Move($xdc,$xdc+'.replace')}catch{$moveBlocked=$true}
    Set-FakeFile (Join-Path $root 'run_status.txt') "S3_TCL_RESULT=PASS:ROUTE_COMPLETE`nWRITE_BLOCKED=$writeBlocked`nREPLACE_BLOCKED=$moveBlocked"
    if($writeBlocked -and $moveBlocked){exit 0}else{exit 10}
  }
  Start-Sleep -Milliseconds 25
}
exit 8
'@
            $brokerFakeCode = $brokerFakeCode.Replace('@ROOT@',(ConvertTo-PowerShellLiteral $layoutRoot)).Replace('@XDC@',(ConvertTo-PowerShellLiteral $brokerXdc)).Replace('@REQUEST@',(ConvertTo-PowerShellLiteral $requestPath)).Replace('@ACK@',(ConvertTo-PowerShellLiteral $ackPath)).Replace('@ERROR@',(ConvertTo-PowerShellLiteral $errorPath))
            $brokerFake = New-FakeChild $testRoot $brokerFakeCode 'xdc-broker-handoff'
            $brokerState = New-GeneratedClockXdcBrokerState 4
            try { $brokerResult = Resolve-SupervisedResult $brokerFake.Process $layoutRoot 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromSeconds(5)) 25 $brokerState $layoutLeases }
            finally { $brokerFake.Process.Dispose() }
            $brokerStatus = [Text.Encoding]::UTF8.GetString($layoutLeases.ReadHeld((Join-Path $layoutRoot 'run_status.txt')))
            if (-not ($brokerResult.Result -eq 'SUCCESS' -and $brokerState.Completed -and $brokerStatus.Contains('WRITE_BLOCKED=True') -and $brokerStatus.Contains('REPLACE_BLOCKED=True'))) {
                $fakeErrorPath = Join-Path $brokerFake.Directory 'fake_error.txt'
                $fakeErrorText = if (Test-Path -LiteralPath $fakeErrorPath -PathType Leaf) { [IO.File]::ReadAllText($fakeErrorPath) } else { 'NONE' }
                [Console]::Error.WriteLine('XDC_BROKER_SELFTEST_DIAGNOSTIC=RESULT:' + $brokerResult.Result + ';STOP:' + $brokerResult.StopReason + ';EXIT:' + $brokerResult.ExitCode + ';ERROR:' + $brokerState.Error + ';BROKER_FAILURE:' + $brokerResult.BrokerError + ';FAKE_ERROR:' + $fakeErrorText + ';STATUS:' + $brokerStatus.Replace("`n",'|'))
            }
            Assert-Test ($brokerResult.Result -eq 'SUCCESS' -and $brokerState.Completed -and $brokerStatus.Contains('WRITE_BLOCKED=True') -and $brokerStatus.Contains('REPLACE_BLOCKED=True')) 'xdc-broker-wait-ack-read-compatible-write-and-replacement-blocked'
            $heldMoveBlocked = $false
            try { [IO.File]::Move($brokerXdc,$brokerXdc+'.held-probe') } catch { $heldMoveBlocked = $true }
            Assert-Test $heldMoveBlocked 'xdc-broker-retains-lease-after-run-child-exit'

            $badRoot = Join-Path $testRoot 'broker-hash-failure'
            $badLeases = Initialize-SafeOutputLeases $badRoot
            try {
                $badXdc = Get-ExpectedGeneratedClockXdcPath $badRoot
                [void][IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($badXdc))
                [S3T03SafeFile]::WriteWithinRoot($badXdc,$badRoot,$true,[Text.Encoding]::UTF8.GetBytes('actual-hash'))
                $badReq = Join-Path $badRoot 'reports\generated_clock_xdc.lease_request'
                $badAck = Join-Path $badRoot 'reports\generated_clock_xdc.lease_ack'
                $badErr = Join-Path $badRoot 'reports\generated_clock_xdc.lease_error'
                $badCode = @'
$root=@ROOT@;$xdc=@XDC@;$request=@REQUEST@;$ack=@ACK@;$errorPath=@ERROR@
Set-FakeFile (Join-Path $root 'run_status.txt') "STAGE=GENERATED_CLOCK_XDC_LEASE_BARRIER`nRESULT=RUNNING"
$pathB64=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($xdc))
Set-FakeFile $request "S3_GENERATED_CLOCK_LEASE=1`nPATH_B64=$pathB64`nSHA256=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`n"
Start-Sleep -Seconds 20
'@
                $badCode = $badCode.Replace('@ROOT@',(ConvertTo-PowerShellLiteral $badRoot)).Replace('@XDC@',(ConvertTo-PowerShellLiteral $badXdc)).Replace('@REQUEST@',(ConvertTo-PowerShellLiteral $badReq)).Replace('@ACK@',(ConvertTo-PowerShellLiteral $badAck)).Replace('@ERROR@',(ConvertTo-PowerShellLiteral $badErr))
                $badFake = New-FakeChild $testRoot $badCode 'xdc-broker-hash-failure'
                $badBroker = New-GeneratedClockXdcBrokerState 4
                try { $badResult = Resolve-SupervisedResult $badFake.Process $badRoot 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromSeconds(5)) 25 $badBroker $badLeases }
                finally { $badFake.Process.Dispose() }
                $badErrorText = [Text.Encoding]::UTF8.GetString($badLeases.ReadHeld($badErr))
                Assert-Test ($badResult.StopReason -eq 'GENERATED_CLOCK_XDC_BROKER_FAILED' -and $badBroker.Error -eq 'REQUEST_SHA256_MISMATCH' -and $badErrorText.Contains('REQUEST_SHA256_MISMATCH')) 'xdc-broker-hash-mismatch-fails-closed'
                $failureMoveBlocked = $false
                try { [IO.File]::Move($badXdc,$badXdc+'.failure-probe') } catch { $failureMoveBlocked = $true }
                Assert-Test $failureMoveBlocked 'xdc-broker-failure-keeps-lease-until-supervisor-cleanup'
                $badLeases.Dispose()
                [IO.File]::Move($badXdc,$badXdc+'.released')
                Assert-Test (Test-Path -LiteralPath ($badXdc+'.released') -PathType Leaf) 'xdc-broker-failure-lease-released-by-finally-disposal'
            } finally { $badLeases.Dispose() }

            $timeoutRoot = Join-Path $testRoot 'broker-wait-timeout'
            $timeoutLeases = Initialize-SafeOutputLeases $timeoutRoot
            try {
                $timeoutCode = @'
$root=@ROOT@
Set-FakeFile (Join-Path $root 'run_status.txt') "STAGE=GENERATED_CLOCK_XDC_LEASE_BARRIER`nRESULT=RUNNING"
Start-Sleep -Seconds 20
'@
                $timeoutCode = $timeoutCode.Replace('@ROOT@',(ConvertTo-PowerShellLiteral $timeoutRoot))
                $timeoutFake = New-FakeChild $testRoot $timeoutCode 'xdc-broker-timeout'
                $timeoutBroker = New-GeneratedClockXdcBrokerState 1
                try { $timeoutResult = Resolve-SupervisedResult $timeoutFake.Process $timeoutRoot 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(7)) ([TimeSpan]::FromSeconds(5)) 25 $timeoutBroker $timeoutLeases }
                finally { $timeoutFake.Process.Dispose() }
                $timeoutErrorText = [Text.Encoding]::UTF8.GetString($timeoutLeases.ReadHeld((Join-Path $timeoutRoot 'reports\generated_clock_xdc.lease_error')))
                Assert-Test ($timeoutResult.StopReason -eq 'GENERATED_CLOCK_XDC_BROKER_FAILED' -and $timeoutBroker.Error -eq 'BROKER_WAIT_TIMEOUT' -and $timeoutErrorText.Contains('BROKER_WAIT_TIMEOUT')) 'xdc-broker-barrier-wait-timeout-stops-child'
            } finally { $timeoutLeases.Dispose() }

            $layoutLeases.Dispose()
            [IO.File]::Move($brokerXdc,$brokerXdc+'.released')
            Assert-Test (Test-Path -LiteralPath ($brokerXdc+'.released') -PathType Leaf) 'xdc-broker-success-lease-released-at-run-exit'
        } finally { $layoutLeases.Dispose() }

        $missingName = 's3_t03_absent_' + [Guid]::NewGuid().ToString('N')
        $absentProcesses = @(Get-ExactNamedProcesses -Name $missingName)
        Assert-Test ($absentProcesses.Count -eq 0) 'exact-name-absence-is-not-enumeration-failure'

        $emptyProcessQuery = { @() }
        Assert-NoVivadoAlreadyRunning -ProcessQuery $emptyProcessQuery
        Assert-Test $true 'empty-process-set-allows-runner'

        $presentProcessQuery = { [pscustomobject]@{ Id=424242; ProcessName='vivado' } }
        $presentRejected = $false
        try { Assert-NoVivadoAlreadyRunning -ProcessQuery $presentProcessQuery } catch { $presentRejected = $_.Exception.Message -match 'PID=424242' }
        Assert-Test $presentRejected 'vivado-present-blocks-runner'

        $lateProcessStartState = [pscustomobject]@{ Count=0 }
        $lateProcessClockState = [pscustomobject]@{ Count=0; Now=$deadlineStartAt.AddMinutes(5) }
        $lateProcessClock = { $lateProcessClockState.Count++; $lateProcessClockState.Now }.GetNewClosure()
        $guardedVivadoStartCommand = Get-Command -Name 'Invoke-GuardedVivadoStart' -CommandType Function
        $lateProcessStartAction = {
            param([DateTime]$RouteDeadlineUtc)
            $childStartAction = { $lateProcessStartState.Count++; 'UNEXPECTED_ROUTE_CHILD_START' }.GetNewClosure()
            & $guardedVivadoStartCommand -ProcessStartAction $childStartAction -ProcessQuery $presentProcessQuery
        }.GetNewClosure()
        $lateProcessStartFailure = $null
        $lateProcessCatchAction = $null
        $lateProcessCapturedStatus = $null
        $lateProcessOutputRoot = Join-Path $testRoot 'late-vivado-output'
        $lateProcessOutputLeases = Initialize-SafeOutputLeases $lateProcessOutputRoot
        try {
            try {
                [void](Invoke-RouteStartGate -PrepareResult $deadlinePrepareResult -StartedAt $deadlineStartAt `
                    -MaxRuntime $deadlineMaxRuntime -Directory $lateProcessOutputRoot -RunId 'S3T03_LATE_VIVADO_GUARD' `
                    -RunnerSha 'selftest-runner-sha' -Leases $lateProcessOutputLeases -CapturedFailureStatus ([ref]$lateProcessCapturedStatus) `
                    -FailureMessage 'SELFTEST_LATE_VIVADO_GUARD' -RouteStartAction $lateProcessStartAction -Clock $lateProcessClock)
            } catch {
                $lateProcessStartFailure = $_.Exception.Message
                $lateProcessCatchAction = Invoke-RunnerCatchStatusHandler $lateProcessOutputRoot 'S3T03_LATE_VIVADO_GUARD' `
                    'selftest-runner-sha' ([DateTime]::UtcNow - $deadlineStartAt) $lateProcessOutputLeases $lateProcessCapturedStatus
            }
            $lateProcessStatus = [Text.Encoding]::UTF8.GetString($lateProcessOutputLeases.ReadHeld((Join-Path $lateProcessOutputRoot 'runner_status.txt')))
        } finally { $lateProcessOutputLeases.Dispose() }
        Assert-Test ($lateProcessStartFailure -match 'PID=424242' -and $lateProcessStartState.Count -eq 0 -and
            $lateProcessClockState.Count -eq 2 -and $null -eq $lateProcessCapturedStatus -and
            $lateProcessCatchAction -eq 'RUNNER_EXCEPTION_WRITTEN' -and
            $lateProcessStatus.Contains('S3_RUNNER_RESULT=RUNNER_EXCEPTION') -and
            $lateProcessStatus.Contains('STOP_REASON=RUNNER_EXCEPTION')) 'route-start-rechecks-vivado-after-prepare-before-child-launch'

        $deniedProcessQuery = { throw [System.UnauthorizedAccessException]::new('Access Denied') }
        $deniedRejected = $false
        try { Assert-NoVivadoAlreadyRunning -ProcessQuery $deniedProcessQuery } catch { $deniedRejected = $_.Exception.Message -match '无法安全枚举 Vivado 进程' }
        Assert-Test $deniedRejected 'process-enumeration-error-fails-closed'

        $unrelatedLine = New-DirectCommandLine $powershellExe @('-NoLogo','-NoProfile','-NonInteractive','-EncodedCommand', [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes('Start-Sleep -Seconds 30')))
        $unrelated = [S3T03RunnerProcess]::Start($powershellExe, $unrelatedLine, $repoRoot)

        $normalCode = @'
Set-FakeFile (Join-Path $d 'run_status.txt') "STAGE=COMPLETE`nRESULT=ROUTE_COMPLETED"
Set-FakeFile (Join-Path $d 'vivado.log') 'S3_TCL_RESULT=PASS:ROUTE_COMPLETE'
Set-FakeFile (Join-Path $d 'vivado.jou') 'journal-complete'
'@
        $normal = New-FakeChild $testRoot $normalCode 'normal'
        try { $normalResult = Resolve-SupervisedResult $normal.Process $normal.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(5)) ([TimeSpan]::FromSeconds(4)) 50 } finally { $normal.Process.Dispose() }
        $normalErrorPath = Join-Path $normal.Directory 'fake_error.txt'
        $normalError = if (Test-Path -LiteralPath $normalErrorPath) { [IO.File]::ReadAllText($normalErrorPath) } else { 'NONE' }
        [Console]::Out.WriteLine('SUPERVISOR_NORMAL_RESULT=' + $normalResult.Result + ';EXIT=' + $normalResult.ExitCode + ';MARKER=' + $(if ($normalResult.Marker) { $normalResult.Marker.Line } else { 'MISSING' }) + ';FAKE_ERROR=' + $normalError)
        Assert-Test ($normalResult.Result -eq 'SUCCESS' -and $normalResult.ExitCode -eq 0) 'normal-exit'

        $alreadyExitedCode = 'Set-FakeFile (Join-Path $d ''run_status.txt'') ''S3_TCL_RESULT=PASS:ROUTE_COMPLETE'''
        $alreadyExitedChild = New-FakeChild $testRoot $alreadyExitedCode 'already-exited-at-deadline'
        try {
            $childExitWait = [DateTime]::UtcNow.AddSeconds(8)
            while (-not $alreadyExitedChild.Process.HasExited -and [DateTime]::UtcNow -lt $childExitWait) { Start-Sleep -Milliseconds 25 }
            Assert-Test $alreadyExitedChild.Process.HasExited 'deadline-classification-child-exited-before-supervision'
            $alreadyExitedStartedAt = [DateTime]::UtcNow.Subtract([TimeSpan]::FromMinutes(60))
            $alreadyExitedResult = Resolve-SupervisedResult $alreadyExitedChild.Process $alreadyExitedChild.Directory 'run' `
                $alreadyExitedStartedAt ([TimeSpan]::FromMinutes(60)) ([TimeSpan]::FromMinutes(15)) 50
            Assert-Test ($alreadyExitedResult.Result -eq 'HARD_TIMEOUT_60_MIN' -and
                $alreadyExitedResult.StopReason -eq 'HARD_TIMEOUT_60_MIN' -and $alreadyExitedResult.ExitCode -eq 0 -and
                $alreadyExitedResult.Marker -and $alreadyExitedResult.Marker.Code -eq 'ROUTE_COMPLETE') `
                'deadline-classification-checks-after-loop-when-child-already-exited'
        } finally { $alreadyExitedChild.Process.Dispose() }

        $nonzeroCode = @'
Set-FakeFile (Join-Path $d 'run_status.txt') 'STAGE=FAILED'
exit 7
'@
        $nonzero = New-FakeChild $testRoot $nonzeroCode 'nonzero'
        try { $nonzeroResult = Resolve-SupervisedResult $nonzero.Process $nonzero.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(5)) ([TimeSpan]::FromSeconds(4)) 50 } finally { $nonzero.Process.Dispose() }
        Assert-Test ($nonzeroResult.Result -eq 'NONZERO_PROCESS_EXIT' -and $nonzeroResult.ExitCode -eq 7) 'nonzero-exit'

        $failedMarkerCode = @'
Set-FakeFile (Join-Path $d 'run_status.txt') 'TCL_RESULT=FAIL:ARGUMENTS'
exit 0
'@
        $failedMarker = New-FakeChild $testRoot $failedMarkerCode 'failure-marker'
        try { $failedMarkerResult = Resolve-SupervisedResult $failedMarker.Process $failedMarker.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(5)) ([TimeSpan]::FromSeconds(4)) 50 } finally { $failedMarker.Process.Dispose() }
        Assert-Test ($failedMarkerResult.Result -eq 'TCL_FAILURE_MARKER' -and $failedMarkerResult.ExitCode -eq 0) 'failure-marker-overrides-swallowed-zero'

        $childPidFile = Join-Path $testRoot 'owned-child.pid'
        $childCode = '$d=' + (ConvertTo-PowerShellLiteral $testRoot) + ";`$pidPath=Join-Path `$d 'owned-child.pid';`$pidBytes=[Text.Encoding]::UTF8.GetBytes([string]`$PID);`$pidStream=[IO.File]::Open(`$pidPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);`$pidStream.Write(`$pidBytes,0,`$pidBytes.Length);`$pidStream.Dispose();Start-Sleep -Seconds 30"
        $childEncoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($childCode))
        $hardCode = '$childEncoded=' + (ConvertTo-PowerShellLiteral $childEncoded) + ';$child=Start-Process -FilePath ' + (ConvertTo-PowerShellLiteral $powershellExe) + ' -ArgumentList @(''-NoLogo'',''-NoProfile'',''-NonInteractive'',''-EncodedCommand'',$childEncoded) -PassThru;$logPath=Join-Path $d ''vivado.log'';$b=[Text.Encoding]::UTF8.GetBytes(''start'');$f=[IO.File]::Open($logPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);$f.Write($b,0,$b.Length);$f.Dispose();while($true){$f=[IO.File]::Open($logPath,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite);[void]$f.Seek(0,[IO.SeekOrigin]::End);$f.WriteByte([byte]120);$f.Dispose();Start-Sleep -Milliseconds 100}'
        $hard = New-FakeChild $testRoot $hardCode 'hard-timeout'
        try {
            $hardResult = Resolve-SupervisedResult $hard.Process $hard.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(5)) ([TimeSpan]::FromSeconds(8)) 50
        } finally { $hard.Process.Dispose() }
        [Console]::Out.WriteLine('SUPERVISOR_HARD_RESULT=' + $hardResult.Result + ';EXIT=' + $hardResult.ExitCode + ';STOP=' + $hardResult.StopReason)
        $hardFakeError = Join-Path $hard.Directory 'fake_error.txt'
        if (Test-Path -LiteralPath $hardFakeError) { [Console]::Out.WriteLine('SUPERVISOR_HARD_FAKE_ERROR=' + [IO.File]::ReadAllText($hardFakeError)) }
        Assert-Test ($hardResult.Result -like 'HARD_TIMEOUT_60_MIN*') 'hard-timeout'
        if (Test-Path -LiteralPath $childPidFile) {
            $ownedChildPid = [int][IO.File]::ReadAllText($childPidFile)
            $deadline = [DateTime]::UtcNow.AddSeconds(3)
            while ([DateTime]::UtcNow -lt $deadline) {
                try { $childProc = [Diagnostics.Process]::GetProcessById($ownedChildPid); if ($childProc.HasExited) { break } }
                catch { break }
                Start-Sleep -Milliseconds 100
            }
            $childAlive = $false
            try { $childProc = [Diagnostics.Process]::GetProcessById($ownedChildPid); $childAlive = -not $childProc.HasExited } catch { }
            Assert-Test (-not $childAlive) 'owned-child-tree-terminated'
        } else { throw 'SUPERVISOR_SELFTEST_FAILED: owned child pid was not recorded' }
        Assert-Test (-not $unrelated.HasExited) 'unrelated-process-preserved'

        $quietCode = @'
Set-FakeFile (Join-Path $d 'run_status.txt') 'STAGE=ROUTE_DESIGN'
Set-FakeFile (Join-Path $d 'vivado.log') 'start'
Start-Sleep -Seconds 30
'@
        $quiet = New-FakeChild $testRoot $quietCode 'no-progress'
        try { $quietResult = Resolve-SupervisedResult $quiet.Process $quiet.Directory 'run' ([DateTime]::UtcNow) ([TimeSpan]::FromSeconds(8)) ([TimeSpan]::FromMilliseconds(1200)) 50 } finally { $quiet.Process.Dispose() }
        Assert-Test ($quietResult.Result -eq 'NO_PROGRESS_15_MIN') 'no-progress-stop'
        Assert-Test (-not $unrelated.HasExited) 'unrelated-process-preserved-after-second-stop'
        $tempParent = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
        $sentinelRoot = Join-Path $tempParent ('s3_t03_runner_cleanup_sentinel_' + [Guid]::NewGuid().ToString('N'))
        $sentinelMarker = Join-Path $sentinelRoot '.s3_t03_runner_selftest_owned'
        $sentinelText = 'owned by supervised-runner cleanup sentinel'
        $sentinelHandle = [S3T03SafeFile]::OpenDirectory($tempParent)
        try {
            $sentinelRootHandle = [S3T03SafeFile]::CreateDirectoryWithinRoot($sentinelRoot, $tempParent)
            $sentinelRootHandle.Dispose()
        } finally { $sentinelHandle.Dispose() }
        $sentinelBytes = [Text.Encoding]::UTF8.GetBytes($sentinelText)
        [S3T03SafeFile]::WriteSingle($sentinelMarker, $true, $sentinelBytes)
        $sentinelHashBefore = Get-S3T03SafeFileHash $sentinelMarker
        $junctionPath = Join-Path $testRoot 'zz_cleanup_external_sentinel_junction'
        $junctionCreated = $false
        $junctionKind = $null
        $junctionCreateError = ''
        try {
            try {
                $null = New-Item -ItemType Junction -Path $junctionPath -Target $sentinelRoot -ErrorAction Stop
                $junctionAttributes = [uint32][IO.File]::GetAttributes($junctionPath)
                if (($junctionAttributes -band [uint32][S3T03SafeFile]::AttributeReparsePoint) -ne 0 -and
                    ($junctionAttributes -band [uint32][S3T03SafeFile]::AttributeDirectory) -ne 0) {
                    $junctionCreated = $true
                    $junctionKind = 'JUNCTION'
                } else { throw 'SELFTEST_JUNCTION_CREATE_DID_NOT_CREATE_REPARSE_DIRECTORY' }
            } catch {
                $junctionCreateError = $_.Exception.Message
                if (Test-Path -LiteralPath $junctionPath) {
                    $leftAttributes = [uint32][IO.File]::GetAttributes($junctionPath)
                    if (($leftAttributes -band [uint32][S3T03SafeFile]::AttributeReparsePoint) -ne 0) {
                        [S3T03SafeFile]::DeleteKnownReparsePoint($junctionPath, (($leftAttributes -band [uint32][S3T03SafeFile]::AttributeDirectory) -ne 0))
                    } else { throw ('SELFTEST_JUNCTION_CREATE_LEFT_UNEXPECTED_ENTRY:' + $_.Exception.Message) }
                }
                if ([S3T03SafeFile]::TryCreateSymbolicLink($junctionPath, $sentinelRoot, $true)) {
                    $junctionCreated = $true
                    $junctionKind = 'DIRECTORY_SYMLINK'
                }
            }

            if ($junctionCreated) {
                $cleanupRejected = $false
                try { Remove-S3T03OwnedSelfTestTree $testRoot $tmpRoot 's3_t03_runner_selftest_' $ownerText }
                catch { $cleanupRejected = $_.Exception.Message -match 'SELFTEST_REPARSE_POINT_REJECTED' }
                Assert-Test $cleanupRejected 'safe-cleanup-refuses-external-junction-before-delete'
                Assert-Test ([IO.File]::Exists($ownerMarker)) 'safe-cleanup-rejection-preserves-selftest-root'
                Assert-Test ((Get-S3T03SafeFileHash $sentinelMarker) -eq $sentinelHashBefore) 'safe-cleanup-rejection-preserves-external-sentinel'
                [S3T03SafeFile]::DeleteKnownReparsePoint($junctionPath, $true)
                $junctionCreated = $false
                Assert-Test (-not [IO.Directory]::Exists($junctionPath)) 'known-junction-unlinked-without-recursive-target-delete'
                $sentinelHashAfter = Get-S3T03SafeFileHash $sentinelMarker
                Assert-Test ($sentinelHashAfter -eq $sentinelHashBefore) 'external-sentinel-unchanged-after-junction-unlink'
                [Console]::Out.WriteLine('SELFTEST_EXTERNAL_SENTINEL=UNCHANGED;SHA256=' + $sentinelHashAfter + ';JUNCTION_KIND=' + $junctionKind)
            } else {
                $syntheticReparseRejected = $false
                try { Assert-S3T03SelfTestAttributes 0x410 $true $junctionPath }
                catch { $syntheticReparseRejected = $_.Exception.Message -match 'SELFTEST_REPARSE_POINT_REJECTED' }
                Assert-Test $syntheticReparseRejected 'safe-cleanup-synthetic-reparse-gate-rejects-directory'
                $sentinelHashAfter = Get-S3T03SafeFileHash $sentinelMarker
                Assert-Test ($sentinelHashAfter -eq $sentinelHashBefore) 'synthetic-fallback-preserves-external-sentinel'
                [Console]::Out.WriteLine('SELFTEST_CLEANUP_JUNCTION_TEST=SKIPPED_UNAVAILABLE; SYNTHETIC_REPARSE_GATE=PASS; CREATE_ERROR=' + $junctionCreateError)
            }
        } finally {
            if ($junctionCreated) {
                $remainingAttributes = [uint32][IO.File]::GetAttributes($junctionPath)
                if (($remainingAttributes -band [uint32][S3T03SafeFile]::AttributeReparsePoint) -eq 0 -or
                    ($remainingAttributes -band [uint32][S3T03SafeFile]::AttributeDirectory) -eq 0) {
                    throw ('SELFTEST_KNOWN_JUNCTION_CHANGED_BEFORE_UNLINK:' + $junctionPath)
                }
                [S3T03SafeFile]::DeleteKnownReparsePoint($junctionPath, $true)
            }
            Remove-S3T03OwnedSelfTestTree $sentinelRoot $tempParent 's3_t03_runner_cleanup_sentinel_' $sentinelText
            [Console]::Out.WriteLine('SELFTEST_SENTINEL_CLEANUP=PASS;ROOT=' + $sentinelRoot)
        }
        $testExitCode = 0
    } catch {
        $testFailureMessage = $_.Exception.ToString()
        $testExitCode = 1
    } finally {
        if ($unrelated) {
            try { $unrelated.Dispose() }
            catch { $cleanupFailureMessage = 'SELFTEST_UNRELATED_PROCESS_DISPOSE_FAILED:' + $_.Exception.Message; $testExitCode = 1 }
        }
        if ($treeMonitor) {
            try { $treeMonitor.Dispose() }
            catch { $cleanupFailureMessage = 'SELFTEST_TREE_MONITOR_DISPOSE_FAILED:' + $_.Exception.Message; $testExitCode = 1 }
        }
        if ($aclTreeSnapshots -and $aclTreeRoot -and $secureLeases) {
            try {
                Restore-SecureMetadataTree -Root $aclTreeRoot -LeaseSet $secureLeases `
                    -OriginalSnapshots $aclTreeSnapshots -OriginalRootDaclSddl $aclTreeOriginalSddl
                $aclTreeSnapshots = $null
                $aclTreeOriginalSddl = $null
            } catch {
                $aclRestoreFailure = 'SELFTEST_METADATA_ACL_RESTORE_FAILED:' + $_.Exception.Message
                if ($cleanupFailureMessage) { $cleanupFailureMessage += ' | ' + $aclRestoreFailure } else { $cleanupFailureMessage = $aclRestoreFailure }
                $testExitCode = 1
            }
        }
        if ($secureLeases) {
            try { $secureLeases.Dispose() }
            catch {
                $leaseFailure = 'SELFTEST_LEASE_DISPOSE_FAILED:' + $_.Exception.Message
                if ($cleanupFailureMessage) { $cleanupFailureMessage += ' | ' + $leaseFailure } else { $cleanupFailureMessage = $leaseFailure }
                $testExitCode = 1
            }
        }
        try {
            Remove-S3T03OwnedSelfTestTree $testRoot $tmpRoot 's3_t03_runner_selftest_' $ownerText
            [Console]::Out.WriteLine('SELFTEST_TEMP_CLEANUP=PASS;ROOT=' + $testRoot)
        } catch {
            $rootFailure = 'SELFTEST_TEMP_CLEANUP=FAIL;ROOT=' + $testRoot + ';ERROR=' + $_.Exception.Message
            if ($cleanupFailureMessage) { $cleanupFailureMessage += ' | ' + $rootFailure } else { $cleanupFailureMessage = $rootFailure }
            $testExitCode = 1
        }
    }
    if ($testFailureMessage) { [Console]::Error.WriteLine('SUPERVISOR_SELFTEST_ERROR=' + $testFailureMessage.Replace("`r", ' ').Replace("`n", ' ')) }
    if ($cleanupFailureMessage) { [Console]::Error.WriteLine($cleanupFailureMessage) }
    if ($testExitCode -eq 0) { [Console]::Out.WriteLine('SUPERVISOR_SELFTEST_RESULT=PASS') }
    else { [Console]::Out.WriteLine('SUPERVISOR_SELFTEST_RESULT=FAIL') }
    return $testExitCode
}

function Assert-OutputTarget([string]$Target) {
    if ([string]::IsNullOrWhiteSpace($Target)) { throw '必须提供全新的输出目录绝对路径。' }
    $full = [IO.Path]::GetFullPath($Target)
    $repoTmp = [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp')).TrimEnd('\')
    $parent = [IO.Path]::GetDirectoryName($full).TrimEnd('\')
    if (-not [string]::Equals($parent, $repoTmp, [StringComparison]::OrdinalIgnoreCase)) {
        throw '输出目录必须是仓库 tmp 的直接子目录。'
    }
    if (Test-Path -LiteralPath $full) { throw '输出目录必须尚不存在；拒绝覆盖。' }
    if ($full.IndexOfAny([char[]]@('%','!','"','&','|','<','>','^',"`r","`n")) -ge 0) { throw '输出路径含批处理不安全字符。' }
    return $full
}

function Test-OutputParentMatchesRepoTmp([string]$OutputParent, [string]$TmpRoot) {
    $parentFull = [IO.Path]::GetFullPath($OutputParent).TrimEnd('\')
    $tmpRootFull = [IO.Path]::GetFullPath($TmpRoot).TrimEnd('\')
    if ([string]::Equals($parentFull, $tmpRootFull, [StringComparison]::OrdinalIgnoreCase)) { return $true }
    return $parentFull.StartsWith($tmpRootFull + '\', [StringComparison]::OrdinalIgnoreCase)
}

function Write-RunnerManifest([string]$Directory, [string]$RunId, [string]$RunnerSha, $Leases) {
    $tclPath = Join-Path $PSScriptRoot 's3_implement_hdmi_only_diag.tcl'
    $manifest = @(
        'RUN_ID=' + $RunId
        'RUNNER_SCRIPT_SHA256=' + $RunnerSha
        'EXECUTION_TCL_PATH=' + $tclPath
        'EXECUTION_TCL_SHA256=' + (Get-FileHash -Algorithm SHA256 -LiteralPath $tclPath).Hash
        'FIXED_VIVADO_BATCH=' + $vivadoBat
        'MAX_RUNTIME=60 minutes'
        'NO_PROGRESS_STOP=15 minutes'
        'COMMAND_WORKING_DIRECTORY=' + $repoRoot
        'TCL_SOURCE_ARGUMENT=scripts/s3_implement_hdmi_only_diag.tcl'
    ) -join "`n"
    Write-SafeOutputText (Join-Path $Directory 'reports\runner_manifest.txt') $manifest $Leases
}

function Initialize-SafeOutputLeases([string]$Directory) {
    $leases = New-Object S3T03OutputLeaseSet($Directory)
    try {
        $leases.LockParentDirectory($repoRoot)
        $tmpRoot = Join-Path $repoRoot 'tmp'
        $leases.LockParentDirectory($tmpRoot)
        $outputParent = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Directory))
        if (-not (Test-OutputParentMatchesRepoTmp $outputParent $tmpRoot)) { throw 'OUTPUT_PARENT_OUTSIDE_REPOSITORY_TMP' }
        $leases.LockParentDirectory($outputParent)
        $rootHandle = [S3T03SafeFile]::CreateDirectoryWithinRoot($Directory, $outputParent)
        $leases.AdoptDirectory($Directory, $rootHandle)
        foreach ($relative in @('reports','checkpoints','sentinels','inputs','project','vendor_ip_metadata')) {
            $leases.CreateDirectory((Join-Path $Directory $relative))
        }
        $outputs = @(
            'run_status.txt', 'prepare.result', 'reports\input_sha256.txt', 'reports\hdmi_xdc_audit.txt',
            'reports\metadata_copy_sha256.txt', 'inputs\hdmi_out.xdc', 'sentinels\preflight.complete',
            'runner_status.txt', 'vivado.log', 'vivado.jou', 'failure_details.txt', 'failure.result',
            'reports\runner_manifest.txt', 'reports\clock_constraint_change.txt',
            'reports\generated_clock_xdc.lease_request','reports\generated_clock_xdc.lease_ack','reports\generated_clock_xdc.lease_error',
            'reports\synth_utilization.rpt', 'reports\synth_clocks.rpt', 'reports\synth_timing_summary.rpt',
            'reports\placed_utilization.rpt', 'reports\placed_timing_summary.rpt',
            'reports\routed_timing_summary.rpt', 'reports\routed_clocks.rpt',
            'reports\routed_clock_interaction.rpt', 'reports\routed_check_timing.rpt',
            'reports\routed_drc.rpt', 'reports\final_summary.txt',
            'checkpoints\synth.dcp', 'checkpoints\opt.dcp', 'checkpoints\placed.dcp', 'checkpoints\routed.dcp',
            'sentinels\synth.complete', 'sentinels\opt.complete', 'sentinels\place.complete',
            'sentinels\route.complete', 'sentinels\final_reports.complete', 'sentinels\failed.sentinel'
        )
        foreach ($relative in $outputs) { $leases.ReserveNew((Join-Path $Directory $relative)) }
        return $leases
    } catch {
        $leases.Dispose()
        throw
    }
}

if ($SupervisorSelfTest) {
    $selfTestExit = Invoke-SupervisorSelfTests
    exit $selfTestExit
}

$outputLeases = $null
$metadataTreeMonitor = $null
$metadataRootAclSnapshots = $null
$metadataRootDaclSddl = $null
$outputFull = $null
$metadataRoot = $null
$runId = $null
$runnerSha = $null
$capturedFailureStatus = $null
try {
    if ([string]::IsNullOrWhiteSpace($VendorRoot)) { throw '必须提供固定官方源码根目录。' }
    if (-not [string]::Equals([IO.Path]::GetFullPath($VendorRoot), [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp\stage3_reference\AX7020_2023.1')), [StringComparison]::OrdinalIgnoreCase)) {
        throw 'VendorRoot 必须逐路径匹配本仓库固定官方资料副本。'
    }
    $vivadoInstall = Assert-FixedVivadoInstall
    Assert-NoVivadoAlreadyRunning
    $outputFull = Assert-OutputTarget $OutputDir
    $runId = 'S3T03_' + [Guid]::NewGuid().ToString('N')
    $supervisionStartedAt = [DateTime]::UtcNow
    $runnerSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $PSCommandPath).Hash
    $vendorFull = [IO.Path]::GetFullPath($VendorRoot)
    $outputLeases = Initialize-SafeOutputLeases $outputFull
    Write-RunnerManifest $outputFull $runId $runnerSha $outputLeases
    $startingPrepare = [pscustomobject]@{
        Result='PREPARE_RUNNING'; StopReason='PREPARE_RUNNING'; ExitCode='RUNNING'; Marker=$null
        ProcessId=0; Elapsed=([DateTime]::UtcNow - $supervisionStartedAt)
    }
    Write-RunnerStatus $outputFull $runId $startingPrepare $runnerSha $outputLeases

    $prepareLogPath = Join-Path $outputFull 'vivado.log'
    $prepareJournalPath = Join-Path $outputFull 'vivado.jou'
    $prepareDigestPipeName = 's3t03_' + [Guid]::NewGuid().ToString('N')
    $prepareArgs = @('-mode','batch','-log',$prepareLogPath,'-journal',$prepareJournalPath,
        '-source','scripts/s3_implement_hdmi_only_diag.tcl',
        '-tclargs',$vendorFull,$outputFull,'prepare-only',$runId,$prepareDigestPipeName)
    $prepareCommand = New-BatchCommandLine $vivadoBat $prepareArgs
    $prepareTrustedFileCount = 0
    $prepareTrustedTreeSha256 = $null
    $prepareDigestAuthorization = $null
    $prepareProcess = Invoke-GuardedVivadoStart -ProcessStartAction { [S3T03RunnerProcess]::StartForPrepare($comSpec,$prepareCommand,$repoRoot,$runId,$vivadoExe,$prepareDigestPipeName) }
    try {
        $prepareResult = Resolve-SupervisedResult $prepareProcess $outputFull 'prepare' $supervisionStartedAt $defaultMaxRuntime $defaultNoProgress $pollIntervalMs $null $outputLeases
        if ($prepareResult.Result -eq 'SUCCESS') {
            $prepareDigestAuthorization = Invoke-PrepareDigestAuthenticationGate `
                $prepareProcess $runId $outputFull $runId $runnerSha $outputLeases `
                ([ref]$capturedFailureStatus) $prepareResult.Elapsed $prepareResult
            $prepareTrustedFileCount = $prepareDigestAuthorization.FileCount
            $prepareTrustedTreeSha256 = $prepareDigestAuthorization.Sha256
        }
    } finally { $prepareProcess.Dispose() }
    if ($prepareResult.Result -ne 'SUCCESS') {
        Invoke-CapturedFailureAndThrow $outputFull $runId $prepareResult $runnerSha $outputLeases 'prepare' ([ref]$capturedFailureStatus) ('受控准备阶段失败：' + $prepareResult.Result + '; STOP_REASON=' + $prepareResult.StopReason + '; EXIT=' + $prepareResult.ExitCode)
    }
    $prepareResultPath = Join-Path $outputFull 'prepare.result'
    $outputLeases.SealExistingReadOnly($prepareResultPath)
    $prepareText = [Text.Encoding]::UTF8.GetString($outputLeases.ReadHeld($prepareResultPath))
    $trustedPrepareResult = Assert-PrepareResultMatchesTrustedDigest -PrepareText $prepareText `
        -ExpectedRunId $runId -ExpectedCount $prepareTrustedFileCount -ExpectedSha256 $prepareTrustedTreeSha256
    $preparedMetadataCount = $trustedPrepareResult.FileCount
    $preparedMetadataTreeSha256 = $trustedPrepareResult.Sha256
    foreach ($relative in @('project','vendor_ip_metadata')) {
        $outputLeases.LockDirectoryChain((Join-Path $outputFull $relative))
    }
    $metadataRoot = Join-Path $outputFull 'vendor_ip_metadata'
    Protect-SecureMetadataTree -Root $metadataRoot -LeaseSet $outputLeases `
        -OriginalSnapshots ([ref]$metadataRootAclSnapshots) -OriginalRootDaclSddl ([ref]$metadataRootDaclSddl)
    $metadataTreeMonitor = New-Object S3T03TreeMonitor($metadataRoot)
    $metadataRecords = @(Get-SecureTreeSha256Manifest -Root $metadataRoot -LeaseSet $outputLeases)
    if ($metadataRecords.Count -ne $preparedMetadataCount) {
        throw ('GUARDED_METADATA_COPY_FILE_COUNT_MISMATCH: EXPECTED=' + $preparedMetadataCount + '; ACTUAL=' + $metadataRecords.Count)
    }
    [void](Assert-PreparedMetadataTreeSha256 -Records $metadataRecords `
        -ExpectedCount $preparedMetadataCount -ExpectedSha256 $preparedMetadataTreeSha256)
    $metadataSnapshotStatus = $metadataTreeMonitor.Status()
    if ($metadataSnapshotStatus -ne 'EVENT_COUNT=0;ERROR_COUNT=0;ERROR=') {
        throw ('METADATA_TREE_CHANGED_DURING_SNAPSHOT: ' + $metadataSnapshotStatus)
    }
    $metadataManifestText = Format-SecureTreeSha256Manifest -Root $metadataRoot -Records $metadataRecords
    $metadataManifestPath = Join-Path $outputFull 'reports\metadata_copy_sha256.txt'
    $metadataManifestBytes = [Text.Encoding]::UTF8.GetBytes($metadataManifestText)
    $metadataManifestSha256 = Get-Sha256Hex $metadataManifestBytes
    $outputLeases.WriteHeld($metadataManifestPath, $metadataManifestBytes)
    if ((Get-Sha256Hex ($outputLeases.ReadHeld($metadataManifestPath))) -cne $metadataManifestSha256) {
        throw 'METADATA_COPY_MANIFEST_WRITEBACK_HASH_MISMATCH'
    }
    $outputLeases.SealExistingReadOnly($metadataManifestPath)
    if ((Get-Sha256Hex ($outputLeases.ReadHeld($metadataManifestPath))) -cne $metadataManifestSha256) {
        throw 'METADATA_COPY_MANIFEST_SEAL_HASH_MISMATCH'
    }
    $metadataBeforeRouteStatus = $metadataTreeMonitor.Status()
    if ($metadataBeforeRouteStatus -ne 'EVENT_COUNT=0;ERROR_COUNT=0;ERROR=') {
        throw ('METADATA_TREE_CHANGED_BEFORE_ROUTE: ' + $metadataBeforeRouteStatus)
    }
    if (-not $prepareDigestAuthorization -or -not $prepareDigestAuthorization.Authenticated) {
        throw 'PREPARE_DIGEST_AUTHORIZATION_REQUIRED_BEFORE_ROUTE'
    }

    $logPath = Join-Path $outputFull 'vivado.log'
    $journalPath = Join-Path $outputFull 'vivado.jou'
    $runArgs = @('-mode','batch','-log',$logPath,'-journal',$journalPath,
        '-source','scripts/s3_implement_hdmi_only_diag.tcl','-tclargs',$vendorFull,$outputFull,'run',$runId,$metadataManifestSha256,$preparedMetadataTreeSha256)
    $runCommand = New-BatchCommandLine $vivadoBat $runArgs
    $xdcBroker = New-GeneratedClockXdcBrokerState
    $process = Invoke-RouteStartGate -PrepareResult $prepareResult -StartedAt $supervisionStartedAt `
        -MaxRuntime $defaultMaxRuntime -Directory $outputFull -RunId $runId -RunnerSha $runnerSha `
        -Leases $outputLeases -CapturedFailureStatus ([ref]$capturedFailureStatus) `
        -FailureMessage '总监督时间达到 60 分钟；已在 route 启动前停止。' `
        -RouteStartAction {
            param([DateTime]$RouteDeadlineUtc)
            Invoke-GuardedVivadoStart -ProcessStartAction { [S3T03RunnerProcess]::Start($comSpec,$runCommand,$repoRoot,$RouteDeadlineUtc) }
        }
    try {
        $result = Resolve-SupervisedResult $process $outputFull 'run' $supervisionStartedAt $defaultMaxRuntime $defaultNoProgress $pollIntervalMs $xdcBroker $outputLeases
    } finally { $process.Dispose() }
    if ($result.Result -ne 'SUCCESS') {
        Invoke-CapturedFailureAndThrow $outputFull $runId $result $runnerSha $outputLeases 'run' ([ref]$capturedFailureStatus) ('诊断失败：' + $result.Result + '; STOP_REASON=' + $result.StopReason + '; EXIT=' + $result.ExitCode)
    }
    $finalMetadataRecords = @(Get-SecureTreeSha256Manifest -Root $metadataRoot -LeaseSet $outputLeases)
    $finalMetadataManifestText = Format-SecureTreeSha256Manifest -Root $metadataRoot -Records $finalMetadataRecords
    if ((Get-Sha256Hex ($outputLeases.ReadHeld($metadataManifestPath))) -cne $metadataManifestSha256) {
        throw 'METADATA_COPY_MANIFEST_CHANGED_DURING_IMPLEMENTATION'
    }
    $metadataTreeMonitor.StopAndDrain()
    $metadataAfterRouteStatus = $metadataTreeMonitor.Status()
    if ($metadataAfterRouteStatus -ne 'EVENT_COUNT=0;ERROR_COUNT=0;ERROR=') {
        throw ('METADATA_TREE_CHANGED_DURING_IMPLEMENTATION: ' + $metadataAfterRouteStatus)
    }
    if (-not [string]::Equals($finalMetadataManifestText, $metadataManifestText, [StringComparison]::Ordinal)) {
        throw 'METADATA_TREE_CHANGED_DURING_IMPLEMENTATION'
    }
    Restore-SecureMetadataTree -Root $metadataRoot -LeaseSet $outputLeases `
        -OriginalSnapshots $metadataRootAclSnapshots -OriginalRootDaclSddl $metadataRootDaclSddl
    $metadataRootAclSnapshots = $null
    $metadataRootDaclSddl = $null
    Write-RunnerStatus $outputFull $runId $result $runnerSha $outputLeases
    foreach ($requiredLog in @($logPath,$journalPath)) { [void]$outputLeases.ReadHeld($requiredLog) }
    $stdoutMarker = Get-ResultMarker $outputFull 'run'
    if (-not $stdoutMarker -or $stdoutMarker.Kind -ne 'PASS' -or $stdoutMarker.Code -ne 'ROUTE_COMPLETE') {
        throw 'Vivado 结束后未找到 PASS:ROUTE_COMPLETE 机器标记。'
    }
    Write-Output ('S3_RUNNER_RESULT=SUCCESS')
    Write-Output ('RUN_ID=' + $runId)
    Write-Output ('EVIDENCE_DIRECTORY=' + $outputFull)
    Write-Output ('VIVADO_LOG=' + $logPath)
    Write-Output ('VIVADO_JOURNAL=' + $journalPath)
    exit 0
} catch {
    $runnerError = $_
    if ($metadataRootAclSnapshots -and $metadataRoot -and $outputLeases) {
        try {
            Restore-SecureMetadataTree -Root $metadataRoot -LeaseSet $outputLeases `
                -OriginalSnapshots $metadataRootAclSnapshots -OriginalRootDaclSddl $metadataRootDaclSddl
            $metadataRootAclSnapshots = $null
            $metadataRootDaclSddl = $null
        } catch {
            [Console]::Error.WriteLine('SECURE_METADATA_ACL_RESTORE_FAILED=' + $_.Exception.Message)
        }
    }
    if ($outputLeases -and $runId -and $runnerSha) {
        try {
            $brokerForFailure = $null
            if (Get-Variable -Name xdcBroker -Scope Script -ErrorAction SilentlyContinue) { $brokerForFailure = $xdcBroker }
            [void](Invoke-RunnerCatchStatusHandler $outputFull $runId $runnerSha ([DateTime]::UtcNow - $supervisionStartedAt) $outputLeases $capturedFailureStatus $brokerForFailure)
        } catch { Write-Error ('无法通过已持有租约写 runner_status：' + $_.Exception.Message) }
    }
    Write-Error $runnerError
    Write-Output 'S3_RUNNER_RESULT=FAIL'
    exit 2
} finally {
    if ($metadataRootAclSnapshots -and $metadataRoot -and $outputLeases) {
        try {
            Restore-SecureMetadataTree -Root $metadataRoot -LeaseSet $outputLeases `
                -OriginalSnapshots $metadataRootAclSnapshots -OriginalRootDaclSddl $metadataRootDaclSddl
            $metadataRootAclSnapshots = $null
            $metadataRootDaclSddl = $null
        } catch {
            [Console]::Error.WriteLine('SECURE_METADATA_ACL_RESTORE_FAILED_IN_FINALLY=' + $_.Exception.Message)
        }
    }
    if ($metadataTreeMonitor) { $metadataTreeMonitor.Dispose() }
    if ($outputLeases) { $outputLeases.Dispose() }
}
