# Using QGIS 3.4.4
mkdir testqgis
cd testqgis
wget https://github.com/aubreymoore/roadside/raw/master/jupyter-notebooks/videosurveydb/objects.csv
wget https://github.com/aubreymoore/roadside/raw/master/jupyter-notebooks/videosurveydb/doit.py
qgis --nologo --code doit.py
# Wait for QGIS to finish processing doit.py. Will take a few minutes.
# Right click on mean_damage_index layer and select Zoom to layer
# Use the Export to Webmap plugin (not yet automated)
