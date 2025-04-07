from pathlib import Path
import pandas as pd

def merge_csv_files(input_folder: str, output_folder: str):
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # Group files by base name
    file_groups = {}
    for file in input_path.glob("*.csv"):
        if file.is_file():
            parts = file.stem.rsplit(".", 1)  # Split base name and letter
            base_name = parts[0] if len(parts) > 1 and len(parts[1]) == 1 else file.stem
            file_groups.setdefault(base_name, []).append(file)

    # Merge and save files
    for base_name, files in file_groups.items():
        if len(files) > 1:  # Only merge if multiple files exist
            dfs = [pd.read_csv(f, sep="\t", header=0, index_col=None) for f in files]
            merged_df = pd.concat(dfs, ignore_index=True)
            merged_df.to_csv(output_path / f"{base_name}.csv", index=False)
            print(f"Merged {len(files)} files into {base_name}.csv")

if __name__ == "__main__":
    input_folder = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\ICSI\input_segs_words\my_output_separated"
    output_folder = r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\ICSI\input_segs_words\my_output_separated\merged_csv_output"
    merge_csv_files(input_folder, output_folder)
