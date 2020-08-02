var wms_layers = [];


        var lyr_OpenStreetMap_0 = new ol.layer.Tile({
            'title': 'OpenStreetMap',
            'type': 'base',
            'opacity': 1.000000,
            
            
            source: new ol.source.XYZ({
    attributions: ' ',
                url: 'http://a.tile.openstreetmap.org/{z}/{x}/{y}.png'
            })
        });
var format_Damageindex_1 = new ol.format.GeoJSON();
var features_Damageindex_1 = format_Damageindex_1.readFeatures(json_Damageindex_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_Damageindex_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_Damageindex_1.addFeatures(features_Damageindex_1);
var lyr_Damageindex_1 = new ol.layer.Vector({
                declutter: true,
                source:jsonSource_Damageindex_1, 
                style: style_Damageindex_1,
                interactive: false,
    title: 'Damage index<br />\
    <img src="styles/legend/Damageindex_1_0.png" /> No damage<br />\
    <img src="styles/legend/Damageindex_1_1.png" />  0.0 - 0.5 <br />\
    <img src="styles/legend/Damageindex_1_2.png" />  0.5 - 1.5 <br />\
    <img src="styles/legend/Damageindex_1_3.png" />  1.5 - 2.5 <br />\
    <img src="styles/legend/Damageindex_1_4.png" />  2.5 - 3.5 <br />\
    <img src="styles/legend/Damageindex_1_5.png" />  3.5 - 4.0 <br />'
        });

lyr_OpenStreetMap_0.setVisible(true);lyr_Damageindex_1.setVisible(true);
var layersList = [lyr_OpenStreetMap_0,lyr_Damageindex_1];
lyr_Damageindex_1.set('fieldAliases', {'fid': 'fid', 'left': 'left', 'top': 'top', 'right': 'right', 'bottom': 'bottom', 'id': 'id', 'damage_mean': 'damage_mean', });
lyr_Damageindex_1.set('fieldImages', {'fid': 'TextEdit', 'left': 'TextEdit', 'top': 'TextEdit', 'right': 'TextEdit', 'bottom': 'TextEdit', 'id': 'Range', 'damage_mean': 'TextEdit', });
lyr_Damageindex_1.set('fieldLabels', {'fid': 'no label', 'left': 'no label', 'top': 'no label', 'right': 'no label', 'bottom': 'no label', 'id': 'no label', 'damage_mean': 'no label', });
lyr_Damageindex_1.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});