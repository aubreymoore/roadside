DROP TABLE IF EXISTS tree_location;

CREATE TABLE tree_location AS
SELECT trees.id, damage_index, frames.geometry
FROM trees, frames
WHERE trees.frame_id=frames.id;

SELECT RecoverGeometryColumn('tree_location', 'geometry', 3857, 'POINT', 'xy');
