import json
import os
import re


def process_line(line):
    submission = json.loads(line)
    if submission['selftext'] != "[removed]" and submission['selftext'] != "[deleted]" and submission['selftext']:
        return (
            submission,
            re.sub("[^\w]", " ", (submission['title'].lower() if submission['title'] != "[removed]" and submission[
                'title'] != "[deleted]" else "") + " " + submission['selftext'].lower()).split())
    else:
        return ("", [])


def get_mental_health_subreddits(file):
    mhsub = set()
    with open(file) as f:
        for line in f:
            mhsub.add(line.replace("\n", ""))
    return mhsub


def extractor(submissions_path, result_path, exception_list):
    for file in os.listdir(submissions_path):
        print("Extracting submissions from dataset: " + file + "...")
        depression_file = open(result_path , 'w')
        with open(submissions_path + file) as fp:
            counter = 0
            totalCounter = 0
            for line in fp:
                if totalCounter % 100 == 0:
                    submission = json.loads(line)
                    appendable = True
                    if submission["subreddit"] not in exception_list:
                        word_list = process_line(line)[1]
                        if len(word_list) > 100:
                            for word in word_list:
                                if "depres" in word:
                                    appendable = False
                                    break
                            if appendable:
                                obj = {}
                                obj["id"] = submission["id"]
                                obj["content"] = submission
                                obj["content_processed"] = word_list
                                json.dump(obj,depression_file)
                                depression_file.write("\n")
                                counter += 1
                    if counter > 150:
                        break
                totalCounter+=1

        depression_file.close()


if __name__ == "__main__":
    extractor("./submissions_dataset/", "./results/results_ejercicio4_random_posts",
              get_mental_health_subreddits("./mental_health_posts"))
