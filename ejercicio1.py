#!/usr/bin/env python3
import os
import re
from math import log, sqrt
import json

#submissions_path = "./submissions_dataset/"

#Ruta donde se sitúan todos los archivos mensuales de posts de depresión. Estos archivos mensuales han sido anteriormente extraídos
#con el script posts_extractor.py. Este script filtra todos los posts mensuales y guarda un archivo con los posts de un subreddit especificado.
depression_submissions_path = "./depression_submissions_dataset/"
depression_results_path = "./results/"


#Función que procesa cada linea. Obtiene el selftext y el title de los posts de reddit y los concatena. Divide el texto obtenido
# en una lista de palabras deshechando todos los símbolos. También limpia todos aquellos posts que están eliminados.
def process_line(line):
    submission = json.loads(line)
    return re.sub("[^\w]", " ", ((submission['title'].lower() if submission['title'] != "[removed]" and submission[
        'title'] != "[deleted]" else "") + " " + (
                                     submission['selftext'].lower() if submission['selftext'] != "[removed]" and
                                                                       submission[
                                                                           'selftext'] != "[deleted]" else ""))).split()

#FUncion que obtiene todas las palabras del archivo de frecuencia absoluta de palabras en lengua inglesa.
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

#FUncion que obtiene el numero de veces que una palabra se repite y la almacena en un diccionario. A su vez también cuenta el núero total de palabras
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


#Funcion que aplica en likelihood ratio de una palabra en base a la lista de frecuencia absoluta y al numbero de observaciones.
def rootLogLikelihoodRatio(a, b, c, d):
    E1 = c * (a + b) / (c + d)
    E2 = d * (a + b) / (c + d)
    result = 2 * (a * log(a / E1 + (1 if a == 0 else 0)) + b * log(b / E2 + (1 if b == 0 else 0)))
    result = sqrt(result)
    if (a / c) < (b / d):
        result = -result
    return result

#Crea la lista de ordenada según el ratio de las palabras.
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
