import sys
import os
import subprocess
import shlex

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            # Read user input
            command = input().strip()
            if not command:
                continue

            # Parse the input into arguments
            args = []
            i = 0
            while i < len(command):
                if command[i] == "'":
                    # We are inside single quotes
                    i += 1  # Move past the opening quote
                    start = i
                    while i < len(command) and command[i] != "'":
                        i += 1
                    if i < len(command):
                        args.append(command[start:i])  # Add the content inside the quotes
                    i += 1  # Move past the closing quote
                elif command[i] == " ":
                    i += 1  # Skip spaces
                else:
                    # Otherwise it's a regular argument
                    start = i
                    while i < len(command) and command[i] not in (" ", "'"):
                        i += 1
                    args.append(command[start:i])  # Add the argument to the list

            # Now we have the args
            cmd = args[0]

            # Handle the `exit` command
            if cmd == "exit":
                exit_code = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
                sys.exit(exit_code)

            # Handle `echo` command
            elif cmd == "echo":
                # Handle literal preservation for single quotes
                output = []
                for arg in args[1:]:
                    output.append(arg)  # Add the argument directly, preserving it
                print(" ".join(output))

            # Handle `cat` command
            elif cmd == "cat":
                for file_path in args[1:]:
                    if file_path.startswith("'") and file_path.endswith("'"):
                        file_path = file_path[1:-1]  # Strip single quotes from file paths
                    try:
                        with open(file_path, "r") as f:
                            print(f.read().strip(), end=" ")
                    except FileNotFoundError:
                        print(f"{file_path}: No such file or directory")
                    except PermissionError:
                        print(f"{file_path}: Permission denied")
                print()

            # Handle external commands
            else:
                try:
                    result = subprocess.run(args, capture_output=True, text=True)
                    print(result.stdout.strip())
                except FileNotFoundError:
                    print(f"{cmd}: command not found")
                except Exception as e:
                    print(f"Error executing command: {e}")

        except EOFError:
            # Exit on EOF (Ctrl+D)
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
