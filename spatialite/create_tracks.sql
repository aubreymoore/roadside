CREATE TABLE tracks (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL);

SELECT AddGeometryColumn('tracks', 'Geometry', 3857, 'LINESTRING', 'XY');

INSERT INTO first_table_name [(column1, column2, ... columnN)] 
   SELECT column1, column2, ...columnN 
   FROM second_table_name
   [WHERE condition];

INSERT INTO tracks (name, Geometry)
SELECT videos.name, ST_Simplify(GeomFromText(AsText(MakeLine(frames.geometry)),3857),10) AS geometry
FROM frames, videos
WHERE frames.video_id=videos.id
GROUP BY videos.name;   
