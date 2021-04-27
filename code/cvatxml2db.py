"""
2021-04-21 'INSERT' changed to 'INSERT OR IGNORE'

2021-01-25 Silent error handling added when there is no corresponding record in frames table.

2021-01-04 Modified by Aubrey Moore

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
# import glob
import os
import xml.etree.ElementTree as ET
# import pandas as pd
# import logging

def main(cvatxml_path, db_path):
    conn = spatialite.connect(db_path)
    cursor = conn.cursor()

    damagedict = {'zero': 0, 'light': 1, 'medium': 2, 'high': 3, 'non_recoverable': 4}

    # Get the video_id from the name field of the videos table
    video = os.path.basename(cvatxml_path).replace('.xml', '.mp4')
    sql = (f'SELECT id FROM videos WHERE name = "{video}"')
    cursor.execute(sql)
    video_id = cursor.fetchone()[0]

    # Iterate through the XML tree, entering records into the trees and vcuts database tables
    root = ET.parse(cvatxml_path).getroot()
    for image in root.iter('image'):
        frame_number = int(image.attrib['id'])
        sql = f'SELECT id FROM frames WHERE video_id={video_id} AND frame_number={frame_number};'
        cursor.execute(sql)

        #frame_id = cursor.fetchone()[0]
        data = cursor.fetchone()
        if data is None:
            print(f'ERROR: No data returned by "{sql}"')
        else:
            frame_id = data[0]
            for box in image.iter('box'):
                damage_index_text = box.attrib['label']
                damage_index = damagedict[damage_index_text]
                xtl = int(float(box.attrib['xtl']))
                ytl = int(float(box.attrib['ytl']))
                xbr = int(float(box.attrib['xbr']))
                ybr = int(float(box.attrib['ybr']))
                geometry = f'GeomFromText("MULTIPOINT({xtl} {ytl},{xbr} {ybr})", -1)'
                sql = f'INSERT OR IGNORE INTO trees(frame_id,damage_index,geometry) VALUES ({frame_id},{damage_index},{geometry});'
                cursor.execute(sql)
                conn.commit()
            for polygon in image.iter('polygon'):
                points = polygon.attrib['points']
                points = points.replace(',', ' ').replace(';', ',') # Reformat points to match WKT for a polygon
                geometry = f'PolyFromText("POLYGON(({points}))",-1)'
                sql = f'INSERT OR IGNORE INTO vcuts(frame_id,geometry) VALUES({frame_id},{geometry});'
                cursor.execute(sql)
                conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    import plac
    plac.call(main)
