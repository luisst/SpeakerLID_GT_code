// Error while importing WaveSurfer from 'wavesurfer.js'
// import WaveSurfer from 'wavesurfer.js'


// Initialize Wavesurfer
const wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'violet',
    progressColor: 'purple'
});


// Handle file input change
document.getElementById('audioInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const objectUrl = URL.createObjectURL(file);
        wavesurfer.load(objectUrl);

    }
});
