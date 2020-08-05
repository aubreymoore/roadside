import os # This is is needed in the pyqgis console also
from qgis.core import QgsVectorLayer

DATADIR = '/home/aubrey/Desktop/roadside/jupyter-notebooks/videosurveydb'

uri = "file://{}/objects.csv?delimiter={}&xField={}&yField={}".format(DATADIR, ",", "lon", "lat")
vlayer = QgsVectorLayer(uri, 'objects', 'delimitedtext')
if not vlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(vlayer)
