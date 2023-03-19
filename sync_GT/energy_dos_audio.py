import numpy
import librosa, librosa.display
from pathlib import Path
import numpy, scipy, matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (14, 5)
plt.style.use('seaborn-muted')
plt.rcParams['figure.figsize'] = (14, 5)
plt.rcParams['axes.grid'] = True
plt.rcParams['axes.spines.left'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.bottom'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0
plt.rcParams['image.cmap'] = 'gray'
plt.rcParams['image.interpolation'] = None

current_audio_1 = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','riogrande','ugesh2', 'sync', 'ugesh_sync_A01.wav')
current_audio_2 = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','riogrande','ugesh2', 'sync', 'ugesh_sync_A02.wav')

# To-do: gather the original audio for the session
original_source = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','riogrande','ugesh2', 'sync', 'ugesh_sync_A02.wav')

x1, sr = librosa.load(str(current_audio_1))
x2, sr = librosa.load(str(current_audio_2))


hop_length = 256
frame_length = 512

rmse_1 = librosa.feature.rms(y=x1, frame_length=frame_length, hop_length=hop_length, center=True)
rmse_1 = rmse_1[0]

frames_1 = range(len(rmse_1))
t_1 = librosa.frames_to_time(frames_1, sr=sr, hop_length=hop_length)


rmse_2 = librosa.feature.rms(y=x2, frame_length=frame_length, hop_length=hop_length, center=True)
rmse_2 = rmse_2[0]

frames_2 = range(len(rmse_2))
t_2 = librosa.frames_to_time(frames_2, sr=sr, hop_length=hop_length)


plt.figure()
librosa.display.waveshow(x2, sr=sr, alpha=0.4)
plt.plot(t_1[:len(rmse_1)], rmse_1/rmse_1.max(), color='g') # normalized for visualization
plt.plot(t_2[:len(rmse_2)], rmse_2/rmse_2.max(), color='r') # normalized for visualization
plt.legend(('audio1', 'audio2'))
plt.show()

