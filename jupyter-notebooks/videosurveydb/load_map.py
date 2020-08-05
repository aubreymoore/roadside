def loadMap():
    if not 'MapMyIndia' in [layer.name() for layer in QgsProject.instance().mapLayers().values()]:
        urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/{z}/{x}/{y}.png&crs=EPSG3857'
        rlayer = QgsRasterLayer(urlWithParams, 'MapMyIndia', 'wms')
        QgsProject.instance().addMapLayer(rlayer)
    rlayer = QgsProject.instance().mapLayersByName('MapMyIndia')[0]
    canvas = iface.mapCanvas()
    rect = QgsRectangle(7589389.42, 889589.56, 10842803.55, 4231219.37)
    canvas.setExtent(rect)
    canvas.update()
    rlayer.triggerRepaint()
    
loadMap()

#action = QAction(QIcon(""), "Load India", iface.mainWindow())
#iface.addToolBarIcon(action)
#action.triggered.connect(loadMap)
# Or to connect to a button on your plugin
#self.dlg.pushButton.clicked.connect(self.loadMap)