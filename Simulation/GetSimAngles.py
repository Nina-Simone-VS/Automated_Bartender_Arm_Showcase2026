from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import math

client = RemoteAPIClient()
sim = client.require("sim")

motors = [
        '/motor1', 
        '/motor2', 
        '/motor3', 
        '/motor4'
      ]

fingers = ['/F1joint',
           '/F2joint',
           '/F3joint']

rWaypoints = []
dWaypoints = []
fingerAngles = []

#get angles i physically set it to
#--- NOTE: give python file radian angle, give CopeliaSIM's position value the degree angle ---#
for m in motors:
    handle = sim.getObject(m)

    #coppeliasim gives radians
    rAngle = sim.getJointPosition(handle)
    dAngle = math.degrees(rAngle)

    rWaypoints.append(round(rAngle, 3))
    dWaypoints.append(round(dAngle, 3))
#end for motor angles

for f in fingers:
    handle = sim.getObject(f)
    fAngle = math.degrees(sim.getJointPosition(handle))

    fingerAngles.append(round(fAngle,3))
#enf for finger angles

print(f"\nRADIAN WAYPOINTS (for .py file): {rWaypoints}")
print(f"DEGREE WAYPOINTS (for position value in CopSim {dWaypoints}")
print(f"DEGREES FINGERS: {fingerAngles}")