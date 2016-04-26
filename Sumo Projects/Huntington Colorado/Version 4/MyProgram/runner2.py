

import os
import sys
import optparse
import subprocess
import MyClasses
import signal
import random

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

    #Settings for the experiment
    connectedRatio = 0.15
    tauUnconnected = 5
    tauConnected = 1
    #End of settings

    """execute the TraCI control loop"""
    traci.init(PORT)
    step = 0

    #Create a vehicle manager
    vehicleManager =  MyClasses.VehicleManager()

    #This loops through all of the simulaton steps as defined by the configuartion file
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()#This performs one simulation step
        step += 1 #Count the steps

        #Gets a list of all of the vehicles in the network
        listOfVehicles = traci.vehicle.getIDList()
        
        newVehicles = vehicleManager.UpdateListActiveVehicles(listOfVehicles)


        for id in newVehicles:
            x = random.random()

            if(x < connectedRatio):
                traci.vehicle.setTau(id, tauConnected)
            else:
                traci.vehicle.setTau(id, tauUnconnected)

            print str(traci.vehicle.getTau(id))

        vehicleManager.Update()

    
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
    sumoProcess = subprocess.Popen([sumoBinary, "-c", myP + "\\huntingtonColorado_exp.sumo.cfg", "--summary-output",
                                    "tripinfo_new_0.15.xml", "--remote-port", str(PORT)], stdout=sys.stdout, stderr=sys.stderr)
    print "~This is my test on running SUMO from the command line~"
    run()
    sumoProcess.wait()
    print "~End of SUMO simulation from the server port~"
