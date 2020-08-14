def loadMap():
    if not 'MapMyGuam' in [layer.name() for layer in QgsProject.instance().mapLayers().values()]:
        urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/{z}/{x}/{y}.png&crs=EPSG3857'
        rlayer = QgsRasterLayer(urlWithParams, 'MapMyGuam', 'wms')
        QgsProject.instance().addMapLayer(rlayer)
    rlayer = QgsProject.instance().mapLayersByName('MapMyGuam')[0]
    canvas = iface.mapCanvas()
    rect = QgsRectangle(16098000.0, 1486000.0, 16137000.0, 1535000.0)
    canvas.setExtent(rect)
    canvas.update()
    rlayer.triggerRepaint()

action = QAction(QIcon(""), "Load Guam", iface.mainWindow())
iface.addToolBarIcon(action)
action.triggered.connect(loadMap)
# Or to connect to a button on your plugin
#self.dlg.pushButton.clicked.connect(self.loadMap)