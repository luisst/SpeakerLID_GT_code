
from pathlib import Path
import re

regex = r"\'(.+)\'(?= \+ vid_cnt3d; \/\/ID_edit!!)"
subst = "another_video_baseline"

current_transcript_pth = Path().absolute().joinpath('tiny_html.html')
print(current_transcript_pth)

f = open(current_transcript_pth, 'r')
long_line = f.read()
f.close()

# print(long_line)

# You can manually specify the number of replacements by changing the 4th argument
result = re.sub(regex, subst, long_line, 0, re.MULTILINE)

if result:
    # print (result)
    new_file = open(current_transcript_pth.with_name('mini_html_output.html'), "w")
    new_file.write(result)
    new_file.close()