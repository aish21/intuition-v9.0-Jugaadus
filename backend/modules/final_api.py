'''
Python Script for the final set of functions to be called.
'''

import cv2
import os
import subprocess
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.editor import *


def extract_audio(input_video):
  audio_file = "/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/audio.wav"
  subprocess.call(['ffmpeg', '-i', input_video, '-vn', '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '2', audio_file])
  return audio_file

def add_audio_to_video(input_video, input_audio, output_video):
    # Use ffmpeg to merge the audio and video files
    command = ["ffmpeg", "-i", input_video, "-i", input_audio, "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest", output_video]
    subprocess.run(command)
    return output_video

def combine_videos(input_path1, input_path2):
    clip1 = VideoFileClip(input_path1)
    clip2 = VideoFileClip(input_path2)

     # Add a small buffer time to the end of the first clip
    clip1 = clip1.set_end(clip1.duration + 0.1)

    # Concatenate the clips and preserve audio
    final_clip = concatenate_videoclips([clip1.set_audio(clip1.audio.set_duration(clip1.duration+clip2.duration)), clip2.set_audio(clip2.audio.set_start(clip1.duration))])

    # Write the output file
    output_path = 'output.mp4'
    final_clip.write_videofile(output_path, fps=clip1.fps, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)

    return output_path

def split_video(input_video_path, timestamp1, timestamp2):
    # Create output file names
    part1_video_path = os.path.splitext(input_video_path)[0] + '_part1.mp4'
    part2_video_path = os.path.splitext(input_video_path)[0] + '_part2.mp4'
    part3_video_path = os.path.splitext(input_video_path)[0] + '_part3.mp4'

    # Calculate start and end times for each part
    start_time1 = '00:00:00'
    end_time1 = f'{int(timestamp1//3600):02d}:{int((timestamp1%3600)//60):02d}:{int(timestamp1%60):02d}'
    start_time2 = end_time1
    end_time2 = f'{int(timestamp2//3600):02d}:{int((timestamp2%3600)//60):02d}:{int(timestamp2%60):02d}'
    start_time3 = end_time2
    end_time3 = '999:59:59'

    # Split the video into three parts while preserving the original audio
    subprocess.call([
        'ffmpeg',
        '-i', input_video_path,
        '-map', '0:v',
        '-map', '0:a',
        '-ss', start_time1,
        '-to', end_time1,
        '-c', 'copy',
        '-y', part1_video_path
    ])
    subprocess.call([
        'ffmpeg',
        '-i', input_video_path,
        '-map', '0:v',
        '-map', '0:a',
        '-ss', start_time2,
        '-to', end_time2,
        '-c', 'copy',
        '-y', part2_video_path
    ])
    subprocess.call([
        'ffmpeg',
        '-i', input_video_path,
        '-map', '0:v',
        '-map', '0:a',
        '-ss', start_time3,
        '-to', end_time3,
        '-c', 'copy',
        '-y', part3_video_path
    ])

    return snip_video(part1_video_path, part3_video_path)

def snip_video(act1, act2):
    video_filenames = []
    video_filenames.append(act1)
    video_filenames.append(act2)
    combine_videos(video_filenames, '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/output_snipped.mp4')

def trim_video(input_video_path, start_time, end_time, output_video_path):
    # Open input video file
    cap = cv2.VideoCapture(input_video_path)

    # Get video frame rate and dimensions
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate start and end frame numbers
    start_frame = int(start_time * fps)
    end_frame = int(end_time * fps)
    if end_frame > frame_count:
        end_frame = frame_count

    # Set video writer parameters
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_params = (fourcc, fps, (width, height))

    # Create video writer
    out = cv2.VideoWriter(output_video_path, *out_params)

    # Read frames and write to output video
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_num >= start_frame and frame_num < end_frame:
            out.write(frame)
        if frame_num >= end_frame:
            break
        frame_num += 1

    # Release resources
    cap.release()
    out.release()

    # Add audio to output video
    command = f"ffmpeg -i {input_video_path} -ss {start_time} -to {end_time} -c copy -map 0:v:0 -map 0:a:0 {os.path.splitext(output_video_path)[0]}_temp.mp4"
    os.system(command)
    os.rename(f"{os.path.splitext(output_video_path)[0]}_temp.mp4", output_video_path)
    
    return output_video_path

def compress_video_ffmpeg(input_file, output_file, bitrate='1000k'):
    # Create the FFmpeg command to compress the video
    command = f'ffmpeg -i {input_file} -vcodec libx264 -b:v {bitrate} -preset slow -pix_fmt yuv420p -movflags +faststart {output_file}'

    # Run the FFmpeg command
    os.system(command)

    print(f'Compressed video saved to {output_file}')
    return output_file


def slowed_down(input_path, output_path, scale=2, interpolation=cv2.INTER_CUBIC):
    # Upscale video
    cap = cv2.VideoCapture(input_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, (width*scale, height*scale))

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            frame = cv2.resize(frame, (width*scale, height*scale), interpolation=interpolation)
            out.write(frame)
        else:
            break

    cap.release()
    out.release()

input_path = '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_upscaled.mp4'
input_path_aud = '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/audio.wav'
output_vid = '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_transition.mp4'

# # Extract audio from mp4 file
# audio_file = extract_audio(input_path)
# print(audio_file)

# # Snip a section out of the video
# output_video_paths = split_video(input_path, 10, 20)
# print(output_video_paths)

# # Trim a section of video
# output_video_path = trim_video(input_path, 10.0, 20.0, '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/output_trimmed.mp4')
# print(f"Trimmed video saved to {output_video_path}")

# Speed up a section of the video
# speed_up_video_pyav(input_path, '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_sped_up.mp4', 3.0)

# Video Compression
# compress_video_ffmpeg(input_path, '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_compressed.mp4', '500k')

# Video Slowdown
# slowed_down(input_path, '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_upscaled.mp4', scale=2, interpolation=cv2.INTER_LINEAR)

# # Add audio to video file
# added_audio = add_audio_to_video(input_path, input_path_aud, output_vid)
# print(added_audio)

# Combine
# combine_videos('/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_part1.mp4', '/Users/aishwarya/Desktop/intuition-v9.0-Jugaadus/backend/tests/OG_part2.mp4')