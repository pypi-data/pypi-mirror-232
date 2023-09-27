from akre.create_akre_model import create_model
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: akre <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "createmodel":
        create_model('apple')
    else:
        print("Invalid command. Use 'createmodel'.")
        sys.exit(1)