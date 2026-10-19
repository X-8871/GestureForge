public sealed class S3T03PhaseSupervisorOptions
{
    public DateTime CommonRunStartUtc { get; private set; }
    public TimeSpan HardTimeout { get; private set; }
    public TimeSpan NoProgressTimeout { get; private set; }
    public TimeSpan PollInterval { get; private set; }
    public TimeSpan TreeExitConfirmationTimeout { get; private set; }
    public DateTime HardDeadlineUtc { get; private set; }

    public S3T03PhaseSupervisorOptions(DateTime commonRunStartUtc)
        : this(commonRunStartUtc, TimeSpan.FromMinutes(60), TimeSpan.FromMinutes(15),
            TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(5))
    {
    }

    public S3T03PhaseSupervisorOptions(DateTime commonRunStartUtc, TimeSpan hardTimeout,
        TimeSpan noProgressTimeout, TimeSpan pollInterval, TimeSpan treeExitConfirmationTimeout)
    {
        if (commonRunStartUtc.Kind != DateTimeKind.Utc)
            throw new ArgumentException("COMMON_RUN_START_MUST_BE_UTC", "commonRunStartUtc");
        if (hardTimeout <= TimeSpan.Zero) throw new ArgumentOutOfRangeException("hardTimeout");
        if (noProgressTimeout <= TimeSpan.Zero) throw new ArgumentOutOfRangeException("noProgressTimeout");
        if (pollInterval < TimeSpan.FromMilliseconds(1) || pollInterval.TotalMilliseconds > Int32.MaxValue)
            throw new ArgumentOutOfRangeException("pollInterval");
        if (treeExitConfirmationTimeout < TimeSpan.Zero ||
            treeExitConfirmationTimeout.TotalMilliseconds > Int32.MaxValue)
            throw new ArgumentOutOfRangeException("treeExitConfirmationTimeout");

        CommonRunStartUtc = commonRunStartUtc;
        HardTimeout = hardTimeout;
        NoProgressTimeout = noProgressTimeout;
        PollInterval = pollInterval;
        TreeExitConfirmationTimeout = treeExitConfirmationTimeout;
        HardDeadlineUtc = commonRunStartUtc.Add(hardTimeout);
    }
}

public sealed class S3T03PhaseSupervisionResult
{
    public bool Succeeded { get; private set; }
    public string RequestedPhase { get; private set; }
    public string Phase { get; private set; }
    public string Marker { get; private set; }
    public string ProgressMarker { get; private set; }
    public DateTime CommonRunStartUtc { get; private set; }
    public DateTime HardDeadlineUtc { get; private set; }
    public TimeSpan HardTimeout { get; private set; }
    public TimeSpan NoProgressTimeout { get; private set; }
    public TimeSpan PollInterval { get; private set; }
    public DateTime CompletedUtc { get; private set; }
    public TimeSpan Elapsed { get; private set; }
    public TimeSpan PhaseElapsed { get; private set; }
    public int? ExitCode { get; private set; }
    public bool TimedOut { get; private set; }
    public string TimeoutOrStopReason { get; private set; }
    public bool JobTreeTerminationAttempted { get; private set; }
    public bool JobTreeTerminationSucceeded { get; private set; }
    public bool JobTreeConfirmedZero { get; private set; }
    public string JobTreeConfirmation { get; private set; }
    public string LastPollLinkAudit { get; private set; }
    public string AfterExitLinkAudit { get; private set; }
    public bool LinkAuditPassed { get; private set; }
    public string FailureDetail { get; private set; }

    internal S3T03PhaseSupervisionResult(bool succeeded, string requestedPhase, string phase,
        string marker, string progressMarker, DateTime commonRunStartUtc, DateTime hardDeadlineUtc,
        TimeSpan hardTimeout, TimeSpan noProgressTimeout, TimeSpan pollInterval,
        DateTime completedUtc, TimeSpan elapsed, TimeSpan phaseElapsed, int? exitCode,
        bool timedOut, string timeoutOrStopReason, bool jobTreeTerminationAttempted,
        bool jobTreeTerminationSucceeded, bool jobTreeConfirmedZero, string lastPollLinkAudit,
        string afterExitLinkAudit, bool linkAuditPassed, string failureDetail)
    {
        Succeeded = succeeded;
        RequestedPhase = requestedPhase;
        Phase = phase;
        Marker = marker;
        ProgressMarker = progressMarker;
        CommonRunStartUtc = commonRunStartUtc;
        HardDeadlineUtc = hardDeadlineUtc;
        HardTimeout = hardTimeout;
        NoProgressTimeout = noProgressTimeout;
        PollInterval = pollInterval;
        CompletedUtc = completedUtc;
        Elapsed = elapsed;
        PhaseElapsed = phaseElapsed;
        ExitCode = exitCode;
        TimedOut = timedOut;
        TimeoutOrStopReason = timeoutOrStopReason;
        JobTreeTerminationAttempted = jobTreeTerminationAttempted;
        JobTreeTerminationSucceeded = jobTreeTerminationSucceeded;
        JobTreeConfirmedZero = jobTreeConfirmedZero;
        JobTreeConfirmation = jobTreeConfirmedZero ? "CONFIRMED_ZERO_ACTIVE_PROCESSES" : "ZERO_ACTIVE_PROCESSES_UNCONFIRMED";
        LastPollLinkAudit = lastPollLinkAudit;
        AfterExitLinkAudit = afterExitLinkAudit;
        LinkAuditPassed = linkAuditPassed;
        FailureDetail = failureDetail;
    }
}

public sealed class S3T03PhaseSupervisor
{
    private const uint SupervisorStopExitCode = 0xE0030015;
    private readonly S3T03PhaseSupervisorOptions options;

    public DateTime HardDeadlineUtc { get { return options.HardDeadlineUtc; } }

    public S3T03PhaseSupervisor(S3T03PhaseSupervisorOptions supervisorOptions)
    {
        if (supervisorOptions == null) throw new ArgumentNullException("supervisorOptions");
        options = supervisorOptions;
    }

    public static S3T03PhaseSupervisor CreateProduction(DateTime commonRunStartUtc)
    {
        return new S3T03PhaseSupervisor(new S3T03PhaseSupervisorOptions(commonRunStartUtc));
    }

    public S3T03PhaseSupervisionResult Supervise(string requestedPhase, S3T03RunnerProcess process,
        S3T03OutputLeaseSet outputLeases, string outputDirectory, CancellationToken cancellationToken)
    {
        if (process == null) throw new ArgumentNullException("process");

        DateTime phaseStartUtc = DateTime.UtcNow;
        string phase = String.IsNullOrWhiteSpace(requestedPhase) ? "UNKNOWN" : requestedPhase.Trim();
        string marker = "UNKNOWN";
        string progressMarker = "NOT_OBSERVED";
        string stopReason = "NONE";
        string failureDetail = "";
        string lastPollLinkAudit = "NOT_RUN";
        string afterExitLinkAudit = "NOT_RUN";
        DateTime lastProgressUtc = phaseStartUtc;
        string previousProgressKey = null;
        int? exitCode = null;
        bool timedOut = false;
        bool jobTreeTerminationAttempted = false;
        bool jobTreeTerminationSucceeded = false;
        bool jobTreeConfirmedZero = false;
        bool processCompletedNormally = false;
        string fullOutputDirectory = null;

        try
        {
            if (String.IsNullOrWhiteSpace(requestedPhase))
                throw new ArgumentException("REQUESTED_PHASE_REQUIRED", "requestedPhase");
            if (outputLeases == null) throw new ArgumentNullException("outputLeases");
            if (String.IsNullOrWhiteSpace(outputDirectory) || !Path.IsPathFullyQualified(outputDirectory))
                throw new ArgumentException("OUTPUT_DIRECTORY_MUST_BE_ABSOLUTE", "outputDirectory");

            fullOutputDirectory = Path.GetFullPath(outputDirectory).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            if (!Directory.Exists(fullOutputDirectory)) throw new DirectoryNotFoundException("SUPERVISOR_OUTPUT_DIRECTORY_MISSING");
            if (DateTime.UtcNow < options.CommonRunStartUtc)
                throw new InvalidOperationException("SUPERVISOR_CLOCK_PRECEDES_COMMON_RUN_START");

            while (stopReason == "NONE")
            {
                DateTime nowUtc = DateTime.UtcNow;
                if (nowUtc >= options.HardDeadlineUtc)
                {
                    stopReason = "HARD_DEADLINE";
                    timedOut = true;
                    break;
                }
                if (cancellationToken.IsCancellationRequested)
                {
                    stopReason = "CANCELLED";
                    break;
                }

                S3T03ProgressSnapshot snapshot = Observe(fullOutputDirectory, outputLeases);
                phase = String.IsNullOrEmpty(snapshot.Stage) || snapshot.Stage == "<MISSING>" ? phase : snapshot.Stage;
                marker = String.IsNullOrEmpty(snapshot.Result) || snapshot.Result == "<MISSING>" ? marker : snapshot.Result;
                progressMarker = snapshot.ProgressKey;

                lastPollLinkAudit = SafeAudit(outputLeases);
                if (!IsPassingAudit(lastPollLinkAudit))
                {
                    stopReason = "OUTPUT_LINK_AUDIT_FAILED_DURING_POLL";
                    failureDetail = lastPollLinkAudit;
                    break;
                }

                if (IsFailureMarker(snapshot.Stage, snapshot.Result))
                {
                    stopReason = "TCL_FAILURE_MARKER";
                    failureDetail = "STAGE=" + snapshot.Stage + ";RESULT=" + snapshot.Result;
                    break;
                }

                if (process.HasExited)
                {
                    exitCode = process.ExitCode;
                    if (exitCode.Value != 0)
                    {
                        stopReason = "PROCESS_EXIT_NONZERO";
                        failureDetail = "EXIT_CODE=" + exitCode.Value.ToString(System.Globalization.CultureInfo.InvariantCulture);
                        break;
                    }
                    if (snapshot.StatusPresent &&
                        (IsPendingMarker(snapshot.Stage) || IsPendingMarker(snapshot.Result)))
                    {
                        stopReason = "RUN_STATUS_TERMINAL_FIELDS_MISSING";
                        failureDetail = "STAGE_OR_RESULT_MISSING_ON_PROCESS_EXIT";
                        break;
                    }
                    if (!snapshot.StatusPresent)
                    {
                        stopReason = "RUN_STATUS_MISSING_ON_PROCESS_EXIT";
                        failureDetail = "RUN_STATUS_FILE_NOT_OBSERVED";
                        break;
                    }

                    int treeWaitMilliseconds = GetTreeWaitMilliseconds(DateTime.UtcNow);
                    jobTreeConfirmedZero = process.WaitForTreeExit(treeWaitMilliseconds);
                    if (!jobTreeConfirmedZero)
                    {
                        if (DateTime.UtcNow >= options.HardDeadlineUtc)
                        {
                            stopReason = "HARD_DEADLINE";
                            timedOut = true;
                        }
                        else
                        {
                            stopReason = "JOB_TREE_ACTIVE_AFTER_LEADER_EXIT";
                        }
                        break;
                    }
                    if (DateTime.UtcNow >= options.HardDeadlineUtc)
                    {
                        stopReason = "HARD_DEADLINE";
                        timedOut = true;
                        break;
                    }
                    processCompletedNormally = true;
                    break;
                }

                if (previousProgressKey != null && !String.Equals(previousProgressKey,
                    snapshot.ProgressKey, StringComparison.Ordinal))
                    lastProgressUtc = nowUtc;
                previousProgressKey = snapshot.ProgressKey;

                if (nowUtc - lastProgressUtc >= options.NoProgressTimeout)
                {
                    stopReason = "NO_PROGRESS_TIMEOUT";
                    timedOut = true;
                    break;
                }

                TimeSpan wait = GetNextWait(nowUtc, lastProgressUtc);
                WaitForNextPoll(wait, cancellationToken);
            }
        }
        catch (Exception error)
        {
            if (stopReason == "NONE") stopReason = "SUPERVISOR_ERROR";
            failureDetail = AppendDetail(failureDetail, FormatError(error));
        }

        if (stopReason != "NONE")
        {
            jobTreeTerminationAttempted = true;
            try
            {
                process.TerminateTree(SupervisorStopExitCode);
                jobTreeTerminationSucceeded = true;
            }
            catch (Exception error)
            {
                failureDetail = AppendDetail(failureDetail, "JOB_TREE_TERMINATE_FAILED:" + FormatError(error));
            }

            try
            {
                jobTreeConfirmedZero = process.WaitForTreeExit(ToMilliseconds(options.TreeExitConfirmationTimeout));
                if (!jobTreeConfirmedZero)
                    failureDetail = AppendDetail(failureDetail, "JOB_TREE_ZERO_ACTIVE_PROCESSES_NOT_CONFIRMED");
            }
            catch (Exception error)
            {
                jobTreeConfirmedZero = false;
                failureDetail = AppendDetail(failureDetail, "JOB_TREE_CONFIRMATION_FAILED:" + FormatError(error));
            }
        }

        afterExitLinkAudit = outputLeases == null ? "AUDIT_UNAVAILABLE_NO_OUTPUT_LEASE" : SafeAudit(outputLeases);
        if (!IsPassingAudit(afterExitLinkAudit) && stopReason == "NONE")
        {
            stopReason = "OUTPUT_LINK_AUDIT_FAILED_AFTER_EXIT";
            failureDetail = AppendDetail(failureDetail, afterExitLinkAudit);
            processCompletedNormally = false;
            jobTreeTerminationAttempted = true;
            try
            {
                process.TerminateTree(SupervisorStopExitCode);
                jobTreeTerminationSucceeded = true;
            }
            catch (Exception error)
            {
                failureDetail = AppendDetail(failureDetail, "JOB_TREE_TERMINATE_FAILED:" + FormatError(error));
            }
            try
            {
                jobTreeConfirmedZero = process.WaitForTreeExit(ToMilliseconds(options.TreeExitConfirmationTimeout));
                if (!jobTreeConfirmedZero)
                    failureDetail = AppendDetail(failureDetail, "JOB_TREE_ZERO_ACTIVE_PROCESSES_NOT_CONFIRMED");
            }
            catch (Exception error)
            {
                jobTreeConfirmedZero = false;
                failureDetail = AppendDetail(failureDetail, "JOB_TREE_CONFIRMATION_FAILED:" + FormatError(error));
            }
            afterExitLinkAudit = SafeAudit(outputLeases);
        }
        else if (!IsPassingAudit(afterExitLinkAudit))
        {
            failureDetail = AppendDetail(failureDetail, "AFTER_EXIT_" + afterExitLinkAudit);
        }

        if (exitCode == null)
        {
            try
            {
                if (process.HasExited) exitCode = process.ExitCode;
            }
            catch (Exception error)
            {
                failureDetail = AppendDetail(failureDetail, "EXIT_CODE_READ_FAILED:" + FormatError(error));
            }
        }

        DateTime completedUtc = DateTime.UtcNow;
        if (completedUtc < options.CommonRunStartUtc) completedUtc = options.CommonRunStartUtc;
        if (completedUtc < phaseStartUtc) completedUtc = phaseStartUtc;
        bool linkAuditPassed = IsPassingAudit(lastPollLinkAudit) && IsPassingAudit(afterExitLinkAudit);
        bool succeeded = stopReason == "NONE" && processCompletedNormally && exitCode == 0 &&
            jobTreeConfirmedZero && linkAuditPassed;
        return new S3T03PhaseSupervisionResult(succeeded, requestedPhase, phase, marker,
            progressMarker, options.CommonRunStartUtc, options.HardDeadlineUtc,
            options.HardTimeout, options.NoProgressTimeout, options.PollInterval, completedUtc,
            completedUtc - options.CommonRunStartUtc, completedUtc - phaseStartUtc, exitCode,
            timedOut, stopReason, jobTreeTerminationAttempted, jobTreeTerminationSucceeded,
            jobTreeConfirmedZero, lastPollLinkAudit, afterExitLinkAudit, linkAuditPassed, failureDetail);
    }

    private static S3T03ProgressSnapshot Observe(string outputDirectory, S3T03OutputLeaseSet outputLeases)
    {
        string statusPath = Path.Combine(outputDirectory, "run_status.txt");
        string logPath = Path.Combine(outputDirectory, "vivado.log");
        string journalPath = Path.Combine(outputDirectory, "vivado.jou");
        byte[] statusBytes = TryReadStatusBytes(statusPath, outputLeases);
        string stage = "<MISSING>";
        string result = "<MISSING>";
        bool statusPresent = statusBytes != null;
        if (statusPresent) ParseStatus(statusBytes, out stage, out result);

        long? logBytes = TryGetFileLength(logPath);
        long? journalBytes = TryGetFileLength(journalPath);
        string progressKey = "STAGE=" + EncodeField(stage) + "|RESULT=" + EncodeField(result) +
            "|LOG_BYTES=" + FormatLength(logBytes) + "|JOU_BYTES=" + FormatLength(journalBytes);
        return new S3T03ProgressSnapshot(stage, result, statusPresent, progressKey);
    }

    private static byte[] TryReadStatusBytes(string path, S3T03OutputLeaseSet outputLeases)
    {
        try
        {
            if (outputLeases.HasFileLease(path)) return outputLeases.ReadHeld(path);
            using (SafeFileHandle handle = S3T03SafeFile.OpenReadLeaf(path))
            {
                using (FileStream stream = new FileStream(handle, FileAccess.Read))
                {
                    if (stream.Length > 1024L * 1024L) throw new IOException("RUN_STATUS_FILE_TOO_LARGE");
                    using (MemoryStream buffer = new MemoryStream())
                    {
                        stream.CopyTo(buffer);
                        if (buffer.Length > 1024L * 1024L) throw new IOException("RUN_STATUS_FILE_TOO_LARGE");
                        return buffer.ToArray();
                    }
                }
            }
        }
        catch (Win32Exception error)
        {
            if (error.NativeErrorCode == 2 || error.NativeErrorCode == 3) return null;
            throw;
        }
        catch (FileNotFoundException) { return null; }
        catch (DirectoryNotFoundException) { return null; }
    }

    private static long? TryGetFileLength(string path)
    {
        try
        {
            using (SafeFileHandle handle = S3T03SafeFile.OpenReadLeaf(path))
            using (FileStream stream = new FileStream(handle, FileAccess.Read))
                return stream.Length;
        }
        catch (Win32Exception error)
        {
            if (error.NativeErrorCode == 2 || error.NativeErrorCode == 3) return null;
            throw;
        }
        catch (FileNotFoundException) { return null; }
        catch (DirectoryNotFoundException) { return null; }
    }

    private static void ParseStatus(byte[] bytes, out string stage, out string result)
    {
        string text = new UTF8Encoding(false, true).GetString(bytes);
        stage = "<MISSING>";
        result = "<MISSING>";
        bool stageSeen = false, resultSeen = false;
        string[] lines = text.Split(new char[] { '\n' }, StringSplitOptions.None);
        foreach (string rawLine in lines)
        {
            string line = rawLine.TrimEnd('\r');
            int separator = line.IndexOf('=');
            if (separator < 0) continue;
            string key = line.Substring(0, separator);
            string value = line.Substring(separator + 1).Trim();
            if (String.Equals(key, "STAGE", StringComparison.Ordinal))
            {
                if (stageSeen) throw new InvalidDataException("RUN_STATUS_DUPLICATE_STAGE_FIELD");
                stageSeen = true;
                stage = value.Length == 0 ? "<EMPTY>" : value;
            }
            else if (String.Equals(key, "RESULT", StringComparison.Ordinal))
            {
                if (resultSeen) throw new InvalidDataException("RUN_STATUS_DUPLICATE_RESULT_FIELD");
                resultSeen = true;
                result = value.Length == 0 ? "<EMPTY>" : value;
            }
        }
    }

    private static bool IsFailureMarker(string stage, string result)
    {
        return StartsWithFailure(stage) || StartsWithFailure(result);
    }

    private static bool IsPendingMarker(string value)
    {
        return String.IsNullOrWhiteSpace(value) || value == "<MISSING>" || value == "<EMPTY>" ||
            String.Equals(value, "NONE", StringComparison.OrdinalIgnoreCase) ||
            String.Equals(value, "STARTING", StringComparison.OrdinalIgnoreCase) ||
            String.Equals(value, "RUNNING", StringComparison.OrdinalIgnoreCase);
    }

    private static bool StartsWithFailure(string value)
    {
        if (String.IsNullOrWhiteSpace(value)) return false;
        return value.StartsWith("FAILED", StringComparison.OrdinalIgnoreCase) ||
            value.StartsWith("FAIL", StringComparison.OrdinalIgnoreCase) ||
            value.StartsWith("ERROR", StringComparison.OrdinalIgnoreCase);
    }

    private int GetTreeWaitMilliseconds(DateTime nowUtc)
    {
        TimeSpan remaining = options.HardDeadlineUtc - nowUtc;
        if (remaining <= TimeSpan.Zero) return 0;
        return Math.Min(ToMilliseconds(options.TreeExitConfirmationTimeout), ToMilliseconds(remaining));
    }

    private TimeSpan GetNextWait(DateTime nowUtc, DateTime lastProgressUtc)
    {
        TimeSpan remainingHard = options.HardDeadlineUtc - nowUtc;
        TimeSpan remainingProgress = options.NoProgressTimeout - (nowUtc - lastProgressUtc);
        TimeSpan wait = options.PollInterval;
        if (remainingHard < wait) wait = remainingHard;
        if (remainingProgress < wait) wait = remainingProgress;
        return wait > TimeSpan.Zero ? wait : TimeSpan.FromMilliseconds(1);
    }

    private static void WaitForNextPoll(TimeSpan wait, CancellationToken cancellationToken)
    {
        int milliseconds = Math.Max(1, ToMilliseconds(wait));
        if (cancellationToken.CanBeCanceled)
            cancellationToken.WaitHandle.WaitOne(milliseconds);
        else
            Thread.Sleep(milliseconds);
    }

    private static int ToMilliseconds(TimeSpan value)
    {
        if (value <= TimeSpan.Zero) return 0;
        double milliseconds = Math.Ceiling(value.TotalMilliseconds);
        return milliseconds >= Int32.MaxValue ? Int32.MaxValue : (int)milliseconds;
    }

    private static string SafeAudit(S3T03OutputLeaseSet outputLeases)
    {
        try { return outputLeases.AuditFileLinkCounts(); }
        catch (Exception error) { return "OUTPUT_LINK_AUDIT_EXCEPTION:" + FormatError(error); }
    }

    private static bool IsPassingAudit(string audit)
    {
        return !String.IsNullOrEmpty(audit) && audit.StartsWith("PASS;", StringComparison.Ordinal);
    }

    private static string EncodeField(string value)
    {
        return Convert.ToBase64String(Encoding.UTF8.GetBytes(value ?? ""));
    }

    private static string FormatLength(long? length)
    {
        return length.HasValue ? length.Value.ToString(System.Globalization.CultureInfo.InvariantCulture) : "MISSING";
    }

    private static string FormatError(Exception error)
    {
        return (error.GetType().Name + ":" + error.Message).Replace("\r", "_").Replace("\n", "_").Replace(";", "_");
    }

    private static string AppendDetail(string current, string next)
    {
        if (String.IsNullOrEmpty(next)) return current ?? "";
        if (String.IsNullOrEmpty(current)) return next;
        return current + ";" + next;
    }

    private sealed class S3T03ProgressSnapshot
    {
        public readonly string Stage;
        public readonly string Result;
        public readonly bool StatusPresent;
        public readonly string ProgressKey;

        public S3T03ProgressSnapshot(string stage, string result, bool statusPresent, string progressKey)
        {
            Stage = stage;
            Result = result;
            StatusPresent = statusPresent;
            ProgressKey = progressKey;
        }
    }
}
