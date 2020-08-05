urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')  

if rlayer.isValid():
    QgsProject.instance().addMapLayer(rlayer)
else:
    print('invalid layer')