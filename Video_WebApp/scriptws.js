// import WaveSurfer from 'https://unpkg.com/wavesurfer.js';
// import WaveSurfer from 'wavesurfer.js'

var ws = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'violet',
    progressColor: 'purple',
    media: document.querySelector('video'),

    // Set a bar width
    barWidth: 2,
    // Optionally, specify the spacing between bars
    barGap: 1,
    // And the bar radius
    barRadius: 2,

    /** The color of the playpack cursor */
    cursorColor: '#2E4053',
    /** The cursor width */
    cursorWidth: 2,
});

// // Initialize the Regions plugin
// const wsRegions = ws.registerPlugin(WaveSurfer.RegionsPlugin.create())

ws.once('interaction', () => {
  wavesurfer.play()
})

