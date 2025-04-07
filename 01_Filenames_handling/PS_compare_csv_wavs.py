from pathlib import Path

def find_unmatched_files(csv_folder: Path, wav_folder: Path):
    csv_files = {file.stem for file in csv_folder.glob("*.csv")}
    wav_files = {file.stem for file in wav_folder.glob("*.wav")}
    
    unmatched_csv = csv_files - wav_files
    unmatched_wav = wav_files - csv_files
    
    if unmatched_csv:
        print("CSV files without a matching WAV:")
        for file in sorted(unmatched_csv):
            print(file + ".csv")
    else:
        print("All CSV files have a matching WAV file.")
    
    if unmatched_wav:
        print("\nWAV files without a matching CSV:")
        for file in sorted(unmatched_wav):
            print(file + ".wav")
    else:
        print("All WAV files have a matching CSV file.")

if __name__ == "__main__":
    csv_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Commercial_Datasets\AMI_SD\GT_final")
    wav_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\Commercial_Datasets\AMI_SD\input_wavs")
    find_unmatched_files(csv_folder, wav_folder)
