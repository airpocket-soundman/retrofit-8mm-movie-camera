
import sys
import numpy as np

import moviepy.editor as mp

clip = mp.VideoFileClip("1_1.mp4")
clip.write_videofile("soundMovie.mp4",audio="silent.mp3")
