#!/usr/bin/env python3
#
# This is a NetworkTables server (eg, the robot or simulator side).
#
# On a real robot, you probably would create an instance of the
# wpilib.SmartDashboard object and use that instead -- but it's really
# just a passthru to the underlying NetworkTable object.
#
# When running, this will continue incrementing the value 'robotTime',
# and the value should be visible to networktables clients such as
# SmartDashboard. To view using the SmartDashboard, you can launch it
# like so:
#
#     SmartDashboard.jar ip 127.0.0.1
#
import time
import pygame
import os
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize()
SD = NetworkTables.getTable("SmartDashboard")
FMS = NetworkTables.getTable("FMSInfo")
#Create a new network table subtable called LightingControl, abbreviated LC
LC = SD.getSubTable("LightingControl")
#Create a new network table subtable under LC called Pixels, abbreviated PX
PX = LC.getSubTable("Pixels")
#Create a new network table subtable under Pixels called LeftBumpers, abbreviated LB
LB = PX.getSubTable("LeftBumpers")
#Create a new network table subtable under Pixels called RightBumpers, abbreviated RB
RB = PX.getSubTable("RightBumpers")
#Create a new network table subtable under Pixels called Intake, abbreviated IN
IN = PX.getSubTable("Intake")

#create a GUI with buttons to control variables
pygame.init()

#create a window 800 by 300
window = pygame.display.set_mode((10*100,400))

#create 5 pygame toggle buttons called "Enabled", "Autonomous", "Teleop", "EStop", "FMS Connection", "Driver Station Connection"
#these buttons will be used to control the virtual robot
Enabled = pygame.Rect(10,10,100,50)
EnabledText = pygame.font.SysFont("Arial", 20).render("Enabled", True, (0,0,0))
EnabledTextRect = EnabledText.get_rect()
EnabledTextRect.center = Enabled.center
EnabledValue = False

Autonomous = pygame.Rect(10,70,100,50)
AutonomousText = pygame.font.SysFont("Arial", 20).render("Autonomous", True, (0,0,0))
AutonomousTextRect = AutonomousText.get_rect()
AutonomousTextRect.center = Autonomous.center
AutonomousValue = False

Teleop = pygame.Rect(10,130,100,50)
TeleopText = pygame.font.SysFont("Arial", 20).render("Teleop", True, (0,0,0))
TeleopTextRect = TeleopText.get_rect()
TeleopTextRect.center = Teleop.center
TeleopValue = False

EStop = pygame.Rect(10,190,100,50)
EStopText = pygame.font.SysFont("Arial", 20).render("EStop", True, (0,0,0))
EStopTextRect = EStopText.get_rect()
EStopTextRect.center = EStop.center
EStopValue = False

FMSConnection = pygame.Rect(10,250,100,50)
FMSConnectionText = pygame.font.SysFont("Arial", 20).render("FMS Connection", True, (0,0,0))
FMSConnectionTextRect = FMSConnectionText.get_rect()
FMSConnectionTextRect.center = FMSConnection.center
FMSConnectionValue = False

DSConnection = pygame.Rect(10,310,100,50)
DSConnectionText = pygame.font.SysFont("Arial", 20).render("DS Connection", True, (0,0,0))
DSConnectionTextRect = DSConnectionText.get_rect()
DSConnectionTextRect.center = DSConnection.center
DSConnectionValue = False

#Make another collumn of buttons to control the virtual robot next to the previous buttons
AutonomousMode = pygame.Rect(120,10,100,50)
AutonomousModeText = pygame.font.SysFont("Arial", 20).render("Autonomous Mode", True, (0,0,0))
AutonomousModeTextRect = AutonomousModeText.get_rect()
AutonomousModeTextRect.center = AutonomousMode.center
AutonomousModeValue = 1

Alliance = pygame.Rect(120,70,100,50)
AllianceText = pygame.font.SysFont("Arial", 20).render("Alliance", True, (0,0,0))
AllianceTextRect = AllianceText.get_rect()
AllianceTextRect.center = Alliance.center
AllianceValue = True


#create a window mainloop
robotTime = 0
ControlWord = 0
running = True
while running:
    #set the background color to gray
    window.fill((200,200,200))

    #check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            #if the button is clicked, toggle the value of the button
            if Enabled.collidepoint(event.pos):
                EnabledValue = not EnabledValue
            if Autonomous.collidepoint(event.pos):
                AutonomousValue = not AutonomousValue
                TeleopValue = not AutonomousValue
            if Teleop.collidepoint(event.pos):
                TeleopValue = not TeleopValue
                AutonomousValue = not TeleopValue
            if EStop.collidepoint(event.pos):
                EStopValue = not EStopValue
            if FMSConnection.collidepoint(event.pos):
                FMSConnectionValue = not FMSConnectionValue
            if DSConnection.collidepoint(event.pos):
                DSConnectionValue = not DSConnectionValue
            if AutonomousMode.collidepoint(event.pos):
                AutonomousModeValue = ((AutonomousModeValue + 1) % 3) + 1
                SD.putNumber("AutonSelection", AutonomousModeValue)
            #Toggle the Alliance value
            if Alliance.collidepoint(event.pos):
                AllianceValue = not AllianceValue
                FMS.putBoolean("IsRedAlliance", AllianceValue)

    #Render the buttons based on their state, green if true, red if false
    if EnabledValue:
        pygame.draw.rect(window, (0,255,0), Enabled)
        window.blit(EnabledText, EnabledTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Enabled)
        window.blit(EnabledText, EnabledTextRect)
    
    if AutonomousValue:
        pygame.draw.rect(window, (0,255,0), Autonomous)
        window.blit(AutonomousText, AutonomousTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Autonomous)
        window.blit(AutonomousText, AutonomousTextRect)

    if TeleopValue:
        pygame.draw.rect(window, (0,255,0), Teleop)
        window.blit(TeleopText, TeleopTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Teleop)
        window.blit(TeleopText, TeleopTextRect)

    if EStopValue:
        pygame.draw.rect(window, (0,255,0), EStop)
        window.blit(EStopText, EStopTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), EStop)
        window.blit(EStopText, EStopTextRect)

    if FMSConnectionValue:
        pygame.draw.rect(window, (0,255,0), FMSConnection)
        window.blit(FMSConnectionText, FMSConnectionTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), FMSConnection)
        window.blit(FMSConnectionText, FMSConnectionTextRect)

    if DSConnectionValue:
        pygame.draw.rect(window, (0,255,0), DSConnection)
        window.blit(DSConnectionText, DSConnectionTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), DSConnection)
        window.blit(DSConnectionText, DSConnectionTextRect)

    if AutonomousModeValue == 1:
        pygame.draw.rect(window, (0,255,0), AutonomousMode)
        window.blit(AutonomousModeText, AutonomousModeTextRect)
    elif AutonomousModeValue == 2:
        pygame.draw.rect(window, (255,0,0), AutonomousMode)
        window.blit(AutonomousModeText, AutonomousModeTextRect)
    elif AutonomousModeValue == 3:
        pygame.draw.rect(window, (0,0,255), AutonomousMode)
        window.blit(AutonomousModeText, AutonomousModeTextRect)

    #if alliance value is true, display as red, otherwise, display as blue
    if AllianceValue:
        pygame.draw.rect(window, (255,0,0), Alliance)
        window.blit(AllianceText, AllianceTextRect)
    else:
        pygame.draw.rect(window, (0,0,255), Alliance)
        window.blit(AllianceText, AllianceTextRect)


    #Draw every pixel from the network table starting from neopixel0 to neopixel79
    #The neopixel0 is the first pixel on the left side of the screen offset to the right by 500 pixels
    #each pixel is only VARIABLE pixels tall
    #label each pixel with its number
    #the value will be in the format of (R,G,B)
    #default color is black
    pixelSize = 5
    BumperLength = LC.getValue("BumperLength", 0)
    BumperLength = int(BumperLength)
    IntakeLength = LC.getValue("IntakeLength", 0)
    IntakeLength = int(IntakeLength)
    for i in range(0,BumperLength):
        pygame.draw.rect(window, LB.getNumberArray("neopixel"+str(i),[0,0,0]), (500+i*pixelSize,0,pixelSize,pixelSize))

    #label the neopixels with a header on the left of the pixels
    text = pygame.font.SysFont("Arial", 20).render("Bumper Left (" + str(BumperLength) + ")", True, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (500-80,10)
    window.blit(text, textRect)

    for i in range(BumperLength,BumperLength * 2):
        i = i - BumperLength
        pygame.draw.rect(window, RB.getNumberArray("neopixel"+str(i),[0,0,0]), (500+i*pixelSize,30,pixelSize,pixelSize))

    #label the neopixels with a header on the left of the pixels
    text = pygame.font.SysFont("Arial", 20).render("Bumper Right (" + str(BumperLength) + ")", True, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (500-80,40)
    window.blit(text, textRect)

    for i in range(BumperLength * 2,BumperLength * 2 + IntakeLength):
        i = i - BumperLength * 2
        pygame.draw.rect(window, IN.getNumberArray("neopixel"+str(i),[0,0,0]), (500+i*pixelSize,60,pixelSize,pixelSize))

    #label the neopixels with a header on the left of the pixels
    text = pygame.font.SysFont("Arial", 20).render("Intake (" + str(IntakeLength) + ")", True, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (500-80,70)
    window.blit(text, textRect)

    #update the window
    pygame.display.update()

    #update the robot time
    SD.putNumber("RobotTime", robotTime)

    #The first bits purpose is Unknown
    #the second bits purpose is Unknown
    #the third bits purpose is Driver station Connection
    #the fourth bits purpose is FMS Connection
    #the fifth bits purpose is Teleop
    #the sixth bits purpose is EStop
    #the seventh bits purpose is Autonomous
    #the eighth bits purpose is Enabled
    #this function takes in a FMS Control word and decodes it into global variables
    #set the bits in the control word based on the state of the buttons
    #the bits are in reverse order
    ControlWord = 0
    if EnabledValue:
        ControlWord = ControlWord | 0b00000001
    if AutonomousValue:
        ControlWord = ControlWord | 0b00000010
    if EStopValue:
        ControlWord = ControlWord | 0b00001000
    if DSConnectionValue:
        ControlWord = ControlWord | 0b00100000
    if FMSConnectionValue:
        ControlWord = ControlWord | 0b00010000

    #send the control word to the robot
    FMS.putNumber("FMSControlData", int(ControlWord))


    time.sleep(0.0625)
    #increment the robot time by 0.0625 if enabled, if disabled set the robot time to 0
    if EnabledValue:
        robotTime += 0.0625
    else:
        robotTime = 0
