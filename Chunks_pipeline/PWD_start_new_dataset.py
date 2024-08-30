import sys
from pathlib import Path

def create_directories(dir_name):
    # Create the main directory
    main_dir = Path.cwd() / dir_name
    main_dir.mkdir(exist_ok=True)

    # Create the subdirectories
    (main_dir / 'input_wavs').mkdir(exist_ok=True)
    (main_dir / 'input_mp4').mkdir(exist_ok=True)
    (main_dir / 'GT_final').mkdir(exist_ok=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python script.py ")
        sys.exit(1)

    create_directories(sys.argv[1])