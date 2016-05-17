from music21 import *
import sys

def printProgress(current, total):
	"""Include in for loop to print current progress to the terminal."""
	progress = current * 100 / total * 100 / 100
	sys.stdout.write("\r%d%%" % progress)

def noteList(fileName):
	"""Convert file into a list of elements, filtered by class 'Note'."""
	ex1 = converter.parse(fileName)
	noteList = ex1.recurse().getElementsByClass('Note')
	print "Generated list of " + str(len(noteList)) + " notes."
	return noteList

# patterns = findPatterns(noteList('FILENAME'), 10)
def findPatterns(list, num):
	"""Find note patterns of a specificied length (num) within a list of notes."""
	# Eventually, may want to work with streams instead of a formatted list
	# Allowing for other music21 functions
	print 'Formatting input list'
	formatted = []
	n = 0
	for thisNote in list:
		formatted.append([thisNote.name, thisNote.quarterLength])
		n += 1
		printProgress(n, len(list))
	#
	print '\nFinding patterns'
	thisIndex, patterns, repeats = 0, [], []
	while thisIndex < (len(formatted) - num):
		thisIndex += 1
		test = formatted[thisIndex:thisIndex + num]
		existingPattern = False
		for p in patterns:
			if p['pattern'] == test:
				matchIndex = p['start']
				length = num
				existingPattern = True
				stillMatching = True
				# Expand the match one by one to find the longest possible
				while stillMatching:
					length += 1
					thisPattern = formatted[thisIndex:thisIndex + length]
					matchPattern = formatted[matchIndex:matchIndex + length]
					if thisPattern != matchPattern:
						# Remove the final items (they did not match)
						stillMatching = False
						thisPattern.pop()
						matchPattern.pop()
						# Test against previous matches and update the repeats collection
						alreadySeen = False
						for r in repeats:
							if matchIndex in r['start']:
								r['start'].append(thisIndex)
								alreadySeen = True
						if not alreadySeen:
							result = {
								'pattern': thisPattern,
								'start': [matchIndex, thisIndex],
								'length': len(thisPattern)
							}
							repeats.append(result)
						# Move the search ahead to the end of the current match
						thisIndex += length
		# Add new pattern for future match tests
		if not existingPattern:
			result = {
				'pattern': test,
				'start': thisIndex
			}
			patterns.append(result)
		printProgress(thisIndex, len(formatted))
	print '\nFound', len(patterns), 'individual patterns of', num, 'or more notes.'
	print 'Found', len(repeats), 'repeated patterns.'
	return repeats

def findLongestRepeat(repeats):
	l = 0
	longest = []
	for r in repeats:
		if r['length'] > l:
			l = r['length']
			longest = r['pattern']
	print 'Longest is', l, 'notes:', longest
	return longest

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
