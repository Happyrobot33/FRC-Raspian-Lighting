from networktables import NetworkTables
import logging
import sys
import time
import os
import numpy as np
import platform

PURPLE = (148, 0, 211)
YELLOW = (255,255,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)

#Local librarys to contain functions better
import Patterns

#check if this code is running on the a Raspberry Pi
OnHardware = platform.machine() == 'armv7l' or platform.machine() == 'aarch64' 

if OnHardware:
    import board
    import neopixel

# Setup networktables and logging
logging.basicConfig(level=logging.DEBUG)
ip = "10.77.80.71"  # default ip
rioip = "10.36.67.2" #IP of the rio on the robot
# Initialize NetworkTables
NetworkTables.initialize(server=rioip)
# Get the NetworkTables instances
SD = NetworkTables.getTable("SmartDashboard")
FMS = NetworkTables.getTable("FMSInfo")

#Front / Back beam count = 9
#Side Beam Count = 42
BumperLEDCount = 9 + 9 + 42
#Single Beam Count = 60
IntakeLEDCount = 60
TotalLEDS = (1 * IntakeLEDCount) + (2 * BumperLEDCount)
if OnHardware:
    pixels = neopixel.NeoPixel(board.D18, TotalLEDS, auto_write=False)

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
IntakeZoneEnd = 2 * BumperLEDCount + (IntakeLEDCount * 1) - 1
IntakeZone = [IntakeLEDCount]
# Fill IntakeZone with (BLACK) using numpy
IntakeZone = np.zeros((IntakeLEDCount, 3), dtype=int)

# create a function that takes in arrays and outputs a single merged array
def mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone):
    # merge the arrays
    LEDArray = np.concatenate(
        (LeftBumperZone, RightBumperZone, np.tile(IntakeZone, (1, 1)))
    )
    return LEDArray

def pushLEDs():
    global pixels
    NDpixels = mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone)
    sendLEDToNetworkTables(NDpixels)
    #copy NDpixels into pixels manually
    if OnHardware:
        for i in range(len(NDpixels)):
            pixels[i] = NDpixels[i]

    if OnHardware:
        pixels.show()
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
RobotTime = 0
Intake_Flag = False
def decodeFMSData():
    global DSConnection_Flag
    global FMSConnection_Flag
    global Teleop_Flag
    global Test_Flag
    global Autonomous_Flag
    global Enabled_Flag
    global IsRed
    global RobotTime
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
    RobotTime = SD.getNumber('robotTime', 0)
    Intake_Flag = SD.getBoolean('Intake_Flag', False)
    pass

#No Connection - Flashing Purple
#Upon FMS Connection - Bumpers go Green
#Upon Driver Station Connection - Intake goes green, followed by the whole robot then fading to our alliance color
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

        #fade between purple, to black, to yellow, to black on all IntakeZone, LeftBumperZone, and RightBumperZone. do not use tuples
        if PREGAME_COUNTER < 0.5:
            Patterns.fadeBetweenColors(IntakeZone, PURPLE, BLACK, PREGAME_COUNTER * 2)
            Patterns.fadeBetweenColors(LeftBumperZone, PURPLE, BLACK, PREGAME_COUNTER * 2)
            Patterns.fadeBetweenColors(RightBumperZone, PURPLE, BLACK, PREGAME_COUNTER * 2)
        elif PREGAME_COUNTER >= 0.5:
            Patterns.fadeBetweenColors(IntakeZone, BLACK, YELLOW, (PREGAME_COUNTER - 0.5) * 2)
            Patterns.fadeBetweenColors(LeftBumperZone, BLACK, YELLOW, (PREGAME_COUNTER - 0.5) * 2)
            Patterns.fadeBetweenColors(RightBumperZone, BLACK, YELLOW, (PREGAME_COUNTER - 0.5) * 2)
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
            Patterns.fadeToColor(LeftBumperZone, RED, fadeSpeed)
            Patterns.fadeToColor(RightBumperZone, RED, fadeSpeed)
        else:
            Patterns.fadeToColor(LeftBumperZone, BLUE, fadeSpeed)
            Patterns.fadeToColor(RightBumperZone, BLUE, fadeSpeed)
        
        AUTON_MODE_OVERLAY()
        
        if DSConnection_Flag == False or FMSConnection_Flag == False:
            CAN_TRANSITION = False
            PREGAME_COUNTER = 0
            INCREMENTING = True
            pass

#Handles the overlay of what auton mode we are in
def AUTON_MODE_OVERLAY():
    #Show which auton is selected
    #1 Ball Auton - Purple with a single 6 pixel yellow strip in the middle
    #2 Ball Normal - Purple with two 6 pixel yellow strips in the middle
    #2 Ball Short - Purple with three 6 pixel yellow strips in the middle
    if SD.getNumber('AutonSelection', 1) == 1:
        #set the intake to purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE], 0.1)
    elif SD.getNumber('AutonSelection', 1) == 2:
        #set the intake to purple, yellow, purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE], 0.1)
    elif SD.getNumber('AutonSelection', 1) == 3:
        #set the intake to purple, yellow, purple, yellow, purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE, YELLOW, PURPLE], 0.1)

#Autonomous:
#For each individual autonomous mode, have a specific color pattern
#Also show the remaining Autonomous time on the bumper strips, decreasing
#1 Ball Auton - Purple with a single 6 pixel yellow strip in the middle
#2 Ball Normal - Purple with two 6 pixel yellow strips in the middle
#2 Ball Short - Purple with three 6 pixel yellow strips in the middle
#These also need to update continously as they are changed by the driverstation
def AUTONOMOUS():
    #set the bumper zones to our alliance color
    if IsRed == True:
        Patterns.fillLEDs(LeftBumperZone, RED)
        Patterns.fillLEDs(RightBumperZone, RED)
    else:
        Patterns.fillLEDs(LeftBumperZone, BLUE)
        Patterns.fillLEDs(RightBumperZone, BLUE)
    
    AUTON_MODE_OVERLAY()

    VELOCITY_OVERLAY()
    
    #Patterns.averageLEDs(IntakeZone, 2)

def VELOCITY_OVERLAY():
    if Enabled_Flag:
        #read the velocity from the network tables
        Velocity = SD.getNumber('Velocity', 20)
        MaxVelocity = SD.getNumber('MaxVelocity', 100)
        Percentage = Velocity / MaxVelocity

        #percentage fill the bumpers with the color purple using the velocity percentage
        Patterns.percentageFillLEDsMirrored(LeftBumperZone, YELLOW, Percentage)
        Patterns.percentageFillLEDsMirrored(RightBumperZone, YELLOW, Percentage)

#Teleop:
#idle - Purple Bumpers, Yellow Intake???
#Continous affect - Percentage fill from 0 to max speed, showing the robots current velocity on the bumpers
#On Pickup - Strobe the intake so it has a "pulling" Pattern up its length
#On Shoot - Charge affect, followed by a percentage fill to make it look like it is "Pushing" the balls out
#On Puke - Strobe the intake so it has a "Pushing" Pattern down its length
#On Climb Detect - Something flashy?????? Unknown, possibly something integrating the current alliance color
#Warning system - Possibly integrating a system to flash colors at ~40 seconds to indicate it is time to climb
Increment = 0
def TELEOP():
    #set the bumper zones to our alliance color
    if IsRed == True:
        Patterns.fillLEDs(LeftBumperZone, RED)
        Patterns.fillLEDs(RightBumperZone, RED)
    else:
        Patterns.fillLEDs(LeftBumperZone, BLUE)
        Patterns.fillLEDs(RightBumperZone, BLUE)
    
    #set the intake to purple
    Patterns.fillLEDs(IntakeZone, PURPLE)

    VELOCITY_OVERLAY()

    #check if time is below 40 seconds
    #TODO fix the time
    if RobotTime > 0:
        if RobotTime % 0.5 == 0:
            Patterns.fillLEDs(IntakeZone, YELLOW)
        else:
            Patterns.fillLEDs(IntakeZone, PURPLE)
    
    #Check if the intake is running
    if Intake_Flag:
        Increment += 1
        #color fade to yellow
        Patterns.fadeLEDs(IntakeZone, PURPLE, YELLOW)
        Patterns.shiftLEDs(IntakeZone, 1)
    pass

#Countdown to match end - Possibly have a countdown visible on the robot as the match is ending, once we have climbed
def CLIMBING():
    pass

#On Disable / Match end - Revert to alliance color with sliding purple strips???
def ENDGAME():
    pass

toPrint = 0
while True:
    decodeFMSData()
    # get the current time
    startTime = time.time()

    PREGAME()
    if DSConnection_Flag and FMSConnection_Flag:
        if Enabled_Flag and Autonomous_Flag:
            AUTONOMOUS()
        if Enabled_Flag and Teleop_Flag:
            TELEOP()

    pushLEDs()

    #ensure the loop runs at 30 fps
    executionTime = time.time() - startTime
    #convert to milliseconds
    MSexecutionTime = round(executionTime * 1000)

    if toPrint == 10:
        toPrint = 0
        print(" ms per frame: " + str(MSexecutionTime),"Framerate: ", 1 / executionTime, "\n Network Table Ip: " + str(ip),"\n Bumper LED Count: " + str(BumperLEDCount),"\n Intake LED Count: " + str(IntakeLEDCount),"\n Total LED Count: " + str(TotalLEDS), end="\033[A\033[A\033[A\033[A\r")
    else:
        toPrint += 1

    if executionTime < (1.0 / 30.0):
        time.sleep((1.0 / 30.0) - executionTime)