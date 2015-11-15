import glob 
import pickle
import re
def pickl(filename1):

		outfile1 = open(filename1, 'w')

		pickle.dump(phrase_dict,outfile1, pickle.HIGHEST_PROTOCOL)
		outfile1.close()

		print "Done!"
if __name__=='__main__':
	phrase_dict = {} #maybe dictionary of tuples later
	testPos = set()
	for filename in glob.glob('pickl/ppdb-*'):
		paraphrase = open(filename, 'r')
		for line in paraphrase:
			line = line.split('|||')
			word = line[2].strip() #target e
			other_word = line[1].strip() #source f
			if len(word) > len(other_word): #if e > f
				#print word 
				#print otherWord
				m = re.search('\sp\(e\|f\)=([0-9.]+)', line[3]) #get prob(f|e), probability of shorter given longer.
				#print m.group(1)
				#print line
				if (word not in phrase_dict): 
					phrase_dict[word] = {}
				phrase_dict[word][other_word] = m.group(1)
				#phrase_dict[(word, other_word)] = m.group(1) #add prob(e|f) to the phrase dict
				#phrase_dict[word] = otherWord
			elif len(other_word) > len(word): #if f > e
				m = re.search('\sp\(f\|e\)=([0-9.]+)', line[3]) #get prob(f|e), probability of shorter given longer.
				#phrase_dict[otherWord] = word
				if (other_word not in phrase_dict): 
					phrase_dict[other_word] = {}
				phrase_dict[other_word][word] = m.group(1)
				#phrase_dict[(other_word, word)] = m.group(1)  #get prob(f|e)
			testPos.add(line[0])
		paraphrase.close()
	#for pos in testPos:
		#print pos
	pickl('pickl/allPhrasesProb')
	pickled = open('pickl/allPhrasesProb', 'r')
	phrases = pickle.load(pickled)
	for key, value in phrases.iteritems() :
		print key, value