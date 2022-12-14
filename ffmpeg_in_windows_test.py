import os
from pathlib import Path
import subprocess as subp
import json
import sys




# script_out = subp.check_output(["ffprobe", "-v", "quiet", "-show_format",
#                                 "-print_format", "json", str(mp4_pth)])
# ffprobe_data = json.loads(script_out)
# video_duration_seconds = float(ffprobe_data["format"]["duration"])

# total_time = str(video_duration_seconds)
# print(total_time)

cmd = f"ffmpeg -i {mp4_pth} -acodec pcm_s16le -ac 1 -ar 16000 mywindows_test.wav"

# os.system(cmd)
print(get_platform())