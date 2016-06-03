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
    results = []
    for i in range(0, len(data) - 2):
        for j in range(i + 1, len(data)):
            similarity = checkSimilarity(data[i], data[j])
            results.append(similarity)
            progress = i * 1.0 / len(data) * 100
            sys.stdout.write("  --  Checking for similarity: %d%%\r" % progress)
            sys.stdout.flush()
    results.sort(key=lambda x: x['similarity'])
    i = 0
    for r in results:
        results[i]['index'] = i + 1
        i += 1
    filtered = filterSameSong(results)
    filteredString = ""
    for f in filtered:
        filteredString += "| " + str(f['index']) + " | " + str(f['similarity']) + " | " + f['melody1'].split('.')[0] + " | " + f['melody2'].split('.')[0] + " |\n"
    resultString = ""
    for r in results:
        resultString += "| " + str(r['index']) + " | " + str(r['similarity']) + " | " + r['melody1'].split('.')[0] + " | " + r['melody2'].split('.')[0] + " |\n"
    savePath = 'contour_chart/malhun_similarity.md'
    headers = "| Rank | Avg. Distance | Melody 1 | Melody 2 |\n| --- | --- | --- | --- |\n"
    outputFile = open(savePath, 'w')
    outputFile.write('# <a name = "top"></a>Similarity between malhun melodies\n')
    outputFile.write('The two lists below measure the average distance between two melodies.\n')
    outputFile.write('There are ' + str(len(results)) + ' total pairs and ' + str(len(filtered)) + ' after removing pairs that are from the same song.\n\n')
    outputFile.write('See [all results](#all).\n\n')
    outputFile.write('### Filtering out melodies from the same song\n')
    outputFile.write(headers + filteredString + "\n")
    outputFile.write('### <a name = "all"></a>All results\n[Back to the top](#top)\n\n')
    outputFile.write(headers + resultString)
    outputFile.close()
    print ' --  Data saved to', savePath

from music21 import *
import json, sys
with open('contour_chart/malhun.json') as data_file:
    data = json.load(data_file)
getSimilarities(data)
