import sys

def main():
    while True:
        # Prompt for input
        sys.stdout.write("$ ")
        sys.stdout.flush()
        
        try:
            # Read user input
            command = input().strip()
            
            # Exit condition
            if command.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            
            # Evaluate and print result
            if command:
                print(f"{command}: command not found")
        
        except EOFError:
            # Handle EOF (Ctrl+D or similar)
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
