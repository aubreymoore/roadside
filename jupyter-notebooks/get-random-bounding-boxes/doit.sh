# Usage ./doit.sh

# exit when any command fails
set -e

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG

# echo an error message before exiting
trap 'echo "\"${last_command}\" command generated exit code $?."' EXIT

NOTEBOOK="reports/job27.ipynb"
papermill --prepare-only get-random-bounding-boxes.ipynb $NOTEBOOK -y '{"NSAMPLES":"10"}' 
jupyter nbconvert --execute --to html $NOTEBOOK

# Commit changes to GitHub

cd ~/Desktop/roadside
git config --global credential.helper store
git add .
git commit -m 'automated push'
git push


