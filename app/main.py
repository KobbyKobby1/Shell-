import sys

def main():
    while True:
        # Prompt for input
        sys.stdout.write("$ ")
        sys.stdout.flush()

        try:
            # Read user input
            command = input().strip()

            # Handle the `exit` command
            if command == "exit":
                print("Exiting the shell. Goodbye!")
                break
            
            # Handle other commands
            if command:
                print(f"{command}: command not found")

        except EOFError:
            # Handle Ctrl+D (EOF)
            print("\nExiting the shell. Goodbye!")
            break

if __name__ == "__main__":
    main()
