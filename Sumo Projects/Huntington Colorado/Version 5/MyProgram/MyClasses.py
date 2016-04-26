"""
@Author Xavier Lavenir
@Title Final Year Project
@Institution - University of California, Berkeley
"""

import os
import sys

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


class Platoon:

	#Constants
	const_MaxSize = 4 #Max and min platoon sizes
	const_MinSize = 2


	#Class variables, default values
	_vehicleList = [] #elements are of type 'Vehicle'
	_id = ""
	_headway = 5 #[m]
	_platoonDesSpeed = 7 #[m/s]

	#Access to classVariables
	def GetVehicleList(self):
		return self._vehicleList

	def SetVehicleList(self, vehicleList):
		self._vehicleList = vehicleList

	def GetID(self):
		return self._id

	def SetHeadway(self, headway):
		self._headway = headway

	def GetHeadway(self):
		return self._headway

	def SetHeadway(self, speed):
		self._platoonDesSpeed = speed

	def GetPlatoonDesSpeed(self):
		return self._platoonDesSpeed


	#Constructor
	def __init__(self, platoonID):
		#Provides an id for the platoon
		self._id = platoonID
		print "Platoon '" +platoonID + "' is initialised!"


	#Methods
	def Add(self, veh):
		#Adds the car to the platoon
		self._vehicleList.append(veh)
		veh.AddToPlatoon(self._id,0)

	def GetLeaderID(self):
		return _vehicleList[0].GetID()

	def Remove(self, veh):
		#Removes the car from the platoon
		self._vehicleList.remove(veh)
		veh.RemoveFromPlatoon()

	def Length(self):
		#Returns the length of the platoon
		return len(self._vehicleList)

	def _determineLeadVehicle(self, veh1, veh2):
		#Returns the id of the lead vehicle or None otherwise, returns none if at a junction
		#Returns 1 if first vehicle, 2 if second, 0 if undertermined, None if not relevant

		#Gets the ID's of the vehicles
		vehID1 = veh1.GetID()
		vehID2 = veh2.GetID()

		#Stores the roads the vehicles are on
		Road1 = traci.vehicle.getRoadID(vehID1)
		Road2 = traci.vehicle.getRoadID(vehID2)
		Route1 = traci.vehicle.getRoute(vehID1)
		Route2 = traci.vehicle.getRoute(vehID2)

		#First determines if each vehicle is on it's own route or if it's @ a junction
		if ((Road1 in Route1) and (Road2 in Route2)):
			#Checks if they are both on the same edge
			if (Road1 == Road2):
				if traci.vehicle.getLanePosition(vehID1) > traci.vehicle.getLanePosition(vehID2):
					return 1
				else:
					return 2
			else:
				#The vehicles are on different edges --> check which one is ahead
				
				#Assume vehicle 1 is ahead and if it isn't then return the other
				if (Road1 in Route2):
					ind1 = Route2.index(Road1)
					ind2 = Route2.index(Road2)

					if  (ind1>ind2):
						return 1
					else:
						return 2
				else:
					return None
				
			return 0
		else:
			return '' #In this case, we simply can't say because one of the vehicles is at an intersection


	def UpdatePlatoonOrder(self):
		#Updates the position of each vehicle within the platoon

		i = 0
		while i < len(self._vehicleList) - 1:#Loops through all vehicles in platoon
			rank = self._determineLeadVehicle(self._vehicleList[i],self._vehicleList[i+1])#Compares the two first vehicles
			
			if(rank == 2):#If the second vehicle is in front
				#Swap the order of the vehicles
				tempVeh = self._vehicleList[i]
				self._vehicleList[i] = self._vehicleList[i+1]
				self._vehicleList[i+1] = tempVeh
				i = 0
			else:
				#Itterate
				i+=1

		#Re-itterates and numbers the position of each vehicle
		j = 0
		while j < len(self._vehicleList) - 1:
			self._vehicleList[j].SetPosition(j)
			j+=1

	def PrintPlatoon(self):

		word = ""
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ' - '

		print word

	def PrintPlatoonVehicleInfo(self):

		word = ""
		for i in range(0,len(self._vehicleList)):
			word += str(traci.vehicle.getSpeed(self._vehicleList[i].GetID())) + ' - '

		print word	

	def Update(self):
		#Update
		self.UpdatePlatoonOrder()

		self.Update2ManPlatoon()
		self.printSpeeds()
		self.UpdateVehicles()



	def RemoveVehicle(self, veh):
		for v in self._vehicleList:
			if v == veh:
				self._vehicleList.remove(v)
				break

	def SetSpeeds(self):
		for v in self._vehicleList:
			traci.vehicle.setSpeed(v.GetID(), self._platoonDesSpeed)

	def Update2ManPlatoon(self):
		#Note that this is a test and obly works for a platoon consitsting of two vehicles
		if(len(self._vehicleList) <1):
			return

		traci.vehicle.setSpeed(self._vehicleList[0].GetID(), self._platoonDesSpeed)

		if(len(self._vehicleList)>1):
			lead = traci.vehicle.getLeader(self._vehicleList[1].GetID())
			if(lead != None):
				#Update the second cars speed to get a fixed distance from the second car
				K = 0.1
				#print lead[1]
				speed =  traci.vehicle.getSpeed(self._vehicleList[0].GetID()) + K*(lead[1]-self._headway)
				
				#print speed
				traci.vehicle.setSpeed(self._vehicleList[1].GetID(), speed)
				#print lead[1]
				#print traci.vehicle.getSpeed(self._vehicleList[0].GetID())
				print str(traci.vehicle.getTau(self._vehicleList[1].GetID()))


	def printSpeeds(self):
		word = ""
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ": " + str(traci.vehicle.getSpeed(self._vehicleList[i].GetID())) + ' - '

		print word	

	def UpdateVehicles(self):

		#Ensures all of the vehicles are on the same lane as the one in front
		for i in range(1,len(self._vehicleList)):

			#Road id's
			R1 = traci.vehicle.getRoadID(self._vehicleList[i-1].GetID())
			R2 = traci.vehicle.getRoadID(self._vehicleList[i].GetID())

			#If they are on the same road
			if(R1 == R2):
				#Lane id's
				L1 = traci.vehicle.getLaneIndex(self._vehicleList[i-1].GetID())
				L2 = traci.vehicle.getLaneIndex(self._vehicleList[i].GetID())
				
				#EDIT: in future edit this so that they can ve in differnt lanes if the platoon orders them to be
				if(L1 != L2):
					dur = 4#EDIT: need to figure out what this means???
					#EDIT: Need to make sure that the vehicle is not 'in the process of changing'
					traci.vehicle.changeLane(self._vehicleList[i].GetID(), L1, dur)
				#else:
					#traci.vehicle.changeLane(self._vehicleList[i].GetID(), L1, 0)




class PlatoonManager:
	#The purpose of this class is to manage all of the platoons in the system
	
	#Class variables, default values
	_platoonList = [] #This is a list of type 'Platoon'

	#Constructor
	def __init__(self):
		print 'Platoon Manager is initialised'


	def AddPlatoon(self, listOfVehicles):
		myPlat = Platoon('platoon' + str(len(self._platoonList)))

		#Loops through all of the vehicles
		for veh in listOfVehicles:
			myPlat.Add(veh)

		self._platoonList.append(myPlat)

	def RemovePlatoon(self, platoonID):
		print 'RemovePlatoon - Not made yet'

	def Update(self):
		for i in range(0,len(self._platoonList)):
			self._platoonList[i].Update()

	def RemoveVehicle(self, veh):

		for i in range(0,len(self._platoonList)):
			if(self._platoonList[i].GetID() == veh.GetPlatoonID()):
				self._platoonList[i].RemoveVehicle(veh)


class VehicleManager:
	#The purpose of this class is to manage all of the vehicles in the system

	#Class variables, default values
	_vehicleList = [] #This is a list of Type 'MyVehicle'
	platoonManager = PlatoonManager() #Manages the platoons


	#Properties
	def GetVehicleList(self):
		return _vehicleList


	#Constructor
	def __init__(self):
		print 'Vehicle Manager is initialised'


	#Methods
	def UpdateListActiveVehicles(self, listOfActiveVehicles):
		#This takes in the active vehicles in SUMO and updates the lists in this class
		_newVehiclesID = []
		_oldVehiclesID = []

		#Simple scrit to display all of th new vehicles
		word = ""

		#Loops through all of the active vehicles in SUMO
		for vehID in listOfActiveVehicles:
			#Checks if it's the currently vehicle list i.e. has it just been added or not?
			exists = False
			for i in range(0,len(self._vehicleList)):
				if(vehID == self._vehicleList[i].GetID()):
					exists = True
					break 

			if (exists == False):
				_newVehiclesID.append(vehID)
				self.AddVehicle(vehID)
				word = vehID + " - "

		for veh in self._vehicleList:
			if veh.GetID() not in listOfActiveVehicles:
				_oldVehiclesID.append(veh.GetID())
				self.RemoveVehicle(veh.GetID())


		return _newVehiclesID

	def AddVehicleList(seld, listOfVehIDs):
		#Add a list of vehicles to the system
		for vehID in listOfVehIDs:
			self.AddVehicle(vehID)

	def AddVehicle(self, vehID):
		#Add a single vehicle ot the system
		veh = MyVehicle(vehID)
		self._vehicleList.append(veh)
		#print 'Adding ' + vehID

	def RemoveVehicle(self, vehID):

		#Add a single vehicle ot the system
		for i in range(0,len(self._vehicleList)):
			if(vehID == self._vehicleList[i].GetID()):
				#print 'Removing ' +  self._vehicleList[i].GetID()
				self.platoonManager.RemoveVehicle(self._vehicleList[i])
				self._vehicleList.pop(i)
				break

	def CreatePlatoon(self, listOfVehIDs):
		self.platoonManager.AddPlatoon(self.GetVehicleListFromIDs(listOfVehIDs))


	def Update(self):
		#Update every vehicle?
		#Update each platoon
		self.platoonManager.Update()

	def GetVehicleListFromIDs(self, listOfVehicleIds):
		localVehicleList = []

		counter = 0
		for veh in self._vehicleList:
			for vehID in listOfVehicleIds:
				if (veh.GetID() == vehID):
					localVehicleList.append(veh)
					counter += 1
					break

			if counter >= len(listOfVehicleIds):
				break

		return localVehicleList
						

class MyVehicle:

	#The vehicle class provided by TracCI is more of a "static class"

	#Class variables
	_id = ""
	_inPlatoon = False
	_platoonID = None
	_platoonPosition = 0

	#Constructor
	def __init__(self, vehicleID):
		#Provides an id for the platoon
		self._id = vehicleID
		#print "Vehicle '" +vehicleID + "' is initialised!"


	#Properties
	def GetID(self):
		return self._id

	def GetPlatoonID(self):
		return self._platoonID

	def GetPosition(self):
		return self._platoonPosition

	def SetPosition(self, position):
		self._platoonPosition = position


	#Methods
	def AddToPlatoon(self, platoonID, platoonPosition):
		self._platoonID = platoonID
		self._platoonPosition = platoonPosition
		self._inPlatoon = True
		#traci.vehicle.setTau(self._id, 0.001)

	def RemoveFromPlatoon(self):
		self._platoonID = None
		self._platoonPosition = 0
		self._inPlatoon = False
