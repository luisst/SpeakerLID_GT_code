import base64
from pathlib import Path
import json

def convert_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


images_folder_path = Path(r"C:\Users\luis2\Dropbox\DATASETS_AUDIO\VAD_aolme\pictures_all")

# Create a list with all the paths in pathlib of the images in the folder
images_list = list(images_folder_path.glob("**/*.png"))

images_dict = {} 
# For loop to convert all the images to base64
for image_path in images_list:
    image_filename = image_path.stem

    print(f'\n\tImage path: {image_filename}')

    speaker_number = str(image_filename.split("_")[-2])
    speaker_name = str(image_filename.split("_")[-1])
    group_name = "_".join(image_filename.split("_")[:-2])

    # print the group name, speaker name and speaker number
    print(f'group_name: {group_name}, speaker_name: {speaker_name}, speaker_number: {speaker_number}')

    image_base64 = convert_image_to_base64(image_path)

    current_image_dict = {
        "speaker_name": speaker_name,
        "speaker_number": speaker_number,
        "image_64": image_base64
    }

    # Create key in images_dict with the group name
    if group_name not in images_dict:
        images_dict[group_name] = [current_image_dict]
    else:
        images_dict[group_name].append(current_image_dict)


# Write the image data to a JSON file
output_path = "images_june4.json"
with open(output_path, "w") as json_file:
    json.dump(images_dict, json_file, indent=4)

print(f'\n\tJSON file created: {output_path}')