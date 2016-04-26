import xml.etree.ElementTree as ET

class TestClass():

	def SayHello(self):
		
		i = 0
		return 'Shit' if (i==6) else 0
		
		return 0

def run():
	tree = ET.parse('huntingtonColorado_exp.sumo.cfg')
	root = tree.getroot()

	theNetAddress = ''

	for child in root:
		if(child.tag == 'input'):
			for sub in child:
				if(sub.tag == 'net-file'):
					theNetAddress =  sub.attrib['value']
				break


	tree = ET.parse(theNetAddress)
	root = tree.getroot()

	myJunctionDic = {}

	for child in root:
		if(child.tag == 'junction'):
			theSubDic = child.attrib
			allLanesList = theSubDic['incLanes'].split()
			uniqueEdgeList = []
			for i in allLanesList:
				edge = i.split('_')[0]

				if(edge not in uniqueEdgeList):
					uniqueEdgeList.append(edge)

			myJunctionDic[theSubDic['id']] = uniqueEdgeList

	print myJunctionDic
	

if __name__ == "__main__":
	run()