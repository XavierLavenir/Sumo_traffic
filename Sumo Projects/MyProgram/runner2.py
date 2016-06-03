

import os
import sys
import optparse
import subprocess
import MyClasses
import signal
import constants
import shutil

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
    programManager = MyClasses.ProgramManager(myP + constants.CONST_CURR_MAP.rsplit('\\',1)[0] + '\\' , constants.CONST_CURR_MAP.rsplit('\\',1)[1], configFile)
    # print '2to14_2: ' + str(traci.lane.getLength('2to14_2'))
    # print '14to1_2: ' + str(traci.lane.getLength('14to1_2'))
    # print ':1_13_0: ' + str(traci.lane.getLength(':1_13_0')) 
    # print '1to15_0: ' + str(traci.lane.getLength('1to15_0'))
    # print '15to6_0: ' + str(traci.lane.getLength('15to6_0'))
    # print '6to7_0: ' + str(traci.lane.getLength('6to7_0'))

    #This loops through all of the simulaton steps as defined by the configuartion file
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()#This performs one simulation step
        step += 1 #Count the steps
        programManager.Update(step)

        if(constants.CONST_FLOW_CUT_OFF and step > constants.CONST_FLOW_SIMULATION_TIME):
            break

        if('type0.54' not in traci.vehicle.getIDList() and step > 400):
            shutil.copyfile('C:\\Users\\Xavier\\Dropbox\\Courses\\Fall\\ME 199 - Final Year Project\\Sumo Projects\\MyProgram\\tripinfo.xml', 'C:\\Users\\Xavier\\Dropbox\\Courses\\Fall\\ME 199 - Final Year Project\\Sumo Projects\\MyProgram\\tripinfo_' +constants.CONST_EXPERIMENT_NAME+'.xml')
            break
    #programManager.OnExit()#tells the software that the program is about to end
    traci.close()
    shutil.copyfile('C:\\Users\\Xavier\\Dropbox\\Courses\\Fall\\ME 199 - Final Year Project\\Sumo Projects\\MyProgram\\tripinfo.xml', 'C:\\Users\\Xavier\\Dropbox\\Courses\\Fall\\ME 199 - Final Year Project\\Sumo Projects\\MyProgram\\tripinfo_' +constants.CONST_EXPERIMENT_NAME+'.xml')
    sys.stdout.flush()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default= not constants.CONST_GUI, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options
    #not constants.CONST_GUI
# this is the main entry point of this script
if __name__ == "__main__":
    
    if(len(sys.argv) <= 1):
        print 'ERROR - NEED TO ADD THE SETTINGS/CONFIGURATION FILE'

    configFile = str(sys.argv[1])
    constants.UpdateParameters(configFile)
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
    print "~This is the start of the SUMO simulation from the server port~"
    run()

    #sumoProcess.terminate()
    sumoProcess.wait()
    print "~End of SUMO simulation from the server port~"
