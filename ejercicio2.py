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


def calculate_weight(cooelements_dict, damping_factor, word_vocab):
    weight_result = dict()
    for key in cooelements_dict:
        val = 0
        for elem in cooelements_dict[key]:
            val += word_vocab[elem] / float(len(cooelements_dict[elem]))
        weight_result[key] = (1 - float(damping_factor)) * (1 / float(len(word_vocab))) + damping_factor * val
    return weight_result


def write_result(dictionary, path):
    with open(path, 'w') as results_file:
        for key in sorted(dictionary, key=dictionary.get, reverse=True):
            results_file.write(key + "\t" + str(dictionary[key]) + "\n")
            # print(key, ":", depression_words[0][key])


def initialize_weight(vocab):
    vocab_len = float(len(vocab))
    for key in vocab:
        vocab[key] = 1 / vocab_len
    return vocab


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
    spearman_correlation_calculation(depression_results_path + "results.txt",
                                     depression_results_path + "results-pagerank.txt")
    print("finalizado")
