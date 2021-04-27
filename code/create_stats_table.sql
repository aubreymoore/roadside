BEGIN;

DROP TABLE IF EXISTS stats;
CREATE TABLE stats (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL UNIQUE,
	val TEXT );

INSERT INTO stats (name, val) SELECT 'videos_count', COUNT(*) FROM videos;

INSERT INTO stats (name, val) SELECT 'tracks_count', COUNT(*) FROM tracks;
INSERT INTO stats (name, val) SELECT 'tracks_total_meters', SUM(ST_Length(geometry)) FROM tracks;

INSERT INTO stats (name, val) SELECT 'frames_count', COUNT(*) FROM frames;
INSERT INTO stats (name, val) SELECT 'frames_min_time', MIN(time) FROM frames;
INSERT INTO stats (name, val) SELECT 'frames_max_time', MAX(time) FROM frames;


INSERT INTO stats (name, val) SELECT 'trees_count', COUNT(*) FROM trees;
INSERT INTO stats (name, val) SELECT 'trees_damage_0', COUNT(*) FROM trees WHERE damage_index=0;
INSERT INTO stats (name, val) SELECT 'trees_damage_1', COUNT(*) FROM trees WHERE damage_index=1;
INSERT INTO stats (name, val) SELECT 'trees_damage_2', COUNT(*) FROM trees WHERE damage_index=2;
INSERT INTO stats (name, val) SELECT 'trees_damage_3', COUNT(*) FROM trees WHERE damage_index=3;
INSERT INTO stats (name, val) SELECT 'trees_damage_4', COUNT(*) FROM trees WHERE damage_index=4;
INSERT INTO stats (name, val) SELECT 'trees_damage_mean', AVG(damage_index) FROM trees;
INSERT INTO stats (name, val) SELECT 'trees_damaged', COUNT(*) FROM trees WHERE damage_index>0;

INSERT INTO stats (name, val) SELECT 'vcuts_count', COUNT(*) FROM vcuts;

COMMIT;
