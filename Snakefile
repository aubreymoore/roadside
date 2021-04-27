"""
Reference: endreback.gitbooks.io/the-snake-make-book/content/

Notes:

To detect objects in videos:
    snakemake -j1 detect_objects --dry-run

To run all rules except detect_objects:
    snakemake -j1 --omit-from detect_objects --dry-run

Create rulegraph:
    snakemake --forceall --rulegraph | dot -Tpdf > dag.pdf

Delete the survey database and flags.
    snakemake -j1 delete_db
"""

date_times, = glob_wildcards('rawdata/{id}.mp4')
#xml_date_times, = glob_wildcards('output/{id}.xml')
#print(f'date_times: {date_times}')

rule all:
    input:
        expand('output/{dt}a.mp4', dt=date_times),
        'output/spatialite.db',
        'flags/video2db.done',
        expand('flags/{dt}.cvatxml2db.done', dt=date_times),
        expand('notebooks/georef_{dt}.ipynb',dt=date_times),
        #'flags/cvatxml2db.done',
        #'flags/create_tracks.done',
        'flags/update_trees_table.done',
        'flags/create_tree_location_table.done',
        'flags/create_views.done',
        'flags/create_grid.done',
        'flags/create_stats_table.done'

# Detect CRB damage in each frame of a video
rule detect_objects:
    input:  'rawdata/{date_time}.mp4'
    output: 'output/{date_time}a.mp4', 'output/{date_time}.xml'
    log:    'output/{date_time}.log'
    shell:
        'cd code && python3 demo.py --dump_sql False --video ../{input} --num_frame 0 --skip_no 5 --output_dir ../output &>> {log}'

# Create a SpatialLite survey database.
rule create_db:
    output: 'output/spatialite.db'
    shell:  'spatialite {output} < code/create_tables2.sql'

# Populate the videos db table.
rule video2db:
    input: 'output/spatialite.db'
    output: touch('flags/video2db.done')
    shell:  'python3 code/video2db.py --data-dir rawdata --db-path {input}'

# Populate the frames db table with timestamp(UTC) and geographic coordinates.
# Also populates tracks table with a record for each video
rule georef:
    input:  'rawdata/{dt}.mp4', 'output/spatialite.db', 'flags/video2db.done'
    output: 'notebooks/georef_{dt}.ipynb'
    shell:  'papermill code/georef.ipynb {output[0]} -p video_path {input[0]} -p db_path {input[1]}'

# Populate trees and vcuts db tables using data in a CVAT XML file.'flags/{date_time}.cvatxml2db.done'
rule cvatxml2db:
    input:  'output/{dt}.xml', 'output/spatialite.db', 'notebooks/georef_{dt}.ipynb'
    output: touch('flags/{dt}.cvatxml2db.done')
    shell: 'python3 code/cvatxml2db.py {input[0]} output/spatialite.db'

rule update_trees_table:
    input:  expand('flags/{dt}.cvatxml2db.done', dt=date_times)
    output: touch('flags/update_trees_table.done')
    shell:  'spatialite output/spatialite.db < code/update_trees_table.sql'

rule create_tree_location_table:
    input: 'flags/update_trees_table.done'
    output: touch('flags/create_tree_location_table.done')
    shell: 'spatialite output/spatialite.db < code/create_tree_location_table.sql'

rule create_views:
    input: 'flags/create_tree_location_table.done'
    output: touch('flags/create_views.done')
    shell: 'spatialite output/spatialite.db < code/create_views.sql'

# Create crb-damage grid (mean_damage_index table)
rule create_grid:
    input:  'flags/create_views.done'
    output: touch('flags/create_grid.done')
    shell:  'spatialite output/spatialite.db < code/create_grid.sql'

rule create_stats_table:
    input:  'flags/create_grid.done'
    output: touch('flags/create_stats_table.done')
    shell:  'spatialite output/spatialite.db < code/create_stats_table.sql'

# Utlity rule to delete the survey database, flags and notebooks.
rule delete_db:
    shell: 'rm -f output/spatialite.db flags/* notebooks/*'

# # Make map.
# rule create_map:
#     input: 'flags/create_grid.done', 'flags/create_tracks.done'
#     output: 'map/dbpath.txt'
#     shell:
#         """
#         mkdir -p map
#         cd map
#         echo output/Guam03.db > dbpath.txt
#         qgis --nologo --code ../code/make-crb-damage-map1.py
#         """
