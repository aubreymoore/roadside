#!/bin/bash

# Aubrey Moore 2020-12-25

# This script uses demo.py to run object detectors for CRB damage.
# demo.py is run using python 3.6 within a virtual environment called py38env

# Note if py38env is moved to a different folder, the following line in py38env/bin/activate needs to be updated:
#     VIRTUAL_ENV='/home/aubreytensor1/Guam02/py38env'  

# Usage:

# This script uses 3 positional parameters: video, num_frames, skip_no
#     1 video:      string; video path
#     2 num_frames: integer; number of frames to be processed; 0 to process all frames
#     3 skip_no:    integer; number of frames to skip; 1 processes every frame; 5 processes every 5th frame
#     4 output_dir  string; output directory for video with detected objects and CVAT xml; no final /   

# Usage  example:
#     ./run-object-detectors.sh /home/aubreytensor1/Guam02/rawdata/20201211_134207.mp4 5 1 /home/aubreytensor1/Guam02/output   

cd ~/Guam02/code/object-detectors
source ~/Guam02/code/py38env/bin/activate
echo py38env activated
python3.6 demo.py --dump_sql False --video $1 --num_frame $2 --skip_no $3 --output_dir $4

