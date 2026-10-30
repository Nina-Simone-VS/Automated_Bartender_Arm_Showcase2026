import time
from coppeliasim_zmqremoteapi_client import RemoteAPIClient

#our functions
from gripperSim import SimulateGripper 
from armMotion import SimulateArm 

def main():
    #connect to copeliasim
    print(f"----------\nCONNECTING TO COPELIASIM\n----------")
    client = RemoteAPIClient()
    sim = client.require('sim')

    #bring in cup and gripper base
    cupHandle = sim.getObject("/Cup")
    gripBaseHandle = sim.getObject("/BartGripper")

    #keep cup start pos
    startPos = sim.getObjectPosition(cupHandle, -1)
    startOri = sim.getObjectOrientation(cupHandle, -1)

    #connect our classes
    gripper = SimulateGripper(sim, jointNames=['/F1joint', '/F2joint', '/F3joint'])
    arm =  SimulateArm(sim)

    #start simulation
    print("----------\nSTARTING SIMULATION\n----------")
    sim.startSimulation()
    time.sleep(1)

    print("----------\nSTARTING AT REST\n----------")
    arm.moveToPosition(arm.rest_position)
    arm.holdPosition(hold_seconds=7)
    gripper.openGrip(-50) # gripper starts open 

    print("----------\nAPPROACHING CUP\n----------")
    arm.moveToPosition(arm.approach_cup)

    print("----------\nMOVING DOWN TO CUP\n----------")
    arm.moveToPosition(arm.at_cup)
    

    print("----------\nGRIPPING CUP\n----------")
    gripper.closeGrip(0)  # close around the cup
    
    #attach cup
    sim.setObjectParent(cupHandle, gripBaseHandle, True)

    arm.holdPosition(hold_seconds=3)

    print("----------\nLIFTING AND MOVING BACK\n----------")
    arm.moveToPosition(arm.lift_back)
    arm.holdPosition(hold_seconds=5)

    print("----------\nMOVING TO OTHER SIDE\n----------")
    arm.moveToPosition(arm.other_side)

    print("----------\nLOWERING TO PLACE CUP\n----------")
    arm.moveToPosition(arm.place_down)

    print("----------\nRELEASING CUP\n----------")
    gripper.openGrip(-50)
    
    print("---------\nBACK TO REST\n-------------")
    arm.moveToPosition(arm.rest_position)

    print("----------\nSTOPPING ACTION\n----------")
    arm.holdPosition(hold_seconds=7)
    #reset cup
    sim.setObjectParent(cupHandle, -1, True)
    sim.setObjectPosition(cupHandle, -1, startPos)
    sim.setObjectOrientation(cupHandle, -1, startOri)

    #close simulation
    print(f"----------\nSTOPPING COMPLETED SIMULATION\n----------")
    sim.stopSimulation()
#end main fn

if __name__ == '__main__':
    main()

