import os

#Obtiene los posts de un determinado subreddit.
def extractor(subreddit_name,submissions_path,result_path):

    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    subreddit_name_len = len('"' + subreddit_name + '"')
    for file in os.listdir(submissions_path):
        depression_file_path = result_path + subreddit_name + '-' + file
        if not os.path.isfile(depression_file_path):
            print("Extracting " + subreddit_name + " submissions from dataset: " + file + "...")
            depression_file = open(depression_file_path, 'w')
            with open(submissions_path + file) as fp:
                counter = 0
                for line in fp:
                    num = line.find('"subreddit":"') + 12
                    if line[num:num + subreddit_name_len].lower() == '"' + subreddit_name.lower() + '"':
                        depression_file.write(line)
                        counter += 1
                print("\t" + str(counter) + " posts found about " + subreddit_name)
            depression_file.close()


if __name__ == "__main__":
    extractor("addiction","./submissions_dataset/","./ejercicio4_submissions_dataset/")
