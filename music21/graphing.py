def getMalhun():
    paths = corpus.getLocalPaths()
    malhun = []
    for p in paths:
        if 'malhun' in p:
            this = corpus.parse(p)
            malhun.append(this)
    return malhun

# file name = title-singer-refrain-final
def createMetadata(thisScore):
    metadata = {}
    fileName = thisScore.metadata.title
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

def findRoot(thisScore):
    # filter for multiple parts
    return thisScore.flat.notes[-1].pitch.frequency

def getNotes(thisScore):
    notes = []
    root = thisScore.flat.notes[-1].pitch
    for n in thisScore.recurse().notesAndRests:
        noteEntry = {}
        noteEntry["offset"] = float(n.getOffsetBySite(thisScore.recurse()))
        noteEntry["duration"] = float(n.quarterLength)
        noteEntry["fromRoot"] = 'rest'
        noteEntry["frequency"] = 'rest'
        if n.isNote:
            noteEntry["fromRoot"] = float(interval.Interval(root, n.pitch).chromatic.semitones)
            noteEntry["frequency"] = n.pitch.frequency
        notes.append(noteEntry)
    return notes

def createEntry(thisScore):
    entry = {}
    entry["metadata"] = createMetadata(thisScore)
    entry["root"] = findRoot(thisScore)
    entry["notes"] = getNotes(thisScore)
    return entry

def getData(collection):
    data = []
    for s in collection:
        data.append(createEntry(s))
    return data

from music21 import *
from json import dumps
data = getData(getMalhun())
jsonData = dumps(data)
print jsonData
