import math
import time

class SimulateGripper:

    def __init__(self, simulation, jointNames=None):
        self.simulation = simulation

        #default names for now
        if jointNames is None:
            self.jointNames = ['f1',
                                'f2', 
                                'f3']
        else:
            self.jointNames = jointNames
        #end if 

        #get finger/joint handles
        self.jointHandles = []
        
        for name in self.jointNames:
            handle = self.simulation.getObject(name) 
            self.jointHandles.append(handle)
        #end getting joint IDs

        #set current angle for fingers in degrees
        self.currentAngle = 0 
    #end constructor fn

    #SET TARGET POSITIONS OF FINGER'S ANGLES
    def setFingerAngle(self, targetDeg):
        #convert degree to radians
        targetRad = math.radians(targetDeg)

        #move fingies
        for joint in self.jointHandles:
            self.simulation.setJointTargetPosition(joint, targetRad)
        #end for moving all 3

        #update current ang
        self.currentAngle = targetDeg
    #end move fingers to target radians fn

    #"step" movements to make it smooth
    def smooving(self, targetDeg, speedDelay = 0.02, stepSize = 1):
        #LET positive = closing & negative = opening
        start = int(self.currentAngle)
        end = int(targetDeg)

        if end > start:
            step = stepSize
        else:
            step = -stepSize
        #end if det opening or close

        #increment degrees
        for angle in range(start, end+step, step):
            self.setFingerAngle(angle)
            time.sleep(speedDelay)
        #end for incremental change to angles (20milisec = 50Hz of servo http://pico.implrust.com/servo/how-servo-works.html)
    #END smooth moving fn

    #OPEN GRIPPER'S FINGERS
    def openGrip(self, openAngle = -50):
        self.smooving(targetDeg=openAngle)
        print(f"GRIPPER: Opening to {openAngle} degrees")
    #end open grip fn
        
    #CLOSE GRIPPER'S FINGERS
    def closeGrip(self, closeAngle = 0):
        self.smooving(targetDeg=closeAngle)
        print(f"GRIPPER: Closing to {closeAngle} degrees")
    #end close grip fn


#end simulated gripper function