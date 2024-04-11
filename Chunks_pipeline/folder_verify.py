import sys
from pathlib import Path

stg2_chunks_wavs_path = Path(sys.argv[1])

if stg2_chunks_wavs_path.exists() and any(stg2_chunks_wavs_path.iterdir()):
    response = input(f"The folder {stg2_chunks_wavs_path} already exists and contains files. Do you want to overwrite them? (y/n): ")

    if response.lower() == "y":
        for item in stg2_chunks_wavs_path.glob('*'):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()
    else:
        print("Left the folder untouched.")


stg2_chunks_wavs_path.mkdir(parents=True, exist_ok=True)