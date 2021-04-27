# RUN USING python 3.8 or higher

import spatialite
import math
import json

db_path = '/home/aubreytensor1/Guam02/map/Guam02.db'
track_name = '20201211_134207.mp4'
max_meters = 1000

def get_points(db_path, track_name):
    with spatialite.connect(db_path) as db:
        sql = f"""
        SELECT AsGeoJSON(geometry)
        FROM tracks
        WHERE name='{track_name}';
        """
        s = db.execute(sql).fetchone()[0]
    points = json.loads(s)['coordinates']
    return points

def remove_bad_points(points):
    prev_point = points[0]
    i = 0
    for point in points[1:]:
        i += 1
        meters = int(math.dist(point, prev_point))
        # print(i, point, prev_point, meters)
        prev_point = point
        if meters > max_meters:
            del points[i]
            # print(f'point {i} removed. Rerun.')
            # print(len(points))
            return points
    return 'NO POINTS REMOVED'

def list_points(points):
    prev_point = points[0]
    i = 0
    for point in points[1:]:
        i += 1
        meters = int(math.dist(point, prev_point))
        print(i, point, prev_point, meters)
        prev_point = point

points = get_points(db_path, track_name)
del points[51]
list_points(points)

def
    geometry = f'TRANSFORM(GeomFromText("POINT({lon} {lat})", 4326), 3857)'






# while True:
#     points = remove_bad_points(points)
#     print(f'{len(points)} remaining')
#     if points == 'NO POINTS REMOVED':
#         break
