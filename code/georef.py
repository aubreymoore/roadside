"""
2021-01-02 Modified by Aubrey Moore
* frame_number now zero based

2021-01-03 Modified by Aubrey Moore
* Now works on a single video file

2021-01-23  Modified by Aubrey Moore
* Added section "Delete all records for video_id in the frames table"
* Added section "Slice dfgps so that is contains data between start_time and stop_time"
"""
import glob
import logging
import spatialite
import os
from datetime import datetime, timedelta
import pandas as pd
import cv2
import plac
import re

def get_video_start_stop(video_path, cursor):
    """
    Get the video start and stop times from the exif field in the videos database table
    """
    filename = os.path.basename(video_path)
    sql = '''
        SELECT
            JSON_EXTRACT(exif, "$.QuickTime:CreateDate") AS start_time_utc,
            JSON_EXTRACT(exif, "$.QuickTime:Duration") AS duration
        FROM videos
        WHERE name = (?);
        '''
    cursor.execute(sql, [filename])
    createDate, duration = cursor.fetchone()
    createDate = datetime.strptime(createDate, '%Y:%m:%d %H:%M:%S')
    start = createDate - timedelta(seconds=duration)
    stop = createDate
    logging.info(f'        {start}   {stop} UTC')
    return start, stop

def get_lat_lon(timestamp, dfgps):
    timestamp = pd.to_datetime(timestamp)
    df = dfgps[dfgps.time==timestamp]
    if not df.empty:
        # There is a record for exact timestamp (unlikely); return lat lon.
        return dfgps.lat.values[0], dfgps.lon.values[0]
    else:
        # Estimate lat lon using linear interpolation records just prior and post timestamp
        df1 = dfgps[dfgps.time<timestamp].tail(1)
        df2 = dfgps[dfgps.time>timestamp].head(1)
        t1 = df1.time.values[0]
        t2 = df2.time.values[0]
        lat1 = df1.lat.values[0]
        lat2 = df2.lat.values[0]
        lon1 = df1.lon.values[0]
        lon2 = df2.lon.values[0]
        fraction = (timestamp-t1)/(t2-t1)
        lat = lat1 + fraction*(lat2-lat1)
        lon = lon1 + fraction*(lon2-lon1)
        return lat, lon

def main(video_path, db_path):
    """
    Populates the frames field in the survey database.
    Columns are: frame_number, timestamp (UTC), lat, lon
    """
    print('STARTING')
    FRAME_INTERVAL = 1000 # Sets frequency for logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(funcName)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[logging.StreamHandler()])
    logging.info('Starting georef.py')

    # Connect database
    conn = spatialite.connect(db_path)
    cursor = conn.cursor()

    # Find the GPS log file
    gpslogpath = re.sub(r'_\d{6}.mp4', '.csv', video_path, 0, re.MULTILINE)
    logging.info(f'gpslogpath = {gpslogpath}')

    # Load the gps log file csv into a dataframe
    logging.info(f'Reading GPS log from {gpslogpath}')
    dfgps = pd.read_csv(gpslogpath, parse_dates=['time'])
    dfgps['time'] = dfgps['time'].dt.tz_localize(None)

    # Slice dfgps so that is contains data between start_time-10s and stop_time+10s
    start_time, stop_time = get_video_start_stop(video_path, cursor)
    pd.set_option('display.max_columns', None)
    logging.info(f'dfgps prior to slicing: {dfgps.time.iloc[0]}   {dfgps.time.iloc[-1]} UTC')
    dfgps = dfgps[ dfgps.time.between(start_time-timedelta(0,10), stop_time+timedelta(0,10)) ]
    logging.info(f'dfgps after slicing:    {dfgps.time.iloc[0]}   {dfgps.time.iloc[-1]} UTC')

    dfgps.to_pickle(f'map/{os.path.basename(video_path)}.pikl')
    logging.info(f'dfgps pickled')

    gpslog_start_time = dfgps.time.min().to_pydatetime()
    gpslog_stop_time = dfgps.time.max().to_pydatetime()
    logging.info(f'dfgps after slicing:    {gpslog_start_time}   {gpslog_stop_time} UTC')

    # Get the video_id from the videos table
    video = os.path.basename(video_path)
    sql = (f'SELECT id FROM videos WHERE name = "{video}"')
    cursor.execute(sql)
    video_id = cursor.fetchone()[0]

    # Delete all records for video_id in the frames table
    sql = (f'DELETE FROM frames WHERE video_id="{video_id}";')
    cursor.execute(sql)
    conn.commit()

    # populate frames table with records for the current video
    if (start_time > gpslog_start_time) and (stop_time < gpslog_stop_time):
        logging.info(f'Started processing {video_path}')
        logging.info('Building timestamp-location table.')

        cap = cv2.VideoCapture(video_path)
        while True:
            pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
            frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
            timestamp = start_time + timedelta(milliseconds=pos_msec)
            lat, lon = get_lat_lon(timestamp, dfgps)
            geometry = f'TRANSFORM(GeomFromText("POINT({lon} {lat})", 4326), 3857)'
            sql = f'INSERT INTO frames(video_id,frame_number,time,geometry) VALUES({video_id},{frame_number},"{timestamp}",{geometry});'
            logging.debug(sql)
            cursor.execute(sql)
            conn.commit()
            if (frame_number % FRAME_INTERVAL == 0):
                logging.info(f'{frame_number} {timestamp} {lat:7.4f} {lon:8.4f}')
            frame_exists, _ = cap.read()
            if not frame_exists:
                break
        cap.release()
    else:
        logging.error(f'Cannot process {video_path} - gps log data not available')

    # Disconnect database
    cursor.close()
    conn.close()

    logging.info(f'FINISHED {video_path}')

if __name__ == '__main__':
    import plac
    plac.call(main)
