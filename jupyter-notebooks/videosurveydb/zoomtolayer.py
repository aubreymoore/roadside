vLayer = iface.activeLayer()
canvas = iface.mapCanvas()
extent = vLayer.extent()
canvas.setExtent(extent)
