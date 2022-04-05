from ast import pattern
from calendar import leapdays
from typing import Pattern
from networktables import NetworkTables
import logging
import sys
import time
import os
import numpy as np
from pygame import PixelArray

PURPLE = (148, 0, 211)
YELLOW = (255,255,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)

#Local librarys to contain functions better
import Patterns

# import board
# import neopixel

# Setup networktables and logging
logging.basicConfig(level=logging.DEBUG)
ip = "127.0.0.1"  # default ip
# Initialize NetworkTables
NetworkTables.initialize(server=ip)
# Get the NetworkTables instances
SD = NetworkTables.getTable("SmartDashboard")
FMS = NetworkTables.getTable("FMSInfo")

BumperLEDCount = 80
IntakeLEDCount = 80
TotalLEDS = (4 * IntakeLEDCount) + (2 * BumperLEDCount)
# pixels = neopixel.NeoPixel(TotalLEDS)

# define bumper LED Zone start and end
LeftBumperZoneStart = 0
LeftBumperZoneEnd = BumperLEDCount - 1
LeftBumperZone = [BumperLEDCount]
# Fill LeftBumperZone with (BLACK) using numpy
LeftBumperZone = np.zeros((BumperLEDCount, 3), dtype=int)

RightBumperZoneStart = BumperLEDCount
RightBumperZoneEnd = 2 * BumperLEDCount - 1
RightBumperZone = [BumperLEDCount]
# Fill RightBumperZone with (BLACK) using numpy
RightBumperZone = np.zeros((BumperLEDCount, 3), dtype=int)

IntakeZoneStart = 2 * BumperLEDCount
IntakeZoneEnd = 2 * BumperLEDCount + (IntakeLEDCount * 4) - 1
IntakeZone = [IntakeLEDCount]
# Fill IntakeZone with (BLACK) using numpy
IntakeZone = np.zeros((IntakeLEDCount, 3), dtype=int)

# create a function that takes in arrays and outputs a single merged array
def mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone):
    # merge the arrays
    LEDArray = np.concatenate(
        (LeftBumperZone, RightBumperZone, np.tile(IntakeZone, (4, 1)))
    )
    return LEDArray

def pushLEDs():
    pixels = mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone)
    sendLEDToNetworkTables(pixels)
    #pixels.show()
    pass

# define a function that takes in a array of (r,g,b) values and sends that to the network tables with the prefix "neopixel"
def sendLEDToNetworkTables(LEDArray):
    for i in range(len(LEDArray)):
        SD.putNumberArray("neopixel" + str(i), LEDArray[i])
    SD.putValue('BumperLength', BumperLEDCount)
    SD.putValue('IntakeLength', IntakeLEDCount)
    pass

#The FMS Control word is a 8 bit integer
#The first bits purpose is Unknown
#the second bits purpose is Unknown
#the third bits purpose is Driver station Connection
#the fourth bits purpose is FMS Connection
#the fifth bits purpose is Teleop
#the sixth bits purpose is Test
#the seventh bits purpose is Autonomous
#the eighth bits purpose is Enabled
#this function takes in a FMS Control word and decodes it into global variables
DSConnection_Flag = False
FMSConnection_Flag = False
Teleop_Flag = False
Test_Flag = False
Autonomous_Flag = False
Enabled_Flag = False
IsRed = True
def decodeFMSData():
    global DSConnection_Flag
    global FMSConnection_Flag
    global Teleop_Flag
    global Test_Flag
    global Autonomous_Flag
    global Enabled_Flag
    global IsRed
    FMSControlWord = int(FMS.getNumber('FMSControlWord', 0))
    #print(FMSControlWord)
    #print(bin(FMSControlWord))
    #print(FMSControlWord & 0b10000000)
    if FMSControlWord & 0b00100000:
        DSConnection_Flag = True
    else:
        DSConnection_Flag = False

    if FMSControlWord & 0b00010000:
        FMSConnection_Flag = True
    else:
        FMSConnection_Flag = False

    if FMSControlWord & 0b00000100:
        Teleop_Flag = True
    else:
        Teleop_Flag = False

    if FMSControlWord & 0b00001000:
        Test_Flag = True
    else:
        Test_Flag = False

    if FMSControlWord & 0b00000010:
        Autonomous_Flag = True
    else:
        Autonomous_Flag = False

    if FMSControlWord & 0b00000001:
        Enabled_Flag = True
    else:
        Enabled_Flag = False

    IsRed = FMS.getBoolean('IsRed', True)
    pass

# main loop
FrameCount = 0
executionTime = 0
FPS = 0

PREGAME_COUNTER = 0
INCREMENTING = True
CAN_TRANSITION = False
def PREGAME():
    global PREGAME_COUNTER
    global INCREMENTING
    global CAN_TRANSITION

    if not CAN_TRANSITION:
        #Create a variable that bounces between 0 and 1
        if PREGAME_COUNTER < 1 and INCREMENTING:
            PREGAME_COUNTER += 0.01
        elif PREGAME_COUNTER > 0 and not INCREMENTING:
            PREGAME_COUNTER -= 0.01
        elif PREGAME_COUNTER >= 1:
            INCREMENTING = False
        elif PREGAME_COUNTER <= 0:
            INCREMENTING = True

        #fade between purple and off on all IntakeZone, LeftBumperZone, and RightBumperZone. do not use tuples
        Patterns.fadeBetweenColors(IntakeZone, YELLOW, PURPLE, PREGAME_COUNTER)
        Patterns.fadeBetweenColors(LeftBumperZone, YELLOW, PURPLE, PREGAME_COUNTER)
        Patterns.fadeBetweenColors(RightBumperZone, YELLOW, PURPLE, PREGAME_COUNTER)
        pass

        #if we have FMS Connection, Set bumpers to green
        if FMSConnection_Flag:
            Patterns.fillLEDs(LeftBumperZone, GREEN)
            Patterns.fillLEDs(RightBumperZone, GREEN)

        #if we have DS Connection, Set intake to green
        if DSConnection_Flag:
            Patterns.fillLEDs(IntakeZone, GREEN)

        if DSConnection_Flag and FMSConnection_Flag:
            CAN_TRANSITION = True
            pushLEDs()
            time.sleep(4)

    else:
        fadeSpeed = 0.1
        #Fade to alliance color on all LEDs
        if IsRed == True:
            Patterns.fadeToColor(IntakeZone, RED, fadeSpeed)
            Patterns.fadeToColor(LeftBumperZone, RED, fadeSpeed)
            Patterns.fadeToColor(RightBumperZone, RED, fadeSpeed)
        else:
            Patterns.fadeToColor(IntakeZone, BLUE, fadeSpeed)
            Patterns.fadeToColor(LeftBumperZone, BLUE, fadeSpeed)
            Patterns.fadeToColor(RightBumperZone, BLUE, fadeSpeed)
        
        if DSConnection_Flag == False or FMSConnection_Flag == False:
            CAN_TRANSITION = False
            PREGAME_COUNTER = 0
            INCREMENTING = True
            pass

def AUTONOMOUS():
    if Autonomous_Flag == True:
        #set the bumper zones to our alliance color
        if IsRed == True:
            Patterns.fillLEDs(LeftBumperZone, RED)
            Patterns.fillLEDs(RightBumperZone, RED)
        else:
            Patterns.fillLEDs(LeftBumperZone, BLUE)
            Patterns.fillLEDs(RightBumperZone, BLUE)

        #Show which auton is selected
        #1 Ball Auton - Purple with a single 6 pixel yellow strip in the middle
        #2 Ball Normal - Purple with two 6 pixel yellow strips in the middle
        #2 Ball Short - Purple with three 6 pixel yellow strips in the middle
        if SD.getNumber('AutonSelection', 0) == 1:
            #set the intake to purple, yellow, purple using segmentedColor
            Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE])
        elif SD.getNumber('AutonSelection', 0) == 2:
            #set the intake to purple, yellow, purple, yellow, purple using segmentedColor
            Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE])
        elif SD.getNumber('AutonSelection', 0) == 3:
            #set the intake to purple, yellow, purple, yellow, purple, yellow, purple using segmentedColor
            Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE, YELLOW, PURPLE])
        
        Patterns.averageLEDs(IntakeZone, 2)

def VELOCITY_OVERLAY():
    if Enabled_Flag:
        #read the velocity from the network tables
        Velocity = SD.getNumber('Velocity', 20)
        MaxVelocity = SD.getNumber('MaxVelocity', 100)
        Percentage = Velocity / MaxVelocity

        #percentage fill the bumpers with the color purple using the velocity percentage
        Patterns.percentageFillLEDs(LeftBumperZone, PURPLE, Percentage)

while True:
    decodeFMSData()
    # get the current time
    startTime = time.time()

    SD.putNumber("AutonSelection", 3)
    FMS.putBoolean("IsRed", False)

    PREGAME()
    if DSConnection_Flag and FMSConnection_Flag:
        AUTONOMOUS()
        VELOCITY_OVERLAY()


    os.system("cls" if os.name == "nt" else "clear")
    #print the current FPS and ms per frame
    print("FPS: " + str(FPS))
    print("ms per frame: " + str(executionTime))

    #If enabled flag is set, then fade from the current color to purple on the left bumper zone using fade to color
#    if Enabled_Flag:
#        Patterns.fillLEDs(LeftBumperZone, 255, 0, 0)
#        Patterns.percentageFillLEDs(LeftBumperZone, 0, 255, 0, SD.getNumber("robotTime", -1) / 15)
#        Patterns.averageLEDsNoWrap(LeftBumperZone, 4)
#        if SD.getNumber("robotTime", -1) > 15:
#            fadeCounter += 0.01
#            Patterns.fadeToColor(LeftBumperZone, 255, 0, 255, fadeCounter)
#    elif not Enabled_Flag:
#        print("Disabled", fadeCounter)
#        if fadeCounter == 1:
#            fadeCounter = 0
#        fadeCounter += 0.01
#        Patterns.fadeToColor(LeftBumperZone, 255, 0, 0, fadeCounter)

    pushLEDs()
    
    # calculate the time it took to run the loop in milliseconds
    executionTime = (time.time() - startTime) * 1000
    #ensure the loop runs at 30 fps
    time.sleep(max(0, 1 / 30 - executionTime / 1000))

    # calculate the fps
    FPS = 1 / (time.time() - startTime)

    FrameCount += 1
