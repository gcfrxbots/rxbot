echo You need to have Python 3.7 (and the included PIP package) installed for this to work! You also need VLC to be installed. Click OK to install all required packages.
pause
cd ./pafy
py -3.7 -m pip install ./ --user
cd ..
py -3.7 -m pip install -r requirements.txt --user --no-warn-script-location

py -3.7 ../RxBot/Settings.py --g


pause