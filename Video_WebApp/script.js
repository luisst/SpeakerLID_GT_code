document.addEventListener('DOMContentLoaded', () => {
    const audioFileInput = document.getElementById('audioFile');
    const playPauseBtn = document.getElementById('playPauseBtn');
    let wavesurfer = null;

    audioFileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const url = URL.createObjectURL(file);
            loadAudio(url);
        }
    });

    playPauseBtn.addEventListener('click', () => {
        if (wavesurfer) {
            wavesurfer.isPlaying() ? wavesurfer.pause() : wavesurfer.play();
        }
    });

    function loadAudio(url) {
        if (wavesurfer) {
            wavesurfer.destroy();
        }
        
        wavesurfer = WaveSurfer.create({
            container: '#waveform',
            waveColor: '#d9dcff',
            progressColor: '#4353ff',
            height: 200,
            responsive: true,
        });

        wavesurfer.load(url);

        wavesurfer.on('ready', () => {
            playPauseBtn.disabled = false;
        });

        wavesurfer.on('finish', () => {
            playPauseBtn.textContent = 'Play';
        });

        wavesurfer.on('play', () => {
            playPauseBtn.textContent = 'Pause';
        });

        wavesurfer.on('pause', () => {
            playPauseBtn.textContent = 'Play';
        });
    }
});
