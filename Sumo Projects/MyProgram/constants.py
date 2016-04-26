#Platoon Settings
CONST_MAXSIZE = 4
CONST_MINSIZE = 2
CONST_STOP_SPEED = 2
CONST_SEARCH_DISTANCE = 50
CONST_MIN_PLATOON_DISTANCE = 500
CONST_EXIT_PLATOON_BUFFER = 200#This is if the vehicle are not on the next edge together, when should they split before the end of the lane
CONST_SPLIT_DISTANCE = 75
CONST_LANE_CHANGE_DURATION = 4#Duration is how long it should try swap lanes
CONST_PROPORTION_CONNECTED_VEHICLES = 0.6
CONST_TAU_UNCONNECTED = 2.6
CONST_TAU_CONNECTED_NO_PLATOON = 1.5
CONST_TAU_CONNECTED_PLATOON = 1.1
CONST_ENABLE_PLATOONING = True

#These are the settings to control which map to load
CONST_MAP1 = "\\Huntington Colorado\\Version 4\\huntingtonColorado_exp.sumo.cfg"
CONST_MAP2 = "\\SimpleIntersection2\\Intersection2Test.sumocfg"
CONST_MAP3 = "\\SimpleIntersection4\\Intersection2Test.sumocfg"
CONST_MAP4 = "\\Huntington Colorado\\Version 5\\huntingtonColorado_exp.sumo.cfg"
CONST_CURR_MAP = CONST_MAP4

#Measure flow at certain nodes
CONST_MEASURE_ALL_JUNCTIONS = False
CONST_JUNCTIONS_TO_MEASURE = ['1']#List of junctions to measure if the variable above is False
CONST_MEASUREMENT_INTERVAL = 19 #In [seconds] --> how to aggregate the data
