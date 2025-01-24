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

def list_executables(directory):
    executables = []
    # Iterate through all files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Skip files longer than 32 characters
            if len(file) > 32:
                continue
            file_path = os.path.join(root, file)
            # Check if the file is executable
            if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                executables.append(file)
    return executables

all_cmds = list(cmd_handlers.keys())
path_str = os.environ.get("PATH")
path_list = path_str.split(":")
for path in path_list:
    all_cmds.extend(list_executables(path))
all_cmds = list(set(all_cmds))

def input_completer(text, state):
    options = [cmd for cmd in all_cmds if cmd.startswith(text)]
    # Uncommented debug print statement
    # print(f"\n->text='{text}' state='{state}' options={options}\n")
    if state == 0 and len(options) == 1:
        return options[0] + " "
    if state < len(options):
        return options[state]
    else:
        sys.stdout.write("\a")  # Ring the bell for no further matches
        sys.stdout.flush()
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

if __name__ == "__main__":
    main()
