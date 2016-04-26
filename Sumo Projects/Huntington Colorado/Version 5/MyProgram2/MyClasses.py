"""
@Author Xavier Lavenir
@Title Final Year Project
@Institution - University of California, Berkeley
"""

import os
import sys
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


class Platoon:


	#Class variables, default values
	_vehicleList = [] #elements are of type 'Vehicle'
	_id = ""
	_headway = 0.1#[m]
	_platoonDesSpeed = 12 #[m/s]
	_baseRoute =[]

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

	def GetPosition(self):
		#Return the position of the lead vehicle
		#Notes: assumes tat the vehicle list is ordered
		if(len(self._vehicleList)>0):
			return self._vehicleList[0].GetPosition()
		else:
			return None

	def GetBaseRoute(self):
		return self._baseRoute

	def SetBaseRoute(self, newBaseRoute):
		self._baseRoute = newBaseRoute

	def Count(self):
		return len(self._vehicleList)

	#Constructor
	def __init__(self, platoonID):
		#Provides an id for the platoon
		self._id = platoonID
		print "Platoon '" +platoonID + "' is initialised!"
		
		#Resets the class
		self._vehicleList = []
		self._baseRoute =[]


	#Methods
	def Add(self, veh):
		#Adds the car to the platoon
		self._vehicleList.append(veh)
		veh.AddToPlatoon(self._id,0)
		print veh.GetID() + ' added to platoon ' + self.GetID()
		#self.PrintPlatoon()

	def GetLeaderID(self):
		return _vehicleList[0].GetID()

	def Remove(self, veh):
		#self.PrintPlatoon()
		#Removes the car from the platoon
		self._vehicleList.remove(veh)
		veh.RemoveFromPlatoon()
		print veh.GetID() + ' removed from platoon ' + self.GetID()
		#self.PrintPlatoon()
		

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
		while j < len(self._vehicleList):
			self._vehicleList[j].SetPosition(j)
			#print str(self._vehicleList[j].GetID()) + ': ' + str(self._vehicleList[j].GetPosition())
			j+=1

	def PrintPlatoon(self):

		word = self.GetID() + ":"
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ' - '

		print word


	def UpdateBaseRoute(self):
		#This updates the base route of the platoon. Should be updated everytime a platoon
		# is created or when a vehicle is added/removed

		#Assumes that the _vehicleList is ordered
		vid = self._vehicleList[len(self._vehicleList)-1].GetID()
		commonEdge = traci.vehicle.getRoute(vid)[traci.vehicle.getRouteIndex(vid)]
		#This is the most recent common edge they share (the last vehicle is on it)
		#commonEdge = traci.vehicle.getRoadID(self._vehicleList[len(self._vehicleList)-1].GetID())
		newBaseRoute = [commonEdge]#The first common road... Make sure it's not a junction
		newListVeh = self._vehicleList

		#We assume that the routes of all vehicles in the platoon contains the baseRoute
		#Loop through all of the vehicles within the platoon
		ex = False

		j = 1#Continues looping until is has found a route which two vehicles are taking
		while(len(newListVeh) > 1 and ex == False):
			
			i = 0#Loops through all of the vehicles
			myNewList = []
			while i < len(newListVeh):
				R = traci.vehicle.getRoute(newListVeh[i].GetID())#Get the route of veh i
				if (newBaseRoute[0] == '83to81'):
					self.PrintPlatoon()
				edgeIndex = R.index(newBaseRoute[0])+j #Get the edge index within veh i's route
	
				#If the curr veh has no more edges, get rid of it
				if(edgeIndex >= len(R)):
					ex = True
					i+=1
					break
				#get the name of the edge
				e = R[edgeIndex]
				#Creates a list of edges and the number of vehicles
				# travelling along the edges in the next 'step'

				#Adds the vehicle to the list
				if(len(myNewList)>0):
					if (e in myNewList[0]) == False:
						myNewList[0].append(e)
						
						#Adds the vehicle to the correct list
						myNewList.append([newListVeh[i]])
					else:
						#Adds the vehicle to the correct list
						myNewList[myNewList[0].index(e)+1].append(newListVeh[i])
				else:
					myNewList.append([e])
					#Adds the vehicle to the correct list
					myNewList.append([newListVeh[i]])

				i+=1#iterate
			
			if(len(myNewList) < 1):
				break

			#default value for the index of the edge with the most vehicles
			maxI = [-1]
			m = 0
			#if(commonEdge == "L1"):
			#	print myNewList
			
			#Determines which is the longest list
			for k in range(0,len(myNewList[0])):
				if(len(myNewList[k+1])>m):
					maxI = [k]
					m = len(myNewList[k+1])
				elif (len(myNewList[k+1]) == m):
					oldMaxI = maxI
					maxI = [oldMaxI, k]

			if(m <= 1):
				print 'm less than 2'
				break

			#If there are equally many vehicles travelling on some path, 
			#then we need to look deeper and see how many are follow the next
			if(len(maxI) == 1):
				newBaseRoute.append(myNewList[0][maxI[0]])
				newListVeh = myNewList[maxI[0]+1]
				#print newListVeh
			else:
				'ERROR - HAVE NOT PROGRAMMED THIS YET'

			j+=1

		self.SetBaseRoute(newBaseRoute)#Update base route

	def PrintPlatoonVehicleInfo(self):

		word = ""
		for i in range(0,len(self._vehicleList)):
			word += str(traci.vehicle.getSpeed(self._vehicleList[i].GetID())) + ' - '

		print word	

	def Update(self):
		#Update
		self.UpdatePlatoonOrder()#Makes sure they are in order
		self.UpdateBaseRoute()#Updates the platoon route
		self.UpdateVehicleSpeedDynamics()#Updates the speed of the vehicles
		self.UpdateVehicleLaneDynamics()#Make sure they are on the correct lanes
		self.CheckRemovalVehicle()#Removes vehicle from the platoon if need be

	def RemoveVehicle(self, veh):
		for v in self._vehicleList:
			if v == veh:
				self._vehicleList.remove(v)
				break

	def CheckRemovalVehicle(self):
		#Checks if the upcoming platoon edge is the same as it's own. 
		#If not then checks how long before it reaches end of lane. If it's less than a certain distance, it leaves the platoon

		#This case is when a vehicle has a different course then the platoon
		for v in self._vehicleList:
			vid = v.GetID()
			R = traci.vehicle.getRoute(vid)
			i = traci.vehicle.getRouteIndex(vid)
			if(i+1 < len(R)):
				nextEdge =R[i+1]
				if(nextEdge not in self.GetBaseRoute()):
					if(traci.lane.getLength(R[i] + "_0") - traci.vehicle.getLanePosition(vid) < constants.CONST_EXIT_PLATOON_BUFFER):
						#Remove the vehicle from the platoon
						self.Remove(v)

		#If the gap between vehicles becomes too large, split the platoon at that gap.
		for i in range(1,len(self._vehicleList)):
			#ASSUMES IN ORDER

			#Vehicles 
			veh1 = self._vehicleList[i-1]
			veh2 = self._vehicleList[i]
			vid1 = veh1.GetID()
			vid2 = veh2.GetID()

			#routes of the subsequent vehicles & #index of the edge which the vehicle is on within its routs
			Ro1 = traci.vehicle.getRoute(vid1)
			ind1 = traci.vehicle.getRouteIndex(vid1)
			Ro2 = traci.vehicle.getRoute(vid2)
			ind2 = traci.vehicle.getRouteIndex(vid2)

			splitDistance = 0#Distance between two vehicles
			
			#If on the same edge
			if(Ro1[ind1] == Ro2[ind2]):
				splitDistance = traci.vehicle.getLanePosition(vid1) -  traci.vehicle.getLanePosition(vid2)
			else:
				#Assume that veh2 will eventually be on veh1s edge
				
				for j in range(ind2,Ro2.index(Ro1[ind1])):
					splitDistance += traci.lane.getLength(Ro2[j] + "_0")

				#Need to consider the case where one of the vehicles is at a junction
				
				if(traci.vehicle.getRoadID(vid2)==Ro2[ind2]):
					splitDistance-=traci.vehicle.getLanePosition(vid2)
				else:	
					splitDistance-=traci.lane.getLength(Ro2[ind2] + "_0")

				if(traci.vehicle.getRoadID(vid1)==Ro1[ind1]):
					splitDistance+=traci.vehicle.getLanePosition(vid1)


			if(splitDistance > constants.CONST_SPLIT_DISTANCE):
				#May be a better way to do this but I just remove all subsequent vehicles from the platoon
				print 'Platoon Split (' + self.GetID() + '), distance = ' + str(splitDistance) + ' between ' + vid1 + ' and ' + vid2

				#Keeps the first i vehicles
				while(i<len(self._vehicleList)):
					self.Remove(self._vehicleList[i])

				break;


	def UpdateVehicleSpeedDynamics(self):
		if(len(self._vehicleList) <1):
			return

		#Limits the speed of the leader vehicle to the platoon speed
		if(traci.vehicle.getSpeed(self._vehicleList[0].GetID()) > self._platoonDesSpeed):
			traci.vehicle.setSpeed(self._vehicleList[0].GetID(), self._platoonDesSpeed)

		if(len(self._vehicleList)>1):
			#Update the second cars speed to get a fixed distance from the second car
			K = 0.1
			
			for j in range(1,len(self._vehicleList)):
				lead = traci.vehicle.getLeader(self._vehicleList[j].GetID())
				if(lead != None):

					if (traci.vehicle.getSpeed(self._vehicleList[j-1].GetID()) != 0):
						#print 'update'
						speed =  traci.vehicle.getSpeed(self._vehicleList[j-1].GetID()) + K*(lead[1]-self._headway)

						#Makes sure the speed does't exceed the speed limit
						speedLim  = traci.lane.getMaxSpeed(traci.vehicle.getRoadID(self._vehicleList[j-1].GetID()) + "_0")
						if(speed>speedLim):
							speed = speedLim

						traci.vehicle.setSpeed(self._vehicleList[j].GetID(), speed)

						#If the vehicle is deccelerating then match it
						leadVAccel = traci.vehicle.getAccel(self._vehicleList[j-1].GetID())
						if(traci.vehicle.getAccel(self._vehicleList[j-1].GetID()) < 0 or traci.vehicle.getAccel(self._vehicleList[j].GetID())<0):
							print "ERROROOOROOR	"
					#else:
						#print 'Lead vehicle has stopped -- follower speed:' + str(traci.vehicle.getSpeed(self._vehicleList[j].GetID()))
						

				else:
					#The vehicle follows the previous speed until is is given a new speed--?if the leader is out of sight, start the car model again
					traci.vehicle.setSpeed(self._vehicleList[j].GetID(), -1)

	def printSpeeds(self):
		word = ""
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ": " + str(traci.vehicle.getSpeed(self._vehicleList[i].GetID())) + ' - '

		print word

	def printAccelss(self):
		word = ""
		for i in range(0,len(self._vehicleList)):
			word += self._vehicleList[i].GetID() + ": " + str(traci.vehicle.getAccel(self._vehicleList[i].GetID())) + ' - '

		print word

	def UpdateVehicleLaneDynamics(self):
		#All of the follower vehicles should just follow the leader vehicle
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
				else:
					#This forces the vehicle to be on the same lane as the leader (or sumo overides this)
					traci.vehicle.changeLane(self._vehicleList[i].GetID(), L1, 0)


	def ShouldVehicleJoin(self, vehID):
		#This checks if the vehicle should join the platoon
		#Distance they can travel together
		if(self.Count() >= constants.CONST_MAXSIZE):
			return False

		totalDistance = 0

		#routes of the subsequent vehicles
		R = traci.vehicle.getRoute(vehID)

		#index of the edge which the vehicle is on within its routs
		ind = traci.vehicle.getRouteIndex(vehID)
		
		if(R[ind] not in self.GetBaseRoute()):
			return False
		else:
			bInd = self.GetBaseRoute().index(R[ind])

		#Loops through the first route starting from the index
		for i in range(bInd,len(self.GetBaseRoute())):

			if(R[ind]!=self.GetBaseRoute()[bInd]):
				break;
			else:
				#Update distance etc...
				totalDistance += traci.lane.getLength(R[ind] + "_0")

				#Update counters
				ind+=1
				bInd+=1

		#Gets total distance and removes the distance it has travelled along the current lane
		totalDistance = totalDistance - traci.vehicle.getLanePosition(vehID)
		if(totalDistance >constants.CONST_MIN_PLATOON_DISTANCE):
			return True
		else:
			return False

class PlatoonManager:
	#The purpose of this class is to manage all of the platoons in the system
	
	#Class variables, default values
	_platoonList = [] #This is a list of type 'Platoon'

	#Properties
	def GetPlatoonIdList(self):
		l = []
		for i in range(0,len(self._platoonList)):
			l.append(self._platoonList[i].GetID())
		return l

	def GetPlatoon(self, platoonID):
		if(platoonID in self.GetPlatoonIdList()):
			for p in self._platoonList:
				if(p.GetID() == platoonID):
					return p
		else:
			print ('Platoon :' + str(platoonID) + ' does not exist.')
			return None

	#Constructor
	def __init__(self):
		print 'Platoon Manager is initialised'

	def AddPlatoon(self, listOfVehicles):

		i = 0
		unique = False
		while not unique:
			newPID = 'platoon' + str(len(self._platoonList) + i)

			if( newPID	not in self.GetPlatoonIdList()):
				unique = True
			i+=1

		myPlat = Platoon(newPID)
		
		#Loops through all of the vehicles
		for veh in listOfVehicles:
			myPlat.Add(veh)

		#Need to update the 'base route' of the platoon

		#Add to the list to be managed
		self._platoonList.append(myPlat)
		myPlat = None

	def RemovePlatoon(self, platoonID):
		#Remove all of the vehicles in the platoon and then delete the platoon
		p = self.GetPlatoon(platoonID)

		for veh in p.GetVehicleList():
			veh.RemoveFromPlatoon()

		for i in range(0,len(self._platoonList)):
			if (p.GetID() == self._platoonList[i].GetID()):
				self._platoonList.pop(i)
				break
		p = None


	def Update(self):

		i = 0
		while i <len(self._platoonList):
			self._platoonList[i].Update()

			#Removes any platoons with less than 2 vehicles
			if(self._platoonList[i].Count() <constants.CONST_MINSIZE):
				self.RemovePlatoon(self._platoonList[i].GetID())
				i-=1


			i+=1
			#print self._platoonList[i].GetID()

	def RemoveVehicle(self, veh):

		for i in range(0,len(self._platoonList)):
			if(self._platoonList[i].GetID() == veh.GetPlatoonID()):
				self._platoonList[i].RemoveVehicle(veh)


	def RequestVehicleJoin(self, vehID, platoonID):
		p = self.GetPlatoon(platoonID)

		if(p == None):
			return False
		else:
			return p.ShouldVehicleJoin(vehID)

	def MergePlatoons(self, platoonID1, platoonID2):


		print 'Merging:' + platoonID2 + ' with ' + platoonID1
		print self.GetPlatoon(platoonID2).PrintPlatoon()
		print self.GetPlatoon(platoonID1).PrintPlatoon()

		p1 = self.GetPlatoon(platoonID1)
		newListofVeh = self.GetPlatoon(platoonID2).GetVehicleList()
		self.RemovePlatoon(platoonID2);

		for i in range(0, len(newListofVeh)):
			p1.Add(newListofVeh[i])

		newListofVeh = None

		print 'Add merge function'

class VehicleManager:
	#The purpose of this class is to manage all of the vehicles in the system

	#Class variables, default values
	_vehicleList = [] #This is a list of Type 'MyVehicle'
	platoonManager = PlatoonManager() #Manages the platoons
	_laneList = []

	#Properties
	def GetVehicleList(self):
		return _vehicleList


	#Constructor
	def __init__(self):
		#Gets a list of all of the lanes in the network
		self._laneList = traci.lane.getIDList()
		print 'Vehicle Manager is initialised'


	#Methods
	def UpdateListActiveVehicles(self, listOfActiveVehicles):
		#This takes in the active vehicles in SUMO and updates the lists in this class
		_newVehiclesID = []
		_oldVehiclesID = []

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

		for veh in self._vehicleList:
			if veh.GetID() not in listOfActiveVehicles:
				_oldVehiclesID.append(veh.GetID())
				self.RemoveVehicle(veh.GetID())

	def AddVehicleList(seld, listOfVehIDs):
		#Add a list of vehicles to the system
		for vehID in listOfVehIDs:
			self.AddVehicle(vehID)

	def AddVehicle(self, vehID):
		#Add a single vehicle ot the system
		veh = MyVehicle(vehID)
		self._vehicleList.append(veh)
		print 'Adding ' + vehID

	def RemoveVehicle(self, vehID):

		#Add a single vehicle ot the system
		for i in range(0,len(self._vehicleList)):
			if(vehID == self._vehicleList[i].GetID()):
				print 'Removing ' +  self._vehicleList[i].GetID()
				self.platoonManager.RemoveVehicle(self._vehicleList[i])
				self._vehicleList.pop(i)
				break

	def CreatePlatoon(self, listOfVehIDs):
		self.platoonManager.AddPlatoon(self.GetVehicleListFromIDs(listOfVehIDs))

	def Update(self):
		#Update every vehicle?
		#Update each platoon
		self.platoonManager.Update()
		self.FormPlatoons()

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

	def GetVehicleFromID(self, vehID):
		localVehicleList = []
		listOfVehicleIds = [vehID]

		counter = 0
		for veh in self._vehicleList:
			for vehID in listOfVehicleIds:
				if (veh.GetID() == vehID):
					localVehicleList.append(veh)
					counter += 1
					break

			if counter >= len(listOfVehicleIds):
				break

		return localVehicleList[0]
						
	def FormPlatoons(self):
		#Loops through all of the id's of the lanes in the network
		for i in self._laneList:
			#List of platoons which have at least one vehicle on the lane
			lanePlatoonList = []

			#List of ifs of the vehicles which are on the lane
			locVehList = traci.lane.getLastStepVehicleIDs(i)
			#Jumps to the next lane if there are not 2 vehicles in the lane
			if (len(locVehList)) < 2:
				continue

			#Loops through all of the vehicles on the lane
			#print locVehList
			for j in range(1,len(locVehList)):

				#Compare subsequent vehicles
				veh1 = self.GetVehicleFromID(locVehList[j])
				veh2 = self.GetVehicleFromID(locVehList[j-1])

				#If the susbsequent vehicles are within the 'search distance'
				if(abs((veh2.GetPosition() - veh1.GetPosition()) < constants.CONST_SEARCH_DISTANCE)):
					
					#First we need to check if one of them is in a platoon
					if(veh1.GetInPlatoon() and veh2.GetInPlatoon()):
						#they are both in platoons
						if(veh1.GetPlatoonID() != veh2.GetPlatoonID()):
							#Not in same platoon... can we merge them?
							print 'POSSIBLE MERGE? -- ADD LATER'

							#Compare both base routes and if they line up then merge them
							if(self.ShouldPlatoonsMerge(veh1.GetPlatoonID(),veh2.GetPlatoonID(),veh1,veh2)):
								self.platoonManager.MergePlatoons(veh1.GetPlatoonID(),veh2.GetPlatoonID())
							continue
						else:
							#In the same platoon..continue
							continue
					elif(veh1.GetInPlatoon() and (not veh2.GetInPlatoon())):
						#Veh1 in platoon and veh2 not in platoon
						
						#Need to check if veh2 should join the platoon. does it travel far enough with the platoon?
						if(self.platoonManager.RequestVehicleJoin(veh2.GetID(), veh1.GetPlatoonID())):
							self.platoonManager.GetPlatoon(veh1.GetPlatoonID()).Add(veh2)
							#print 'Adding: ' + veh2.GetID()+ ' because of ' + veh1.GetID()
						else:
							continue

					elif(veh2.GetInPlatoon() and (not veh1.GetInPlatoon())):
						#Veh1 not in platoon and veh2  in platoon
						
						#Need to check if veh1 should join the platoon. does it travel far enough with the platoon?
						if(self.platoonManager.RequestVehicleJoin(veh1.GetID(), veh2.GetPlatoonID())):
							self.platoonManager.GetPlatoon(veh2.GetPlatoonID()).Add(veh1)
							#print 'Adding: ' + veh1.GetID() + ' because of ' + veh2.GetID()
						else:
							continue
					else:
						#neither in platoon
						#Distance they can travel together
						totalDistance = self._getDistanceTravelledTogether(locVehList[j-1],locVehList[j]) - traci.vehicle.getLanePosition(locVehList[j-1])
						
						if(totalDistance > constants.CONST_MIN_PLATOON_DISTANCE):
							#print 'new platoon!'
							newPlatoon = [veh1, veh2]
							self.platoonManager.AddPlatoon(newPlatoon)


	def ShouldPlatoonsMerge(self, platoonID1, platoonID2, veh1, veh2):
		#Checks whether 2 platoons should merge, the two vehicles 
		#are the ones who initiated the convo

		#Assume platoon 1 is ahead of platoon 2
		#Assume veh 1 is ahead of veh 2

		vehID1 = veh1.GetID()
		vehID2 = veh2.GetID()

		print vehID1 + ' - ' + vehID2
		#Compare their base routes
		p1 = self.platoonManager.GetPlatoon(platoonID1)
		p2 = self.platoonManager.GetPlatoon(platoonID2)
		BR1 = p1.GetBaseRoute()
		BR2 = p2.GetBaseRoute()

		if(len(BR1) == 0 or len(BR2) ==0):
			return False

		#Only merge if the veh are the last and first in their respective platoons
		if(veh1.GetPosition() != p1.Count() - 1 or veh2.GetPosition() != 0):
			return False

		#If the merged platoon would be too big, return false
		if(p1.Count() + p2.Count() > constants.CONST_MAXSIZE):
			return False 

		R1 = traci.vehicle.getRoute(vehID1)
		R2 = traci.vehicle.getRoute(vehID2)

		#index of the edge which the vehicle is on within its routs
		indV1 = traci.vehicle.getRouteIndex(vehID1)
		indV2 = traci.vehicle.getRouteIndex(vehID2)

		print BR1
		print BR2
		print R1[indV1]
		print R2[indV2]

		#Indices within the base routes
		ind1 = BR1.index(R1[indV1])
		ind2 = BR2.index(R2[indV2])

		#Distance they can travel together
		totalDistance = 0
		
		#Loops through the first route starting from the index

		if(len(BR1) < len(BR2)):
			for i in range(ind1,len(BR1)):
				if(BR1[ind1]!=BR2[ind2]):
					break;
				else:
					#Update distance etc...
					totalDistance += traci.lane.getLength(BR1[ind1] + "_0")

					#Update counters
					ind1+=1
					ind2+=1
		else:
			for i in range(ind2,len(BR2)):
				if(BR1[ind1]!=BR2[ind2]):
					break;
				else:
					#Update distance etc...
					totalDistance += traci.lane.getLength(BR1[ind1] + "_0")

					#Update counters
					ind1+=1
					ind2+=1


		totalDistance-=traci.vehicle.getLanePosition(vehID2)


		print str(totalDistance)
		if(totalDistance > constants.CONST_MIN_PLATOON_DISTANCE):
			return True
		else:
			return False


	def _getDistanceTravelledTogether(self, vehID1, VehID2):
		#Distance they can travel together
		totalDistance = 0

		#routes of the subsequent vehicles
		R1 = traci.vehicle.getRoute(vehID1)
		R2 = traci.vehicle.getRoute(VehID2)

		#index of the edge which the vehicle is on within its routs
		ind1 = traci.vehicle.getRouteIndex(vehID1)
		ind2 = traci.vehicle.getRouteIndex(VehID2)

		#Loops through the first route starting from the index
		for i in range(ind1,len(R1)):
			if(R1[ind1]!=R2[ind2]):
				break;
			else:
				#Update distance etc...
				totalDistance += traci.lane.getLength(R1[ind1] + "_0")

				#Update counters
				ind1+=1
				ind2+=1
		return totalDistance


class MyVehicle:
	#The vehicle class provided by TracCI is more of a "static class"

	#Class variables
	_id = ""
	_inPlatoon = False
	_platoonID = None
	_platoonPosition = 1
	_requestMerge = 0 #Testing this feature out


	#Constructor
	def __init__(self, vehicleID):
		#Provides an id for the platoon
		self._id = vehicleID
		#print "Vehicle '" +vehicleID + "' is initialised!"
		self.UpdateColor()


	#Properties
	def GetID(self):
		return self._id

	def GetPlatoonID(self):
		return self._platoonID

	def GetPosition(self):
		return self._platoonPosition

	def SetPosition(self, position):
		if (self._platoonPosition != position):
			self._platoonPosition = position
			self.UpdateColor()

	def GetPreviousEdgeID(self):
		return 'not impl'

	def GetInPlatoon(self):
		return self._inPlatoon

	#Methods
	def AddToPlatoon(self, platoonID, platoonPosition):
		self._platoonID = platoonID
		self._platoonPosition = platoonPosition
		self._inPlatoon = True
		#traci.vehicle.setTau(self._id, 0.001)
		#Test maybe remove after
		traci.vehicle.setLaneChangeMode(self._id,257)#341#321
		#traci.vehicle.setSpeedMode(self._id,31)
		self.UpdateColor()

	def RemoveFromPlatoon(self):
		self._platoonID = None
		self._platoonPosition = 1
		self._inPlatoon = False
		traci.vehicle.setLaneChangeMode(self._id,597)
		#traci.vehicle.setSpeedMode(self._id,31)
		self.UpdateColor()

	def UpdateColor(self):

		#The color code will be:
		#Red: leader
		#Blue: platoon
		#Yellow: not in platoon
		
		if(self._inPlatoon):
			if(self._platoonPosition == 0):
				traci.vehicle.setColor(self._id, (255,0,0,0))
			else:
				traci.vehicle.setColor(self._id, (100,149,237,0))
		else:
			traci.vehicle.setColor(self._id, (255,255,0,0))

