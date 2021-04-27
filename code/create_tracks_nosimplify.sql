/*
-- Creates a tracks table for use with QGIS 
-- Contains a track for each video
-- Point data from the frames table is converted to line data
-- Spacing of vertices is reduced to 10 meters

Tried to implement this as a view, but this does not seem possible. See: 
https://gis.stackexchange.com/questions/232479/how-to-make-a-spatialite-view-with-geometries-for-qgis-based-on-two-table 
*/

DROP TABLE IF EXISTS tracks;

CREATE TABLE tracks AS
SELECT videos.name, frames.ROWID AS ROWID, GeomFromText(AsText(MakeLine(frames.geometry)),3857) AS geometry
FROM frames, videos
WHERE frames.video_id=videos.id
GROUP BY videos.name;

SELECT RecoverGeometryColumn('tracks', 'geometry', 3857, 'LINESTRING', 'XY');



