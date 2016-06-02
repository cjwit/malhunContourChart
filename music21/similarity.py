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

def formatTo100(melody, increment, sampleSize):
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
    while x <= sampleSize - 1:
        currentNote = scaled[i]
        newPoint = {}
        if i < len(scaled) - 1:
            nextNote = scaled[i + 1]
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
    sampleSize = 1000                               # can be changed to increase or decrease resolution
    increment1 = sampleSize * 1.0 / melody1['notes'][-1]['offset']
    increment2 = sampleSize * 1.0 / melody2['notes'][-1]['offset']
    formatted1 = formatTo100(melody1, increment1, sampleSize)
    formatted2 = formatTo100(melody2, increment2, sampleSize)
    diffFromRoot = 0
    for i in range(0, len(formatted1)):
        diff = abs(formatted1[i]['fromRoot'] - formatted2[i]['fromRoot'])
        diffFromRoot += diff
    result = {}
    result['melody1'] = melody1['metadata']['fileName']
    result['melody2'] = melody2['metadata']['fileName']
    result['similarity'] = diffFromRoot * 1.0 / sampleSize
    return result

def filterSameSong(listOfResults):
    filtered = []
    for result in listOfResults:
        if result['melody1'].split("-")[0] != result['melody2'].split("-")[0]:
            filtered.append(result)
    return filtered

def getSimilarities(data):
    print 'Beginning check for similarity'
    results = []
    for i in range(0, len(data) - 2):
        for j in range(i + 1, len(data)):
            similarity = checkSimilarity(data[i], data[j])
            results.append(similarity)
    results.sort(key=lambda x: x['similarity'])
    i = 0
    for r in results:
        results[i]['index'] = i + 1
        print results[i]
        print 'index' in results[i]
        i += 1
    filtered = filterSameSong(results)
    print len(filtered), len(results)
    filteredString = ""
    for f in filtered:
        print 'index' in f
        filteredString += "| " + str(f['index']) + " | " + str(f['similarity']) + " | " + f['melody1'].split('.')[0] + " | " + f['melody2'].split('.')[0] + " |\n"
    resultString = ""
    for r in results:
        resultString += "| " + str(r['index']) + " | " + str(r['similarity']) + " | " + r['melody1'].split('.')[0] + " | " + r['melody2'].split('.')[0] + " |\n"
    savePath = 'contour_chart/malhun_similarity.md'
    headers = "| Rank | Avg. Distance | Melody 1 | Melody 2 |\n| --- | --- | --- | --- |\n"
    outputFile = open(savePath, 'w')
    outputFile.write('# Similarity between malhun melodies\n')
    outputFile.write('#### Measured by average distance from the root\n')
    outputFile.write('#### Total pairs: ' + str(len(results)) + ", pairs that are not from the same melody: " + str(len(filtered)) + '\n')
    outputFile.write('## Filtering out melodies from the same song\n')
    outputFile.write(headers + filteredString + "\n")
    outputFile.write('## All results\n')
    outputFile.write(headers + resultString)
    outputFile.close()
    print 'Data saved to', savePath

def getData(collection):
    data = []
    total = len(collection)
    for i, s in enumerate(collection):
        data.append(createEntry(s))
    	progress = i * 1.0 / total * 100
        print '\r' + str(round(progress, 0)) + '%'
    return data

from music21 import *
import json
data = getData(getMalhun())
getSimilarities(data)
