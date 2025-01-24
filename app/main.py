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

# Globals to track TAB behavior
tab_state = {
    "text": None,
    "matches": [],
    "tab_count": 0,
}


def input_completer(text, state):
    global tab_state

    # Reset tab state if the text changes
    if tab_state["text"] != text:
        tab_state["text"] = text
        tab_state["tab_count"] = 0

        # Find matches
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
        
        # Combine and sort matches alphabetically
        tab_state["matches"] = sorted(built_in_matches + path_matches)

    # Handle TAB presses
    matches = tab_state["matches"]
    if len(matches) == 1:
        # Auto-complete single match
        return matches[0] + " "
    elif len(matches) > 1:
        # Multiple matches: cycle through options on subsequent TAB presses
        if tab_state["tab_count"] == 0:
            # First TAB press: Ring the bell
            tab_state["tab_count"] += 1
            sys.stdout.write("\a")
            sys.stdout.flush()
        else:
            # Second TAB press: Display matches
            print("\n" + "  ".join(matches))
            print(f"$ {text}", end="", flush=True)
    return None




def find_cmd_in_env_path(cmd):
    path_str = os.environ.get("PATH", "")
    for path in path_str.split(":"):
        cmd_path = os.path.join(path, cmd)
        if os.path.isfile(cmd_path) and os.access(cmd_path, os.X_OK):
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
        try:
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
                args = args[:index] + args[index + 2:]
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
                args = args[:index] + args[index + 2:]
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
        except EOFError:
            print("\nExiting shell...")
            break


if __name__ == "__main__":
    main()
