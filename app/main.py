import sys

def main():
    while True:
        # Display the shell prompt
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            # Read user input
            command = input().strip()

            # Handle `exit` command
            if command.startswith("exit"):
                parts = command.split()
                if len(parts) > 1 and parts[1].isdigit():
                    exit_code = int(parts[1])
                else:
                    exit_code = 0
                sys.exit(exit_code)

            # Handle `echo` command
            elif command.startswith("echo "):
                # Extract and print the text after `echo`
                print(command[5:])

            # Handle invalid commands
            elif command:
                print(f"{command}: command not found")

        except EOFError:
            # Handle Ctrl+D (EOF)
            sys.exit(0)

if __name__ == "__main__":
    main()
