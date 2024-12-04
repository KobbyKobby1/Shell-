import sys

def main():
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        try:
            command = input().strip()

            # Handle `exit` with an optional exit code
            if command.startswith("exit"):
                parts = command.split()
                if len(parts) > 1 and parts[1].isdigit():
                    exit_code = int(parts[1])
                else:
                    exit_code = 0  # Default to exit code 0
                print(f"Exiting the shell with code {exit_code}. Goodbye!")
                sys.exit(exit_code)

            if command:
                print(f"{command}: command not found")
        
        except EOFError:
            print("\nExiting the shell. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main()
