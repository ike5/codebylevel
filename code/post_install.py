import subprocess
import sys


def install_completion():
    print("Your CLI supports shell completion to enhance your experience.")
    print("This script can add the necessary completion setup to your shell config.")
    confirm = input("Do you want to proceed with installing shell completion? [y/N]: ").strip().lower()

    if confirm != "y":
        print("Skipping shell completion installation.")
        return

    try:
        # Adjust 'cbl' to your CLI command name if different
        subprocess.check_call([sys.executable, "-m", "cbl", "completion", "--install", "--shell", "bash"])
        print("Shell completion installed successfully.")
        print("Please restart your terminal or source your shell config file to activate completion.")
    except Exception as e:
        print(f"Failed to install shell completion: {e}")


if __name__ == "__main__":
    install_completion()
