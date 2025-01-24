import sys
import os
import subprocess
import shlex

def generate_prompt():
    sys.stdout.write("$ ")
    sys.stdout.flush()

def is_command_builtin(command):
    return command in builtins

def autocomplete(partial_command):
    # Autocomplete for builtin commands
    builtins_matching = [cmd for cmd in builtins if cmd.startswith(partial_command)]
    
    # If exactly one match, return the full command with a space
    if len(builtins_matching) == 1:
        return builtins_matching[0] + " "
    
    return partial_command

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
        
        # Custom input handling with tab completion
        current_input = ""
        while True:
            char = sys.stdin.read(1)
            
            # Normal character input
            if char and char != '\t' and char != '\n':
                current_input += char
                sys.stdout.write(char)
                sys.stdout.flush()
            
            # Tab completion
            elif char == '\t':
                # Attempt to autocomplete the current input
                completed_input = autocomplete(current_input)
                
                # Clear current line and rewrite with completed input
                sys.stdout.write('\r$ ' + completed_input)
                sys.stdout.flush()
                current_input = completed_input
            
            # Enter pressed
            elif char == '\n':
                sys.stdout.write('\n')
                break
        
        # Tokenize the input
        try:
            command_args = shlex.split(current_input)
        except ValueError:
            # Handle invalid input (e.g., unclosed quotes)
            print("Invalid input")
            continue
        
        if not command_args:
            continue
        
        command = command_args[0]
        arguments = command_args[1:]
        
        # Rest of the existing command execution logic remains the same
        rdo = None
        outfile_path = None

        # Handle redirection operators
        if len(arguments) >= 2 and arguments[-2] in [">", "1>", ">>", "1>>", "2>", "2>>"]:
            rdo = arguments[-2]
            outfile_path = arguments[-1]
            arguments = arguments[:-2]

        out, err = "", ""

        # Check if the command is a builtin
        is_builtin = is_command_builtin(command)

        # Execute command
        match command:
            case "pwd":
                out = f"{os.getcwd()}"
            case "cd":
                if arguments:
                    out = change_directory(arguments[0])
                else:
                    out = "cd: missing argument"
            case "type":
                if arguments:
                    path = find_executable(arguments[0])
                    is_builtin = is_command_builtin(arguments[0])
                    if is_builtin:
                        out = f"{arguments[0]} is a shell builtin"
                    elif path is not None:
                        out = f"{arguments[0]} is {path}"
                    else:
                        out = f"{arguments[0]}: not found"
                else:
                    out = "type: missing argument"
            case "echo":
                out = " ".join(arguments)
            case "exit":
                sys.exit(0 if not arguments else int(arguments[0]))
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
                    err = f"{command}: command not found"

        # Handle redirection to file
        if rdo:
            if rdo == "2>":
                with open(outfile_path, "w") as file:
                    file.write(err + "\n" if err else "")
                err = ""
            elif rdo == "2>>":
                with open(outfile_path, "a") as file:
                    file.write(err + "\n" if err else "")
                err = ""
            elif rdo in [">", "1>"]:
                with open(outfile_path, "w") as file:
                    file.write(out + "\n" if out else "")
                out = ""
            elif rdo in [">>", "1>>"]:
                with open(outfile_path, "a") as file:
                    file.write(out + "\n" if out else "")
                out = ""

        # Print output or error
        if err:
            print(err)
        if out:
            print(out)

if __name__ == "__main__":
    main()