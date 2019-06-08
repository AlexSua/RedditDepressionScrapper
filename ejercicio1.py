#!/usr/bin/env python3
import itertools
import os
from multiprocessing import Manager, Process

import praw
import json

from urllib3.connectionpool import xrange


def process_line(work, results):
    result = dict()
    while True:
        line = work.get()
        if (line is None):
            results.append(result)
            return

        subreddit_name = '"depression"'
        num = line.find('"subreddit":"') + 12

        substr = line[num:num + 12]
        if substr == subreddit_name:
            submission = json.loads(line)
            print(submission['title'])

        # if '"subreddit":"depression"' in line:
        #     print(substr)
        #     submission = json.loads(line)
        #     print(submission['title'])


def sort_results(results):
    print("completed")


def parallel_reading():
    num_workers = 4

    manager = Manager()
    results = manager.list()
    work = manager.Queue(num_workers)
    pool = []
    for i in xrange(num_workers):
        p = Process(target=process_line, args=(work, results))
        p.start()
        pool.append(p)

    with open("./RS_2018-11") as fp:
        iterator = itertools.chain(fp, (None,) * num_workers)
        for line in iterator:
            work.put(line)

    for p in pool:
        p.join()

    sort_results(results)


if __name__ == "__main__":
    # reddit = praw.Reddit(client_id='maPFuBmFp45gJA',
    #                      client_secret='Rjh-6HYe5cMle8LZGa0cW_8bNbQ',
    #                      user_agent='web_semantica bot depression scrapping')
    #
    # reddit.read_only = True
    # counter = 0
    # for submission in  reddit.subreddit('depression').new(limit=None):
    #     print("Title: "+submission.title)
    #     print("Self text: "+submission.selftext)
    #     # print("Comments: "+submission.comments[0])
    #     submission.comments.replace_more(limit=None)
    #     for comment in submission.comments.list():
    #         print(comment)
    #     counter+=1
    #     print(counter)
    #     print(submission)

    subreddit_name = '"depression"'

    dataset_path = "./submissions_dataset/"
    for file in os.listdir(dataset_path):
        print("Extracting depression submissions from dataset: " + file + " ...")
        depression_path = './depression_submissions_dataset/depression-' + file
        depression_file = open(depression_path, 'w')
        with open(dataset_path + file) as fp:
            counter = 0
            for line in fp:
                num = line.find('"subreddit":"') + 12
                substr = line[num:num + 12]
                if substr == subreddit_name:
                    # submission = json.loads(line)
                    depression_file.write(line)
                    # print(submission['title'])
                    counter += 1
            print("\t"+counter + "posts found about depression")
        depression_file.close()