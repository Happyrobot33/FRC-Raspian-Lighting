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
LC = NetworkTables.getTable("LightingControl")
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
AutonomousValue = True

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

Intake = pygame.Rect(120,130,100,50)
IntakeText = pygame.font.SysFont("Arial", 20).render("Intake", True, (0,0,0))
IntakeTextRect = IntakeText.get_rect()
IntakeTextRect.center = Intake.center
IntakeValue = False

Outtake = pygame.Rect(120,190,100,50)
OuttakeText = pygame.font.SysFont("Arial", 20).render("Outtake", True, (0,0,0))
OuttakeTextRect = OuttakeText.get_rect()
OuttakeTextRect.center = Outtake.center
OuttakeValue = False

Shooter = pygame.Rect(120,250,100,50)
ShooterText = pygame.font.SysFont("Arial", 20).render("Shooter", True, (0,0,0))
ShooterTextRect = ShooterText.get_rect()
ShooterTextRect.center = Shooter.center
ShooterValue = False

Climber = pygame.Rect(120,310,100,50)
ClimberText = pygame.font.SysFont("Arial", 20).render("Climber", True, (0,0,0))
ClimberTextRect = ClimberText.get_rect()
ClimberTextRect.center = Climber.center
ClimberValue = False


#create a window mainloop
robotTime = 0
ControlWord = 0
running = True
backgroundColor = (200,200,200)
while running:
    #set the background color to gray
    window.fill(backgroundColor)

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
                LC.putNumber("AutonSelection", AutonomousModeValue)
            #Toggle the Alliance value
            if Alliance.collidepoint(event.pos):
                AllianceValue = not AllianceValue
                FMS.putBoolean("IsRedAlliance", AllianceValue)
            #Toggle the Intake value
            if Intake.collidepoint(event.pos):
                IntakeValue = not IntakeValue
                LC.putBoolean("Intake_Flag", IntakeValue)
            #Toggle the Outtake value
            if Outtake.collidepoint(event.pos):
                OuttakeValue = not OuttakeValue
                LC.putBoolean("Outtake_Flag", OuttakeValue)
            #Toggle the Shooter value
            if Shooter.collidepoint(event.pos):
                ShooterValue = not ShooterValue
                LC.putBoolean("Shooting_Flag", ShooterValue)
            #Toggle the Climber value
            if Climber.collidepoint(event.pos):
                ClimberValue = not ClimberValue
                LC.putBoolean("Climber_Flag", ClimberValue)

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

    #if intake value is true, display as green, otherwise, display as red
    if IntakeValue:
        pygame.draw.rect(window, (0,255,0), Intake)
        window.blit(IntakeText, IntakeTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Intake)
        window.blit(IntakeText, IntakeTextRect)

    #if outtake value is true, display as green, otherwise, display as red
    if OuttakeValue:
        pygame.draw.rect(window, (0,255,0), Outtake)
        window.blit(OuttakeText, OuttakeTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Outtake)
        window.blit(OuttakeText, OuttakeTextRect)

    #if shooter value is true, display as green, otherwise, display as red
    if ShooterValue:
        pygame.draw.rect(window, (0,255,0), Shooter)
        window.blit(ShooterText, ShooterTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Shooter)
        window.blit(ShooterText, ShooterTextRect)

    #if climber value is true, display as green, otherwise, display as red
    if ClimberValue:
        pygame.draw.rect(window, (0,255,0), Climber)
        window.blit(ClimberText, ClimberTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Climber)
        window.blit(ClimberText, ClimberTextRect)


    pixelSize = 5
    BumperLength = LC.getValue("BumperLength", 20)
    BumperLength = int(BumperLength)
    IntakeLength = LC.getValue("IntakeLength", 20)
    IntakeLength = int(IntakeLength)

    #Define a sub surface to draw on
    bumperShortSegment = 8
    width = bumperShortSegment * pixelSize + pixelSize
    height = (BumperLength - bumperShortSegment - bumperShortSegment) * pixelSize
    sub = pygame.Surface((width,height))
    sub.fill(backgroundColor)
    #sub.set_alpha(128)

    for i in range(0, bumperShortSegment):
        inversei = bumperShortSegment - i
        pygame.draw.rect(sub, LB.getNumberArray("neopixel"+str(inversei),[0,0,0]), (i * pixelSize + pixelSize, height - pixelSize, pixelSize, pixelSize))

    for i in range(BumperLength - bumperShortSegment, BumperLength):
        offsetX = i - (BumperLength - bumperShortSegment)
        pygame.draw.rect(sub, LB.getNumberArray("neopixel"+str(i),[0,0,0]), (offsetX * pixelSize + pixelSize, 0, pixelSize, pixelSize))
    
    for i in range(bumperShortSegment, BumperLength - bumperShortSegment):
        inversei = BumperLength - i
        pygame.draw.rect(sub, LB.getNumberArray("neopixel"+str(inversei),[0,0,0]), (0, (i * pixelSize) - bumperShortSegment * pixelSize, pixelSize, pixelSize))

    window.blit(sub, (window.get_width() / 2,window.get_height() / 3))

    #Do the same for the right bumper
    sub = pygame.Surface((width,height))
    sub.fill(backgroundColor)
    #sub.set_alpha(128)

    for i in range(0, bumperShortSegment):
        inversei = bumperShortSegment - i
        pygame.draw.rect(sub, RB.getNumberArray("neopixel"+str(inversei),[0,0,0]), (i * pixelSize + pixelSize, height - pixelSize, pixelSize, pixelSize))

    for i in range(BumperLength - bumperShortSegment, BumperLength):
        offsetX = i - (BumperLength - bumperShortSegment)
        pygame.draw.rect(sub, RB.getNumberArray("neopixel"+str(i),[0,0,0]), (offsetX * pixelSize + pixelSize, 0, pixelSize, pixelSize))

    for i in range(bumperShortSegment, BumperLength - bumperShortSegment):
        inversei = BumperLength - i
        pygame.draw.rect(sub, RB.getNumberArray("neopixel"+str(inversei),[0,0,0]), (0, (i * pixelSize) - bumperShortSegment * pixelSize, pixelSize, pixelSize))

    #mirror the image
    sub = pygame.transform.flip(sub, True, False)
    window.blit(sub, (window.get_width() / 2 + width + 100,window.get_height() / 3))

    #draw an arrow pointing up to indicate the direction of the robot, centered on the intake
    arrow = pygame.Surface((width,height))
    arrow.fill(backgroundColor)
    #arrow.set_alpha(12)
    pygame.draw.polygon(arrow, (0,0,0), ((width / 2, height), (width / 2 - pixelSize, height - pixelSize), (width / 2 + pixelSize, height - pixelSize)))
    #flip the image
    arrow = pygame.transform.flip(arrow, False, True)
    window.blit(arrow, (window.get_width() / 2 + (width + 100) / 2,window.get_height() / 3 - 50))

    #Do the same for the intake, centered in the middle of the two bumpers, going vertically, starting from the top going down
    height = (IntakeLength) * pixelSize
    sub = pygame.Surface((width,height))
    sub.fill(backgroundColor)
    #sub.set_alpha(128)

    for i in range(0, IntakeLength):
        pygame.draw.rect(sub, IN.getNumberArray("neopixel"+str(i),[0,0,0]), (0, i * pixelSize, pixelSize, pixelSize))

    for i in range(0, IntakeLength):
        pygame.draw.rect(sub, IN.getNumberArray("neopixel"+str(i),[0,0,0]), (width - pixelSize, i * pixelSize, pixelSize, pixelSize))

    window.blit(sub, (window.get_width() / 2 + (width + 100) / 2,window.get_height() / 3 - 40))


    #Draw every pixel from the network table starting from neopixel0 to neopixel79
    #The neopixel0 is the first pixel on the left side of the screen offset to the right by 500 pixels
    #each pixel is only VARIABLE pixels tall
    #label each pixel with its number
    #the value will be in the format of (R,G,B)
    #default color is black
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
    LC.putNumber("RobotTime", robotTime)

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
        robotTime -= 0.0625
        if robotTime < 0:
            robotTime = -1
    else:
        robotTime = 60 * 2
