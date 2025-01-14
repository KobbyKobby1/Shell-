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
            redirect_output_file = None
            redirect_error_file = None
            redirect_index = -1
            redirect_error_index = -1
            
            args = shlex.split(command, posix=True)

            # Check for output redirection (1> or >)
            for i, arg in enumerate(args):
                if arg in ['>', '1>']:
                    redirect_index = i
                    if i + 1 < len(args):
                        redirect_output_file = args[i + 1]
                    break

            # Check for error redirection (2>)
            for i, arg in enumerate(args):
                if arg == '2>':
                    redirect_error_index = i
                    if i + 1 < len(args):
                        redirect_error_file = args[i + 1]
                    break

            if redirect_index != -1:
                args = args[:redirect_index]
            if redirect_error_index != -1:
                args = args[:redirect_error_index]

            if not args:
                continue

            cmd = args[0]

            # Function to handle output redirection
            def execute_with_redirect(output, file, error=False):
                if file:
                    try:
                        os.makedirs(os.path.dirname(file), exist_ok=True)  # Ensure parent dirs exist
                        with open(file, 'w') as f:
                            f.write(str(output))
                            if not str(output).endswith('\n'):
                                f.write('\n')
                    except IOError as e:
                        print(f"Error writing to {file}: {e}", file=sys.stderr)
                elif error:
                    print(output, file=sys.stderr)
                else:
                    print(output)

            if cmd == "exit":
                exit_code = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
                sys.exit(exit_code)

            elif cmd == "type":
                if len(args) < 2:
                    execute_with_redirect("type: missing operand", redirect_error_file, error=True)
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
                execute_with_redirect(output, redirect_error_file)

            elif cmd == "pwd":
                execute_with_redirect(os.getcwd(), redirect_output_file)

            elif cmd == "cd":
                target_dir = args[1] if len(args) > 1 else os.environ.get("HOME", "/")
                if target_dir == "~":
                    target_dir = os.environ.get("HOME", "/")
                try:
                    os.chdir(target_dir)
                except FileNotFoundError:
                    execute_with_redirect(f"cd: {target_dir}: No such file or directory", redirect_error_file, error=True)
                except PermissionError:
                    execute_with_redirect(f"cd: {target_dir}: Permission denied", redirect_error_file, error=True)

            elif cmd == "echo":
                output = " ".join(args[1:])
                execute_with_redirect(output, redirect_output_file)

            elif cmd == "cat":
                output_parts = []
                
                for file_path in args[1:]:
                    try:
                        with open(file_path, "r") as f:
                            content = f.read().rstrip('\n')
                            output_parts.append(content)
                    except FileNotFoundError:
                        execute_with_redirect(f"cat: {file_path}: No such file or directory", redirect_error_file, error=True)
                    except PermissionError:
                        execute_with_redirect(f"cat: {file_path}: Permission denied", redirect_error_file, error=True)
                
                if output_parts:
                    output = "".join(output_parts)
                    execute_with_redirect(output, redirect_output_file)

            else:
                try:
                    result = subprocess.run(
                        args,
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        execute_with_redirect(result.stdout.rstrip('\n'), redirect_output_file)
                    if result.stderr:
                        execute_with_redirect(result.stderr.rstrip('\n'), redirect_error_file, error=True)
                except FileNotFoundError:
                    execute_with_redirect(f"{cmd}: not found", redirect_error_file, error=True)
                except Exception as e:
                    execute_with_redirect(f"Error running {cmd}: {e}", redirect_error_file, error=True)

        except EOFError:
            sys.exit(0)

if __name__ == "__main__":
    main()