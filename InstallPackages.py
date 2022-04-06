#This program will automatically install all the packages needed for lightingControl.py to run.

import subprocess
import os
import sys

def resetColor():
    #change print color to white
    print("\033[0;0m", '\r', end="")

#change print color to blue
print("\033[94m", end="")
print("Checking for pip...")
resetColor()
#call apt upgrade
#subprocess.call(["sudo", "apt", "update"])
#subprocess.call(["sudo", "apt-get", "install", "python3-pip"])


required_modules = ["rpi_ws281x", "adafruit-circuitpython-neopixel", "adafruit-blinka", "numpy", "pynetworktables"] 


#change print color to blue
print("\033[94m", end="")
print("Checking for required modules...")
resetColor()

#create a for loop to access each module, with an indice
for i in range(len(required_modules)):
    #change print color to blue
    print("\033[94m", end="")
    print("Checking for " + required_modules[i] + " (" + str(i+1) + "/" + str(len(required_modules)) + ")")
    resetColor()
    subprocess.call([sys.executable, "-m", "pip", "install", required_modules[i]])

#change print color to green
print("\033[92m", end="")
print("All packages have been tried.")
#change print color to yellow
print("\033[93m", end="")
print("Packages may or may not have been installed correctly.")
resetColor()

#run the program
print("Running lightingControl.py...")
subprocess.call([sys.executable, "lightingControl.py"])