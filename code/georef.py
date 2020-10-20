import glob
import logging
import spatialite
import os
from datetime import datetime, timedelta
import pandas as pd
import cv2
import plac

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
    logging.info(f'Video started at {start} UTC')
    stop = createDate
    logging.info(f'Video ended at {stop} UTC')
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

@plac.opt('data_dir',abbrev='dd')
@plac.opt('db_path', abbrev='db')
@plac.opt('date', abbrev='d')
def main(data_dir='/home/aubrey/Desktop/Guam01', db_path='/home/aubrey/Desktop/Guam01/Guam01.db', date='20201001'):
    """
    Populates the frames field in the survey database.
    Columns are: frame, timestamp (UTC), lat, lon

    Directory structure for data:

    <data_dir>
        <date_dir>
            <video_file>
            <video_file>

    Example:

        /home/aubrey/Desktop/
            20201001/
                20201001_092426.mp4
                20201001_095445.mp4
    """
    FRAME_INTERVAL = 1000

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(funcName)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[logging.StreamHandler()])

    # Connect database
    conn = spatialite.connect(db_path)
    cursor = conn.cursor()

    # Find the GPS log file
    logging.info('Starting georef.py')
    gpslogpath = glob.glob(f'{data_dir}/{date}/{date}.csv')[0]
    logging.info(f'gpslogpath = {gpslogpath}')

    # Load the gps log file csv into a dataframe
    logging.info(f'Reading GPS log from {gpslogpath}')
    dfgps = pd.read_csv(gpslogpath, parse_dates=['time'])
    dfgps['time'] = dfgps['time'].dt.tz_localize(None)
    gpslog_start_time = dfgps.time.min().to_pydatetime()
    gpslog_stop_time = dfgps.time.max().to_pydatetime()

    for video_path in glob.glob(f'{data_dir}/{date}/{date}_??????.mp4'):

        # Get the video_id from the videos table
        video = os.path.basename(video_path)
        sql = (f'SELECT id FROM videos WHERE name = "{video}"')
        cursor.execute(sql)
        video_id = cursor.fetchone()[0]

        start_time, stop_time = get_video_start_stop(video_path, cursor)
        if (start_time > gpslog_start_time) and (stop_time < gpslog_stop_time):
            logging.info(f'Started processing {video_path}')
            logging.info('Building timestamp-location table.')
            # data = list()
            cap = cv2.VideoCapture(video_path)
            i = 0
            while (cap.isOpened()):
                frame_exists, curr_frame = cap.read()
                if frame_exists:
                    pos_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                    frame_number = cap.get(cv2.CAP_PROP_POS_FRAMES)
                    timestamp = start_time + timedelta(milliseconds=pos_msec)
                    lat, lon = get_lat_lon(timestamp, dfgps)
                    # data.append([i, timestamp, lat, lon])

                    #row = dfgps.loc[dfgps['frame'] == int(frame_number)]
                    #time = row.iloc[0]['timestamp']
                    #lon = row.iloc[0]['lon']
                    #lat = row.iloc[0]['lat']
                    geometry = f'TRANSFORM(GeomFromText("POINT({lon} {lat})", 4326), 3857)'
                    sql = f'INSERT INTO frames(video_id,frame_number,time,geometry) VALUES({video_id},{frame_number},"{timestamp}",{geometry});'
                    logging.debug(sql)
                    cursor.execute(sql)
                    conn.commit()

                    if (i % FRAME_INTERVAL == 0):
                        logging.info(f'{i} {timestamp} {lat:7.4f} {lon:8.4f}')
                    i += 1
                else:
                    break
            cap.release()
        else:
            logging.error(f'Cannot process {video_path} - gps log data not available')

    # Disconnect database
    cursor.close()
    conn.close()

    logging.info('FINISHED ALL')

if __name__ == '__main__':
    import plac; plac.call(main)
