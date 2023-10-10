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

current_audio = Path.home().joinpath('Dropbox','DATASETS_AUDIO','AOLME_SD_Collection','riogrande','ugesh2', 'samples_sync', 'ugesh_sync_A01.wav')

x, sr = librosa.load(str(current_audio))

hop_length = 256
frame_length = 512

energy = numpy.array([
    sum(abs(x[i:i+frame_length]**2))
    for i in range(0, len(x), hop_length)
])

rmse = librosa.feature.rms(y=x, frame_length=frame_length, hop_length=hop_length, center=True)
rmse = rmse[0]

frames = range(len(energy))
t = librosa.frames_to_time(frames, sr=sr, hop_length=hop_length)

plt.figure()
librosa.display.waveshow(x, sr=sr, alpha=0.4)
plt.plot(t, energy/energy.max(), 'r--')             # normalized for visualization
plt.plot(t[:len(rmse)], rmse/rmse.max(), color='g') # normalized for visualization
plt.legend(('Energy', 'RMSE'))
plt.show()

