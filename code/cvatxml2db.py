"""

Enters object detector results from CVAT XML files into the survey database.
Data are inserted into the trees and vcuts tables.

The CVAT XML files contain data which looks like this:

  <image id="3280" name="frame_003280" width="1920" height="1080">
    <box label="zero" occluded="0" xtl="474.00" ytl="836.00" xbr="636.00" ybr="1070.00">
    </box>
    <box label="zero" occluded="0" xtl="0.00" ytl="895.00" xbr="264.00" ybr="1077.00">
    </box>
    <box label="light" occluded="0" xtl="1395.00" ytl="235.00" xbr="1918.00" ybr="918.00">
    </box>
    <box label="light" occluded="0" xtl="677.00" ytl="734.00" xbr="894.00" ybr="1029.00">
    </box>
  </image>
  <image id="3280" name="frame_003280" width="1920" height="1080">
    <polygon label="cut" occluded="0" points="805.00,762.50;796.00,762.50;792.50,754.00;804.00,736.50;813.00,734.50;814.50,747.00;805.00,762.50">
    </polygon>
  </image>

"""

import plac
import spatialite
import glob
import os
import xml.etree.ElementTree as ET
import pandas as pd
import logging

DEBUG = False  # WARNING: ALL DATA IN THE frames, trees, and vcuts TABLES WILL BE DELETED.

def get_xml_path(video_path):
    """
    Returns a path to the CVAT XML file which corresponds to the video_path
    """
    dir = os.path.dirname(video_path)
    base = os.path.basename(video_path).replace('.mp4','')
    pattern = f'{dir}/cvat_annotation_{base}*.xml'
    xml_path = glob.glob(pattern)
    if len(xml_path) != 1:
        print(f'ERROR: {pattern} does not return a single result as expected.')
    return xml_path[0]

# def get_gps_path(video_path):
#     """
#     Returns a path to the GPS CSV file which corresponds to the video_path
#     """
#     dir = os.path.dirname(video_path).replace('.mp4', '')
#     base = os.path.basename(video_path).replace('.mp4','')
#     pattern = f'{dir}/{base}_gps.csv'
#     gps_path = glob.glob(pattern)
#     if len(gps_path) != 1:
#         print(f'ERROR: {pattern} does not return a single result as expected.')
#     return gps_path[0]

def add_records(video_path, conn, cursor):

    damagedict = {'zero': 0, 'light': 1, 'medium': 2, 'high': 3, 'non_recoverable': 4}

    # Get the video_id from the videos field
    video = os.path.basename(video_path)
    sql = (f'SELECT id FROM videos WHERE name = "{video}"')
    cursor.execute(sql)
    video_id = cursor.fetchone()[0]

    # Load the CVAT XML data into root
    xml_path = get_xml_path(video_path)
    print(f'xml_path: {xml_path}')
    root = ET.parse(xml_path).getroot()

    # Load the gps csv data into a pandas dataframe. Columns are frame, timestamp, lat, and lon.
    # gpspath = get_gps_path(video_path)
    # dfgps = pd.read_csv(gpspath)

    # Iterate through the XML tree, entering records into the frames, trees, and vcuts database tables
    # Time and location data come from dfgps.
    for image in root.iter('image'):
        frame_number = int(image.attrib['id'])

        # TODO: The following line is kludge which needs to be fixed.
        # There is no id=0 in the frames table. I need to check if frame numbers in Opencv and CVATXML are zero-based
        # or 1-based.
        if frame_number>0:
            sql = f'SELECT id FROM frames WHERE video_id={video_id} AND frame_number={frame_number};'
            logging.debug(sql)
            cursor.execute(sql)
            frame_id = cursor.fetchone()[0]

            for box in image.iter('box'):
                damage_index_text = box.attrib['label']
                damage_index = damagedict[damage_index_text]
                xtl = int(float(box.attrib['xtl']))
                ytl = int(float(box.attrib['ytl']))
                xbr = int(float(box.attrib['xbr']))
                ybr = int(float(box.attrib['ybr']))
                geometry = f'GeomFromText("MULTIPOINT({xtl} {ytl},{xbr} {ybr})", -1)'
                sql = f'INSERT INTO trees(frame_id,damage_index,geometry) VALUES ({frame_id},{damage_index},{geometry});'
                logging.debug(sql)
                cursor.execute(sql)
                conn.commit()
            for polygon in image.iter('polygon'):
                points = polygon.attrib['points']
                points = points.replace(',', ' ').replace(';', ',') # Reformat points to match WKT for a polygon
                geometry = f'PolyFromText("POLYGON(({points}))",-1)'
                sql = f'INSERT INTO vcuts(frame_id,geometry) VALUES({frame_id},{geometry});'
                logging.debug(sql)
                cursor.execute(sql)
                conn.commit()

@plac.opt('data_dir', abbrev='dd')
@plac.opt('db_path', abbrev='db')
@plac.opt('date', abbrev='d')
def main(data_dir='/home/aubrey/Desktop/Guam01', db_path='/home/aubrey/Desktop/Guam01/test20201005.db', date='20201005'):
    """
    Enters object detector results from CVAT XML files into the survey database.

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


    conn = spatialite.connect(db_path)
    cursor = conn.cursor()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s [%(levelname)s] %(funcName)s : %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        handlers=[logging.StreamHandler()])

    if DEBUG:
        # WARNING: ALL DATA IN THE frames, trees, and vcuts TABLES WILL BE DELETED.
        conn.execute(f'DELETE FROM frames;')
        conn.execute(f'DELETE FROM trees;')
        conn.execute(f'DELETE FROM vcuts;')

    search_path = f'{data_dir}/{date}/{date}_??????.mp4'
    logging.info(f'Search path: {search_path}')
    for video_path in glob.glob(search_path):
        add_records(video_path, conn, cursor)

    cursor.close()
    conn.close()

    print('FINISHED')

if __name__ == '__main__':
    import plac; plac.call(main)
