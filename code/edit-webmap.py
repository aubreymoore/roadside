"""
Run this script within the web map folder

python3 /home/aubrey/Documents/roadside/code/edit_webmap.py
"""

import re
import plac
import matplotlib.pyplot as plt

def bake_pie(survey_folder):
    data = {'0 No damage':9282,
            '1 Light damage':38944,
            '2 Medium damage':7458,
            '3 High damage':1063,
            '4 Moribund or dead': 519
            }
    colors = ['#00ff00', '#ffff00', '#ffa500', '#ff6400', '#ff0000']

    data1 = {'not damaged': 9282, 'damaged': 38994+7458+1063+519}
    colors1 = ['white', 'lightgrey']

    plt.pie(x=data.values(),
            colors=colors,
            labels=data.keys(),
            autopct='%1.0f%%',
            pctdistance=0.85,
            counterclock=False,
            rotatelabels=True,
            shadow=True
            )
    plt.pie(x=data1.values(),
            colors=colors1,
            radius=0.75,
            counterclock=False,
            rotatelabels=True
            )
    percent_damaged = 100*data1['damaged']/(data1['damaged']+data1['not damaged'])
    plt.text(0,0,f'{percent_damaged:.0f}%\ndamaged\ntrees', horizontalalignment='center', verticalalignment='center',
             fontsize=28)
    fig = plt.gcf()
    plt.savefig(f'{survey_folder}/images/pie.svg')


@plac.opt('original_index',abbrev='i')
@plac.opt('survey_folder',abbrev='s')
def main(original_index='/tmp/qgis2web/qgis2web_2020_10_29-14_53_58_467543/index.html',
         survey_folder='/home/aubrey/Desktop/Guam-CRB-damage-map-2020-10'):

    bake_pie(survey_folder)

    abstract =  '<b>Coconut Rhinoceros Beetle Damage</b><br>'
    abstract += '<b>Guam Roadside Video Survey 1</b><br><br>'
    abstract += '<table>'
    abstract += '<tr><td>Start date:</td><td  style="text-align:right">2020-10-01</td></tr>'
    abstract += '<tr><td>End date:</td><td  style="text-align:right">2020-10-22</td></tr>'
    abstract += '<tr><td>Video frames examined:</td><td style="text-align:right">174,944</td></tr>'
    abstract += '<tr></tr>'
    abstract += '<tr><td><b>V-cuts detected:</b></td><td style="text-align:right"><b>12,089</b></td></tr>'
    abstract += '<tr></tr>'
    abstract += '<tr><td>Coconut palm images:</td><td style="text-align:right">57,666</td></tr>'
    abstract += '<tr><td>0 No damage:</td><td style="text-align:right">9,282</td></tr>'
    abstract += '<tr><td>1 Light damage:</td><td style="text-align:right">38,944</td></tr>'
    abstract += '<tr><td>2 Medium damage:</td><td style="text-align:right">7,458</td></tr>'
    abstract += '<tr><td>3 High damage:</td><td style="text-align:right">1,063</td></tr>'
    abstract += '<tr><td>4 Moribund or dead:</td><td style="text-align:right">519</td></tr>'
    abstract += '<tr><td><b>Mean damage index:</td><td style="text-align:right"><b>1.025</b></td></tr>'
    abstract += '</table>'
    abstract += '<img src="images/pie.svg" width="350">'
    abstract += '<br>Data source:'
    abstract += '<br><a href="https:/github.com/aubreymoore/Guam-CRB-damage-map-2020-10">https:/github.com/aubreymoore/Guam-CRB-damage-map-2020-1</a>'

    # Load string with file contents
    filepath = '/tmp/qgis2web/qgis2web_2020_10_29-14_53_58_467543/index.html'
    with open(original_index, 'r') as f:
        s = f.read()

    # Change fillOpacity for mean_damage_index symbology
    s = re.sub(r"(feature\.properties\['mean_damage_index'\][\S\s]*?)(fillOpacity: 1)", r'\1fillOpacity: 0.75', s)

    # Change width of the abstract box
    s = re.sub(r"(\<style\>)", r"\1\n.abstractUncollapsed {max-width: 100%;}", s)

    # Change abstract text
    s = re.sub(r"(div.classList.add\(\"abstractUncollapsed\"\);\s+this._div.innerHTML = ')(.*)(';)", f'\\1{abstract}\\3', s)

    # Disable hiding abstract: comment 2 lines and change another
    s = re.sub(r"(this._div.setAttribute)", r'//\1', s)
    s = re.sub(r"this.hide", r'this.show', s)

    filepath = f'{survey_folder}/index.html'
    with open(filepath, 'w') as f:
        f.write(s)

if __name__ == '__main__':
    plac.call(main)