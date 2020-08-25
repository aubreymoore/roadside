"""

# Input files

* {date}_trees.csv
* {date}_vcuts.csv
* {datetime}geojson One for each video

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
from sqlalchemy import create_engine
import pandas as pd
import os

DATADIR = '/home/aubrey/Desktop/roadside/jupyter-notebooks/videosurveydb'
VIDEOLIST = ['20200630_131814.mp4', '20200630_132859.mp4', '20200630_133212.mp4',
    '20200630_134257.mp4', '20200703_121802.mp4', '20200703_122847.mp4',
    '20200703_124043.mp4', '20200703_125239.mp4', '20200703_130434.mp4',
    '20200703_131630.mp4', '20200703_132826.mp4', '20200706_120855.mp4',
    '20200706_122002.mp4', '20200706_123047.mp4', '20200706_124645.mp4',
    '20200706_125730.mp4', '20200706_130926.mp4', '20200706_132122.mp4',
    '20200706_133318.mp4']
    
#VIDEOLIST = ['20200703_124043.mp4', '20200703_125239.mp4', '20200703_130434.mp4',
#    '20200703_131630.mp4', '20200703_132826.mp4']

    
def video_list_string():
    return ','.join("'{}'".format(v) for v in VIDEOLIST)


def connect_to_db():
    engine = create_engine('mysql+pymysql://{}:{}@mysql.guaminsects.net/videosurvey'.format('readonlyguest', 'readonlypassword'))
    conn = engine.connect()
    return conn


################################################################################
# Get data from the database and write to files 
################################################################################


def write_geojson_files():
    """
    Writes all geojson strings from the videos database table to text files named like
    20200630_131814.geojson
    Input paramater is a date sting in the form '20200630'
    """
    sql = """
    SELECT video_id, gps_track_json
    FROM videos 
    WHERE video_id IN ({});
    """.format(video_list_string());
    df = pd.read_sql_query(sql, conn)
    for index, row in df.iterrows():
        filename = row.video_id.replace('.mp4', '.geojson')
        cwd = os.getcwd()
        filename = '{}/{}'.format(DATADIR, filename)
        print('writing {}'.format(filename))
        with open(filename, 'w') as f:
            f.write(row.gps_track_json)


def write_trees_csv():
    """
    Writes tree data to a CSV
    """
    sql = """SELECT frames.frame_id, lat, lon, damage 
             FROM videos, frames, trees 
             WHERE 
             videos.video_id=frames.video_id
             AND frames.frame_id=trees.frame_id
             AND videos.video_id IN ({});
          """.format(video_list_string())
    df = pd.read_sql_query(sql, conn)
    filename = '{}/trees.csv'.format(DATADIR)
    df.to_csv(filename, index=False)


def write_vcuts_csv():
    """
    Writes vcut data to a CSV
    """
    sql = """SELECT frames.frame_id, lat, lon 
             FROM videos, frames, vcuts 
             WHERE 
             videos.video_id=frames.video_id
             AND frames.frame_id=vcuts.frame_id 
             AND videos.video_id IN ({});
          """.format(video_list_string())
    df = pd.read_sql_query(sql, conn)
    filename = '{}/vcuts.csv'.format(DATADIR)
    df.to_csv(filename, index=False)


def get_data_from_db():
    write_geojson_files()
    write_trees_csv()
    write_vcuts_csv()


################################################################################
# Load layers
################################################################################


def load_guam_osm():
    canvas = iface.mapCanvas()
    urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/{z}/{x}/{y}.png&crs=EPSG3857'
    rlayer = QgsRasterLayer(urlWithParams, 'Guam', 'wms')
    QgsProject.instance().addMapLayer(rlayer)
    rect = QgsRectangle(16098000.0, 1486000.0, 16137000.0, 1535000.0)
    canvas.setExtent(rect)
    canvas.update()


def load_tracks_layers(): 
    geojsonlist = [filename.replace('.mp4', '.geojson') for filename in VIDEOLIST]
    for f in geojsonlist:
        vlayer = QgsVectorLayer(f, f, 'ogr')
        QgsProject.instance().addMapLayer(vlayer, True)
        vlayer.renderer().symbol().setWidth(1)
        vlayer.renderer().symbol().setColor(QColor('#ff0000'))
        vlayer.triggerRepaint()


def load_trees_layer():
    uri = "file://{}/trees.csv?delimiter=,&xField=lon&yField=lat&crs=epsg:4326".format(DATADIR)
    vlayer = QgsVectorLayer(uri, 'trees', 'delimitedtext')
    if vlayer.isValid():
        QgsProject.instance().addMapLayer(vlayer)

        # Reproject objects layer from EPSG:4326 to EPSG:3857 so that we can do a spatial join
        print('Reprojecting objects layer.')
        parameters = {'INPUT': 'trees', 'TARGET_CRS': 'EPSG:3857', 'OUTPUT': 'memory:Reprojected'}
        result = processing.run('native:reprojectlayer', parameters)
        QgsProject.instance().addMapLayer(result['OUTPUT'])
    else:
        print("ERROR: trees layer failed to load!")


def load_vcuts_layer():
    uri = "file://{}/vcuts.csv?delimiter={}&xField={}&yField={}&crs=epsg:4326".format(DATADIR, ",", "lon", "lat")
    vlayer = QgsVectorLayer(uri, 'vcuts', 'delimitedtext')
    if vlayer.isValid():
        QgsProject.instance().addMapLayer(vlayer)
    else:
        print("ERROR: vcut layer failed to load!")


################################################################################
# Other stuff
################################################################################


def set_layer_visibility(layer_name, True_or_False):
    prj = QgsProject.instance()
    layer = prj.mapLayersByName(layer_name)[0]
    prj.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(True_or_False)
    

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


def get_video_list():
    return pd.read_sql_query("SELECT video_id FROM videos ORDER BY video_id;", conn)
    

def cleanup():
    project = QgsProject.instance()

    # zoom to mean_damage_index layer - NOT WORKING
    layer = QgsProject.instance().mapLayersByName('mean_damage_index')[0]
    canvas = qgis.utils.iface.mapCanvas()
    canvas.setExtent(layer.extent())

    #delete grid layer
    to_be_deleted = project.mapLayersByName('grid')[0]
    project.removeMapLayer(to_be_deleted.id())

    #delete trees layer
    to_be_deleted = project.mapLayersByName('trees')[0]
    project.removeMapLayer(to_be_deleted.id())

    #change name of layer from Reprojected to trees
    to_be_renamed = project.mapLayersByName('Reprojected')[0]
    to_be_renamed.setName('trees')

    #style trees layer; set color to #00ff00
    layer = project.mapLayersByName('trees')[0]
    layer.renderer().symbol().setColor(QColor(0,255,0))
    layer.triggerRepaint()

    #style vcuts; set color to #ff00ff
    layer = project.mapLayersByName('vcuts')[0]
    layer.renderer().symbol().setColor(QColor(255,0,255))
    layer.triggerRepaint()


################################################################################
# MAIN
################################################################################

# Set project CRS to EPSG:3857. This is the one used by OSM and coordinates are in meters.
#QgsProject.instance().setCrs(QgsCoordinateReferenceSystem(3857))

conn = connect_to_db()
get_data_from_db()
load_guam_osm()
load_tracks_layers()
load_trees_layer()
create_grid()
create_join()
style_mean_damage_index()
load_vcuts_layer()
cleanup()


print("FINISHED")

