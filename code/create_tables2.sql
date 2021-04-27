--
-- Aubrey Moore 2021-01-24
--
    CREATE TABLE videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        device TEXT,
        video_app TEXT,
        camera_options TEXT,
        location_app TEXT,
        notes TEXT,
        lens TEXT,
        camera_mount TEXT,
        vehicle TEXT,
        camera_mount_position TEXT,
        camera_orientation TEXT,
        horizontal_angle FLOAT,
        vertical_angle FLOAT,
	exif JSON
    );


CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER,
    frame_number INTEGER NOT Null,
    time TEXT,
    geometry,
    FOREIGN KEY(video_id) REFERENCES videos(id),
    UNIQUE(video_id, frame_number)
);

SELECT RecoverGeometryColumn('frames', 'geometry', 3857, 'POINT', 'XY');

--
CREATE TABLE trees ( 
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER,
    damage_index INTEGER NOT NULL,
    geometry,
    FOREIGN KEY(frame_id) REFERENCES frames(id),
    UNIQUE(frame_id, geometry)
);

SELECT RecoverGeometryColumn('trees', 'geometry', -1, 'MULTIPOINT', 'XY');

--
CREATE TABLE vcuts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER,
    geometry,
    FOREIGN KEY(frame_id) REFERENCES frames(id),
    UNIQUE(frame_id, geometry)
);

SELECT RecoverGeometryColumn('vcuts', 'geometry', -1, 'POLYGON', 'XY');

/*
Creates a tracks table for use with QGIS 
Contains a track for each video
Point data from the frames table is converted to LineString data

Tried to implement this as a view, but this does not seem possible. See: 
https://gis.stackexchange.com/questions/232479/how-to-make-a-spatialite-view-with-geometries-for-qgis-based-on-two-table 
*/

DROP TABLE IF EXISTS tracks;

CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    FOREIGN KEY(name) REFERENCES videos(name));

SELECT AddGeometryColumn('tracks', 'geometry', 3857, 'LINESTRING', 'XY');



