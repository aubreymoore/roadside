# Crates a new Spltialite database for roadside video surveys of CRB damage

# Usage:

# ./createdb.sh ~/Desktop/Guam01/test.db

spatialite $1 < create_tables.sql
spatialite $1 < create_views.sql
#spatialite $1 < create_grid.sql

