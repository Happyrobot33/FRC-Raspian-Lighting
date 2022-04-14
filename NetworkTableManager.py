from tokenize import String
from networktables import NetworkTables
import logging
import os
import platform
import subprocess
import threading
import time

import networktables

class NetworkTableManager:
    FMSIPACCESIBLE = False
    def __init__(self, BumperLEDCount, IntakeLEDCount, ipAddress = "10.36.67.2"):
        # Setup networktables and logging
        #logging.basicConfig(level=logging.DEBUG)
        # Initialize NetworkTables
        NetworkTables.initialize(server=ipAddress)
        # Get the NetworkTables instances
        self.SD = NetworkTables.getTable("SmartDashboard")
        self.FMS = NetworkTables.getTable("FMSInfo")
        #Create a new network table subtable called LightingControl, abbreviated LC
        self.LC = NetworkTables.getTable("LightingControl")
        #Create a new network table subtable under LC called Pixels, abbreviated PX
        self.PX = self.LC.getSubTable("Pixels")
        #Create a new network table subtable under Pixels called LeftBumpers, abbreviated LB
        self.LB = self.PX.getSubTable("LeftBumpers")
        #Create a new network table subtable under Pixels called RightBumpers, abbreviated RB
        self.RB = self.PX.getSubTable("RightBumpers")
        #Create a new network table subtable under Pixels called Intake, abbreviated IN
        self.IN = self.PX.getSubTable("Intake")
        
        #add the LED counts to the network table
        self.LC.putValue('BumperLength', BumperLEDCount)
        self.LC.putValue('IntakeLength', IntakeLEDCount)

        pingInstance = threading.Thread(target=self.pingFMS)
        pingInstance.start()

    def roundTuple(self, tuple):
        #round each value in the tuple to the nearest integer
        return (round(tuple[0]), round(tuple[1]), round(tuple[2]))

    #Send the LED data to the network table, in their corresponding subtable
    def sendPixelsToNetworkTables(self, LeftBumper, RightBumper, Intake):
        for i in range(len(LeftBumper)):
            self.LB.putNumberArray("neopixel" + str(i), self.roundTuple(LeftBumper[i]))
        for i in range(len(RightBumper)):
            self.RB.putNumberArray("neopixel" + str(i), self.roundTuple(RightBumper[i]))
        for i in range(len(Intake)):
            self.IN.putNumberArray("neopixel" + str(i), self.roundTuple(Intake[i]))
        pass

    def sendFPS(self, FPS):
        self.LC.putNumber("FPS", FPS)

    def getRemoteAddress(self):
        return NetworkTables.getRemoteAddress()

    def getFMSData(self):
        return int(self.FMS.getValue("FMSControlData", 0))

    #All variables sent from the FMS
    def isDSAttached(self):
        return bool(self.getFMSData() & 0b00100000)

    def isFMSAttached(self):
        return bool(self.getFMSData() & 0b00010000)

    def pingFMS(self):
        FMSIP = "10.0.100.5"
        #Check if the FMS IP Address is reachable
        # Option for the number of packets as a function of
        param = '-n' if platform.system().lower()=='windows' else '-c'

        # Building the command. Ex: "ping -c 1 google.com"
        command = ['ping', param, '1', FMSIP]

        while True:
            self.FMSIPACCESIBLE = subprocess.call(command) == 0
            time.sleep(1)

    def isFMSIPReachable(self):
        return self.FMSIPACCESIBLE

    def getFMSControlData(self):
        return self.getFMSData()

    def isTeleop(self):
        return bool(self.isEnabled() and not self.isAutonomous())

    def isEnabled(self):
        return bool(self.getFMSData() & 0b00000001)

    def isAutonomous(self):
        return bool(self.getFMSData() & 0b00000010)

    def isTest(self):
        return bool(self.getFMSData() & 0b00000100)

    def isEStopped(self):
        return bool(self.getFMSData() & 0b00001000)

    def isDisabled(self):
        return not self.isEnabled()

    def isRedAlliance(self):
        return self.FMS.getBoolean('IsRedAlliance', True)

    #All variables sent from the roborio itself
    def getRobotTime(self):
        if self.LC.getValue("RobotTime", 1) == 0:
            return -1
        return self.LC.getValue("RobotTime", 0)

    def isIntakeRunning(self):
        return bool(self.LC.getBoolean("Intake_Flag", 0))

    def isShooterRunning(self):
        return bool(self.LC.getBoolean("Shooting_Flag", 0))
    
    def isOuttakeRunning(self):
        return bool(self.LC.getBoolean("Outtake_Flag", 0))

    def getAutonomousMode(self):
        chooser = self.LC.getString("AutonMode", "")
        #three options available
        #LeavePath1
        #2 Ball
        #2 Ball Short

        if chooser == "LeavePath1":
            return 1
        elif chooser == "2Ball":
            return 2
        else:
            return 3

    def getVelocity(self):
        return self.SD.getValue("Velocity", 0)
    
    def getMaxVelocity(self):
        return self.SD.getValue("MaxVelocity", 1)

    def isClimberRunning(self):
        return bool(self.LC.getBoolean("Climber_Flag", False))