import sys
import os
import subprocess
import shlex
def generate_prompt():
    sys.stdout.write("$ ")
    sys.stdout.flush()
def is_command_builtin(command):
    if command in builtins:
        return True
    return False
def change_directory(path):
    home = os.environ.get("HOME", "")
    if os.path.exists(path):
        os.chdir(path)
    elif path == "~":
        os.chdir(home)
    else:
        return f"{path}: No such file or directory"
def find_executable(command):
    path = os.environ.get("PATH", "")
    for directory in path.split(":"):
        file_path = os.path.join(directory, command)
        if os.path.exists(file_path):
            return file_path
    return None
builtins = ["exit", "echo", "type", "pwd", "cd"]
def main():
    while True:
        generate_prompt()
        command_args = shlex.split(input())
        command = command_args[0]
        arguments = command_args[1:]
        rdo = None
        outfile_path = None
        if len(arguments) >= 3 and arguments[-2] in [">", "1>", "2>"]:
            rdo = arguments[-2]
            outfile_path = arguments[-1]
            arguments = arguments[:-2]
        out, err = "", ""
        # Checks
        is_builtin = is_command_builtin(command)
        # Do something
        match (command):
            case "pwd":
                out = f"{os.getcwd()}"
            case "cd":
                out = change_directory(arguments[0])
            case "type":
                # Find find path of argument
                path = find_executable(arguments[0])
                # Check if argument provided is a builtin
                is_builtin = is_command_builtin(arguments[0])
                if is_builtin:
                    out = f"{arguments[0]} is a shell builtin"
                elif path is not None:
                    out = f"{arguments[0]} is {path}"
                else:
                    out = f"{arguments[0]}: not found"
            case "echo":
                out = " ".join(arguments)
            case "exit":
                if arguments[0] == "0":
                    sys.exit()
            case _:
                if find_executable(command):
                    result = subprocess.run(
                        [command] + arguments,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    out = result.stdout.rstrip()
                    err = result.stderr.rstrip()
                else:
                    out = f"{command}: command not found"
        if rdo:
            if rdo == "2>":
                with open(outfile_path, "w") as file:
                    file.write(err)
                err = ""
            elif rdo in [">", "1>"]:
                with open(outfile_path, "w") as file:
                    file.write(out)
                out = ""
        if err:
            print(err)
        if out:
            print(out)
        # if is_builtin:
        #     run_builtin_command(command, arguments)
        #     arguments.remove(arguments[rdo_index])
        #     subprocess_command = [command] + arguments
        #     print(subprocess_command)
        # result = subprocess.run(
        #     args=subprocess_command,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        #     text=True)
        # with open(outfile_path, 'w') as out_file:
    #                 out_file.write(result.stdout)
    # if result.stdout:
    #     print(result.stdout.strip("\n"))
    # if result.stderr:
    # print(result.stderr)
    # else:
if __name__ == "__main__":
    main()