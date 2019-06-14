import json
import os
import re

from nltk.corpus import stopwords
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def get_ejercicio3_posts(files):
    posts = dict()

    for file in files:
        with open(file) as f:
            for line in f:
                obj = json.loads(line)
                posts[obj["id"]] = obj
    return posts


def process_line(line):
    submission = json.loads(line)
    if submission['selftext'] != "[removed]" and submission['selftext'] != "[deleted]" and submission['selftext']:
        return (
            submission,
            re.sub("[^\w]", " ", (submission['title'].lower() if submission['title'] != "[removed]" and submission[
                'title'] != "[deleted]" else "") + " " + submission['selftext'].lower()).split())
    else:
        return ("", [])


def prepare_positive_data_for_training(posts):
    post_text_list = []
    positiveness_list = []
    for key in posts:
        new_content_processed = []
        for token in posts[key]["content_processed"]:
            if "depres" not in token:
                new_content_processed.append(token)
        if bool(posts[key]["positive"]):
            post_text_list.append(' '.join(new_content_processed))
            positiveness_list.append(1)
    return post_text_list, positiveness_list


def prepare_negative_data_for_training(file):
    negative_list = []
    positiveness_list = []
    counter = 0
    with open(file) as f:
        for line in f:
            submission = json.loads(line)
            appendable = True
            for word in submission["content_processed"]:
                if "depres" in word:
                    appendable = False
                    break
            if appendable:
                negative_list.append(' '.join(submission["content_processed"]))
                positiveness_list.append(0)
                counter += 1
            if counter >= 100:
                break
    return negative_list, positiveness_list


def get_ad_al_stop_submissions(path):
    result = dict()
    for file in os.listdir(path):
        with open(path + file) as f:
            for line in f:
                line_processed = process_line(line)
                if len(line_processed[1]) > 5:
                    d = {}
                    d["content"] = line_processed[0]
                    d["content_processed"] = line_processed[1]
                    result[line_processed[0]["id"]] = d

    return result


def get_list_from_dict(dictionary):
    result = []
    id_list = []
    for key in dictionary:
        result.append(' '.join(dictionary[key]["content_processed"]))
        id_list.append(key)
    return result, id_list


if __name__ == "__main__":
    results_dir = "./results/"
    posts = get_ejercicio3_posts([results_dir + "results_ejercicio3_best_posts", results_dir + "results_ejercicio3_worst_posts"])

    Depression, true_array = prepare_positive_data_for_training(posts)
    NotDepression, false_array = prepare_negative_data_for_training(results_dir + "results_ejercicio4_random_posts")

    x = Depression + NotDepression
    y = true_array + false_array

    # vectorizer = CountVectorizer(max_features=1500, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))
    # X = vectorizer.fit_transform(x).toarray()

    vectorizer = TfidfVectorizer(binary=True, ngram_range=(1, 3), stop_words=stopwords.words('english'))

    X = vectorizer.fit_transform(x).toarray()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    classifier = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
    classifier.fit(X_train, y_train)

    submissions = get_ad_al_stop_submissions("./ejercicio4_submissions_dataset/")
    submissions_list, id_list = get_list_from_dict(submissions)

    prediction_result = classifier.predict(vectorizer.transform(submissions_list))

    depressed_people = set()
    for i, x in enumerate(prediction_result):
        if x == 1:
            print(submissions[id_list[i]]["content"])
            if "deleted" not in submissions[id_list[i]]["content"]["author"]:
                depressed_people.add(submissions[id_list[i]]["content"]["author"])

    print("\n"
          "Depressed persons:")
    for person in depressed_people:
        print(person)

    print("\n")

    print("Accuracy test %s"
          % (accuracy_score(y_test, classifier.predict(X_test))))
    print("Accuracy training %s"
          % (accuracy_score(y_train, classifier.predict(X_train))))
