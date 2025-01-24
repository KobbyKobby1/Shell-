import os
import subprocess
import sys
from typing import Optional
BUILTINS = ["echo", "exit", "type", "pwd", "cd"]
def present_on_path(command) -> Optional[str]:
    path = os.environ.get("PATH")
    if path:
        dirs = path.split(":")
        for dir in dirs:
            full_path = os.path.join(dir, command)
            if os.path.isfile(full_path):
                return full_path
    return None
def handle_type(args) -> tuple[str, str]:
    if args[0] in BUILTINS:
        return (f"{args[0]} is a shell builtin", "")
    else:
        full_path = present_on_path(args[0])
        if full_path:
            return (f"{args[0]} is {full_path}", "")
    return ("", f"{args[0]}: not found")
def normalise_args(user_input) -> list[str]:
    res = []
    arg = ""
    i = 0
    while i < len(user_input):
        if user_input[i] == "'":
            i += 1
            start = i
            while i < len(user_input) and user_input[i] != "'":
                i += 1
            arg += user_input[start:i]
            i += 1
        elif user_input[i] == '"':
            i += 1
            while i < len(user_input):
                if user_input[i] == "\\":
                    if user_input[i + 1] in ["\\", "$", '"', "\n"]:
                        arg += user_input[i + 1]
                        i += 2
                    else:
                        arg += user_input[i]
                        i += 1
                elif user_input[i] == '"':
                    break
                else:
                    arg += user_input[i]
                    i += 1
            i += 1
        elif user_input[i] == " ":
            if arg:
                res.append(arg)
            arg = ""
            i += 1
        elif user_input[i] == "\\":
            i += 1
        else:
            while i < len(user_input) and user_input[i] != " ":
                if user_input[i] == "\\":
                    arg += user_input[i + 1]
                    i += 2
                else:
                    arg += user_input[i]
                    i += 1
    if arg:
        res.append(arg)
    return res
def cd_cmd(args, cur_dir) -> tuple[str, str]:
    path = args[0]
    new_dir = cur_dir
    if path.startswith("/"):
        new_dir = path
    else:
        for p in filter(None, path.split("/")):
            if p == "..":
                new_dir = new_dir.rsplit("/", 1)[0]
            elif p == "~":
                new_dir = os.environ["HOME"]
            elif p != ".":
                new_dir += f"/{p}"
    if not os.path.exists(new_dir):
        return (cur_dir, f"cd: {path}: No such file or directory")
    else:
        return (new_dir, "")
def main():
    cur_dir = os.getcwd()
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        user_input = input()
        args = normalise_args(user_input)
        cmd, args = args[0], args[1:]
        # Handle redirections
        redir = None
        redir_file = None
        if len(args) >= 3 and args[-2] in ["1>", ">", "2>"]:
            redir = args[-2]
            redir_file = args[-1]
            args = args[:-2]
        out, err = "", ""
        if cmd == "exit":
            if args[0] == "0":
                break
        elif cmd == "echo":
            out = " ".join(args)
        elif cmd == "type":
            out, err = handle_type(args)
        elif cmd == "pwd":
            out = cur_dir
        elif cmd == "cd":
            cur_dir, err = cd_cmd(args, cur_dir)
        else:
            if present_on_path(cmd):
                res = subprocess.run(
                    args=([cmd] + args),
                    capture_output=True,
                    text=True,
                )
                out = res.stdout.rstrip()
                err = res.stderr.rstrip()
            else:
                err = f"{user_input}: command not found"
        # Write output and errors
        if redir:
            assert redir_file
            if redir == "2>":
                with open(redir_file, "w") as f:
                    f.write(err)
                err = ""
            elif redir in ["1>", ">"]:
                with open(redir_file, "w") as f:
                    f.write(out)
                out = ""
        if err:
            print(err, file=sys.stderr)
        if out:
            print(out, file=sys.stdout)
if __name__ == "__main__":
    main()