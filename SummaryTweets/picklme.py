import pickle

from collections import defaultdict, Counter
import argparse
import math
import os
import re
import collections
import nltk

class Pickle:
	def __init__(self, corpusDirectory):
		self.allCorpora = {} #will be a dictionary pointing to the corpus file, each of which is a dictionary of the all the word counts.
		self.allPoSCorpora = {} 
		self.testWhatPOS = set()
		for filename in os.listdir(corpusDirectory):
			if filename.endswith(".pos"):
				self.taggedWordDictionary(corpusDirectory+str(filename))
	
	def taggedWordDictionary(self, filename):
		wordCount = defaultdict(int)
		tagCount = defaultdict(int)
		words = open(str(filename)).readlines()
		for line in words:
			"""insert a function to clean up lines"""
			line = line.split()
			for word in line:
				m = re.match(r"(?P<word>[\w.,!?()-]+)(\/)(?P<tag>[\w.,!?()-]+)", word) 
				if m != None:
					#print m.group('word'), m.group('tag')
					wordCount[m.group('word').lower()] +=1
					tagCount[m.group('tag').lower()] +=1
					self.testWhatPOS.add(m.group('tag'))
		self.allCorpora[filename] = wordCount #adds the corpus to the corpora dictionary
		self.allPoSCorpora[filename] = tagCount #adds the corpus to the corpora dictionary
	
	#pickle the first two dicts
	def pickl(self, filename1, filename2):

		outfile1 = open(filename1, 'w')
		outfile2 = open(filename2, 'w')

		pickle.dump(self.allCorpora,outfile1, pickle.HIGHEST_PROTOCOL)
		pickle.dump(self.allPoSCorpora,outfile2, pickle.HIGHEST_PROTOCOL)

		outfile1.close()
		outfile2.close()

		print "Done!"


if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', type=str, help='corpus', required=True)
	parser.add_argument('-text', type=str, help='input file', required=True)

	args = parser.parse_args()

	print "Parsing Corpus..."
	program = Pickle(args.c)
	print "Pickling..."

	program.pickl('pickl/allCorpora', 'pickl/allPoSCorpora')


