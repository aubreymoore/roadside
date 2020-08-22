"""

# Clean up

* Put all the **geojson** layers into a group called **tracks** and edit style
* rename **reprojected** layer to **camera positions**
* remove **objects** layer
* remove **grid** layer

# Generate web map

* make canvas as small as posible QGIS gui
* web | qgis2web | Create web map
* Select Leaflet in the radio buttons at bottom of dialog
* Appearance | Appearance | Add layers list: collapsed

"""

from glob import glob
import processing
from qgis.utils import iface
from qgis.core import *
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt, QRectF
from PyQt5.QtGui import *

#from qgis.core import (
#    QgsVectorLayer,
#    QgsPoint,
#    QgsPointXY,
#    QgsProject,
#    QgsGeometry,
#    QgsMapRendererJob,
#)
#
#from qgis.gui import (
#    QgsMapCanvas,
#    QgsVertexMarker,
#    QgsMapCanvasItem,
#    QgsRubberBand,
#)
#
#
##from PyQt4.QtGui import *  
#from PyQt5.QtCore import QSettings, QTranslator, QVersionNumber, QCoreApplication, Qt, QObject, pyqtSignal 
#from PyQt5.QtGui import QIcon 
#from PyQt5.QtWidgets import QAction, QDialog, QFormLayout

DATADIR = '/home/aubrey/Desktop/roadside/jupyter-notebooks/videosurveydb'

def set_layer_visibility(layer_name, True_or_False):
    prj = QgsProject.instance()
    layer = prj.mapLayersByName(layer_name)[0]
    prj.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True_or_False)
    
   # Set project CRS to EPSG:3857. This is the one used by OSM and coordinates are in meters.
QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(3857))

def load_guam_osm():
    canvas = iface.mapCanvas()
    urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/{z}/{x}/{y}.png&crs=EPSG3857'
    rlayer = QgsRasterLayer(urlWithParams, 'Guam', 'wms')
    QgsProject.instance().addMapLayer(rlayer)
    rect = QgsRectangle(16098000.0, 1486000.0, 16137000.0, 1535000.0)
    canvas.setExtent(rect)
    canvas.update()


def load_objects_layer():
    uri = "file://{}/objects.csv?delimiter={}&xField={}&yField={}&crs=epsg:4326".format(DATADIR, ",", "lon", "lat")
    vlayer = QgsVectorLayer(uri, 'objects', 'delimitedtext')
    if vlayer.isValid():
        QgsProject.instance().addMapLayer(vlayer)

        # Reproject objects layer from EPSG:4326 to EPSG:3857 so that we can do a spatial join
        print('Reprojecting objects layer.')
        parameters = {'INPUT': 'objects', 'TARGET_CRS': 'EPSG:3857', 'OUTPUT': 'memory:Reprojected'}
        result = processing.run('native:reprojectlayer', parameters)
        QgsProject.instance().addMapLayer(result['OUTPUT'])
    else:
        print("Layer failed to load!")


def create_grid():
    result = processing.run("qgis:creategrid", {'TYPE': 2,
                'EXTENT': '16098000,16137000,1486000,1535000',
                'HSPACING': 1000.0,
                'VSPACING': 1000.0,
                'CRS': 'EPSG:3857',
                'OUTPUT': 'memory:grid'  
                 })
    QgsProject.instance().addMapLayer(result['OUTPUT'])


def create_join():
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


def style_mean_damage_index():
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

    
def zoom_to_guam():
    rect = QgsRectangle(16098000.0, 1486000.0, 16137000.0, 1535000.0)
    canvas = iface.mapCanvas()
    canvas.setExtent(rect)
    canvas.refresh()


def add_track_geojsons():    
    geojsonlist = glob('*.geojson')
    for f in geojsonlist:
        vlayer = QgsVectorLayer(f, f, 'ogr')
        QgsProject.instance().addMapLayer(vlayer, True)
    

# MAIN

load_guam_osm()
add_track_geojsons()
#load_guam_osm()
#zoom_to_guam()
load_objects_layer()
create_grid()
create_join()
style_mean_damage_index()

set_layer_visibility('grid', False)
set_layer_visibility('Reprojected', False)
set_layer_visibility('objects', False)


print("FINISHED")

