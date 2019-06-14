#!/usr/bin/env python3
import os
import re
from math import log, sqrt
import json

submissions_path = "./submissions_dataset/"
depression_submissions_path = "./depression_submissions_dataset/"
depression_results_path = "./results/"


def process_line(line):
    submission = json.loads(line)
    return re.sub("[^\w]", " ", ((submission['title'].lower() if submission['title'] != "[removed]" and submission[
        'title'] != "[deleted]" else "") + " " + (
                                     submission['selftext'].lower() if submission['selftext'] != "[removed]" and
                                                                       submission[
                                                                           'selftext'] != "[deleted]" else ""))).split()


def getAbsoluteFrequency():
    result = dict()
    totalNumber = 0
    with open("./count_1w.txt") as file:
        for line in file:
            lineArray = line.replace("\n", "").split("\t")
            wordNumber = int(lineArray[1])
            result[lineArray[0]] = wordNumber
            totalNumber += wordNumber
    return result, totalNumber


def getDepressionFrequency(words):
    depressionDict = dict()
    observationsNumber = 0
    for file in os.listdir(depression_submissions_path):
        print(file)
        with open(depression_submissions_path + file) as depression_file:
            for line in depression_file:
                lineArray = process_line(line)
                for word in lineArray:
                    if word in depressionDict:
                        depressionDict[word] = depressionDict.get(word) + 1
                        observationsNumber += 1
                    else:
                        if word in words:
                            depressionDict[word] = 1
                            observationsNumber += 1
    return depressionDict, observationsNumber


def rootLogLikelihoodRatio(a, b, c, d):
    E1 = c * (a + b) / (c + d)
    E2 = d * (a + b) / (c + d)
    result = 2 * (a * log(a / E1 + (1 if a == 0 else 0)) + b * log(b / E2 + (1 if b == 0 else 0)))
    result = sqrt(result)
    if (a / c) < (b / d):
        result = -result
    return result


def createLLRlist(words, depression_words):
    for key in depression_words[0].keys():
        depression_words[0][key] = (rootLogLikelihoodRatio(depression_words[0][key], words[0][key], depression_words[1],
                                                           words[1]), depression_words[0][key])

    with open(depression_results_path + "results_ejercicio1.txt", 'w') as results_file:
        for key in sorted(depression_words[0], key=depression_words[0].get, reverse=True):
            if depression_words[0][key][0] >= 0:
                results_file.write(key + "\t" + str(depression_words[0][key][0]) + "\n")
            # print(key, ":", depression_words[0][key])
    return depression_words[0]




if __name__ == "__main__":
    words = getAbsoluteFrequency()
    depression_words = getDepressionFrequency(words[0])
    createLLRlist(words, depression_words)
    print("finalizado")
