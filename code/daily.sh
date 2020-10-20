#!/bin/bash

# Run this bash script from within the roadside/code directory

# daily.sh date dat-dir db-path

# ./daily.sh 20201002 /home/aubrey/Desktop/Guam01 /home/aubrey/Desktop/Guam01/test.db

# Activate the virtual environment
source ./venv/bin/activate

echo "Positional Parameters"
videodate=$1
datadir=$2
dbpath=$3
makemap=$4
echo 'videodate = ' $videodate
echo 'datadir = ' $datadir
echo 'dbpath = ' $dbpath

# Run within the /home/aubrey/Documents/roadside/code directory

# Set flag to halt whenever an error is detected
set -e

# Create database if it does not already exist
if [ -f "$dbpath" ];then
    echo "Database exists"
else
    spatialite $dbpath < /home/aubrey/Documents/roadside/spatialite/create_tables2.sql
    spatialite $dbpath < /home/aubrey/Documents/roadside/spatialite/create_views.sql
    echo "Database created"
fi

# Create directory for date in arg1
# Not yet automated

# Copy GPS track and video files from smart phone into  data directory
# Not yet automated

# Reduce frame rate to 3 FPS
# Note:3 FPS videos are not created if they already exist
echo "python3 reducefps.py --date $videodate --data-dir $datadir"
python3 reducefps.py --date $videodate --data-dir $datadir 

# Upload 3FPS videos to S3 - NEED TO FIX Rota01
#echo aws s3 sync ${datadir}/${videodate}/ s3://cnas-re.uog.onepanel.io/Rota01/ --exclude "*.csv" --exclude "*original.mp4"
#aws s3 sync ${datadir}/${videodate}/ s3://cnas-re.uog.onepanel.io/Rota01/ --exclude "*.csv" --exclude "*original.mp4"

# Run object detectors
# Not yet automated

# Download CVAT XML files
# Not yet automated

pattern=${datadir}/${videodate}/cvat_annotation*.xml
xmlfilecount=$(ls $pattern | wc -l)
if [[ $xmlfilecount -eq 0 ]] ; then
    echo Exiting because no CVAT XML files exist in the ${datadir}/${videodate} directory.
    exit
else
    echo The ${datadir}/${videodate} directory contains $xmlfilecount CVAT XML files.
fi

# Register videos in videos database table
# Get exif metadata from original videos and save this in a JSON field
echo "python3 video2db.py --date $videodate --data-dir $datadir --db-path $dbpath"
python3 video2db.py --date $videodate --data-dir $datadir --db-path $dbpath


# Georeference video frames
echo "python3 georef.py --date $videodate --data-dir $datadir --db-path $dbpath"
python3 georef.py --date $videodate --data-dir $datadir --db-path $dbpath 

# Parse CVAT XML files and populate survey database
echo "python3 cvatxml2db.py --date $videodate --data-dir $datadir --db-path $dbpath"
python3 cvatxml2db.py --date $videodate --data-dir $datadir --db-path $dbpath 

# Make map

# Create crb-damage grid
echo "$dbpath < /home/aubrey/Documents/roadside/spatialite/create_grid.sql"
spatialite $dbpath < /home/aubrey/Documents/roadside/spatialite/create_grid.sql

# Deactivate virtual environment
deactivate

# Create map
# Write $dbpath to a text file so that make_crb_damage_map.py can read it.
echo $dbpath>dbpathdbpath.txt
qgis --nologo --code make_crb_damage_map.py

