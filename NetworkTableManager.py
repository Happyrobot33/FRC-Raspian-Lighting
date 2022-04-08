from networktables import NetworkTables
import logging

class NetworkTableManager:
    def __init__(self, BumperLEDCount, IntakeLEDCount, ipAddress = "10.36.67.2"):
        # Setup networktables and logging
        #logging.basicConfig(level=logging.DEBUG)
        # Initialize NetworkTables
        NetworkTables.initialize(server=ipAddress)
        # Get the NetworkTables instances
        self.SD = NetworkTables.getTable("SmartDashboard")
        self.FMS = NetworkTables.getTable("FMSInfo")
        #Create a new network table subtable called LightingControl, abbreviated LC
        self.LC = self.SD.getSubTable("LightingControl")
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
    
    #Send the LED data to the network table, in their corresponding subtable
    def sendPixelsToNetworkTables(self, LeftBumper, RightBumper, Intake):
        for i in range(len(LeftBumper)):
            self.LB.putNumberArray("neopixel" + str(i), LeftBumper[i])
        for i in range(len(RightBumper)):
            self.RB.putNumberArray("neopixel" + str(i), RightBumper[i])
        for i in range(len(Intake)):
            self.IN.putNumberArray("neopixel" + str(i), Intake[i])
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
        return self.SD.getValue("RobotTime", 0)

    def isIntakeRunning(self):
        return bool(self.SD.getBoolean("Intake_Flag", 0))

    def isShooterRunning(self):
        return bool(self.SD.getBoolean("Shooting_Flag", 0))
    
    def isOuttakeRunning(self):
        return bool(self.SD.getBoolean("Outtake_Flag", 0))

    def getAutonomousMode(self):
        return self.SD.getValue("AutonSelection", 1)

    def getVelocity(self):
        return self.SD.getValue("Velocity", 0)
    
    def getMaxVelocity(self):
        return self.SD.getValue("MaxVelocity", 1)

    def isClimberRunning(self):
        return bool(self.SD.getBoolean("Climber_Flag", False))