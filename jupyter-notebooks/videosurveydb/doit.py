import processing
from qgis.utils import iface
from qgis.core import *
#from PyQt4.QtGui import *  
#from PyQt5.QtCore import QSettings, QTranslator, QVersionNumber, QCoreApplication, Qt, QObject, pyqtSignal 
#from PyQt5.QtGui import QIcon 
#from PyQt5.QtWidgets import QAction, QDialog, QFormLayout
from PyQt5.QtGui import *

# Set project CRS to EPSG:3857. This is the one used by OSM and coordinates are in meters.
#QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(3857))

print('Loading OSM')

urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')  

if rlayer.isValid():
    QgsProject.instance().addMapLayer(rlayer)
else:
    print('invalid layer')

print('Load objects layer')

DATADIR = '/home/aubrey/Desktop/roadside/jupyter-notebooks/videosurveydb'

uri = "file://{}/objects.csv?delimiter={}&xField={}&yField={}".format(DATADIR, ",", "lon", "lat")
vlayer = QgsVectorLayer(uri, 'objects', 'delimitedtext')
if not vlayer.isValid():
    print("Layer failed to load!")
else:
    QgsProject.instance().addMapLayer(vlayer)

    # Reproject objects layer from EPSG:4326 to EPSG:3857 so that we can do a spatial join
    print('Reprojecting objects layer.')
    parameters = {'INPUT': 'objects', 'TARGET_CRS': 'EPSG:3857', 'OUTPUT': 'memory:Reprojected'}
    result = processing.run('native:reprojectlayer', parameters)
    QgsProject.instance().addMapLayer(result['OUTPUT'])
    

print('Create grid')

# DON'T RECREATE GRID: JUST LOAD IT

# hexagonal grid

#processing.run("qgis:creategrid", {'TYPE': 4,
#            'EXTENT': '144.61,144.97,13.23,13.67',
#            'HSPACING': 0.01,
#            'VSPACING': 0.01,
#            'CRS': 'ProjectCrs',
#            'OUTPUT': '/home/aubrey/Desktop/roadside/jupyter-notebooks/videosurveydb/grid.shp'  
#             })
#iface.addVectorLayer('grid.shp','grid','ogr')


# rectangular grid

result = processing.run("qgis:creategrid", {'TYPE': 2,
            'EXTENT': '16098000,16137000,1486000,1535000',
            'HSPACING': 1000.0,
            'VSPACING': 1000.0,
            'CRS': 'EPSG:3857',
            'OUTPUT': 'memory:grid'  
             })
QgsProject.instance().addMapLayer(result['OUTPUT'])


print('Create join')
# processing.algorithmHelp("qgis:joinbylocationsummary")

parameters = {
    'INPUT': 'grid',
    'JOIN': 'Reprojected',
    'PREDICATE': 0, # intersects
    'JOIN_FIELDS': 'damage',
    'SUMMARIES': 6, # mean
    'DISCARD_NONMATCHING': True,
    'OUTPUT': 'memory:mean_damage_index'
}
result = processing.run("qgis:joinbylocationsummary", parameters)
QgsProject.instance().addMapLayer(result['OUTPUT'])


#iface.addVectorLayer('mean_damage_index.shp','mean_damage_index','ogr')

print('Style mean damage index')

join_layer = QgsProject.instance().mapLayersByName('mean_damage_index')[0]
target_field = 'damage_mean'

legend = [
    {'low':0.0, 'high':0.0, 'color':'#008000', 'label':'No damage'},
    {'low':0.0, 'high':0.5, 'color':'#00ff00', 'label':'0.0 - 0.5'},
    {'low':0.5, 'high':1.5, 'color':'#ffff00', 'label':'0.5 - 1.5'},
    {'low':1.5, 'high':2.5, 'color':'#ffa500', 'label':'1.5 - 2.5'},
    {'low':2.5, 'high':3.5, 'color':'#ff6400', 'label':'2.5 - 3.5'},
    {'low':3.5, 'high':4.0, 'color':'#ff0000', 'label':'3.5 - 4.0'},
]

myRangeList = []
for i in legend:
    symbol = QgsSymbol.defaultSymbol(join_layer.geometryType())     
    symbol.setColor(QColor(i['color']))                             
    myRangeList.append(QgsRendererRange(i['low'], i['high'], symbol, i['label'], True))                   

myRenderer = QgsGraduatedSymbolRenderer(target_field, myRangeList)  
myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)               

join_layer.setRenderer(myRenderer)

#print('Zoom to grid')
#
#path = 'grid.shp'
#layerName = 'grid'
#
#layer = QgsVectorLayer(path, layerName, 'ogr')
#ex    = layer.extent()
#
## Add a small space/border on each side of the layer
#hborder = ex.height() / 100
#wborder = ex.width() / 100
#ex.set(ex.xMinimum() - wborder, 
#       ex.yMinimum() - hborder, 
#       ex.xMaximum() + wborder, 
#       ex.yMaximum() + hborder
#)
#
## Find out if we need to transform coordinates
#proj = QgsProject.instance()
#if layer.crs().authid() != proj.crs().authid():
#    print("Layer has not the same CRS as proj", 
#          layer.crs().authid(), 
#          proj.crs().authid()
#    )
#    tr = QgsCoordinateTransform(layer.crs(), proj.crs(), proj)
#    ex = tr.transform(ex)
#
#iface.mapCanvas().setExtent(ex)
#iface.mapCanvas().refresh()
#
###
print("FINISHED")


