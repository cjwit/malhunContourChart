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

def getData(collection):
    data = []
    total = len(collection)
    for i, s in enumerate(collection):
        data.append(createEntry(s))
    	progress = i * 1.0 / total * 100
        print '\r' + str(round(progress, 0)) + '%'
    savePath = 'contour_chart/malhun.json'
    with open(savePath, 'w') as outfile:
        json.dump(data, outfile)
        print 'Data saved to', savePath

from music21 import *
import json
getData(getMalhun())
