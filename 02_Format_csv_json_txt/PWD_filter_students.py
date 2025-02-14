from pathlib import Path
import pandas as pd

def get_speaker_selection(df: pd.DataFrame, filename: str) -> int:
    """Show preview and get speaker selection for a single file."""
    print(f"\nProcessing file: {filename}")
    print("\nFirst 15 rows of the dataset:")
    print(df.head(15))

    # Get unique speaker IDs from the first 15 rows
    available_speakers = df.iloc[:15, 0].unique()
    
    # Get user input
    while True:
        try:
            print("\nAvailable speaker IDs from the first 15 rows:")
            print(available_speakers)
            selected_speaker = int(input("\nPlease select a speaker ID from the above list: "))
            
            if selected_speaker in df[0].values:
                return selected_speaker
            else:
                print("Error: Selected speaker ID not found in the dataset.")
        except ValueError:
            print("Error: Please enter a valid integer.")

def process_speaker_data(input_file: Path) -> bool:
    """Process a single CSV file for the selected speaker."""
    try:
        # Read the tab-separated CSV file without header
        df = pd.read_csv(input_file, sep='\t', header=None)
        
        # Get speaker selection for this file
        selected_speaker = get_speaker_selection(df, input_file.name)
        
        # Filter rows for selected speaker
        filtered_df = df[df[0] == selected_speaker]

        # Create output directory if it doesn't exist
        output_dir = Path("filtered_output")
        output_dir.mkdir(exist_ok=True)

        # Generate output filename
        output_file = output_dir / f"{input_file.stem}_student{input_file.suffix}"

        # Save filtered data without header
        filtered_df.to_csv(output_file, sep='\t', index=False, header=False)
        print(f"Saved {len(filtered_df)} rows to {output_file}")
        
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return False

def process_folder(input_folder: Path):
    """Process all CSV files in the specified folder."""
    # Get all CSV files in the folder
    csv_files = list(input_folder.glob("*.txt"))
    
    if not csv_files:
        print(f"No CSV files found in {input_folder}")
        return

    print(f"\nFound {len(csv_files)} CSV files to process")
    
    # Process all files
    successful_count = 0
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"\n--- Processing file {i} of {len(csv_files)} ---")
        if process_speaker_data(csv_file):
            successful_count += 1

            print(f'----------------------\n')
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed {successful_count} out of {len(csv_files)} files")
    print(f"Filtered files have been saved in the 'filtered_output' directory")


if __name__ == "__main__":
    # Specify your input folder path here
    input_folder = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\interviews_wavs\final_csv_v3.3")  # Replace with your folder path
    process_folder(input_folder)