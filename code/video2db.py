"""
2021-01-02 Modified by Aubrey Moore

Example usage:

    python3 code/video2db.py --data-dir rawdata --db-path output/Guam02.db
"""
from datetime import datetime
import exiftool
import sqlite3
import json
import os
import glob
import plac

def get_exif(video_path):
    with exiftool.ExifTool() as et:
        exif = et.get_metadata(video_path)
    return exif

def update_db(db_path, video_path, exif):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    sql = 'INSERT INTO videos (name, exif) VALUES (?, ?)'
    c.execute(sql, [os.path.basename(video_path), json.dumps(exif)])
    conn.commit()
    c.close()
    conn.close()

@plac.opt('data_dir',abbrev='dd')
@plac.opt('db_path', abbrev='db')
def main(data_dir, db_path):
    """
    Enters filename and EXIF metadata from a video into the survey database.
    Note: the EXIF metdata is extracted from original videos, not the 3FPS versions.
    """
    video_list = glob.glob(f'{data_dir}/????????_??????.mp4')
    for video_path in video_list:
        exif = get_exif(video_path)
        try:
            update_db(db_path, video_path, exif)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    import plac; plac.call(main)
