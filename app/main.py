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

            # Check for output redirection operator
            if ">" in args:
                redirect_index = args.index(">")
            elif "1>" in args:
                redirect_index = args.index("1>")
            else:
                redirect_index = None

            # Handle redirection if the operator is present
            if redirect_index is not None:
                output_file = args[redirect_index + 1]
                command_args = args[:redirect_index]
                redirect_mode = "w"  # Overwrite file content
                output_file = os.path.expanduser(output_file)

                with open(output_file, redirect_mode) as f:
                    if command_args:
                        execute_command(command_args, builtins, output=f)
                    else:
                        print("Syntax error: Missing command before redirection", file=sys.stderr)
                continue

            # Execute the command without redirection
            execute_command(args, builtins)

        except EOFError:
            sys.exit(0)
        except IndexError:
            print("Syntax error: Missing file after redirection", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def execute_command(args, builtins, output=sys.stdout):
    cmd = args[0]

    # Handle `exit` command
    if cmd == "exit":
        exit_code = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
        sys.exit(exit_code)

    # Handle `type` command
    elif cmd == "type":
        if len(args) < 2:
            print("type: missing operand", file=output)
        else:
            cmd_to_check = args[1]
            if cmd_to_check in builtins:
                print(f"{cmd_to_check} is a shell builtin", file=output)
            else:
                for directory in os.environ["PATH"].split(":"):
                    command_path = os.path.join(directory, cmd_to_check)
                    if os.path.isfile(command_path) and os.access(command_path, os.X_OK):
                        print(f"{cmd_to_check} is {command_path}", file=output)
                        break
                else:
                    print(f"{cmd_to_check}: not found", file=output)

    # Handle `pwd` command
    elif cmd == "pwd":
        print(os.getcwd(), file=output)

    # Handle `cd` command
    elif cmd == "cd":
        target_dir = args[1] if len(args) > 1 else os.environ.get("HOME", "/")
        target_dir = os.path.expanduser(target_dir)

        try:
            os.chdir(target_dir)
        except FileNotFoundError:
            print(f"cd: {target_dir}: No such file or directory", file=output)
        except PermissionError:
            print(f"cd: {target_dir}: Permission denied", file=output)

    # Handle `echo` command
    elif cmd == "echo":
        print(" ".join(args[1:]), file=output)

    # Handle `cat` command
    elif cmd == "cat":
        for file_path in args[1:]:
            try:
                with open(os.path.expanduser(file_path), "r") as f:
                    print(f.read(), end="", file=output)
            except FileNotFoundError:
                print(f"{file_path}: No such file or directory", file=sys.stderr)
            except PermissionError:
                print(f"{file_path}: Permission denied", file=sys.stderr)

    # Handle external commands
    else:
        for directory in os.environ["PATH"].split(":"):
            program_path = os.path.join(directory, cmd)
            if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
                try:
                    subprocess.run([program_path] + args[1:], stdout=output, stderr=sys.stderr, text=True)
                except Exception as e:
                    print(f"Error running {cmd}: {e}", file=sys.stderr)
                break
        else:
            print(f"{cmd}: not found", file=sys.stderr)


if __name__ == "__main__":
    main()
