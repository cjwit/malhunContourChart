def getMalhun():
    paths = corpus.getLocalPaths()
    malhun = []
    for p in paths:
        if 'malhun' in p:
            this = corpus.parse(p)
            malhun.append(this)
    return malhun

# file name = title-singer-refrain-Final
def createMetadata(fileName):
    metadata = {}
    metadata["fileName"] = fileName
    splitName = fileName.split('-')
    metadata["title"] = splitName[0]
    metadata["artist"] = splitName[1]
    metadata["refrain"] = splitName[2].split('.')[0]
    if len(splitName) == 4:
        metadata["isFinal"] = 1
    else:
        metadata["isFinal"] = 0
    return metadata

def fromRoot(pitchFrequency, rootFrequency, pitchCollection):
    # return value from pitchCollection - root's value
    rootIndex = pitchCollection.index(rootFrequency)
    pitchIndex = pitchCollection.index(pitchFrequency)
    return pitchIndex - rootIndex

def getPitchCollection(flatScore):
    pitches = [];
    for n in flatScore:
        if n.pitch.frequency not in pitches:
            pitches.append(n.pitch.frequency)
    pitches.sort()
    return pitches

def getNotes(recursiveScore, rootFrequency):
    notes = []
    pitchCollection = getPitchCollection(recursiveScore.notes)
    transposingUp = rootFrequency < 312 # just above D# in the middle of the bass clef
    for n in recursiveScore.notes:
        noteEntry = {}
        noteEntry["offset"] = float(n.getOffsetBySite(recursiveScore))
        noteEntry["duration"] = float(n.quarterLength)
        noteEntry["fromRoot"] = 'rest'
        noteEntry["frequency"] = 'rest'
        if n.isNote:
            noteEntry["fromRoot"] = fromRoot(n.pitch.frequency, rootFrequency, pitchCollection)
            noteEntry["frequency"] = n.pitch.frequency
            if transposingUp:
                noteEntry["frequency"] *= 2
        notes.append(noteEntry)
    return notes

def createEntry(thisScore):
    entry = {}
    recursiveScore = thisScore.recurse()
    entry["metadata"] = createMetadata(thisScore.metadata.title)
    entry["root"] = recursiveScore.notes[-1].pitch.frequency
    entry["notes"] = getNotes(recursiveScore, entry["root"])
    return entry

def formatTo100(melody, increment):
    scaled = []
    for n in melody['notes']:
        formattedNote = {}
        formattedNote['offset'] = n['offset'] * increment
        formattedNote['frequency'] = n['frequency']
        formattedNote['fromRoot'] = n['fromRoot']
        scaled.append(formattedNote)
    sampled = []
    x = 0
    i = 0
    while x <= 99:
        currentNote = melody['notes'][i]
        newPoint = {}
        if i < len(melody['notes']) - 1:
            nextNote = melody['notes'][i + 1]
            if x > nextNote['offset']:
                currentNote = nextNote
                i += 1
        newPoint['offset'] = x
        newPoint['frequency'] = currentNote['frequency']
        newPoint['fromRoot'] = currentNote['fromRoot']
        sampled.append(newPoint)
        x += 1
    return sampled

def checkSimilarity(melody1, melody2):
    name1 = melody1['metadata']['fileName']
    name2 = melody2['metadata']['fileName']
    sampleSize = 100.0
    increment1 = sampleSize / melody1['notes'][-1]['offset'] # + melody1['notes'][-1]['duration']
    increment2 = sampleSize / melody2['notes'][-1]['offset'] # + melody2['notes'][-1]['duration']
    formatted1 = formatTo100(melody1, increment1)
    formatted2 = formatTo100(melody2, increment2)
    print 'last:', formatted1[0]['offset'], formatted1[-1]['offset'], len(formatted1)
    print 'last:', formatted1[0]['offset'], formatted2[-1]['offset'], len(formatted1)

checkSimilarity(data[0], data[1])
    # find closest previous y at x value, append to formatted list
    # find distance between y values at x = 0-100
    # return average distance

def getData(collection):
    data = []
    total = len(collection)
    for i, s in enumerate(collection):
        data.append(createEntry(s))
    	progress = i * 1.0 / total * 100
        print '\r' + str(round(progress, 0)) + '%'
    results = []
    return data
    # check each set against every other set
    # save similarity to an object: melody1, melody2, similarity
    # sort and print: Similarity: X, melody 1, melody 2

##### to save, once I figure out a format
#    savePath = 'contour_chart/malhun_similarity.json'
#    with open(savePath, 'w') as outfile:
#        json.dump(data, outfile)
#        print 'Data saved to', savePath

from music21 import *
import json
getData(getMalhun())
