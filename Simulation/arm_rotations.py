import math

def sysCall_init():
    global sim
    global joints

    sim = require('sim')

    #the five joints thats gonna be in the model
    joints = [
        sim.getObject('/UR5/joint'),                                      # Base
        sim.getObject('/UR5/joint/link/joint'),                           # Shoulder
        sim.getObject('/UR5/joint/link/joint/link/joint'),                # Elbow
        sim.getObject('/UR5/joint/link/joint/link/joint/link/joint'),     # Wrist rotation
        sim.getObject('/UR5/joint/link/joint/link/joint/link/joint/link/joint')  # Wrist pitch
    ]


#general joint rotation function
def rotateJoint(jointNumber, angleDegrees):

    targetAngle = math.radians(angleDegrees)

    sim.setJointTargetPosition(
        joints[jointNumber],
        targetAngle
    )


#joint 1
def rotateBase(angle):
    rotateJoint(0, angle)


#joint 2
def rotateShoulder(angle):
    rotateJoint(1, angle)


#joint 3
def rotateElbow(angle):
    rotateJoint(2, angle)


#joint 4
def rotateWrist(angle):
    rotateJoint(3, angle)


#joint 5
def rotateWristPitch(angle):
    rotateJoint(4, angle)


#function to rotate all 5 joints
def rotateArm(base, shoulder, elbow, wrist, wristPitch):

    rotateBase(base)
    rotateShoulder(shoulder)
    rotateElbow(elbow)
    rotateWrist(wrist)
    rotateWristPitch(wristPitch)


def sysCall_actuation():
    pass