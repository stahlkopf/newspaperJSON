from collections import defaultdict, Counter
import argparse
import math
import os
import re
import collections
import pickle
import sys
import string
import parse_compress #for sentence compression
from newspaper import Article#to get an article from a url
from unidecode import unidecode #to handle non-unicode characters


class tfidf:


	def __init__(self):
		"""open and load pickl files containing dictionary"""
		all_corpora = open('pickl/allCorpora')
		all_phrases = open('pickl/allPhrases')

		self.all_corpora = pickle.load(all_corpora) #dictionary pointing to the corpus file, each of which is a dictionary of all the word counts.
		self.all_phrases = pickle.load(all_phrases)

		all_corpora.close()
		all_phrases.close()

		self.url = ''	#store url, if any

		self.compressor = parse_compress.compressor()

	def has_url(self):
		return self.url != ''

	def get_input_text(self, filename):
		"""Return the text within a file for summarizing"""
		try:
			my_file = open(filename, 'r')
			text = ''
			for line in my_file:
				text = text + line
			return text
		except IOError:
			print 'ERROR: Invalid filename'
			return False

	def read_input_text(self, input_text):
		"""Preprocesses the input_text. removes and stores the url, and also fixes any ascii character bugs"""

		#first search for a url, store it and remove it from the input text
		#we are assuming only 1 url per input - makes sense in the context of twitter
		m = re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[~$-_@.&#+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', input_text)
		if m: #if there is a url
			self.url = str(m.group(0))
			input_text = input_text.replace(self.url, '')
		if len(input_text)==0: #if the only text provided was a url scrape the webpage for the text.
			input_text = self.extract(self.url)
		input_text = unidecode(input_text) #handle non unicode characters - does not work on the server

		return input_text

	def extract(self, article_url):

		article = Article(url=article_url)
		article.download()
		article.parse()

		return article.text

	def tf_idf(self, input_text):
		"""returns a tf-idf dictionary for each term in input_text"""
		tfidf_dict = {}
		input_word_dictionary = defaultdict(int)
		input_text = input_text.split()
		for w in input_text:
			word = w.strip("\"'.,!?;:'*()-")
			input_word_dictionary[string.lower(word)] +=1

		for w in input_text:
			word = w.strip("\"'.,!?;:'*()-")

			tf = input_word_dictionary[string.lower(word)]

			num_files = 0
			for corpus in self.all_corpora:
				if word in self.all_corpora[corpus]:
					num_files +=1
			if num_files ==0: #if the word isn't in any of the corpora
				num_files = .1 #assume it is important

			idf = math.log((len(self.all_corpora)/(num_files)))
			tfidf = tf * idf
			tfidf_dict[string.lower(word)] = tfidf

		return tfidf_dict

	def total_sent_score(self, input_text, scores):
		"""Compute the total tf-idf score of a sentence by summing the scores of each word in each sentence"""

		sentences = re.split('(?<=[.!?]) +', input_text)
		top_sentences = []

		for index, sentence in enumerate(sentences):
			words = sentence.split()
			total_score = 0.0
			num_words = 0.0
			word_list = []
			if len(sentence) > 1: #to avoid single punctuation marks or one-word sentences.
				for word in words:
					if word != '-': #dashes are interpreted as word because they have spaces on both sides - and get very high tf- idf
						num_words += 1
						score = scores[string.lower(word.strip("\"'.,!?;:'*()-"))]
						#print word
						#print score
						total_score += score
						word_list.append((word, score))

				if num_words != 0: top_sentences.append((word_list, total_score / num_words, index))

		#returns all the sentences with a score and index
		return top_sentences

	def output_sentences(self, sentences, out_length):
		"""ordering sentences and printing to correct length"""
		output = []
		total_length = 0
		sentences.sort(key = lambda x:x[1], reverse = True)
		#print sentences

		for sentence in sentences:
			length = len(sentence[0]) + 1 #+1 for space before sentences
			if total_length + length > out_length: continue
			total_length += length

			#insert sentences in the correct order
			counter = 0
			for i in range(len(output)):
				if output[i][2] < sentence[2]:
					counter += 1
			output.insert(counter, sentence)

		#create the output string, append url
		out_string = ''
		for i in output:
			out_string += i[0]
		if len(out_string)>0:
			out_string += self.url
		else:
			out_string += 'It seems that all the sentences were too long to be compressed to a Tweet or the input text was not in English. Thank you for using SummaryTweets.'

		return out_string

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-text', type=str, help='input text', required=False)
	parser.add_argument('-textfile', type=str, help='boolean if given input file', required=False)
	parser.add_argument('-length', type=str, help='length of final compression', required=False, default=134) #140 for twitter,
																											  # -6 for #CS73 hashtag+space
	args = parser.parse_args()

	if args.text is None and args.textfile is None:
		print "Either command line text or a text file is required!"
		sys.exit()

	print "Parsing Corpus..."
	program = tfidf()
	if args.textfile != None:
		print 'Opening Input Text File...'
		text = program.get_input_text(args.textfile)
		args.text = text
		if text == False:
			sys.exit()
	print "Calculating Score..."

	processed_text = program.read_input_text(args.text)
	scores = program.tf_idf(processed_text)

	summary = program.total_sent_score(processed_text, scores)
	dropped = program.compressor.simple_drop(summary, processed_text, scores)
	if program.has_url(): length = args.length - 23 #-23 for link+space(twitter condenses all links to max 22 characters)
	else: length = args.length
	compressed = program.compressor.compress_sentences(dropped)
	output = program.output_sentences(compressed, length)

	print 'The output text is:'
	print output
