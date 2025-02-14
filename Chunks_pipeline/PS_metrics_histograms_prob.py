from pathlib import Path
import pprint
import matplotlib.pyplot as plt


def plot_histogram(probabilities_dict):
    # Flatten the list of probabilities
    all_probabilities = [prob for sublist in probabilities_dict.values() for prob in sublist]
    
    # Plot the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(all_probabilities, bins=20, color='blue', alpha=0.7, edgecolor='black')
    plt.title('Histogram of Probabilities')
    plt.xlabel('Probability')
    plt.ylabel('Frequency')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


def extract_probabilities_from_subfolders(folder_path):
    # Dictionary to store subfolder names and their probabilities
    result = {}
    
    # Convert folder_path to a Path object
    folder = Path(folder_path)
    
    # Iterate through all subdirectories in the given folder
    for subfolder in folder.iterdir():
        if subfolder.is_dir():  # Process only directories
            probabilities = []
            
            # Iterate through files in the subfolder
            for file in subfolder.iterdir():
                if file.suffix == '.wav':  # Process only .wav files
                    try:
                        # Extract probability from the filename
                        probability = file.stem.rsplit('_', 1)[-1]  # Get the last part of the filename without extension
                        probabilities.append(float(probability))
                    except ValueError:
                        print(f"Skipping file with invalid probability format: {file.name}")
            
            # Add subfolder name and probabilities to the dictionary
            result[subfolder.name] = probabilities
    
    return result

# Example usage
root_ex = Path.home().joinpath('Dropbox','DATASETS_AUDIO', 'Proposal_runs','TestAO-Irmadb')

folder_output_folder = root_ex / Path('STG_3/STG3_EXP010-SHAS-DV-TDA/TDA_pred_output')

probabilities_dict = extract_probabilities_from_subfolders(folder_output_folder)
pprint.pprint(probabilities_dict)

# Plot the histogram
plot_histogram(probabilities_dict)