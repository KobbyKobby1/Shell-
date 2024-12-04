import sys
import os

def main():
    # Define the list of built-in commands
    builtins = {"echo", "exit", "type"}

    while True:
        # Display the shell prompt
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            # Read user input
            command = input().strip()

            # Handle `exit` command
            if command.startswith("exit"):
                parts = command.split()
                if len(parts) > 1 and parts[1].isdigit():
                    exit_code = int(parts[1])
                else:
                    exit_code = 0
                sys.exit(exit_code)

            # Handle `type` command
            elif command.startswith("type "):
                # Extract the command to check
                _, cmd_to_check = command.split(maxsplit=1)
                if cmd_to_check in builtins:
                    print(f"{cmd_to_check} is a shell builtin")
                else:
                    # Search for the command in the directories listed in PATH
                    found = False
                    for directory in os.environ["PATH"].split(":"):
                        command_path = os.path.join(directory, cmd_to_check)
                        if os.path.isfile(command_path) and os.access(command_path, os.X_OK):
                            print(f"{cmd_to_check} is {command_path}")
                            found = True
                            break
                    
                    if not found:
                        print(f"{cmd_to_check}: not found")

            # Handle `echo` command
            elif command.startswith("echo "):
                print(command[5:])

            # Handle invalid commands
            elif command:
                print(f"{command}: command not found")

        except EOFError:
            # Handle Ctrl+D (EOF)
            sys.exit(0)

if __name__ == "__main__":
    main()
