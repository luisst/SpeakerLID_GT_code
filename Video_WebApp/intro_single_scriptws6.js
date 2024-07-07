
var videoName = '';
var started_flag = false;
let current_src = '';

// document.getElementById('select-folder').addEventListener('click', async () => {

// });

// Select the input element
const videoInput = document.getElementById('videoInput');
// Select the video player element
const videoPlayer = document.getElementById('video');

// Add an event listener for the input change event
videoInput.addEventListener('change', function(event) {
    // Get the selected file
    const file = videoInput.files[0];

    // Check if a file is selected
    if (file) {
        // Log the video name to the console
        console.log('Selected video name:', file.name);

        // Create a URL for the selected video file
        const videoURL = URL.createObjectURL(file);

        // Set the video player's source to the selected file
        videoPlayer.src = videoURL;
        videoPlayer.style.display = 'block';
        started_flag = true;
        current_src = file.name;

        // Extract the filename without the extension
        videoName = file.name.split('.')[0];

        // // Load the corresponding CSV file
        // fetch(videoName + '.csv')
        //     .then(response => response.text())
        //     .then(data => {
        //         // data contains the CSV data
        //         console.log(data);
        //     })
        //     .catch(error => console.error('Error:', error));

    }
});



// Load JSON file
const jsonButton = document.getElementById('load_from_json');
const manualButton = document.getElementById('load_manually');
const top_div_start = document.getElementById('start_buttons');
const WSstartButton = document.getElementById('btn_start_ws');
const pasteAllButton = document.getElementById('paste_all');


jsonButton.addEventListener('click', () => {

  if (started_flag == true) {
    var group_code = '';

    group_code = videoName.substring(0, videoName.lastIndexOf('-'));

    // log the group code to the console
    console.log('Group code:', group_code);

    load_picture_json('images_june4.json', group_code);
  } else {
    alert('Please select a video first');
  }

  });


manualButton.addEventListener('click', () => {
  if (started_flag == true) {
    top_div_start.remove();
    jsonButton.remove();
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

  document.getElementById('mbtn-1').addEventListener('click', async () => {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (let item of clipboardItems) {
            if (item.types.includes('image/png')) {
                const blob = await item.getType('image/png');
                const img = new Image();
                img.src = URL.createObjectURL(blob);

                img.onload = () => {
                    const canvas = document.getElementById('canvas-1');
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


  document.getElementById('mbtn-2').addEventListener('click', async () => {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (let item of clipboardItems) {
            if (item.types.includes('image/png')) {
                const blob = await item.getType('image/png');
                const img = new Image();
                img.src = URL.createObjectURL(blob);

                img.onload = () => {
                    const canvas = document.getElementById('canvas-2');
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


  document.getElementById('mbtn-3').addEventListener('click', async () => {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (let item of clipboardItems) {
            if (item.types.includes('image/png')) {
                const blob = await item.getType('image/png');
                const img = new Image();
                img.src = URL.createObjectURL(blob);

                img.onload = () => {
                    const canvas = document.getElementById('canvas-3');
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


  document.getElementById('mbtn-4').addEventListener('click', async () => {
    try {
        const clipboardItems = await navigator.clipboard.read();
        for (let item of clipboardItems) {
            if (item.types.includes('image/png')) {
                const blob = await item.getType('image/png');
                const img = new Image();
                img.src = URL.createObjectURL(blob);

                img.onload = () => {
                    const canvas = document.getElementById('canvas-4');
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

      if (group_data){
        // Log the length of group_data to the console
        console.log("group data length", group_data.length);

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

            top_div_start.remove();
            jsonButton.remove();
            manualButton.remove();
            pasteAllButton.remove();
        });
        } else {
            console.log('No data found for this video');
            alert('No data found for this video');
        }

    })
    .catch(error => console.error(' json Error:', error));
  }

document.getElementById('paste_all').addEventListener('click', function() {
  if (started_flag == true) {
    html2canvas(document.querySelector("#image-container")).then(canvas => {
        let link = document.createElement('a');
        link.download = 'speakers_image.png';
        link.href = canvas.toDataURL();
        link.click();
    });
  } else {
    alert('Please select a video first');
  }
});

function load_next_page() {
  if (started_flag == true) {
    console.log(current_src)
    window.location.href = `video_ws4.html?text=${encodeURIComponent(current_src)}`;
  } else {
    alert('Please select a video first');
  }
}