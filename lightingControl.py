from glob import glob
import math
import time
import numpy as np
import platform
import pygame
import sys

#Local librarys to contain functions better
import Patterns
import NetworkTableManager as NTM

PURPLE = (148, 0, 211)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#use this to make a value independent of the frame rate
FPS = 1
def syncWithFrameRate(Value):
    global FPS
    return Value / max(FPS, 1)

def FPS_SAFE_SLEEP(Value):
    global FPS
    time.sleep(Value)
    for i in range(20):
        Clock.tick(20)

#check if this code is running on the a Raspberry Pi
OnHardware = platform.machine() == 'armv7l' or platform.machine() == 'aarch64'

if OnHardware:
    import board
    import neopixel


#Front / Back beam count = 9
#Side Beam Count = 42
BumperLEDCount = (8 * 2) + 40
#Single Beam Count = 60
IntakeLEDCount = 49
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

NTM = NTM.NetworkTableManager(BumperLEDCount, IntakeLEDCount)

# create a function that takes in arrays and outputs a single merged array
def mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone):
    # merge the arrays
    LEDArray = np.concatenate(
        (LeftBumperZone, RightBumperZone, np.tile(IntakeZone, (1, 1)))
    )
    return LEDArray

def pushLEDs():
    global pixels
    LeftBumperZoneGamma = Patterns.correctGamma(LeftBumperZone)
    RightBumperZoneGamma = Patterns.correctGamma(RightBumperZone)
    IntakeZoneGamma = Patterns.correctGamma(IntakeZone)
    NDpixels = mergeLEDs(LeftBumperZoneGamma, RightBumperZoneGamma, IntakeZoneGamma)
    NTM.sendPixelsToNetworkTables(LeftBumperZoneGamma, RightBumperZoneGamma, IntakeZoneGamma)
    #copy NDpixels into pixels manually
    if OnHardware:
        for i in range(len(NDpixels)):
            pixels[i] = NDpixels[i]
        pixels.show()
    else:
        #This is done to simulate the LED strip and how long it takes to update
        #BitsPerPixel = 24
        #MicroSecondsPerPixel = BitsPerPixel / 800000 * 1000
        #MicroSecondsForAllPixels = len(NDpixels) * MicroSecondsPerPixel
        #time.sleep(MicroSecondsForAllPixels / 1000 * 6)
        
        #This code is much accurate, even though it seems more inneficient.
        #This is taken directly from the neopixel librarys calculations
        #about 100ms per 100 bytes
        bytes = 0
        for i in range(len(NDpixels)):
            bytes += NDpixels[i].tobytes().__len__()
        time.sleep(0.001 * ((bytes // 100) + 1))
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
            PREGAME_COUNTER += syncWithFrameRate(0.5)
        elif PREGAME_COUNTER > 0 and not INCREMENTING:
            PREGAME_COUNTER -= syncWithFrameRate(0.5)
        elif PREGAME_COUNTER >= 1:
            INCREMENTING = False
        elif PREGAME_COUNTER <= 0:
            INCREMENTING = True

        #fade between purple, to black, to yellow, to black on all IntakeZone, LeftBumperZone, and RightBumperZone. do not use tuples
        if PREGAME_COUNTER < 0.5:
            Patterns.fadeBetweenColors(
                IntakeZone, PURPLE, BLACK, PREGAME_COUNTER * 2)
            Patterns.fadeBetweenColors(
                LeftBumperZone, PURPLE, BLACK, PREGAME_COUNTER * 2)
            Patterns.fadeBetweenColors(
                RightBumperZone, PURPLE, BLACK, PREGAME_COUNTER * 2)
        elif PREGAME_COUNTER >= 0.5:
            Patterns.fadeBetweenColors(
                IntakeZone, BLACK, YELLOW, (PREGAME_COUNTER - 0.5) * 2)
            Patterns.fadeBetweenColors(
                LeftBumperZone, BLACK, YELLOW, (PREGAME_COUNTER - 0.5) * 2)
            Patterns.fadeBetweenColors(
                RightBumperZone, BLACK, YELLOW, (PREGAME_COUNTER - 0.5) * 2)

        #if we have FMS Connection, Set bumpers to green
        if NTM.isFMSAttached():
            Patterns.fillLEDs(LeftBumperZone, GREEN)
            Patterns.fillLEDs(RightBumperZone, GREEN)

        #if we have DS Connection, Set intake to green
        #This overrides the FMS Connection, as if it didnt, then the robot would never change if we werent on the field
        #this should still work on the field however, as it is physically impossible to have a DS connection without a FMS connection
        if NTM.isDSAttached():
            #set everything to green
            Patterns.fillLEDs(IntakeZone, GREEN)
            Patterns.fillLEDs(LeftBumperZone, GREEN)
            Patterns.fillLEDs(RightBumperZone, GREEN)
            CAN_TRANSITION = True
            pushLEDs()
            FPS_SAFE_SLEEP(4)
            #time.sleep(4)

    else:
        fadeSpeed = syncWithFrameRate(3)
        #Fade to alliance color on all LEDs
        if NTM.isRedAlliance() == True:
            Patterns.fadeToColor(LeftBumperZone, RED, fadeSpeed)
            Patterns.fadeToColor(RightBumperZone, RED, fadeSpeed)
        else:
            Patterns.fadeToColor(LeftBumperZone, BLUE, fadeSpeed)
            Patterns.fadeToColor(RightBumperZone, BLUE, fadeSpeed)

        AUTON_MODE_OVERLAY()

        if NTM.isDSAttached() == False:
            CAN_TRANSITION = False
            PREGAME_COUNTER = 0
            INCREMENTING = True
            pass

#Handles the overlay of what auton mode we are in
PREVIOUSAUTONMODE = 0
def AUTON_MODE_OVERLAY():
    global PREVIOUSAUTONMODE
    #Show which auton is selected
    #1 Ball Auton - Purple with a single 6 pixel yellow strip in the middle
    #2 Ball Normal - Purple with two 6 pixel yellow strips in the middle
    #2 Ball Short - Purple with three 6 pixel yellow strips in the middle
    CURRENTAUTONMODE = NTM.getAutonomousMode()

    if CURRENTAUTONMODE != PREVIOUSAUTONMODE:
        Patterns.fillLEDs(IntakeZone, PURPLE)

    FadeSpeed = syncWithFrameRate(7)

    if CURRENTAUTONMODE == 1:
        #set the intake to purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE], FadeSpeed)
    elif CURRENTAUTONMODE == 2:
        #set the intake to purple, yellow, purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE], FadeSpeed)
    elif CURRENTAUTONMODE == 3:
        #set the intake to purple, yellow, purple, yellow, purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE, YELLOW, PURPLE], FadeSpeed)
    
    PREVIOUSAUTONMODE = CURRENTAUTONMODE

#Autonomous:
#For each individual autonomous mode, have a specific color pattern
#Also show the remaining Autonomous time on the bumper strips, decreasing
#1 Ball Auton - Purple with a single 6 pixel yellow strip in the middle
#2 Ball Normal - Purple with two 6 pixel yellow strips in the middle
#2 Ball Short - Purple with three 6 pixel yellow strips in the middle
#These also need to update continously as they are changed by the driverstation
def AUTONOMOUS():
    ALLIANCE_COLOR_MACRO()
    AUTON_MODE_OVERLAY()
    VELOCITY_OVERLAY()


def VELOCITY_OVERLAY():
    if NTM.isEnabled():
        #read the velocity from the network tables
        Velocity = NTM.getVelocity()
        MaxVelocity = NTM.getMaxVelocity()
        Percentage = Velocity / MaxVelocity

        #percentage fill the bumpers with the color purple using the velocity percentage
        Patterns.percentageFillLEDsMirrored(LeftBumperZone, YELLOW, Percentage)
        Patterns.percentageFillLEDsMirrored(RightBumperZone, YELLOW, Percentage)

def ALLIANCE_COLOR_MACRO():
    #set the bumper zones to our alliance color
    if NTM.isRedAlliance() == True:
        Patterns.fillLEDs(LeftBumperZone, RED)
        Patterns.fillLEDs(RightBumperZone, RED)
    else:
        Patterns.fillLEDs(LeftBumperZone, BLUE)
        Patterns.fillLEDs(RightBumperZone, BLUE)

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
    global Increment
    ALLIANCE_COLOR_MACRO()

    #set the intake to purple
    Patterns.fillLEDs(IntakeZone, PURPLE)

    VELOCITY_OVERLAY()

    #check if time is below 40 seconds
    if NTM.getRobotTime() > 35 and NTM.getRobotTime() < 45:
        if NTM.getRobotTime() % 2 == 0:
            Patterns.fillLEDs(IntakeZone, YELLOW)
        else:
            Patterns.fillLEDs(IntakeZone, PURPLE)

    #Check if the intake is running
    if NTM.isIntakeRunning():
        Increment += syncWithFrameRate(100)
        #color fade to yellow
        Patterns.fadeLEDs(IntakeZone, PURPLE, YELLOW)
        Patterns.shiftLEDs(IntakeZone, Increment)
    #Check if the intake is puking
    elif NTM.isOuttakeRunning():
        Increment += syncWithFrameRate(100)
        #color fade to purple
        Patterns.fadeLEDs(IntakeZone, YELLOW, PURPLE)
        Patterns.shiftLEDs(IntakeZone, -Increment)
    #Check if the intake is shooting
    elif NTM.isShooterRunning():
        Increment += syncWithFrameRate(1)
        Patterns.fillLEDs(IntakeZone, YELLOW)
        if Increment <= 1:
            Patterns.fillLEDs(IntakeZone, YELLOW)
            Patterns.percentageFillLEDs(IntakeZone, PURPLE, 1 - Increment)
        elif Increment >= 2:
            Patterns.fillLEDs(IntakeZone, YELLOW)
            Patterns.percentageFillLEDs(IntakeZone, PURPLE, (Increment - 2) * 2)
    #Check if the climber is running
    elif NTM.isClimberRunning():
        Increment += syncWithFrameRate(100)
        
        #Slide an "ant" across the bumpers, with the current alliance color
        if NTM.isRedAlliance():
            Patterns.fadeLEDs(LeftBumperZone, RED, YELLOW)
            Patterns.fadeLEDs(RightBumperZone, RED, YELLOW)
        else:
            Patterns.fadeLEDs(LeftBumperZone, BLUE, YELLOW)
            Patterns.fadeLEDs(RightBumperZone, BLUE, YELLOW)
        Patterns.shiftLEDs(LeftBumperZone, Increment)
        Patterns.shiftLEDs(RightBumperZone, Increment)

        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE], 1)
        Patterns.shiftLEDs(IntakeZone, math.sin(Increment / 40) * 20)
    else:
        Increment = 0 #reset the increment to ensure it doesnt get too big and cause an error
    pass

#On Disable / Match end - Revert to alliance color with sliding purple strips???
def ENDGAME():
    ALLIANCE_COLOR_MACRO()
    Patterns.fillLEDs(IntakeZone, PURPLE)
    pass


def ESTOP():
    Patterns.fillLEDs(LeftBumperZone, YELLOW)
    Patterns.fillLEDs(RightBumperZone, YELLOW)
    Patterns.fillLEDs(IntakeZone, YELLOW)
    Patterns.alternateLEDs(LeftBumperZone, PURPLE, 1)
    Patterns.alternateLEDs(RightBumperZone, PURPLE, 1)
    Patterns.alternateLEDs(IntakeZone, PURPLE, 1)


toPrint = 0
Clock = pygame.time.Clock()
#main loop
if __name__ == "__main__":
    while True:
        PREGAME()
        if NTM.isDSAttached():
            if NTM.isEnabled() and NTM.isAutonomous():
                AUTONOMOUS()
            if NTM.isEnabled() and NTM.isTeleop():
                TELEOP()
            if NTM.isGameEnded():
                ENDGAME()

        if NTM.isEStopped():
            ESTOP()

        pushLEDs()

        NTM.sendFPS(FPS)
        FPS = Clock.get_fps()

        if toPrint == 0:
            toPrint = 0
            print("FPS: ", str(Clock.get_fps()) + "                                                                                               ",
                "\nFPS Adjustment Value: ", syncWithFrameRate(20),
                "\nNetwork Table Ip: " + str(NTM.getRemoteAddress()),
                "\nControl Word: " + str(NTM.getFMSControlData()) + "                                                                                               ",
                "\nBumper LED Count: " + str(BumperLEDCount),
                "\nIntake LED Count: " + str(IntakeLEDCount),
                "\nTotal LED Count: " + str(TotalLEDS),
                "\nSendable Chooser: " + str(NTM.getAutonomousMode()),
                end="\033[A\033[A\033[A\033[A\033[A\033[A\033[A\r")
        else:
            toPrint += 1

        Clock.tick()