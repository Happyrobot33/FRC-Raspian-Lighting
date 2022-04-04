from networktables import NetworkTables
import logging
import sys
import time
import os
import numpy as np

# import board
# import neopixel

# Setup networktables and logging
logging.basicConfig(level=logging.DEBUG)
ip = "127.0.0.1"  # default ip
# Initialize NetworkTables
NetworkTables.initialize(server=ip)
# Get the NetworkTables instance
sd = NetworkTables.getTable("SmartDashboard")

BumperLEDCount = 20
IntakeLEDCount = 20
TotalLEDS = (4 * IntakeLEDCount) + (2 * BumperLEDCount)
# pixels = neopixel.NeoPixel(TotalLEDS)

# define bumper LED Zone start and end
LeftBumperZoneStart = 0
LeftBumperZoneEnd = BumperLEDCount - 1
LeftBumperZone = [BumperLEDCount]
# Fill LeftBumperZone with (0,0,0) using numpy
LeftBumperZone = np.zeros((BumperLEDCount, 3), dtype=int)

RightBumperZoneStart = BumperLEDCount
RightBumperZoneEnd = 2 * BumperLEDCount - 1
RightBumperZone = [BumperLEDCount]
# Fill RightBumperZone with (0,0,0) using numpy
RightBumperZone = np.zeros((BumperLEDCount, 3), dtype=int)

IntakeZoneStart = 2 * BumperLEDCount
IntakeZoneEnd = 2 * BumperLEDCount + (IntakeLEDCount * 4) - 1
IntakeZone = [IntakeLEDCount]
# Fill IntakeZone with (0,0,0) using numpy
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
    pixels.show()
    pass

# define a function that takes in a array of (r,g,b) values and sends that to the network tables with the prefix "neopixel"
def sendLEDToNetworkTables(LEDArray):
    for i in range(len(LEDArray)):
        sd.putNumberArray("neopixel" + str(i), LEDArray[i])
    pass

def fillLEDs(LEDArray, r, g, b):
    for i in range(len(LEDArray)):
        LEDArray[i] = [r, g, b]
    pass

def alternateLEDs(LEDArray, r, g, b, offset):
    for i in range(len(LEDArray)):
        if i % 2 == offset:
            LEDArray[i] = [r, g, b]
    pass

def randomFillLEDs(LEDArray):
    for i in range(len(LEDArray)):
        LEDArray[i] = [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)]
    pass

#Define a function that fades from one color to the other, as the index of the LED increases
#inputs: LEDArray, r1, g1, b1, r2, g2, b2
def fadeLEDs(LEDArray, r1, g1, b1, r2, g2, b2):
    for i in range(len(LEDArray)):
        if i < len(LEDArray):
            LEDArray[i] = [r1 + ((r2 - r1) * i / len(LEDArray)), g1 + ((g2 - g1) * i / len(LEDArray)), b1 + ((b2 - b1) * i / len(LEDArray))]
    pass


def percentageFillLEDs(LEDArray, r, g, b, percentage):
    for i in range(len(LEDArray)):
        if i < (len(LEDArray) * percentage):
            LEDArray[i] = [r, g, b]
    pass

# main loop
i = False
while True:
    os.system("cls" if os.name == "nt" else "clear")
    print(
        "robotTime:",
        sd.getNumber("robotTime", -1),
        " \n mergedLEDLength",
        len(mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone)),
        "Calculated expected length:",
        TotalLEDS,
        " \n LeftBumperZoneStart:",
        LeftBumperZoneStart,
        "LeftBumperZoneEnd:",
        LeftBumperZoneEnd,
        " \n RightBumperZoneStart:",
        RightBumperZoneStart,
        "RightBumperZoneEnd:",
        RightBumperZoneEnd,
        " \n IntakeZoneStart:",
        IntakeZoneStart,
        "IntakeZoneEnd:",
        IntakeZoneEnd,
        "\n leftBumperZone Length =",
        len(LeftBumperZone),
        " \n rightBumperZone Length =",
        len(RightBumperZone),
        " \n intakeZone Length =",
        len(IntakeZone),
    )

    alternateLEDs(LeftBumperZone, 255, 0, 0, 0)
    alternateLEDs(LeftBumperZone, 255, 255, 0, 1)

    fillLEDs(RightBumperZone, 255, 0, 0)
    percentageFillLEDs(RightBumperZone, 0, 255, 0, sd.getNumber("robotTime", -1) / 10)

    fadeLEDs(IntakeZone, 0, 0, 255, 255, 0, 0)    

    sendLEDToNetworkTables(mergeLEDs(LeftBumperZone, RightBumperZone, IntakeZone))
    # For debugging purposes on the emulated robot to ensure the connection is active
    sd.putNumber("HeartBeat", i)
    i = not i
