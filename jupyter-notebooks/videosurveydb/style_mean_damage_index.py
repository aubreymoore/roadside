join_layer = QgsProject.instance().mapLayersByName('mean_damage_index')[0]
target_field = 'damage_mea'

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

print("Graduated color scheme applied")


