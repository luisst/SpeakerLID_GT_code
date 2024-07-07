function getParameterByName(name) {
    const url = new URL(window.location.href);
    const params = new URLSearchParams(url.search);
    return params.get(name);
  }

// Loop a region on click
let loop = true
var wsRegions = null;
var ws = null;

document.addEventListener('DOMContentLoaded', function () {

  const current_src_url = getParameterByName('text');
  // const current_src_url = 'G-C1L1P-Apr27-E-Irma_q2_03-08-377.mp4';
  document.getElementById('video').src = current_src_url;
  const videoName = current_src_url.split('/').pop().split('.')[0];

  ws = WaveSurfer.create({
      container: '#waveform',
      height: 80,
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
      minPxPerSec: 100,
      plugins: [WaveSurfer.Timeline.create()],
  });

  // Play on click
  ws.once('interaction', () => {
    ws.play()
  })

  // Initialize the Regions plugin
  wsRegions = ws.registerPlugin(WaveSurfer.Regions.create())


  wsRegions.on('region-updated', (region) => {
    console.log('Updated region', region)
  })

  // Toggle looping with a checkbox
  document.querySelector('#loopBox').onclick = (e) => {
    loop = e.target.checked
  }

  {
    let activeRegion = null
    wsRegions.on('region-in', (region) => {
      activeRegion = region
    })
    wsRegions.on('region-out', (region) => {
      if (activeRegion === region) {
        if (loop) {
          region.play()
        } else {
          activeRegion = null
        }
      }
    })
    wsRegions.on('region-clicked', (region, e) => {
      e.stopPropagation() // prevent triggering a click on the waveform
      activeRegion = region
      region.play()
      region.setOptions({ color: randomColor() })
    })
    // Reset the active region when the user clicks anywhere in the waveform
    ws.on('interaction', () => {
      activeRegion = null
    })
  }


  // Update the zoom level on slider change
  ws.once('decode', () => {
    document.querySelector('input[type="range"]').oninput = (e) => {
      const minPxPerSec = Number(e.target.value)
      ws.zoom(minPxPerSec)
    }
  })


  // Log video name
  console.log(videoName);

  findAndLoadImage(videoName);

  started_flag = true;

});


// Function to automatically look for a PNG image with the name equal to group_code
function findAndLoadImage(full_video_name) {
  // Assuming the existence of a function `imageExists` to check if the image file exists
  // This is a placeholder and needs to be implemented based on the environment (Node.js, browser, etc.)
  imageExists(`${full_video_name}.png`, (exists) => {
    if (exists) {
      // If the image exists, log success and potentially do something with the image
      console.log(`Image found: ${full_video_name}.png`);

      // Create a div element
      let idivElement = document.createElement('div');
      // Set the ID of the div
      idivElement.id = 'loadedimg';

      // Create an img element
      let loadedimgElement = document.createElement('img');
      // Set the src attribute of the img
      loadedimgElement.src = 'G-C1L1P-Apr27-E-Irma_q2_03-08-377.png';

      // Append the img element to the div
      idivElement.appendChild(loadedimgElement);

      let imageDiv = document.getElementById('image-container');
      imageDiv.appendChild(idivElement);


    } else {
      // If the image does not exist, log the error
      console.log(`Image not found: ${full_video_name}.png`);

      var group_code = '';
      group_code = full_video_name.substring(0, full_video_name.lastIndexOf('-'));

      // Call the load_picture_json function as per the requirement
      load_picture_json('images_june4.json', group_code);
    }
  });
}

// Placeholder for the imageExists function
// This needs to be implemented based on specific environment requirements
function imageExists(imagePath, callback) {
  // Example implementation for a browser environment
  // This would need to be adjusted for server-side (Node.js) or other environments
  let img = new Image();
  img.onload = () => callback(true);
  img.onerror = () => callback(false);
  img.src = imagePath;
}

// The URL path to the CSV file
const csvFilePath = 'csv_predictions/G-C1L1P-Apr27-E-Irma_q2_03-08-377.csv';


let inputData = [];
let outputData = [];
let inputData_index = 0;
let numberOfUniqueValues = 0;
let total_samples = 0;

var videoName = '';
var started_flag = false;

fetch(csvFilePath)
  .then(response => {
      if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
      }
      return response.text();
  })
  .then(data => {
      const rows = data.trim().split('\n');
      inputData = rows.map(row => row.split('\t'));

      // Sort the list based on the second element, which is a float stored as a string
      inputData.sort((a, b) => parseFloat(a[1]) - parseFloat(b[1]));

      // Using a Set to store unique values from the first column
      const uniqueValues = new Set();

      // Iterating through the array and adding the first column values to the Set
      inputData.forEach(row => {
          uniqueValues.add(row[0]);
      });

      // Getting the number of unique values
      numberOfUniqueValues = uniqueValues.size;

      total_samples = inputData.length;

      console.log("Number of unique values: " + numberOfUniqueValues)

      document.getElementById('tclustertotal').textContent = String(numberOfUniqueValues);

      document.getElementById('tsampletotal').textContent = String(total_samples);


      inputData.forEach(subList => {
          subList.push(99);
      });
  })
  .catch(error => {
      console.error('There was a problem with the fetch operation:', error);
  });



function load_picture_json(json_path, group_code){
  fetch(json_path)
    .then(response => response.json())
    .then(data => {
      const container = document.getElementById('image-container');

      var group_data = data[group_code];

      group_data.forEach((element) => {

        var speaker_name = element['speaker_name'];
        var speaker_number = element['speaker_number'];
        var speaker_picture_data = element['image_64'];
        const speaker_picture = "data:image/png;base64," + speaker_picture_data;

        const img = document.createElement('img');
        img.src = speaker_picture; // The Base64 string is already in the correct format
        img.alt = `${speaker_name}`;
        img.width = 80;
        img.height = 80;

        // Create a caption element
        const caption = document.createElement('p');
        caption.classList.add(`src_${speaker_number}`);
        caption.textContent = `${speaker_number} - ${speaker_name}`;

        // Create a container for each image and its caption
        const div = document.createElement('div');
        div.classList.add('speakerIDcontainer');
        div.appendChild(img);
        div.appendChild(caption);

        // Append the container to the main container
        container.appendChild(div);
      });

    })
    .catch(error => console.error('Error:', error));
  }



// -------------------------------------------------------------------------



// Give regions a random color when they are created
const random = (min, max) => Math.random() * (max - min) + min
const randomColor = () => `rgba(${random(0, 255)}, ${random(0, 255)}, ${random(0, 255)}, 0.5)`



let currentRegion = null;
let currentRow = null;

let current_src = 0;

let assumption_flag = false;

function nextSegment() {
  // Check if csvData is not empty
  if (inputData.length > 0 && inputData_index < inputData.length) {
    // Remove the last region if it exists
    if (currentRegion) {
      currentRegion.remove();
    }

    if (inputData[inputData_index][4] != 99) {
      assumption_flag = true;
    } else {
      assumption_flag = false;
    }

    draw_prev_after_segment(inputData_index);

    // Get the first row from csvData
    currentRow = inputData[inputData_index++];

    // Extract the second and third values as floats

    current_src = parseFloat(currentRow[0]);
    var current_start_time = parseFloat(currentRow[1]);
    var current_end_time = parseFloat(currentRow[2]);

    // Use them as start and end time with the wsRegions.addRegion
    currentRegion = wsRegions.addRegion({
      start: current_start_time,
      end: current_end_time,
      color: assumption_flag ? return_speaker_color(inputData_index -1) : `rgba(93,109,126, 0.5)`, 
      drag: true,
      resize: true,
      minLength: 0.5,
      maxLength: 20,
    });

    // Calculate the duration of the segment
    const duration = current_end_time - current_start_time;

    // Calculate the zoom level so the segment occupies 80% of the view
    const zoomLevel = ws.getDuration() / (duration / 0.8);

    // Set the zoom level
    ws.zoom(zoomLevel);

    // Calculate the scroll position so the segment is centered
    const scrollPosition = (current_start_time + duration / 2) * ws.options.minPxPerSec -  ws.renderer.scrollContainer.clientWidth/ 2;

    // Scroll to the calculated position
    ws.renderer.scrollContainer.scrollLeft = scrollPosition;

    ws.media.currentTime = current_start_time;


    // Write the current cluster number to the page 
    document.getElementById('tclusternum').textContent = String(current_src);

    // Write the current segment number to the page
    document.getElementById('tsamplenum').textContent = String(inputData_index);

    // Write the current segment start time to the page
    document.getElementById('tstartt').textContent = current_start_time.toFixed(2);

    // Write the current segment end time to the page
    document.getElementById('tstopt').textContent = current_end_time.toFixed(2);


  } else {
    alert('No more data in csvData');
  }
}

let prevRegion = null;
let nxtRegion = null;

function draw_prev_after_segment(tmp_index){

  if (inputData[tmp_index -1] !== undefined) {

    if (prevRegion) {
      prevRegion.remove();
    }

    // Get the first row from csvData
    let prevRow = inputData[tmp_index -1];

    // Extract the second and third values as floats

    var prev_current_src = parseFloat(prevRow[0]);
    var prev_start_time = parseFloat(prevRow[1]);
    var prev_end_time = parseFloat(prevRow[2]);

    // Use them as start and end time with the wsRegions.addRegion
    prevRegion = wsRegions.addRegion({
      start: prev_start_time,
      end: prev_end_time,
      color: `rgba(235, 152, 78, 0.5)`, 
      drag: false,
      resize: false,
    });
  }

  if (inputData[tmp_index +1] !== undefined) {

    if (nxtRegion) {
      nxtRegion.remove();
    }

    // Get the first row from csvData
    let nxtRow = inputData[tmp_index +1];

    // Extract the second and third values as floats

    var next_current_src = parseFloat(nxtRow[0]);
    var next_start_time = parseFloat(nxtRow[1]);
    var next_end_time = parseFloat(nxtRow[2]);

    // Use them as start and end time with the wsRegions.addRegion
    nxtRegion = wsRegions.addRegion({
      start: next_start_time,
      end: next_end_time,
      color: `rgba(72, 201, 176, 0.5)`, 
      drag: false,
      resize: false,
    });
  }



}

function return_speaker_color(tmp_index){
  var speaker_number = inputData[tmp_index][4];

  if (speaker_number == 'S0') {
    return hexToRgba('#EC7063', 0.5);
  } else if (speaker_number == 'S1') {
    return hexToRgba('#AF7AC5', 0.5);
  } else if (speaker_number == 'S2') {
    return hexToRgba('#5DADE2', 0.5);
  } else if (speaker_number == 'S3') {
    return hexToRgba('#52BE80', 0.5);
  } else if (speaker_number == 'S4') {
    return hexToRgba('#F5B041', 0.5);
  }

}






document.getElementById('playPauseButton').addEventListener('click', function() {
  if (ws.isPlaying()) {
    ws.pause();
  } else {
    ws.play();
  }
});

// Add event listener on keydown
document.addEventListener('keydown', (event) => {
  var code = event.code;
  if (code == 'KeyV')
    if (ws.isPlaying()) {
      ws.pause();
    } else {
      ws.play();
    }
}, false);


let current_name = "S0";

function hexToRgba(hex, alpha = 1) {
    // Remove the hash at the start if it's there
    hex = hex.replace(/^#/, '');

    // Parse the r, g, b values
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);

    // Return the RGBA string
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function change_0(){
  current_name = "S0";
  if (currentRegion) {
          currentRegion.setOptions({ color: hexToRgba('#EC7063', 0.5) })
      }
}

function change_1(){
  current_name = "S1";
  if (currentRegion) {
          currentRegion.setOptions({ color: hexToRgba('#AF7AC5', 0.5) })
      }
}

function change_2(){
  current_name = "S2";
  if (currentRegion) {
          currentRegion.setOptions({ color: hexToRgba('#5DADE2', 0.5) })
      }
}


function change_3(){
  current_name = "S3";
  if (currentRegion) {
          currentRegion.setOptions({ color: hexToRgba('#52BE80', 0.5) })
      }
}

function change_4(){
  current_name = "S4";
  if (currentRegion) {
          currentRegion.setOptions({ color: hexToRgba('#F5B041', 0.5) })
      }
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Y' || event.key === 'y') {
        change_0();
      }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'U' || event.key === 'u') {
        change_1();
      }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'I' || event.key === 'i') {
        change_2();
      }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'O' || event.key === 'o') {
        change_3();
      }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'P' || event.key === 'p') {
        change_4();
      }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'K' || event.key === 'k') {
        add_segment_table();
      }
});



function add_segment_table(){

  // Format for table
  var table = document.getElementById("myTable");
  var row = table.insertRow(1);

  var src = row.insertCell(0);
  var start_time = row.insertCell(1);
  var end_time = row.insertCell(2);

  if (current_name == 'S0'){
    src.innerHTML = '<p style="color:#E74C3C; margin: 2px;">' + current_name + '</p>';
    start_time.innerHTML ='<p style="color:#E74C3C; margin: 2px;">' + currentRegion.start.toFixed(2)  + '</p>';
    end_time.innerHTML ='<p style="color:#E74C3C; margin: 2px;">' + currentRegion.end.toFixed(2) + '</p>';
  } else if (current_name == 'S1'){
    src.innerHTML = '<p style="color:#8E44AD; margin: 2px;">' + current_name + '</p>';
    start_time.innerHTML ='<p style="color:#8E44AD; margin: 2px;">' + currentRegion.start.toFixed(2) + '</p>';
    end_time.innerHTML ='<p style="color:#8E44AD; margin: 2px;">' + currentRegion.end.toFixed(2) + '</p>';
  } else if (current_name == 'S2'){
    src.innerHTML = '<p style="color:#3498DB; margin: 2px;">' + current_name + '</p>';
    start_time.innerHTML ='<p style="color:#3498DB; margin: 2px;">' + currentRegion.start.toFixed(2) + '</p>';
    end_time.innerHTML ='<p style="color:#3498DB; margin: 2px;">' + currentRegion.end.toFixed(2) + '</p>';
  } else if (current_name == 'S3'){
    src.innerHTML = '<p style="color:#27AE60; margin: 2px;">' + current_name + '</p>';
    start_time.innerHTML ='<p style="color:#27AE60; margin: 2px;">' + currentRegion.start.toFixed(2) + '</p>';
    end_time.innerHTML ='<p style="color:#27AE60; margin: 2px;">' + currentRegion.end.toFixed(2) + '</p>';
  } else if (current_name == 'S4'){
    src.innerHTML = '<p style="color:#9A7D0A; margin: 2px;">' + current_name + '</p>';
    start_time.innerHTML ='<p style="color:#9A7D0A; margin: 2px;">' + currentRegion.start.toFixed(2) + '</p>';
    end_time.innerHTML ='<p style="color:#9A7D0A; margin: 2px;">' + currentRegion.end.toFixed(2) + '</p>';
  }

  // Add to outputData
  outputData.push([current_name, currentRegion.start.toFixed(2), currentRegion.end.toFixed(2), current_src]);


  // Assign assumptions
  update_assumptions(current_name, inputData_index);

  console.log(outputData);

  //Delete last entry
  document.getElementById("myTable").deleteRow(7);
}

function update_assumptions(current_name, inputData_index){

  current_cluster_pred = inputData[inputData_index][0];

  // Change current line
  inputData[inputData_index][4] = current_name;

  // Find all the lines with the same cluster prediction
  for (let i = inputData_index + 1; i < inputData.length; i++) {
    if (inputData[i][0] == current_cluster_pred) {
      inputData[i][4] = current_name;
    }
  }

}
  
document.getElementById('eraseAllButton').addEventListener('click', function() {
    // Display the confirm dialog
    const userConfirmed = confirm('Do you want to erase all data saved?');
    
    // If the user clicked "OK", change the color of the square
    if (userConfirmed) {
      restart_table_time();
      console.log("Data erased");
      console.log(outputData);
    }
});


// Undo last entry
function undoLastEntry(){

  // Delete it from the main csvdata
  outputData.pop();
  inputData_index--;

  // Delete it from the table
  document.getElementById("myTable").deleteRow(1);

  // fill at the bottom of the table with ---- to keep shape
  var table = document.getElementById("myTable");    
  var row = table.insertRow(6);
  var src = row.insertCell(0);
  var start_time = row.insertCell(1);
  var end_time = row.insertCell(2);

  src.innerHTML = "-";
  start_time.innerHTML = "-";
  end_time.innerHTML = "-";

  console.log(outputData);

}

function restart_table_time(){
  // Erase timetable
    outputData.length = 0

    // Erase table
    document.getElementById("myTable").deleteRow(1);
    document.getElementById("myTable").deleteRow(1);
    document.getElementById("myTable").deleteRow(1);
    document.getElementById("myTable").deleteRow(1);
    document.getElementById("myTable").deleteRow(1);
    document.getElementById("myTable").deleteRow(1);

    var table = document.getElementById("myTable");

    ws.setTime(0)
    inputData_index = 0;
    for (let i = 0; i < 6; i++) {      
      var row = table.insertRow(i+1);
      var src = row.insertCell(0);
      var start_time = row.insertCell(1);
      var end_time = row.insertCell(2);

      src.innerHTML = "-";
      start_time.innerHTML = "-";
      end_time.innerHTML = "-";

      // set video time to zero
    }
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'X' || event.key === 'x') {
       // Toggle loop on/off
        if (loop) {
          loop = false;
          document.getElementById('loopBox').checked = false;
        } else {
          loop = true;
          document.getElementById('loopBox').checked = true;
        }
      }
});


document.addEventListener('keydown', function(event) {
    if (event.key === 'J' || event.key === 'j') {
      nextSegment();
    }
});

function aroundPlaySegment(){

  // Disable loop
  loop = false;
  document.getElementById('loopBox').checked = false;

  new_segment_start = currentRegion.start - 2;
  ws.setTime(new_segment_start);
  ws.play();
}


//create a user-defined function to download CSV file   
function download_csv_file() {  
  
    //define the heading for each row of the data  
    var csv = 'Src\tStartTime\tEndTime\tClusterPred\n';  
      
    //merge the data with CSV  
    outputData.forEach(function(row) {  
            csv += row.join('\t');  
            csv += "\n";  
    });  
   
    var hiddenElement = document.createElement('a');  
    hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csv);  
    hiddenElement.target = '_blank';  

    const current_video_name = "temp_video_name";

    //provide the name for the CSV file to be downloaded
    const timeElapsed = Date.now();
    const today = new Date(timeElapsed);
    var mydate = today.toISOString();
    hiddenElement.download = String(current_video_name) + '-' + mydate + '.csv';  
    hiddenElement.click();
} 
