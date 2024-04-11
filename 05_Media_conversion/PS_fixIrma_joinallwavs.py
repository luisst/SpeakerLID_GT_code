import os
import wave

def combine_wavs(input_folder, output_file):
    # Initialize variables for the output WAV file
    output_wave = None
    output_frames = []

    # Iterate through all WAV files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.wav'):
            input_path = os.path.join(input_folder, filename)
            with wave.open(input_path, 'rb') as input_wave:
                # Read parameters of the input WAV file
                nchannels, sampwidth, framerate, nframes, comptype, compname = input_wave.getparams()

                # Initialize the output WAV file if it hasn't been initialized yet
                if output_wave is None:
                    output_wave = wave.open(output_file, 'wb')
                    output_wave.setparams((nchannels, sampwidth, framerate, 0, 'NONE', 'not compressed'))

                # Read frames from the input WAV file and append them to the output frames
                frames = input_wave.readframes(nframes)
                output_frames.append(frames)

    # Combine all frames and write to the output WAV file
    output_frames = b''.join(output_frames)
    output_wave.writeframes(output_frames)

    # Close the output WAV file
    output_wave.close()

# Example usage:
input_folder = r'C:\Users\luis2\Dropbox\DATASETS_AUDIO\AOLME_SD_Collection\TestSet\02_Selected_clips\G-C1L1P-Apr27-E-Irma_q2_03-08\sync_audios_test\all_audios'
output_file = "combined_output.wav"
combine_wavs(input_folder, output_file)
