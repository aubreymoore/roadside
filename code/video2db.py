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
    sql = """
        INSERT INTO videos (name, exif)
        VALUES (?, ?)
        """
    c.execute(sql, [os.path.basename(video_path), json.dumps(exif)])
    conn.commit()
    c.close()
    conn.close()

@plac.opt('data_dir',abbrev='dd')
@plac.opt('db_path', abbrev='db')
@plac.opt('date', abbrev='d')
def main(data_dir='/home/aubrey/Desktop/Guam01', db_path='/home/aubrey/Desktop/Guam01/Guam01.db', date='20201002'):
    """
    Enters filename and EXIF metadata from a video into the survey database.
    Note: the EXIF metdata is extracted from original videos, not the 3FPS versions.
    """
    for video_path in glob.glob(f'{data_dir}/{date}/{date}_??????.mp4'):
        original_video_path = video_path.replace('.mp4', 'original.mp4')
        exif = get_exif(original_video_path)
        try:
            update_db(db_path, video_path, exif)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    import plac; plac.call(main)
