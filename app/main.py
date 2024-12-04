import sys

def main():
    while True:
        # Display the shell prompt
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            # Read user input
            command = input().strip()

            # Handle the `exit` command
            if command == "exit":
                sys.exit(0)  # Exit with a 0 status code
            
            # Handle other commands
            if command:
                print(f"{command}: command not found")

        except EOFError:
            # Handle Ctrl+D (EOF)
            sys.exit(0)

if __name__ == "__main__":
    main()
