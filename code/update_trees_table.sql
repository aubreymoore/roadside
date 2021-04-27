BEGIN TRANSACTION;

CREATE TEMP TABLE trees_vcuts AS
    SELECT
        trees.frame_id, 
        trees.id AS tree_id, 
        trees.damage_index, 
        vcuts.id As tree_cut_id, 
        ST_Intersects(ST_Envelope(trees.geometry),vcuts.geometry) AS tree_intersects_vcut
    FROM trees
    LEFT JOIN vcuts ON trees.frame_id=vcuts.frame_id;

CREATE TEMP TABLE tree_vcut_count AS
    SELECT tree_id, damage_index, SUM(tree_intersects_vcut>0) AS vcut_count 
    FROM trees_vcuts
    GROUP BY tree_id;

ALTER TABLE trees ADD vcut_count;

UPDATE trees
  SET vcut_count = ( 
    SELECT vcut_count 
    FROM tree_vcut_count 
    WHERE tree_id = trees.id);

UPDATE trees
SET damage_index=1
WHERE damage_index=0 AND vcut_count>0;

UPDATE trees
SET damage_index=0
WHERE damage_index=1 AND vcut_count=0;

UPDATE trees
SET damage_index=0
WHERE damage_index=2 AND vcut_count=0;

COMMIT;
