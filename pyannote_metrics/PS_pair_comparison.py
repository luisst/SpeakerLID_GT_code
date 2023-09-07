import pandas as pd
from pyannote.core import Annotation, Segment
from pathlib import Path


file1_path = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection',
                             '02_Selected_clips','G-C2L1P-Feb16-B-Shelby_q2_03-05','csv_from_webapp',
                             'G-C2L1P-Feb16-B-Shelby_q2_03-05_001.csv')

file2_path = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection',
                             '02_Selected_clips','G-C2L1P-Feb16-B-Shelby_q2_03-05','final_csv',
                             'G-C2L1P-Feb16-B-Shelby_q2_03-05_001_praat_ready.csv')

# Load the two CSV files
file1 = pd.read_csv(file1_path, sep='\t')
file2 = pd.read_csv(file2_path, sep='\t')

# Create the Annotation object
annotation = Annotation()

# Iterate over each row in the CSV files and add segments to the Annotation
for i, row in file1.iterrows():
    segment = Segment(start=row[1], end=row[2])
    annotation[segment] = 'speaker1'

for i, row in file2.iterrows():
    segment = Segment(start=row[1], end=row[2])
    annotation[segment] = 'speaker2'

# Now you can use the annotation object to compare with voice activity detection metrics
# For example, you can compute the Diarization Error Rate (DER) using the following code:
from pyannote.metrics.diarization import DiarizationErrorRate
der_metric = DiarizationErrorRate()
der = der_metric(annotation, reference_annotation)  # Replace reference_annotation with your ground truth annotation

print('Diarization Error Rate:', der)
