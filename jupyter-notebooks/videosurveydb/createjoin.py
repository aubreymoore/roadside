print('started')
parameters = {
    'INPUT': 'grid',
    'JOIN': 'objects',
    'PREDICATE': 0, # intersects
    'JOIN_FIELDS': 'damage',
    'SUMMARIES': 6, # mean
    'DISCARD_NONMATCHING': True,
    'OUTPUT': '/home/aubrey/Desktop/roadside/jupyter-notebooks/videosurveydb/mean_damage_index.shp'
}
processing.run("qgis:joinbylocationsummary", parameters)
print(finished)
