import glob 
import pickle
import re
def pickl(filename1, filename2):

	outfile1 = open(filename1, 'w')
	outfile2 = open(filename2, 'w')

	pickle.dump(matchings1,outfile1, pickle.HIGHEST_PROTOCOL)
	pickle.dump(matchings2,outfile2, pickle.HIGHEST_PROTOCOL)
	outfile1.close()
	outfile2.close()

	print "Done!"

if __name__=='__main__':
	#pat's arpa parsing code
	file = open('../CorpusFolder/guten_brown_reuters_state.arpa', 'r')
	matchings1 = {}
	for line in file:
		if '\\1-grams:' in line:
			break
	for line in file:
		if '\\2-grams:' in line:
			break
		matches = line.split()
		try:
			temp1 = matches.pop(1)
			#if temp1.isalpha() == False:
				#continue
			temp2 = (float(matches.pop(0)), float(matches.pop(0)))
		except IndexError:
			continue
		matchings1[temp1] = temp2

	matchings2 = {}
	for line in file:
		matches = line.split()
		try:
			temp1 = matches.pop(2) #the word
			temp2 = matches.pop(1) #the prevword
			#if temp1.isalpha() == False or temp2.isalpha() == False:
				#continue
			temp3 = float(matches.pop(0)) #the logP
		except IndexError:
			continue
		if matchings2.has_key(temp1):
			tempDict = matchings2[temp1]
		else:
			tempDict = {}
			matchings2[temp1] = tempDict
		tempDict[temp2] = temp3
		matchings2[temp1] = tempDict

	pickl('arpaUnigrams', 'arpaBigrams')
	#pickled = open('arpaUnigrams', 'r')
	pickled = open('arpaBigrams', 'r')
	phrases = pickle.load(pickled)
	#for key, value in phrases.iteritems() :
		#print key, value
