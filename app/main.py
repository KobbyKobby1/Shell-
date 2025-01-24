import sys
import os
import subprocess
import shlex

def generate_prompt():
    sys.stdout.write("$ ")
    sys.stdout.flush()

def is_command_builtin(command):
    return command in ["exit", "echo", "type", "pwd", "cd"]

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

def main():
    while True:
        generate_prompt()
        command_line = input()
        command_args = shlex.split(command_line)
        command = command_args[0]
        arguments = command_args[1:]
        
        # Handle redirect and append operators
        rdo = None
        outfile_path = None
        append_mode = False
        
        # Check for append or write redirect operators
        if len(arguments) >= 3 and arguments[-2] in [">", "1>", "2>", ">>", "1>>", "2>>"]:
            rdo = arguments[-2]
            outfile_path = arguments[-1]
            arguments = arguments[:-2]
            
            # Check if it's an append mode
            append_mode = rdo in [">>", "1>>", "2>>"]
        
        out, err = "", ""
        
        # Execute commands
        match (command):
            case "pwd":
                out = f"{os.getcwd()}"
            case "cd":
                out = change_directory(arguments[0] if arguments else "~")
            case "type":
                path = find_executable(arguments[0])
                if is_command_builtin(arguments[0]):
                    out = f"{arguments[0]} is a shell builtin"
                elif path is not None:
                    out = f"{arguments[0]} is {path}"
                else:
                    out = f"{arguments[0]}: not found"
            case "echo":
                out = " ".join(arguments)
            case "exit":
                if not arguments or arguments[0] == "0":
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
        
        # Handle redirection
        if rdo:
            mode = "a" if append_mode else "w"
            try:
                if rdo in ["2>>", "2>"]:
                    with open(outfile_path, mode) as file:
                        file.write(err)
                    err = ""
                elif rdo in [">", "1>", ">>", "1>>"]:
                    with open(outfile_path, mode) as file:
                        file.write(out)
                    out = ""
            except IOError as e:
                print(f"Error writing to file: {e}")
        
        # Print outputs
        if err:
            print(err, file=sys.stderr)
        if out:
            print(out)

if __name__ == "__main__":
    main()