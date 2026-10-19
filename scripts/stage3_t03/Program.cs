using System;

internal static class Program
{
    private static int Main(string[] args)
    {
        if (args != null && args.Length == 2 && args[0] == "--internal-race-target-check")
        {
            return T03InternalCommands.ValidateRaceTarget(args[1]);
        }

        if (args != null && args.Length == 4 && args[0] == "--internal-race-try")
        {
            return T03InternalCommands.TryCreateRaceTarget(args[1], args[2], args[3]);
        }

        if (args != null && args.Length == 2 && args[0] == "--internal-source-write-probe")
        {
            return T03InternalCommands.ProbePinnedSourceWrite(args[1]);
        }

        if (args == null || args.Length == 0 || args[0] == "help")
        {
            Console.Error.WriteLine("Stage3T03 helper command is required.");
            return 2;
        }

        if (args[0] == "version")
        {
            Console.WriteLine("STAGE3_T03_HELPER=1");
            return 0;
        }

        if (args[0] == "path-guard")
        {
            string[] commandArgs = new string[args.Length - 1];
            Array.Copy(args, 1, commandArgs, 0, commandArgs.Length);
            return PathGuardCommand.Run(commandArgs);
        }

        if (args[0] == "secure-io")
        {
            string[] commandArgs = new string[args.Length - 1];
            Array.Copy(args, 1, commandArgs, 0, commandArgs.Length);
            return SecureFileCommands.Run(commandArgs);
        }

        Console.Error.WriteLine("UNKNOWN_HELPER_COMMAND=" + args[0]);
        return 2;
    }
}
