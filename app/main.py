import sys


def main():
    # Uncomment this block to pass the first stage
    sys.stdout.write("$ ")
    sys.stdout.flush()

    # Wait for user input
    input()
    command = input()
    sys.stdout.write(f"{command}: command not found\n")


if __name__ == "__main__":
    main()
