import sys
import os
import subprocess
import shlex  # For parsing quoted and escaped strings

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

            # Parse input with shlex (handling quotes and escapes)
            args = shlex.split(command, posix=True)

            if not args:
                continue  # Skip empty commands

            cmd = args[0]

            # Handle `exit` command
            if cmd == "exit":
                if len(args) > 1 and args[1].isdigit():
                    exit_code = int(args[1])
                else:
                    exit_code = 0
                sys.exit(exit_code)

            # Handle `type` command
            elif cmd == "type":
                if len(args) < 2:
                    print("type: missing operand")
                    continue

                cmd_to_check = args[1]
                if cmd_to_check in builtins:
                    print(f"{cmd_to_check} is a shell builtin")
                else:
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
            elif cmd == "pwd":
                print(os.getcwd())

            # Handle `cd` command (absolute, relative paths, and `~`)
            elif cmd == "cd":
                if len(args) < 2:
                    target_dir = os.environ.get("HOME", "/")  # Default to home directory
                else:
                    target_dir = args[1]

                if target_dir == "~":
                    target_dir = os.environ.get("HOME", "/")

                try:
                    os.chdir(target_dir)
                except FileNotFoundError:
                    print(f"cd: {target_dir}: No such file or directory")
                except PermissionError:
                    print(f"cd: {target_dir}: Permission denied")

            # Handle `echo` command with backslashes and single quotes
            elif cmd == "echo":
                result = []
                for arg in args[1:]:
                    if arg.startswith("'") and arg.endswith("'"):
                        result.append(arg[1:-1].replace("\\'", "'"))  # Handle escaped single quotes
                    else:
                        result.append(arg)
                print("".join(result))  # Concatenate without spaces

            # Handle `cat` command with backslashes in file paths
            elif cmd == "cat":
                contents = []
                for file_path in args[1:]:
                    try:
                        if file_path.startswith("'") and file_path.endswith("'"):
                            file_path = file_path[1:-1].replace("\\'", "'")  # Handle escaped single quotes
                        with open(file_path, "r") as f:
                            contents.append(f.read().strip())  # Read content and strip whitespace
                    except FileNotFoundError:
                        print(f"{file_path}: No such file or directory")
                    except PermissionError:
                        print(f"{file_path}: Permission denied")
                
                # Print all contents without additional spaces
                print("".join(contents))

            # Handle running external programs
            else:
                found = False
                for directory in os.environ["PATH"].split(":"):
                    program_path = os.path.join(directory, cmd)
                    if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
                        found = True
                        try:
                            result = subprocess.run([program_path] + args[1:], capture_output=True, text=True)
                            print(result.stdout.strip())
                        except Exception as e:
                            print(f"Error running {cmd}: {e}")
                        break
                
                if not found:
                    print(f"{cmd}: not found")

        except EOFError:
            sys.exit(0)

if __name__ == "__main__":
    main()