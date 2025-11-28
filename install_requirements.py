"""
Helper script to install requirements with progress indication.
"""
import subprocess
import sys

def install_requirements():
    """Install packages from requirements.txt"""
    print("Installing required packages...")
    print("This may take several minutes, especially for sentence-transformers.")
    print()
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print()
        print("✓ Successfully installed all requirements!")
        return True
    except subprocess.CalledProcessError as e:
        print()
        print(f"✗ Error installing requirements: {e}")
        print("Please try manually: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = install_requirements()
    if success:
        print("All done!")
