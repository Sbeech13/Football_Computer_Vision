# Football_Computer_Vision
This is a computer vision script that uses Channel and Spatial Reliability Tracker (CSRT) to track the position of the ball, in pixels, throughout each video. This can later be compared with preprocessed eye tracking data to compare attention to the ball

The analysis requires that have downloaded EDF2MAT, which extracts the temporally stamped gaze coordinates relative to the screen's dimensions. This will not include a redistribution of EDF2MAT - this can be found here https://github.com/uzh/edf-converter 

Due to copyright laws I cannot redistribute the videos in which this pipeline was used for research, but the script should work on any standard 1080 x 1920 resolution scale video. 

CONTENTS:

'ball_tracker_py' is the main script that extracts the ball coordinates for a given video
'ball_tracker_overlay.py' renders the position of the ball over the video in temporal synchrony to allow you to confirm that the tracker is accurate. 
'Football_Ball_Convergence.m' is a matlab script that will extract the gaze data from an EDF file and calculate metrics relating to the gaze-to-ball distance throughout each video using the extracted ball coordinates.
