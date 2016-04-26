

import os
import sys
import optparse
import subprocess
import MyClasses
import signal
import constants

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

    #Create a vehicle manager

    vehicleManager =  MyClasses.VehicleManager(myP + constants.CONST_CURR_MAP.rsplit('\\',1)[0] + '\\' , constants.CONST_CURR_MAP.rsplit('\\',1)[1])

    #This loops through all of the simulaton steps as defined by the configuartion file
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()#This performs one simulation step
        step += 1 #Count the steps

        #Gets a list of all of the vehicles in the network
        listOfVehicles = traci.vehicle.getIDList()

        #Adds the vehicles to the list
        vehicleManager.UpdateListActiveVehicles(listOfVehicles)
        if(constants.CONST_ENABLE_PLATOONING):
            vehicleManager.Update(step)

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
    sumoProcess = subprocess.Popen([sumoBinary, "-c", myP + constants.CONST_CURR_MAP, "--tripinfo-output",
                                    "tripinfo.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    print "~This is my test on running SUMO from the command line~"
    run()

    sumoProcess.terminate()
    print "~End of SUMO simulation from the server port~"
