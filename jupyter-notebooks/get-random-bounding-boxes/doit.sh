# Usage ./doit.sh

# PREP

# Manually dump annotations from https://app.cnas-re-uog.onepanel.io/crb/workspaces/cvat-5-classes
# and download and save in <DATADIR>/<CVATXMLFILE>

# Get the VIDEOFILE name from the netadata section of CVATXMLFILE 
# Download VIDEFILE from S3 save in <DATADIR>/<VIDEOFILE>
# aws s3 cp s3://cnas-re.uog.onepanel.io/raw-input/raw_input_processed/20200630_134257_processed.mp4 .

# SETUP

# exit when any command fails
set -e
# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command generated exit code $?."' EXIT

# Ensure output directory exists (nothing is over-written if it does)
mkdir -p reports/job28

# ASSIGN VARIABLES

NOTEBOOK="reports/job28/job28.ipynb"

# EXECUTE

papermill --prepare-only get-random-bounding-boxes.ipynb $NOTEBOOK -y "
DATADIR: /media/aubrey/9C33-6BBD/job28
CVATXMLFILE: DONT-ANNOTATE-06-30-2020-134257-5-class-inference.xml
VIDEOFILE: 20200630_134257_processed.mp4
NSAMPLES: 10
REPORTURL: https://raw.githubusercontent.com/aubreymoore/roadside/master/jupyter-notebooks/get-random-bounding-boxes/reports
REPORTDIR: job28"
 
jupyter nbconvert --execute --to html $NOTEBOOK

# Commit changes to GitHub

cd ~/Desktop/roadside
git config --global credential.helper store
git pull
git add .
git commit -m 'automated push'
git push


