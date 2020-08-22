from glob import glob

#root = QgsProject.instance().layerTreeRoot()
#group = root.addGroup('Routes')
#
geojsonlist = glob('*.geojson')
for f in geojsonlist:
    vlayer = QgsVectorLayer(f, f, 'ogr')
    QgsProject.instance().addMapLayer(vlayer, True)
#    group.insertChildNode(1, QgsLayerTreeLayer(f))
#    

