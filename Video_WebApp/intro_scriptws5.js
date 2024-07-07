
var videoName = '';
var started_flag = false;
let current_src = '';

document.getElementById('select-folder').addEventListener('click', async () => {
    const directoryHandle = await window.showDirectoryPicker();
    const videoPaths = [];
    const videoURLs = [];
    const videoFilenames = [];

    const csvPaths = [];
    const csvFilenames = [];
    const csvTextList = [];

    // Locate the 'my_videos' folder and get all the video file paths and filenames
    const myVideosFolder = await directoryHandle.getDirectoryHandle('input_mp4');
    for await (const [name, handle] of myVideosFolder.entries()) {
        if (handle.kind === 'file' && name.endsWith('.mp4')) {
            const videoFile = await handle.getFile();
            const videoUrl = URL.createObjectURL(videoFile);
            videoURLs.push(videoUrl);
            videoPaths.push(videoFile);
            videoFilenames.push(name);
        }
    }


    // Select the first video (index 0) if available
    if (videoPaths.length > 0) {
        document.getElementById('video').src = videoPaths[0].name;
    } else {
        alert('No video files found in the "my_videos" folder.');
    }

    console.log(videoPaths[0]);
    console.log(videoFilenames[0]);

    // current_src = videoPaths[0];
    current_src = 'G-C1L1P-Apr27-E-Irma_q2_03-08-377.mp4';


    // Locate the 'my_csvfiles' folder and get the CSV file
    const stg3_folder = await directoryHandle.getDirectoryHandle('STG_3');
    const exp_folder = await stg3_folder.getDirectoryHandle('STG3_EXP001-SHAS-DV-HDB');
    const myCsvFilesFolder = await exp_folder.getDirectoryHandle('final_csv');


    for await (const [name, handle] of myCsvFilesFolder.entries()) {
        if (handle.kind === 'file' && name.endsWith('.csv')) {
            const csvFile = await handle.getFile();
            const csvText = await csvFile.text();
            csvFilenames.push(csvFile.name);
            csvTextList.push(csvText);
        }
    }


  console.log(csvFilenames[0]);

  var videoFilename = videoFilenames[0];

  // Extract the filename without the extension
  videoName = videoFilename.split('.')[0];

  const csvFileContent = csvTextList[0];


  started_flag = true;

});



document.getElementById('select-video').addEventListener('click', async () => {


});

// Load JSON file
const jsonButton = document.getElementById('load_from_json');
const rootButton = document.getElementById('select-folder');
const manualButton = document.getElementById('load_manually');
const top_div_start = document.getElementById('start_buttons');
const WSstartButton = document.getElementById('btn_start_ws');
const pasteAllButton = document.getElementById('paste_all');


jsonButton.addEventListener('click', () => {

  if (started_flag == true) {
    top_div_start.remove();
    jsonButton.remove();
    rootButton.remove();
    manualButton.remove();
    pasteAllButton.remove();


    var group_code = '';


    group_code = videoName.substring(0, videoName.lastIndexOf('-'));

    load_picture_json('images_june4.json', group_code);
  } else {
    alert('Please select a video first');
  }

  });


manualButton.addEventListener('click', () => {
  if (started_flag == true) {
    top_div_start.remove();
    jsonButton.remove();
    rootButton.remove();
    manualButton.remove();

    // Create 5 new div elements
    for (let i = 0; i < 5; i++) {
      var newDiv = document.createElement("div");

      // Set the div's ID
      newDiv.id = "msrc-div-" + i;

      // Add a class to the div
      newDiv.classList.add("msrc_class");

      // Find the container div
      var containerDiv = document.getElementById("manual_load");

      // Add the new div to the container div
      containerDiv.appendChild(newDiv);
    }

    // Create 5 new input elements
    for (let i = 0; i < 5; i++) {
      var newInput = document.createElement("input");

      // Set the input's type
      newInput.type = "text";

      // Set the input's ID
      newInput.id = "msrc-input-" + i;

      // Set the input's placeholder
      newInput.placeholder = "Enter the speaker name";

      // Find the div to add the input to
      var divToAddTo = document.getElementById("msrc-div-" + i);

      // Add the input to the div
      divToAddTo.appendChild(newInput);
    }

    // Create 5 new canvas elements
    for (let i = 0; i < 5; i++) {
      // Create a new canvas element
      var newCanvas = document.createElement("canvas");

      // Set the canvas's ID
      newCanvas.id = "canvas-" + i;

      // Add a class to the canvas
      newCanvas.classList.add("canvas-class");

      // Set the canvas's height and width
      newCanvas.height = 80;
      newCanvas.width = 80;

      // Find the div to add the canvas to
      var divToAddTo = document.getElementById("msrc-div-" + i);

      // Add the canvas to the div
      divToAddTo.appendChild(newCanvas);
    }

    // Create 5 new input elements
    for (let i = 0; i < 5; i++) {

      // Create a new button element
      var newButton = document.createElement("button");

      // Set the button's text
      newButton.innerHTML = "Paste img";

      // Set the button's ID
      newButton.id = "mbtn-" + i;

      // Add a class to the div
      newButton.classList.add("mbtn_class");

      // Set the button's style
      newButton.style.height = "30px";

      // Find the div to add the input to
      var divToAddTo = document.getElementById("msrc-div-" + i);

      // Add the input to the div
      divToAddTo.appendChild(newButton);
    }

  document.getElementById('mbtn-0').addEventListener('click', async () => {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (let item of clipboardItems) {
            if (item.types.includes('image/png')) {
                const blob = await item.getType('image/png');
                const img = new Image();
                img.src = URL.createObjectURL(blob);

                img.onload = () => {
                    const canvas = document.getElementById('canvas-0');
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    URL.revokeObjectURL(img.src);
                };
                break;
            } else {
                alert('Clipboard does not contain an image.');
            }
        }
    } catch (err) {
        console.error('Failed to read clipboard contents: ', err);
        alert('Failed to read clipboard contents.');
    }
  })

  } else {
    alert('Please select a video first');
  }

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



function load_next_page() {
  if (started_flag == true) {
    console.log(current_src)
    window.location.href = `video_ws4.html?text=${encodeURIComponent(current_src)}`;
  } else {
    alert('Please select a video first');
  }
}