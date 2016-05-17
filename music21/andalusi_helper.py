from music21 import *

def noteList(fileName):
	"""Convert file into a list of elements, filtered by class 'Note'."""
	ex1 = converter.parse(fileName)
	noteList = ex1.recurse().getElementsByClass('Note')
	print "Generated list of " + str(len(noteList)) + " notes."
	return noteList

import sys
def printProgress(current, total):
	"""Include in for loop to print current progress to the terminal."""
	progress = current * 100 / total * 100 / 100
	sys.stdout.write("\r%d%%" % progress)

def findPatterns(list, num):
	"""Find note patterns of a specificied length (num) within a list of notes."""
	# what I want is a sort of musical regex, but one that is greedy
	# find patterns that are equal to or longer than num
	# begin searching again at the conclusion of the previous pattern
	# print "found pattern, length N" for each
	patterns = []
	repeats = []
	for n in range(0, len(list) - num):
		testPattern = []
		for noteIndex in range(n, n + num):
			testPattern.append([list[noteIndex].name, list[noteIndex].quarterLength])
		if testPattern not in patterns:
			patterns.append(testPattern)
		else:
			repeats.append(testPattern)
		printProgress(n, len(list))
	print '\n', len(repeats), 'repeated patterns found'
	return repeats

def streamOfPatterns(patterns):
	s = stream.Stream()
	for i, p in enumerate(patterns):
		pattern = stream.Stream()
		for n in p:
			newNote = note.Note(n[0])
			newNote.quarterLength = n[1]
			pattern.append(newNote)
		s.append(pattern)
		# update results counter
		printProgress(i, len(patterns))
	return s
