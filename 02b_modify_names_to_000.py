import os
import glob

src_videos = '/home/luis/Dropbox/SpeechFall2022/GT_speakerLID/G-C3L1P-Mar21-A-Venkatesh_q2_02-05'

folder_videos_list = sorted(glob.glob("{}/*.mp4".format(src_videos)))

# iterate over all audio sorted
for idx_seg, current_video_path in enumerate(folder_videos_list):
    current_video_name = current_video_path.split('/')[-1]
    new_video_name = '-'.join(current_video_name.split('-')[0:-2]) + '-segment_' + str(idx_seg).zfill(3) + '.mp4'
    new_video_path = '/'.join(current_video_path.split('/')[:-1]) + '/' + new_video_name
    print(f'{current_video_path}\n{new_video_path}\n\n')
    os.rename(current_video_path, new_video_path)
