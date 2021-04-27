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


