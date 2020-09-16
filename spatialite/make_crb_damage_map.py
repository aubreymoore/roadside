# qgis --codepath make_crb_damage_map.py

# This script is not yet complete.

# After it gas run, zoom to the mean_damage_index layer.

# Use the qgis2web plugin to make an interactive web map
# leaflet; Add layer list: expanded; extnet: fit layers extent; template:full_screen
# Upload /tmp/qgis2web/qgis2web/qgis2web_2020_09_16-06_58_26_614131 to
# https://github.com/aubreymoore/Guam-CRB-damage-map

def load_guam_osm():
    canvas = iface.mapCanvas()
    url = 'type=xyz&url=https://a.tile.openstreetmap.org/{z}/{x}/{y}.png&crs=EPSG3857'
    rlayer = QgsRasterLayer(url, 'Guam', 'wms')
    QgsProject.instance().addMapLayer(rlayer)
    rect = QgsRectangle(16098000.0, 1486000.0, 16137000.0, 1535000.0)
    canvas.setExtent(rect)
    canvas.update()


def load_layer_from_db(table_name):
    uri = QgsDataSourceUri()
    uri.setDatabase('/home/aubrey/Documents/populate_spatialite/videosurvey.db')
    schema = ''
    table = table_name
    geom_column = 'geometry'
    uri.setDataSource(schema, table, geom_column)
    display_name = table_name
    vlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
    QgsProject.instance().addMapLayer(vlayer)


def style_mean_damage_index():
    mean_damage_index_layer = QgsProject.instance().mapLayersByName(
        'mean_damage_index')[0]
    target_field = 'mean_damage_index'
    legend = [
        {'low': 0.0, 'high': 0.0, 'color': '#008000', 'label': 'No damage'},
        {'low': 0.0, 'high': 0.5, 'color': '#00ff00', 'label': '0.0 - 0.5'},
        {'low': 0.5, 'high': 1.5, 'color': '#ffff00', 'label': '0.5 - 1.5'},
        {'low': 1.5, 'high': 2.5, 'color': '#ffa500', 'label': '1.5 - 2.5'},
        {'low': 2.5, 'high': 3.5, 'color': '#ff6400', 'label': '2.5 - 3.5'},
        {'low': 3.5, 'high': 4.0, 'color': '#ff0000', 'label': '3.5 - 4.0'},
    ]
    myRangeList = []
    for i in legend:
        symbol = QgsSymbol.defaultSymbol(mean_damage_index_layer.geometryType())
        symbol.setColor(QColor(i['color']))
        myRangeList.append(QgsRendererRange(
            i['low'], i['high'], symbol, i['label'], True))
    myRenderer = QgsGraduatedSymbolRenderer(target_field, myRangeList)
    myRenderer.setMode(QgsGraduatedSymbolRenderer.Custom)
    mean_damage_index_layer.setRenderer(myRenderer)

    
def style_tracks_layer():
    tracks_layer = QgsProject.instance().mapLayersByName('tracks')[0]
    tracks_layer.renderer().symbol().setWidth(1)
    tracks_layer.renderer().symbol().setColor(QColor(255,0,0))
  

def style_vcuts_view_layer():
    vcuts_view_layer = QgsProject.instance().mapLayersByName('vcuts_view')[0]
    vcuts_view_layer.renderer().symbol().setColor(QColor(255,0,255))

    
# MAIN

load_guam_osm()
load_layer_from_db('tracks')
load_layer_from_db('mean_damage_index')
load_layer_from_db('vcuts_view')
style_mean_damage_index()
style_tracks_layer()
style_vcuts_view_layer()


