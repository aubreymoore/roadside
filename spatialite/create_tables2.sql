--
-- Aubrey Moore 2020-10-10
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

--
--  CREATE TABLE tracks (
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    name TEXT NOT NULL UNIQUE,
--    FOREIGN KEY(name) REFERENCES frames(name)
--  );

--  SELECT AddGeometryColumn('tracks', 'geometry', 3857, 'LINESTRING', 'XY');

--
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

