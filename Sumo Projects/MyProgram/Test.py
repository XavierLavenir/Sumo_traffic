if __name__ == "__main__":
	correct = True

	for i  in range(0,3):
		print(i)
		if(i ==2 and correct == True):
			print 'reset'
			i = 0
			correct = False
