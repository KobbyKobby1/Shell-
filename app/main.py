import sys
import os
import subprocess

def main():
    # Define the list of built-in commands
    builtins = {"echo", "exit", "type", "pwd", "cd"}

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

            # Handle `pwd` command
            elif command == "pwd":
                print(os.getcwd())

            # Handle `cd` command (absolute and relative paths)
            elif command.startswith("cd "):
                # Extract the target directory
                _, target_dir = command.split(maxsplit=1)
                try:
                    os.chdir(target_dir)  # Handles both absolute and relative paths
                except FileNotFoundError:
                    print(f"cd: {target_dir}: No such file or directory")
                except PermissionError:
                    print(f"cd: {target_dir}: Permission denied")

            # Handle `echo` command
            elif command.startswith("echo "):
                print(command[5:])

            # Handle running external programs
            elif command:
                # Split the command and arguments
                args = command.split()
                program = args[0]
                program_args = args[1:]

                # Search for the program in PATH
                found = False
                for directory in os.environ["PATH"].split(":"):
                    program_path = os.path.join(directory, program)
                    if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
                        found = True
                        try:
                            # Run the program with its arguments
                            result = subprocess.run([program_path] + program_args, capture_output=True, text=True)
                            # Print the program's output
                            print(result.stdout.strip())
                        except Exception as e:
                            print(f"Error running {program}: {e}")
                        break
                
                if not found:
                    print(f"{program}: not found")

        except EOFError:
            # Handle Ctrl+D (EOF)
            sys.exit(0)

if __name__ == "__main__":
    main()
