import sys
import os
import subprocess
import shlex

def find_executable(command):
    """Search for the command in directories specified by PATH."""
    path_dirs = os.getenv("PATH", "").split(":")  # Split PATH into directories
    for directory in path_dirs:
        executable_path = os.path.join(directory, command)
        if os.path.isfile(executable_path) and os.access(executable_path, os.X_OK):
            return executable_path  # Return the first matching executable
    return None

def parse_command(input_command):
    """
    Parse the command string, handling both single and double quotes.
    We preserve backslashes within single quotes.
    """
    result = []  # List to hold parsed arguments
    current_arg = []  # List to build the current argument
    in_single_quotes = False  # Flag for single-quoted sections
    escape_next = False  # Flag for backslash escaping

    i = 0
    while i < len(input_command):
        char = input_command[i]

        if in_single_quotes:
            # Inside single quotes, treat everything literally, including backslashes
            if char == "'":
                in_single_quotes = False  # Exit single-quote mode
            else:
                current_arg.append(char)
        elif escape_next:
            # Handle escaped characters outside quotes
            current_arg.append(char)
            escape_next = False
        elif char == "\\":
            escape_next = True  # Start escaping the next character
        elif char == "'":
            in_single_quotes = True  # Enter single-quote mode
        elif char == '"':
            # Inside double quotes, preserve everything literally (handled by shlex)
            current_arg.append(char)
        elif char.isspace():
            # End of an argument
            if current_arg:
                result.append("".join(current_arg))
                current_arg = []
        else:
            current_arg.append(char)

        i += 1

    # Add the last argument if any
    if current_arg:
        result.append("".join(current_arg))

    return result

def main():
    # Define a set of shell builtin commands
    builtins = {"echo", "exit", "type", "pwd", "cd"}

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            # Read user input
            input_command = input().strip()
            if not input_command:
                continue

            # Parse the input command
            parts = parse_command(input_command)

            if not parts:
                continue

            if parts[0] == "exit":
                exit_code = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                sys.exit(exit_code)

            elif parts[0] == "echo":
                # Handle echo command
                sys.stdout.write(f"{' '.join(parts[1:])}\n")
                continue
            elif parts[0] == "cat":
                # Run the cat command
                try:
                    result = subprocess.run(
                        parts,  # Use the parsed list directly
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    sys.stdout.write(result.stdout)
                    sys.stdout.write(result.stderr)
                except subprocess.CalledProcessError as e:
                    sys.stdout.write(e.stderr)
                continue
            elif parts[0] == "type":
                if len(parts) == 2:
                    queried_command = parts[1]
                    if queried_command in builtins:
                        sys.stdout.write(f"{queried_command} is a shell builtin\n")
                    else:
                        executable_path = find_executable(queried_command)
                        if executable_path:
                            sys.stdout.write(
                                f"{queried_command} is {executable_path}\n"
                            )
                        else:
                            sys.stdout.write(f"{queried_command}: not found\n")
                else:
                    sys.stdout.write("type: usage: type <command>\n")
                continue
            elif parts[0] == "pwd":
                # Print the current working directory
                sys.stdout.write(f"{os.getcwd()}\n")
                continue
            elif parts[0] == "cd":
                # Handle changing directory
                if len(parts) == 2:  # Expect exactly one argument
                    target_dir = parts[1]
                    # Handle the ~ character
                    if target_dir.startswith("~"):
                        home_dir = os.getenv("HOME", "")
                        if home_dir:
                            # Replace ~ with the home directory
                            target_dir = os.path.join(home_dir, target_dir[1:])
                        else:
                            sys.stdout.write(
                                "cd: HOME environment variable is not set\n"
                            )
                            continue
                    try:
                        os.chdir(target_dir)  # Attempt to change the directory
                    except FileNotFoundError:
                        sys.stdout.write(
                            f"cd: {target_dir}: No such file or directory\n"
                        )
                    except NotADirectoryError:
                        sys.stdout.write(f"cd: {target_dir}: Not a directory\n")
                    except Exception as e:
                        sys.stdout.write(f"cd: {target_dir}: {str(e)}\n")
                else:
                    sys.stdout.write("cd: usage: cd <directory>\n")
                continue

            # Handle external commands
            executable_path = find_executable(parts[0])
            if executable_path:
                try:
                    # Run the external program and print its output
                    result = subprocess.run(
                        [executable_path] + parts[1:],
                        check=True,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    sys.stdout.write(result.stdout)
                    sys.stdout.write(result.stderr)
                except subprocess.CalledProcessError as e:
                    sys.stdout.write(e.stderr)
                continue

            # Command not found
            sys.stdout.write(f"{parts[0]}: command not found\n")
        except EOFError:
            # Handle EOF (Ctrl+D)
            break
    sys.stdout.write("\n")  # Print a newline for a clean exit

if __name__ == "__main__":
    main()
