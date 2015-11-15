from stat_parser.parser import Parser
import re
import nltk
import numpy
import pickle

nouns = ['NN','NNS','NNP','NNPS']
adverbs = ['RB','RBR','RBS']
adjs = ['JJ','JJR','JJS']
nodrop = ['not','never','last', 'next']

class compressor:


	def __init__(self):
		"""load dictionaries"""
		all_phrases = open('pickl/allPhrasesProb')
		self.all_phrases = pickle.load(all_phrases)
		all_phrases.close()

		all_unigrams = open('pickl/arpaUnigrams')
		all_bigrams = open('pickl/arpaBigrams')

		self.all_unigrams = pickle.load(all_unigrams)
		self.all_bigrams = pickle.load(all_bigrams)

		all_unigrams.close()
		all_bigrams.close()

	def simple_drop(self, sentences, text, scores):
		"""drops adjs and adverbs based on tf-idf scores and location"""
		score = numpy.percentile([scores.values()], 75) #threshold for deleting words - upper quartile

		for sentence in sentences:
			tokenized = [i[0] for i in sentence[0]] #gets word in the sentence

			POS = nltk.pos_tag(tokenized)
			#print POS
			for i, word_tuple in enumerate(sentence[0]):
				if POS[i][1] in adjs: #if adj
					#if the word coming after the adjective is a noun and the adj is not important by tf_idf, delete it
					if i < len(sentence[0])-1 and POS[i+1][1] in nouns and word_tuple[1]<= score and word_tuple[0].lower() not in nodrop:
						sentence[0].remove(word_tuple)
						del POS[i]
				elif POS[i][1] in adverbs:
					if word_tuple[1]<=score and word_tuple[0].lower() not in nodrop:
						sentence[0].remove(word_tuple)
						del POS[i]
		return sentences

	# def simple_drop(self, sentences, text, scores):
	# 	#alternate method just utilizing bigram probability, but it is not choosing good words.
	# 	score = numpy.percentile([scores.values()], 85) #threshold for deleting words - upper quartile
	# 	print score
	# 	for sentence in sentences:
	# 		tokenized = [i[0].strip("'.,?!") for i in sentence[0]] #just gets word in the sentence
	# 		print tokenized

	# 		POS = nltk.pos_tag(tokenized)
	# 		#print POS
	# 		for i, word_tuple in enumerate(sentence[0]):
	# 			drop_word = word_tuple[0].lower().strip("'.,?")
	# 			if i < len(tokenized)-1 and word_tuple[1]<= score and drop_word not in nodrop:

	# 				if i != 0: prev_word = sentence[0][i-1][0]
	# 				else: prev_word = '<s>'
	# 				if i != len(tokenized)-2: next_word_if_delete = tokenized[i+2]
	# 				else: next_word_if_delete = '.'
	# 				p_sentence_w_word = self.get_probability(drop_word, prev_word, tokenized[i+1])[1]
	# 				p_sentence_wo_word = self.get_probability(tokenized[i+1],prev_word,next_word_if_delete)[1]

	# 				if p_sentence_w_word <= p_sentence_wo_word:
	# 					sentence[0].remove(word_tuple)
	# 					del POS[i]
	# 					print "removed {0}".format(word_tuple)
	# 				else: print "score too low"

	# 	return sentences

	def get_probability(self, poss_paraphrase, prev_word, next_word):

		prob_p = 0
		paraphrase = poss_paraphrase #copy, in case overwritten by <unk> in next step

		if poss_paraphrase not in self.all_unigrams:
			poss_paraphrase = '<unk>'

		if prev_word in self.all_bigrams and poss_paraphrase in self.all_bigrams[prev_word]:
			prob_p += self.all_bigrams[prev_word][poss_paraphrase]
		else:
			if prev_word not in self.all_unigrams: #must put in <unk> probability
				prev_word = '<unk>'
			prob_p += self.all_unigrams[prev_word][1] + self.all_unigrams[poss_paraphrase][0] #backoff(c-1) and P(c)

		if poss_paraphrase in self.all_bigrams and next_word in self.all_bigrams[poss_paraphrase]:
			prob_p += self.all_bigrams[poss_paraphrase][next_word]
		else:
			if next_word not in self.all_unigrams: #must put in <unk> probability
				next_word = '<unk>'
			prob_p += self.all_unigrams[poss_paraphrase][1] + self.all_unigrams[poss_paraphrase][0] #backoff(c-1) and P(c)
		return (paraphrase, prob_p)

	def get_dictionary_paraphrase(self, unigram, prev_word, next_word):
		"""gets best phrase"""
		#r_punc and l_punc just to keep syntax
		r_punc = ''
		l_punc = ''
		if unigram.rstrip(".'.,!?;:'*)]") != unigram: #if there exists a punctuation on the right
			r_punc = unigram[-1]
		if unigram.lstrip(".'.,!?;:'*([") != unigram: #if there exists a punctuation on the left
			l_punc = unigram[-1]

		unigram_uniform = unigram.strip(".'.,!?;:'*()[]").lower()

		#getting the probability of the orgininal word in the sentence, in case of bad paraphrases
		phrase_prob = self.get_probability(unigram_uniform, prev_word, next_word)
		maxscore = (phrase_prob[0], phrase_prob[1]*1.2) #weight so it's not biased to choosing original word

		for poss_paraphrase in self.all_phrases[unigram_uniform]:

			prob_p = self.all_phrases[unigram_uniform][poss_paraphrase]*(-1) #p(e|f) in PPDB
			phrase = self.get_probability(poss_paraphrase, prev_word, next_word)

			phrase_prob = prob_p + phrase[1]
			#print "changes to {0} with prob {1}".format(phrase[0], phrase_prob)

			if phrase_prob > maxscore[1]:
				#print "update"
				maxscore = (phrase[0], phrase_prob)

		guess_unigram = maxscore[0]
		#print "max score is {0}".format(maxscore)

		if unigram[0].lower() != unigram[0]: #check if capitalized
			guess_unigram = guess_unigram.capitalize() #then also capitalize the new unigram
		new_unigram = l_punc + guess_unigram + r_punc
		return new_unigram

	def compress_sentences(self, sentences_in_lists):
		sentences = []

		"""unigram compression"""
		for sent_list in sentences_in_lists:
			max_changes = len(sent_list[0])/2 #the greatest number of changes we want to make in each sentence
			unigrams = []
			changes = 0
			new_sent = []

			for index, unigram in enumerate(sent_list[0]):
			#if changes > max_changes: break
				unigram_uniform = unigram[0].strip(".'.,!?;:'*()[]").lower() #stripped and lowercased to check in the dictionary
				if unigram_uniform in self.all_phrases: #if there is a paraphrase in the dictionary,

					if index != 0: prev_word = sent_list[0][index-1][0]
					else: prev_word = '<s>'

					if index != len(sent_list[0])-1: next_word = sent_list[0][index+1][0]
					else: next_word = '</s>'
					new_unigram = self.get_dictionary_paraphrase(unigram[0], prev_word, next_word)
					unigram = (new_unigram, unigram[1])
					changes += 1
				new_sent.append(unigram)

			sentence = ''
			for ind,i in enumerate(new_sent):
				word = i[0]
				sentence += word
				if ind < len(new_sent):
					sentence += ' '

			sentences.append((sentence, sent_list[1], sent_list[2]))

		return sentences

#might expand this in the future.
# def tag(text):
# 	parser = Parser()
# 	sentences = re.split('(?<=[.!?-]) +', text)
	# tree = parser.parse(text)
	# for subtree in tree.subtrees():
	# 	print subtree
	# 	print "parent = {0}".format(subtree.parent())
	# return tree

# def drop_phrases(sentences, text):
# 	"""reads in sentences and drops certain parts of speech based on their tf-idf score"""
# 	parser = Parser()
