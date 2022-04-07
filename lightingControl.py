import time
import numpy as np
import platform
import pygame

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

#check if this code is running on the a Raspberry Pi
OnHardware = platform.machine() == 'armv7l' or platform.machine() == 'aarch64'

if OnHardware:
    import board
    import neopixel


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

NTM = NTM.NetworkTableManager(BumperLEDCount, IntakeLEDCount, "localhost")

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
    NTM.sendPixelsToNetworkTables(LeftBumperZone, RightBumperZone, IntakeZone)
    #copy NDpixels into pixels manually
    if OnHardware:
        for i in range(len(NDpixels)):
            pixels[i] = NDpixels[i]
        Patterns.correctGamma(pixels)
        pixels.show()
    else:
        #This is done to simulate the LED strip and how long it takes to update
        BitsPerPixel = 24
        MicroSecondsPerPixel = BitsPerPixel / 800000 * 1000
        MicroSecondsForAllPixels = len(NDpixels) * MicroSecondsPerPixel
        time.sleep(MicroSecondsForAllPixels / 1000)
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
            PREGAME_COUNTER += 0.005
        elif PREGAME_COUNTER > 0 and not INCREMENTING:
            PREGAME_COUNTER -= 0.005
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
        pass

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
            time.sleep(4)

    else:
        fadeSpeed = 0.1
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
def AUTON_MODE_OVERLAY():
    #Show which auton is selected
    #1 Ball Auton - Purple with a single 6 pixel yellow strip in the middle
    #2 Ball Normal - Purple with two 6 pixel yellow strips in the middle
    #2 Ball Short - Purple with three 6 pixel yellow strips in the middle
    if NTM.getAutonomousMode() == 1:
        #set the intake to purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(IntakeZone, [PURPLE, YELLOW, PURPLE], 0.1)
    elif NTM.getAutonomousMode() == 2:
        #set the intake to purple, yellow, purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(
            IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE], 0.1)
    elif NTM.getAutonomousMode() == 3:
        #set the intake to purple, yellow, purple, yellow, purple, yellow, purple using segmentedColor
        Patterns.segmentedColor(
            IntakeZone, [PURPLE, YELLOW, PURPLE, YELLOW, PURPLE, YELLOW, PURPLE], 0.1)

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
    ALLIANCE_COLOR_MACRO()

    #set the intake to purple
    Patterns.fillLEDs(IntakeZone, PURPLE)

    VELOCITY_OVERLAY()

    #check if time is below 40 seconds
    #TODO fix the time
    if NTM.getRobotTime() > 0:
        if NTM.getRobotTime() % 0.5 == 0:
            Patterns.fillLEDs(IntakeZone, YELLOW)
        else:
            Patterns.fillLEDs(IntakeZone, PURPLE)

    #Check if the intake is running
    if NTM.isIntakeRunning():
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

        if NTM.isEStopped():
            ESTOP()

        pushLEDs()

        NTM.sendFPS(Clock.get_fps())

        if toPrint == 1:
            toPrint = 0
            print("FPS: ", str(Clock.get_fps()) + "                                                                                               ",
                "\nNetwork Table Ip: " + str(NTM.getRemoteAddress()),
                "\nControl Word: " + str(NTM.getFMSControlData()) + "                                                                                               ",
                "\nBumper LED Count: " + str(BumperLEDCount),
                "\nIntake LED Count: " + str(IntakeLEDCount),
                "\nTotal LED Count: " + str(TotalLEDS),
                end="\033[A\033[A\033[A\033[A\033[A\r")
        else:
            toPrint += 1

        Clock.tick(60)