# Small-target-detection-Longitude-latitude-positioning
## Function  
Small target detection  
Longitude and latitude positioning  
Image registration   
software interface  
gui  

## method  
**Small target detection using k-means clustering algorithm based on color**  
**Image registration with offline maps using cv template matching**  
**Latitude and longitude positioning using folium.LatLngPopup() to click on a html**  
**Drawing UI interface using Qt Designer**  
**Editing UI interface using PyQt5**  

## .ui to .py  
Use the following command in terminal:  
pyuic5 -x gui.ui -o gui.py  

## .py to .exe  
Use the following command in terminal:  
pip install pyinstaller  
pyinstaller --onefile gui.py  
