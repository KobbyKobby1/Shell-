import sys
import os
import shlex
import subprocess
import readline
cmd_handlers = {
    "echo": lambda stdout, stderr, *args: stdout.write(" ".join(args) + "\n"),
    "pwd": lambda stdout, stderr, *args: stdout.write(os.getcwd() + "\n"),
    "cd": lambda stdout, stderr, *args: handle_cd(stdout, stderr, *args),
    "type": lambda stdout, stderr, *args: handle_type(stdout, stderr, *args),
    "exit": lambda stdout, stderr, *args: exit(int(args[0])) if args else exit(0),
}
def input_completer(text, state):
    options = [cmd for cmd in cmd_handlers.keys() if cmd.startswith(text)]
    if state < len(options):
        return options[state] + " "
    else:
        return None
def find_cmd_in_env_path(cmd):
    path_str = os.environ.get("PATH")
    path_list = path_str.split(":")
    for path in path_list:
        cmd_path = f"{path}/{cmd}"
        if os.path.isfile(cmd_path):
            return cmd_path
    return None
def execute_cmd(cmd, stdout, stderr, *args):
    if cmd in cmd_handlers.keys():
        cmd_handlers[cmd](stdout, stderr, *args)
    else:
        if find_cmd_in_env_path(cmd):
            subprocess.run([cmd, *args], stdout=stdout, stderr=stderr)
        else:
            sys.stdout.write(f"{cmd}: command not found\n")
            sys.stdout.flush()
def handle_type(stdout, stderr, *args):
    cmd = args[0]
    if cmd in cmd_handlers.keys():
        stdout.write(f"{cmd} is a shell builtin\n")
    else:
        if cmd_path := find_cmd_in_env_path(cmd):
            stdout.write(f"{cmd} is {cmd_path}\n")
        else:
            stdout.write(f"{cmd}: not found\n")
def handle_cd(stdout, stderr, *args):
    if not args:
        return
    to_path = args[0]
    if os.path.isdir(to_path):
        os.chdir(to_path)
    elif to_path.strip() == "~":
        os.chdir(os.environ.get("HOME"))
    else:
        stderr.write(f"cd: {to_path}: No such file or directory\n")
def main():
    readline.set_completer(input_completer)
    readline.parse_and_bind("tab: complete")
    while True:
        input_str = input("$ ")
        cmd, *args = shlex.split(input_str)
        stdout_file = None
        if ">" in args or "1>" in args or ">>" in args or "1>>" in args:
            index = None
            mode = "w"
            if ">" in args:
                index = args.index(">")
            elif ">>" in args:
                index = args.index(">>")
                mode = "a"
            elif "1>" in args:
                index = args.index("1>")
            elif "1>>" in args:
                index = args.index("1>>")
                mode = "a"
            stdout_file = args[index + 1]
            args = args[:index] + args[index + 2 :]
            stdout = open(stdout_file, mode)
        else:
            stdout = sys.stdout
        stderr_file = None
        if "2>" in args or "2>>" in args:
            index = None
            mode = "w"
            if "2>" in args:
                index = args.index("2>")
            elif "2>>" in args:
                index = args.index("2>>")
                mode = "a"
            stderr_file = args[index + 1]
            args = args[:index] + args[index + 2 :]
            stderr = open(stderr_file, mode)
        else:
            stderr = sys.stderr
        try:
            execute_cmd(cmd, stdout, stderr, *args)
        finally:
            stdout.flush()
            stderr.flush()
            if stdout_file:
                stdout.close()
            if stderr_file:
                stderr.close()



def input_completer(text, state):
    # Combine built-ins and executables in PATH
    built_in_matches = [cmd for cmd in cmd_handlers.keys() if cmd.startswith(text)]
    path_matches = []
    path_str = os.environ.get("PATH", "")
    for path in path_str.split(":"):
        try:
            path_matches.extend(
                cmd for cmd in os.listdir(path)
                if cmd.startswith(text) and os.access(os.path.join(path, cmd), os.X_OK)
            )
        except FileNotFoundError:
            continue

    all_matches = built_in_matches + path_matches
    if state < len(all_matches):
        return all_matches[state] + " "
    else:
        return None

if __name__ == "__main__":
    main()