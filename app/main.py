import sys
import os
import subprocess
import shlex

def main():
    builtins = {"echo", "exit", "type", "pwd", "cd"}

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            command = input().strip()
            if not command:
                continue

            # Parse for redirection
            redirect_file = None
            redirect_index = -1
            
            # Split command but preserve spaces in quotes
            args = shlex.split(command, posix=True)
            
            # Look for redirection operators
            for i, arg in enumerate(args):
                if arg in ['>', '1>']:
                    redirect_index = i
                    if i + 1 < len(args):
                        redirect_file = args[i + 1]
                    break
            
            # Remove redirection parts from args if found
            if redirect_index != -1:
                args = args[:redirect_index]
            
            if not args:
                continue

            cmd = args[0]

            # Function to handle output redirection
            def execute_with_redirect(output):
                if redirect_file:
                    try:
                        with open(redirect_file, 'w') as f:
                            f.write(str(output))
                    except IOError as e:
                        print(f"Error writing to {redirect_file}: {e}", file=sys.stderr)
                else:
                    print(output)

            if cmd == "exit":
                exit_code = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
                sys.exit(exit_code)

            elif cmd == "type":
                if len(args) < 2:
                    print("type: missing operand", file=sys.stderr)
                    continue

                cmd_to_check = args[1]
                if cmd_to_check in builtins:
                    output = f"{cmd_to_check} is a shell builtin"
                else:
                    found = False
                    for directory in os.environ["PATH"].split(":"):
                        command_path = os.path.join(directory, cmd_to_check)
                        if os.path.isfile(command_path) and os.access(command_path, os.X_OK):
                            output = f"{cmd_to_check} is {command_path}"
                            found = True
                            break
                    if not found:
                        output = f"{cmd_to_check}: not found"
                execute_with_redirect(output)

            elif cmd == "pwd":
                execute_with_redirect(os.getcwd())

            elif cmd == "cd":
                target_dir = args[1] if len(args) > 1 else os.environ.get("HOME", "/")
                if target_dir == "~":
                    target_dir = os.environ.get("HOME", "/")
                try:
                    os.chdir(target_dir)
                except FileNotFoundError:
                    print(f"cd: {target_dir}: No such file or directory", file=sys.stderr)
                except PermissionError:
                    print(f"cd: {target_dir}: Permission denied", file=sys.stderr)

            elif cmd == "echo":
                output = " ".join(args[1:])
                execute_with_redirect(output)

            elif cmd == "cat":
                output = []
                error_occurred = False
                for file_path in args[1:]:
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                            output.append(content)
                    except FileNotFoundError:
                        print(f"cat: {file_path}: No such file or directory", file=sys.stderr)
                        error_occurred = True
                    except PermissionError:
                        print(f"cat: {file_path}: Permission denied", file=sys.stderr)
                        error_occurred = True
                
                if output and not error_occurred:
                    execute_with_redirect("".join(output))

            else:
                found = False
                for directory in os.environ["PATH"].split(":"):
                    program_path = os.path.join(directory, cmd)
                    if os.path.isfile(program_path) and os.access(program_path, os.X_OK):
                        found = True
                        try:
                            result = subprocess.run(
                                [program_path] + args[1:],
                                capture_output=True,
                                text=True
                            )
                            if result.stdout:
                                execute_with_redirect(result.stdout.strip())
                            if result.stderr:
                                print(result.stderr.strip(), file=sys.stderr)
                        except Exception as e:
                            print(f"Error running {cmd}: {e}", file=sys.stderr)
                        break
                
                if not found:
                    print(f"{cmd}: not found", file=sys.stderr)

        except EOFError:
            sys.exit(0)

if __name__ == "__main__":
    main()