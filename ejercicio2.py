#!/usr/bin/env python3
import os
import json

import nltk
from nltk import tokenize, word_tokenize
from nltk.corpus import stopwords
import scipy.stats

nltk.download('punkt')
nltk.download('stopwords')
stop_words_list = set(stopwords.words('english'))

submissions_path = "./submissions_dataset/"
depression_submissions_path = "./depression_submissions_dataset/"
depression_results_path = "./results/"

#Transforma la linea obtenida en una lista de frases.
def process_line(line):
    sentences = []
    submission = json.loads(line)
    if submission['title'] != "[removed]" and submission['title'] != "[deleted]":
        sentences += tokenize.sent_tokenize(submission['title'], 'english')
    if submission['selftext'] != "[removed]" and submission['selftext'] != "[deleted]":
        sentences += tokenize.sent_tokenize(submission['selftext'], 'english')
    return filter_sentences(sentences)

#Filtra las frases obtenidas eliminado las stop words, palabras comunes en inglés.
def filter_sentences(sentences):
    filtered_sentences = []
    for sentence in sentences:
        sentence = sentence.lower()
        word_tokens = word_tokenize(sentence, 'english')
        filtered_sentence = []
        for word in word_tokens:
            if word not in stop_words_list:
                # filtered_word = re.sub("[^\w]", " ", word.lower())
                if word.isalpha():
                    filtered_sentence.append(word)
        filtered_sentences.append(filtered_sentence)
    return filtered_sentences


#Del conjunto de frases obtenidas en un post se crean los cooelementos, que serán cada una de las relaciones bidireccionales del grafo final.
#De esta funcion se obtendrán todas las palabras presentas en las frases anteriores y un conjunto de cooelementos.
#ws es el tamaño de ventana (Window Size)
#Los cooelementos al principio se almacenarán en un set debido a su rendimiento a la hora de chequear apariciones.
def get_vocab_and_cooelements(sentences, ws, word_vocab, cooelements):
    for s in sentences:
        sentence_len = len(s)
        for i, word in enumerate(s):
            if word not in word_vocab:
                word_vocab[word] = 1
            for j in range(i + 1, i + ws):
                if j >= sentence_len:
                    break
                cooelement = (word, s[j])
                if cooelement not in cooelements:
                    cooelements.add(cooelement)
    return word_vocab, cooelements


# def stop_words():
#     stop_word_list = []
#     with open("./stop.txt") as file:
#         for line in file:
#             line = line.replace(" ", "").replace("\n", "")
#             lineArray = line.split("|")
#             word = ""
#             if len(lineArray) > 1:
#                 word = lineArray[0]
#             else:
#                 word = line
#             if word:
#                 stop_word_list.append(word)
#
#     return stop_word_list


#Transforma el set de cooelementos en un diccionario. En este diccionario se almacenará un elemento como clave
#y como valor una lista de elementos que son cooelementos del elemento anterior. Esto se hace porque como resultado obtendremos
#un diccionario que contiene para cada elemento todos aquellos elementos que le aportarán valor. Este valor para cada uno de ellos posteriormente
# se puede calcular accediendo al elemento dentro del diccionario y chequeando su longitud.
def get_cooelements_dict(cooelements):
    cooelementsDict = dict()
    for cooelement in cooelements:
        if cooelement[0] not in cooelementsDict:
            cooelementsDict[cooelement[0]] = [cooelement[1]]
        else:
            cooelementsDict[cooelement[0]] += [cooelement[1]]
        if cooelement[1] not in cooelementsDict:
            cooelementsDict[cooelement[1]] = [cooelement[0]]
        else:
            cooelementsDict[cooelement[1]] += [cooelement[0]]
    return cooelementsDict

#Calcula el peso para cada elemento. Para ello se recorre el diccionario de cooelementos, dentro de cada elemento se recorre la lista de sus cooelementos.
#una vez se obtiene un cooelemento se accede en el diccionario a este elemento y se obtiene su longitud como objetivo de calcular el valor que le aporta al elemento protagonista.
#El sumatorio del valor de todos sus cooelementos será su valor final.
def calculate_weight(cooelements_dict, damping_factor, word_vocab):
    weight_result = dict()
    for key in cooelements_dict:
        val = 0
        for elem in cooelements_dict[key]:
            val += word_vocab[elem] / float(len(cooelements_dict[elem]))
        weight_result[key] = (1 - float(damping_factor)) * (1 / float(len(word_vocab))) + damping_factor * val
    return weight_result


#Escribe el resultado ordenador en un fichero
def write_result(dictionary, path):
    with open(path, 'w') as results_file:
        for key in sorted(dictionary, key=dictionary.get, reverse=True):
            results_file.write(key + "\t" + str(dictionary[key]) + "\n")
            # print(key, ":", depression_words[0][key])

#Inicializa el valor de cada palabra a 1/numero de palabras del vocabulario.
def initialize_weight(vocab):
    vocab_len = float(len(vocab))
    for key in vocab:
        vocab[key] = 1 / vocab_len
    return vocab

#Funcion que se encargará de obener todos los archivos de depresión del directorio que se le asigne y ejecutará las funciones explicadas anteriormente
# con el objetivo de obtener el valor del pagerank para cada token.
#Se le aplicará un total de 50 iteraciones.
def analyzing_files(path, d, iter, ws):
    vocab = dict()
    cooelements = set()

    for file in os.listdir(path):
        print(path + file)
        counter = 0
        with open(depression_submissions_path + file) as depression_file:
            for line in depression_file:
                counter += 1
                sentences = process_line(line)
                vocab, cooelements = get_vocab_and_cooelements(sentences, ws, vocab, cooelements)

    codict = get_cooelements_dict(cooelements)
    vocab = initialize_weight(vocab)
    for i in range(iter):
        print("Iteration [" + str(i) + "]")
        vocab = calculate_weight(codict, d, vocab)
    return vocab

#Función que calcula el spearman correlation entre dos listas de valores. En este caso el resultado de los pesos de las palabras
#resultado del ejercicio 1 y el resultado del ejercicio2. El resultado obtenido es de 0.8. Esto quiere decir que ambas listas
#tienen una correlación  del 80%.
def spearman_correlation_calculation(file1, file2):
    file2dict = dict()
    correlationlist1 = []
    correlationlist2 = []

    with open(file2) as f2:
        for line in f2:
            lineArray = line.replace("\n", "").split("\t")
            file2dict[lineArray[0]] = lineArray[1]

    with open(file1) as f1:
        for line in f1:
            lineArray = line.replace("\n", "").split("\t")
            if lineArray[0] in file2dict:
                correlationlist1.append(float(lineArray[1]))
                correlationlist2.append(float(file2dict[lineArray[0]]))

    spear = scipy.stats.stats.spearmanr(correlationlist1, correlationlist2)
    print(spear)


if __name__ == "__main__":
    damping = 0.85
    iterations = 50
    window_size = 3

    result = analyzing_files(depression_submissions_path, damping, iterations, window_size)
    write_result(result, depression_results_path + "results-pagerank.txt")
    spearman_correlation_calculation(depression_results_path + "results_ejercicio1.txt",
                                     depression_results_path + "results_ejercicio2_pagerank.txt")
    print("finalizado")
