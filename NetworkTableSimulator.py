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
sd = NetworkTables.getTable("SmartDashboard")

#create a GUI with buttons to control variables
pygame.init()

#create a window 800 by 300
window = pygame.display.set_mode((10*120,300))

#create 5 pygame toggle buttons called "Enabled", "Autonomous", "Teleop", "Test"
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

Test = pygame.Rect(10,190,100,50)
TestText = pygame.font.SysFont("Arial", 20).render("Test", True, (0,0,0))
TestTextRect = TestText.get_rect()
TestTextRect.center = Test.center
TestValue = False


#create a window mainloop
robotTime = 0
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
                sd.putBoolean("Enabled", EnabledValue)
            if Autonomous.collidepoint(event.pos):
                AutonomousValue = not AutonomousValue
                sd.putBoolean("Autonomous", AutonomousValue)
            if Teleop.collidepoint(event.pos):
                TeleopValue = not TeleopValue
                sd.putBoolean("Teleop", TeleopValue)
            if Test.collidepoint(event.pos):
                TestValue = not TestValue
                sd.putBoolean("Test", TestValue)

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

    if TestValue:
        pygame.draw.rect(window, (0,255,0), Test)
        window.blit(TestText, TestTextRect)
    else:
        pygame.draw.rect(window, (255,0,0), Test)
        window.blit(TestText, TestTextRect)

    #Draw every pixel from the network table starting from neopixel0 to neopixel19
    #The neopixel0 is the first pixel on the left side of the screen offset to the right by 500 pixels
    #each pixel is only 20 pixels tall
    #label each pixel with its number
    #the value will be in the format of (R,G,B)
    #default color is black
    for i in range(0,20):
        pygame.draw.rect(window, sd.getNumberArray("neopixel"+str(i),[0,0,0]), (500+i*20,0,20,20))

    #label the neopixels with a header on the left of the pixels
    text = pygame.font.SysFont("Arial", 20).render("Bumper Left", True, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (500-80,10)
    window.blit(text, textRect)

    for i in range(20,40):
        i = i - 20
        pygame.draw.rect(window, sd.getNumberArray("neopixel"+str(i + 20),[0,0,0]), (500+i*20,30,20,20))

    #label the neopixels with a header on the left of the pixels
    text = pygame.font.SysFont("Arial", 20).render("Bumper Right", True, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (500-80,40)
    window.blit(text, textRect)

    for i in range(40,60):
        i = i - 40
        pygame.draw.rect(window, sd.getNumberArray("neopixel"+str(i + 40),[0,0,0]), (500+i*20,60,20,20))

    #label the neopixels with a header on the left of the pixels
    text = pygame.font.SysFont("Arial", 20).render("Intake", True, (0,0,0))
    textRect = text.get_rect()
    textRect.center = (500-80,70)
    window.blit(text, textRect)

    #update the window
    pygame.display.update()

    os.system("cls" if os.name == "nt" else "clear")
    print("Lighting HeartBeat:", sd.getNumber("HeartBeat", -1), "Enabled:", sd.getBoolean("Enabled", False), "Autonomous:", sd.getBoolean("Autonomous", False), "Teleop:", sd.getBoolean("Teleop", False), "Test:", sd.getBoolean("Test", False), "RobotTime:", sd.getNumber("robotTime", 0))
    
    #update the networktables values
    sd.putBoolean("Enabled", EnabledValue)
    sd.putBoolean("Autonomous", AutonomousValue)
    sd.putBoolean("Teleop", TeleopValue)
    sd.putBoolean("Test", TestValue)
    #update the robot time
    sd.putNumber("robotTime", robotTime)

    time.sleep(0.0625)
    #increment the robot time by 0.0625 if enabled, if disabled set the robot time to 0
    if EnabledValue:
        robotTime += 0.0625
    else:
        robotTime = 0
