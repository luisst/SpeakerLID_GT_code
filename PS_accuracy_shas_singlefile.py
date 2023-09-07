from pathlib import Path


filename = Path.home().joinpath('Dropbox', 'SpeechSpring2023','shas','results_TTSsingles_ymal3.txt')

count_wav = 0
count_dur_wav = 0
count_other = 0
count_dur_other = 0

with open(filename, "r") as file:
    for line in file:
        if "noise_" in line and "wav" in line and line.split("wav:")[1].strip().startswith("noise_"):
            count_wav += 1
            if "duration" in line and float(line.split("duration:")[1].split(",")[0].strip()) != 0:
                count_dur_wav += 1
        else:
            count_other += 1
            if "duration" in line and float(line.split("duration:")[1].split(",")[0].strip()) != 0:
                count_dur_other += 1
                
print("Number of lines with 'noise_xxxx.wav':", count_wav)
print("Number of lines with non-zero duration (with 'noise_xxxx.wav' format):", count_dur_wav)
print("Number of lines without 'noise_xxxx.wav':", count_other)
print("Number of lines with non-zero duration (without 'noise_xxxx.wav' format):", count_dur_other)

# True positive, false positive, false negative, and true negative
TP = count_dur_other
FP = count_other - count_dur_other
FN = count_wav - count_dur_wav 
TN = count_dur_wav

# Precision, recall, and F1 score
precision = TP / (TP + FP)
recall = TP / (TP + FN)
f1_score = 2 * (precision * recall) / (precision + recall)

print("Precision:", round(precision, 2))
print("Recall:", round(recall, 2))
print("F1 Score:", round(f1_score, 2))