"""

This script does great stuff.

Usage:
  my_program (--fromdate=<date>) [--todate=<date>] (--datadir=<path>) (--database=<filename>)
  my_program -h | --help

Options:
  -h --help              Show this screen.
  --fromdate=<date>      First survey date represented as an integer; example: 20201001 (required)
  --todate=<date>        Last survey date represented as an integer; example: 20201031 (optional)
  --datadir=<path>       Data directory; example: /home/aubrey/Desktop/Guam01
  --database=<filename>  Database file name; example: guam01.db

"""

from docopt import docopt
import subprocess
import os
import logging
import glob

def main():

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[logging.StreamHandler()])

    # Get command line arguments
    args = docopt(__doc__, version='0.1')
    fromdate = args.get('--fromdate')
    todate = args.get('--todate')
    datadir = args.get('--datadir')
    database = args.get('--database')
    dbpath = f'{datadir}/{database}'

    # Get path to python interpreter used by virtual environment
    python_bin = '/home/aubrey/Documents/roadside/code/venv/bin/python'

    # Create database if it does not already exist
    logging.info('Creating database if it does not already exist.')
    if os.path.exists(dbpath):
        logging.info(f'{dbpath} already exists.')
    else:
        logging.info(f'Creating {dbpath}')
        command= f'spatialite {dbpath} < /home/aubrey/Documents/roadside/spatialite/create_tables2.sql'
        subprocess.run(command, shell=True)
        command = f'spatialite {dbpath} < /home/aubrey/Documents/roadside/spatialite/create_views.sql'
        subprocess.run(command, shell=True)

    # Process directories for specified survey dates
    if not todate:
        todate = fromdate
    for videodate in range(int(fromdate), int(todate)+1):
        videodatedir = f'{datadir}/{videodate}'
        if os.path.exists(videodatedir):
            logging.info(f'Processing {videodatedir}')

            # Reduce frame rate to 3 FPS for each video. The original video is renamed to *_oriiginal.mp4
            logging.info('Reducing frame rates.')
            for video_path in glob.glob(f'{videodatedir}/{videodate}_??????.mp4'):
                new_path = video_path.replace('.mp4', 'original.mp4')
                if os.path.exists(new_path):
                    logging.info(f'{new_path} alreadyexists. Skipping FPS reduction.')
                else:
                    os.rename(video_path, new_path)
                    logging.info(f'{video_path} --> {new_path}')
                    command = f'ffmpeg -i {new_path} -filter:v fps=fps=3 {video_path}'
                    output = subprocess.run(command, shell=True)
                    logging.info(f'output:{output}')
            logging.info('Finished frame rate reduction.')

            # Upload video files to S3 (3 FPS files only, run object detection using OnePanel API,
            # and finally download CVAT XML files.
            if len(glob.glob(f'{videodatedir}/cvat_annotation*.xml'))==0:
                command = f'python detect_objects.py -dd {datadir} -d {videodate}'
                logging.info(command)
                output = subprocess.run(command, shell=True)
                logging.info(output)
            else:
                logging.info('Skipping detect_objects.py because {videodatedir} already contains CVAT XML files}')

            # Break from this loop if this survey date directory does not contain any CVAT XML files.
            # Otherwise proceed to populating database tables
            if len(glob.glob(f'{videodatedir}/cvat_annotation*.xml'))==0:
                break

            # Register videos in videos database table
            # Get exif metadata from original videos and save this in a JSON field
            command = f'python3 video2db.py --date {videodate} --data-dir {datadir} --db-path {dbpath}'
            logging.info(command)
            output = subprocess.run(command, shell=True)
            logging.info(output)

            # Georeference video frames
            command = f'python3 georef.py --date {videodate} --data-dir {datadir} --db-path {dbpath}'
            logging.info(command)
            output = subprocess.run(command, shell=True)
            logging.info(output)

            # Parse CVAT XML files
            # Populates frames, trees and vcuts table.
            command = f'python3 cvatxml2db.py --date {videodate} --data-dir {datadir} --db-path {dbpath}'
            logging.info(command)
            output = subprocess.run(command, shell=True)
            logging.info(output)

    # Make map

    # Create crb-damage grid (mean_damage_index table)
    command = f'spatialite {dbpath} < /home/aubrey/Documents/roadside/spatialite/create_grid.sql'
    logging.info(command)
    output = subprocess.run(command, shell=True)
    logging.info(output)

    # Create tracks table
    command = f'spatialite {dbpath} < /home/aubrey/Documents/roadside/spatialite/create_tracks.sql'
    logging.info(command)
    output = subprocess.run(command, shell=True)
    logging.info(output)

    # Write $dbpath to a text file so that make_crb_damage_map.py can read it.
    command = f'echo {dbpath} > dbpath.txt'
    logging.info(command)
    output = subprocess.run(command, shell=True)
    logging.info(output)

    # Deactivate virtual environment
    #deactivate

    # Create map using QGIS
    #command = 'qgis --nologo --code make_crb_damage_map.py'
    #logging.info(command)
    #output = subprocess.run(command, shell=True)
    #logging.info(output)

    logging.info('*** FINISHED ALL ***')
    logging.info('To see map, deactivate venv, run "qgis --nologo --code make_crb_damage_map.py" and zoom to mean-damage_index layer.')

if __name__ == '__main__':
    main()
