#!/usr/bin/env python3
import json
import operator
import os
import re

submissions_path = "./submissions_dataset/"
depression_submissions_path = "./depression_submissions_dataset/"
depression_results_path = "./results/"


def process_line(line):
    submission = json.loads(line)
    if submission['selftext'] != "[removed]" and submission['selftext'] != "[deleted]" and submission['selftext']:
        return (
            submission,
            re.sub("[^\w]", " ", (submission['title'].lower() if submission['title'] != "[removed]" and submission[
                'title'] != "[deleted]" else "") + " " + submission['selftext'].lower()).split())
    else:
        return ("", [])


def calculate_weight_posts(posts_path, keywords):
    posts = dict()
    for file in os.listdir(posts_path):
        print(file)
        with open(posts_path + file) as depression_file:
            for line in depression_file:
                line_tuple = process_line(line)
                if len(line_tuple[1]) <= 1:
                    continue
                value = 0
                for word in line_tuple[1]:
                    if word in keywords:
                        value += keywords[word]
                posts[line_tuple[0]["id"]] = (value, line_tuple[0], line_tuple[1])
    return posts


def combine_results(file1, file2):
    file2dict = dict()
    result = dict()

    with open(file2) as f2:
        for line in f2:
            lineArray = line.replace("\n", "").split("\t")
            file2dict[lineArray[0]] = lineArray[1]

    with open(file1) as f1:
        for line in f1:
            lineArray = line.replace("\n", "").split("\t")
            if lineArray[0] in file2dict:
                if "depres" not in lineArray[0]:
                    result[lineArray[0]] = float(lineArray[1])
                    print(lineArray[0], result[lineArray[0]])

    return result


def create_post_object(actual_post):
    positive = False
    for word in actual_post[2]:
        if "depres" in word:
            positive = True

    post = {}
    post["id"] = actual_post[1]["id"]
    post["positive"] = positive
    post["weight"] = actual_post[0]
    post["content"] = actual_post[1]
    return post


def get_best_worst_posts(posts):
    counter = 0
    best_posts = []
    worst_posts = []
    result = dict()
    for key in sorted(posts, key=lambda x: posts.get(x)[0], reverse=True):
        print(posts[key][0])
        if counter < 100:
            best_posts.append(create_post_object(posts[key]))
            counter += 1
        else:
            break

    counter = 0

    for key in sorted(posts, key=lambda x: posts.get(x)[0], reverse=False):
        print(posts[key][0])
        if counter < 100:
            worst_posts.append(create_post_object(posts[key]))
            counter += 1
        else:
            break
    return best_posts, worst_posts



def write_list_in_file(list,file):
    with open(file,"w") as f:
        for element in list:
            json.dump(element, f)
            f.write("\n")


if __name__ == "__main__":

    results_dir = "./results/"
    keywords = combine_results(results_dir+ "results.txt",
                               results_dir+ "results-pagerank.txt")

    posts = calculate_weight_posts("./offmychest_submissions_dataset/", keywords)
    best_posts, worst_posts = get_best_worst_posts(posts)
    write_list_in_file(best_posts,results_dir+"results_ejercicio3_best_posts")
    write_list_in_file(worst_posts, results_dir + "results_ejercicio3_worst_posts")



    print("finalizado")
