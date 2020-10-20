-- Aubrey Moore 2020-10-2021

-- Creates a view for use with QGIS
-- The geometry column contains camera location coordinates.
-- Note: SQL for this spatially enabled view was developed using spatiallite_gui Query/View Composer

CREATE VIEW "trees_view" AS
SELECT "a"."damage_index" AS "damage_index", "b"."ROWID" AS "ROWID", "b"."geometry" AS "geometry"
FROM "trees" AS "a"
JOIN "frames" AS "b" ON ("a"."frame_id" = "b"."id");

INSERT INTO views_geometry_columns
(view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
VALUES ('trees_view', 'geometry', 'rowid', 'frames', 'geometry', 1);

-- Creates a view for use with QGIS
-- The geometry column contains camera location coordinates.
-- Note: SQL for this spatially enabled view was developed using spatiallite_gui Query/View Composer    

CREATE VIEW "vcuts_view" AS
SELECT  "b"."ROWID" AS "ROWID", "b"."geometry" AS "geometry"
FROM "vcuts" AS "a"
JOIN "frames" AS "b" ON ("a"."frame_id" = "b"."id");

INSERT INTO views_geometry_columns(
view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
VALUES ('vcuts_view', 'geometry', 'rowid', 'frames', 'geometry', 1);  

-- Creates a view for use with QGIS 
-- Ccontains a track for each video
-- Point data from the frames table is converted to line data
-- Spacing of vertices is reduced to 10 meters

CREATE VIEW tracks_view AS
SELECT videos.name, frames.ROWID AS ROWID, Simplify(GeomFromText(AsText(MakeLine(frames.geometry)),3857),10) AS geometry
FROM frames, videos
WHERE frames.video_id=videos.id
GROUP BY videos.name;

INSERT INTO views_geometry_columns
(view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
VALUES ('tracks_view', 'geometry', 'rowid', 'frames', 'geometry', 1); 
   


