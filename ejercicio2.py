#!/usr/bin/env python3
import itertools
import os
import re
from math import log, sqrt
import json

import nltk
from nltk import tokenize, word_tokenize, OrderedDict

nltk.download('punkt')

from nltk.corpus import stopwords
from websocket._abnf import numpy as np

nltk.download('stopwords')
stop_words_list = set(stopwords.words('english'))

submissions_path = "./submissions_dataset/"
depression_submissions_path = "./depression_submissions_dataset/"
depression_results_path = "./results/"
# stop_words_list = []
# word_list = dict()

word_weight = OrderedDict()
cooelements = set()
word_index = 0


# words_number = 13507227


def process_line(line):
    sentences = []
    submission = json.loads(line)
    if submission['title'] != "[removed]" and submission['title'] != "[deleted]":
        sentences += tokenize.sent_tokenize(submission['title'], 'english')
    if submission['selftext'] != "[removed]" and submission['selftext'] != "[deleted]":
        sentences += tokenize.sent_tokenize(submission['selftext'], 'english')

    return filter_sentences(sentences)


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


def get_cooelements(sentences, window_size):
    global word_index
    for s in sentences:
        sentence_len = len(s)
        for i, word in enumerate(s):

            if word not in word_weight:
                word_weight[word] = word_index
                word_index += 1
            for j in range(i + 1, i + window_size):
                if j >= sentence_len:
                    break
                cooelement = (word, s[j])
                if cooelement not in cooelements:
                    cooelements.add(cooelement)
    return cooelements


def stop_words():
    stop_word_list = []
    with open("./stop.txt") as file:
        for line in file:
            line = line.replace(" ", "").replace("\n", "")
            lineArray = line.split("|")
            word = ""
            if len(lineArray) > 1:
                word = lineArray[0]
            else:
                word = line
            if word:
                stop_word_list.append(word)

    return stop_word_list


#
#
# def filter_stop_words(list):
#     filtered_list = []
#     for word in list:
#         if word not in stop_list:
#             if word in word_list:
#                 filtered_list.append(word)
#     return filtered_list


# def page_rank(word_list, window_size):
#     word_list = filter_stop_words(word_list)
#     for i in range(len(word_list)):
#         sublist = word_list[i:i + window_size]
#         number_elements_sublist = len(sublist)
#         if number_elements_sublist > 1:
#             values_list = [0] * number_elements_sublist
#             for x in range(number_elements_sublist):
#                 if sublist[x] not in word_value:
#                     word_value[sublist[x]] = 1
#                 value = word_value[sublist[x]] / (number_elements_sublist - 1)
#                 for y in range(number_elements_sublist):
#                     if x != y:
#                         values_list[y] += value
#             for x in range(number_elements_sublist):
#                 word_value[sublist[x]] = values_list[x]


# def page_rank(word_list, window_size):
#     word_list = filter_stop_words(word_list)
#     for i in range(len(word_list)):
#         window_list = word_list[i - window_size if i - window_size >= 0 else 0:i + window_size + 1]
#         elem_num = len(window_list) - 1
#         if word_list[i] not in word_value:
#             word_value[word_list[i]] = 1/words_number
#         for word in window_list:
#             if word not in word_value:
#                 word_value[word] = 1/words_number
#             if word_list[i] != word:
#                 value_to_give =word_value[word_list[i]]/ elem_num
#                 word_value[word_list[i]] += word_value[word] / elem_num
#                 word_value[word] = word_value[word] - (word_value[word] / elem_num)
#                 word_value[word]+=value_to_give
#
# def get_relations_number(index, list_size, window_size):
#
#     floor= (index - window_size if index - window_size >= 0 else 0)
#     ceil = ((index + window_size + 1) if (list_size ) >= index + window_size + 1 else list_size )
#
#
#     return ceil-floor-1


# def page_rank(word_list, window_size):
#     word_list = filter_stop_words(word_list)
#     len_word_list = len(word_list)
#     if len_word_list>1:
#         for i in range(len(word_list)):
#             if word_list[i] not in word_value:
#                 word_value[word_list[i]] = 1/words_number
#             sum_value = word_value[word_list[i]] / get_relations_number(i,len_word_list,2)
#             word_value[word_list[i]] = 0
#             for j in range(-window_size, window_size + 1):
#                 if i+j>0 and i+j<len_word_list:
#                     if word_list[j+i] not in word_value:
#                         word_value[word_list[j+i]] = 1/words_number
#
#                     substract_value = word_value[word_list[j+i]] / get_relations_number(j+i,len_word_list,2)
#                     word_value[word_list[j+i]] -= substract_value
#                     word_value[word_list[i]] += sum_value


# def getAbsoluteFrequency():
#     result = dict()
#     totalNumber = 0
#     with open("./count_1w.txt") as file:
#         for line in file:
#             lineArray = line.replace("\n", "").split("\t")
#             wordNumber = int(lineArray[1])
#             result[lineArray[0]] = wordNumber
#             totalNumber += wordNumber
#     return (result, totalNumber)


# def countWords():
#     counter = 0
#     for file in os.listdir(depression_submissions_path):
#         print(depression_submissions_path + file)
#         with open(depression_submissions_path + file) as depression_file:
#             for line in depression_file:
#                 line_tuple = process_line(line)
#                 for tuple_element in line_tuple:
#                     filtered_list = filter_stop_words(tuple_element)
#                     counter += len(filtered_list)
#     return counter


def create_matrix(cooelements):
    word_weight_len = len(word_weight)
    matrix = np.zeros((word_weight_len, word_weight_len), dtype='float')
    for cooelement1, cooelement2 in cooelements:
        cooelement1Index = word_weight[cooelement1]
        cooelement2Index = word_weight[cooelement2]
        matrix[cooelement1Index][cooelement2Index] = 1
        matrix[cooelement2Index][cooelement1Index] = 1

    norm = np.sum(matrix, axis=0)
    g_norm = np.divide(matrix, norm, where=norm != 0)
    return g_norm


def get_cooelements_dict():
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

    for key in word_weight:
        word_weight[key] = 1
    return cooelementsDict


def calculate_weight(cooelements_dict, damping_factor, word_vocab):
    result = dict()

    for key in cooelements_dict:
        val = 0
        for elem in cooelements_dict[key]:
            val += word_vocab[elem] / len(cooelements_dict[elem])
        result[key] = (1 - damping_factor) + damping_factor * val
    return result


def print_result(dictionary):
    with open(depression_results_path + "results-pagerank.txt", 'w') as results_file:
        for key in sorted(dictionary, key=dictionary.get, reverse=True):
            results_file.write(key + "\t" + str(dictionary[key]) + "\n")
            # print(key, ":", depression_words[0][key])


def processing_file():
    for file in os.listdir(depression_submissions_path):
        print(depression_submissions_path + file)
        counter = 0
        with open(depression_submissions_path + file) as depression_file:
            for line in depression_file:
                counter += 1
                sentences = process_line(line)
                # print(counter)
                get_cooelements(sentences, 3)

    d = 0.85  # damping coefficient, usually is .85
    # min_diff = 1e-5  # convergence threshold
    steps = 30  # iteration steps

    codict = get_cooelements_dict()

    # matrix = create_matrix(cooelements)

    # pr = np.array([1] * int(word_index))

    # Iteration
    # previous_pr = 0

    global word_weight
    for i in range(steps):
        word_weight = calculate_weight(codict, d, word_weight)

        # pr = (1 - d) + d * np.dot(matrix, pr)
        # if abs(previous_pr - sum(pr)) < min_diff:
        #     break
        # else:
        # previous_pr = sum(pr)

    # Get weight for each node
    # node_weight = dict()
    # for word, index in word_weight.items():
    #    node_weight[word] = pr[index]
    print_result(word_weight)


if __name__ == "__main__":
    # stop_words_list = stop_words()
    # word_list = getAbsoluteFrequency()[0]
    word_index = 0
    # words_number = countWords()
    # print(words_number)
    processing_file()

    print("finalizado")
