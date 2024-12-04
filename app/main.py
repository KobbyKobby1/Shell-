import sys

def main():
    while True:  # Allows the shell to repeatedly take commands
        sys.stdout.write("$ ")  # Display the shell prompt
        sys.stdout.flush()
        
        command = input()  # Get user input
        
        if command.strip():  # Check if input is not empty
            print(f"{command}: command not found")
        else:
            break  # Exit the loop if no command is entered

if __name__ == "__main__":
    main()
