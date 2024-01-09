import sys
import numpy as np
import glob
import moviepy.editor as mp

print("read filenames")
files = glob.glob("data/*")

print("files")
for file in files:
    print(file)
    fileName = file[:-4] + "s.mp4"
    print(fileName)
    clip = mp.VideoFileClip(file)
    clip.write_videofile(fileName, audio="silent.mp3")

print("end")

#clip = mp.VideoFileClip("1_1.mp4")
#clip.write_videofile("soundMovie.mp4",audio="silent.mp3")
