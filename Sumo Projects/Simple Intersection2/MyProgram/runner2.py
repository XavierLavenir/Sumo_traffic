

import os
import sys
import optparse
import subprocess
import MyClasses
import signal

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
# the port used for communicating with your sumo instance
PORT = 8873

def run():

    
    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0

    #Some constants for this test run
    checkDistance = 500
    maintainDistance = 10;
    errorMargin = 5;

    #Initialise the platoon
    #p1 = MyClasses.Platoon('p1')
    newPlat = True

    #Create a vehicle manager
    vehicleManager =  MyClasses.VehicleManager()

    #This loops through all of the simulaton steps as defined by the configuartion file
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()#This performs one simulation step
        step += 1 #Count the steps

        #Gets a list of all of the vehicles in the network
        listOfVehicles = traci.vehicle.getIDList()
        
        vehicleManager.UpdateListActiveVehicles(listOfVehicles)

        if len(listOfVehicles) == 4:
            if(newPlat):

                newList = [listOfVehicles[2], listOfVehicles[1], listOfVehicles[3], listOfVehicles[0]]
                vehicleManager.CreatePlatoon(newList)
                newPlat = False


        vehicleManager.Update()

        #If all of the cars are in the network
        #if len(listOfVehicles) == 4:

            #p1.Add(listOfVehicles[0])
            #p1.Add(listOfVehicles[1])
            #p1.Add(listOfVehicles[2])
            #p1.Add(listOfVehicles[3])
            


            #for myID in listOfVehicles:#Loops throug all of the vehicle ID's
                
                #Calculates the information from the leader
                #leaderInfo = traci.vehicle.getLeader(myID,checkDistance)


                #if(myID == "type0.1"):
                    #print "ID: " + str(myID) + " - roadID: " + str(traci.vehicle.getRoute(myID))
                    #print "Lead: " + str(p1._determineLeadVehicle('type0.0','type0.1'))

                #Checks if there is actually a leader
                #if(leaderInfo != None):
                    #if(abs(maintainDistance - leaderInfo[1]) > errorMargin):
                        #traci.vehicle.setSpeed(myID,traci.vehicle.getSpeed(myID) + 1)

                        #if(myID == "type0.1" or myID == "type0.0"):
                            #print "ID: " + str(myID) + " - speed: " + str(traci.vehicle.getSpeed(myID)) + " - dist: " +  str(leaderInfo[1]) + " ---leadSpeed: " + str(traci.vehicle.getSpeed("type0.0"))
                           # print "ID: " + str(myID) + " - pos: " + str(traci.vehicle.getLanePosition(myID))
                            #p1.SayHello()

    
    traci.close()
    sys.stdout.flush()



def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":
	
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    myP = os.path.abspath(os.path.join(os.getcwd(),os.pardir))
    sumoProcess = subprocess.Popen([sumoBinary, "-c", myP + "\\Intersection2Test.sumocfg", "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    print "~This is my test on running SUMO from the command line~"
    run()
    sumoProcess.terminate()
    print "~End of SUMO simulation from the server port~"
