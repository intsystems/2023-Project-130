from pathlib import *
import re
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import json
import shutil


def find_files_with_terms(dir_path='Dataset/Texts'):
    """
    Finding files that have terms and removing files that have less than 20 valid terms
            Parameters:
                    dir_path (str): directory with documents sorted by year
            Return:
                    statistics (list): list of the number of terms in documents
                    save_files (list): list of names of selected files
    """
    files = []
    with open('Dataset/Terms/_all_annotation_map_to_acl_arc_id.txt') as fin:
        for i in re.finditer(r'^[A-Z][0-9]{2}-[0-9]{4}', fin.read(), re.M):
            files.append(i.group(0))

    statistics = []
    save_files = []
    dict_files = dict(Counter(files))
    for k in dict_files.keys():
        if dict_files[k] > 20:
            save_files.append(k)
            statistics.append(dict_files[k])

    for direct in Path(dir_path).iterdir():
        number = direct.stem
        new_path = Path(dir_path + '/' + number)
        for item in Path(new_path).iterdir():
            if item.stem not in save_files:
                item.unlink()
    return save_files, statistics


def plot_statistics(statistics, bins=60):
    """
    Builds a histogram with the number of terms in the documents and saves it to a file in eps format
            Parameters:
                    statistics (list): list of the number of terms in documents
                    bins (int): number of bins
    """
    plt.rcParams["font.family"] = "Times New Roman"
    plt.hist(statistics, bins=bins)
    plt.xlabel('Количество терминов')
    plt.ylabel('Количество документов')
    plt.savefig('Dataset/Statistics.eps', format='eps', bbox_inches='tight')


def create_markup(save_files, json_name='Marks.json'):
    """
    Saves the markup file in json format
            Parameters:
                    save_files (list): list of names of selected files
                    json_name (str): The name of the file to save in json format in 'Dataset/Terms/'

    """
    previous_file = 'A00-1005'
    words = []
    marks = {}

    with open('Dataset/Terms/_all_annotation_map_to_acl_arc_id.txt', 'r') as fin:
        for line in fin.readlines():
            if line[0:8] != previous_file:
                print(previous_file)
                marks[previous_file] = words
                words = []
                previous_file = line[0:8]
            if line[0:8] in save_files:
                with open('Dataset/Terms/valid_terms.txt', 'r') as terms:
                    for term in terms.readlines():
                        if line.split()[1] == term.split()[0]:
                            split_terms = term.split()[1:-1]
                            words.append(' '.join(split_terms))
                            break

            marks[line[0:8]] = words

    save_name = 'Dataset/Terms/' + json_name
    with open(save_name, 'w') as fp:
        json.dump(marks, fp)


def find_1_term_files(json_name='Marks.json'):
    """
    Collects statistics on terms from a single word
            Parameters:
                    json_name (str): The name of the file to load markup in json format in 'Dataset/Terms/'
            Return:
                    statistics (list): list of the number of 1-word-terms in documents
    """
    name = 'Dataset/Terms/' + json_name
    with open(name, 'r') as fp:
        data = json.load(fp)
    data_1 = {}
    statistics = []

    for k in data.keys():
        data_1[k] = []
        for term in data[k]:
            if len(term.split()) == 1:
                data_1[k].append(term)
        if not data_1[k]:
            del data_1[k]
        else:
            statistics.append(len(data_1[k]))
    return statistics


def cutting_info(input_path='Dataset/Texts', output_path='Dataset/Texts_cut'):
    """
    Deleting the title, authors and references
            Parameters:
                    input_path (str): directory with documents sorted by year to load
                    output_path (str): directory with documents sorted by year to save
            Return:
                    statistics (list): list of the number of 1-word-terms in documents
    """
    for direct in Path(input_path).iterdir():
        number = direct.stem
        new_input_path = Path(input_path + '/' + number)

        for item in Path(new_input_path).iterdir():
            new_output_path = Path(output_path + '/' + number + '/' + item.name)
            fout = open(new_output_path, 'w')
            f = 0

            with open(item, 'r', errors="ignore") as fin:
                for line in fin.readlines():
                    if 'Abstract' in line or 'ABSTRACT' in line:
                        f = 1
                    elif 'References' in line or 'REFERENCES' in line:
                        if f == 0:
                            f = 3
                        else:
                            f = 2
                    if f == 1:
                        fout.write(line)
                if f == 0:
                    shutil.copy(item, new_output_path)

            if f == 3:
                with open(item, 'r', errors="ignore") as fin:
                    for line in fin.readlines():
                        fout.write(line)
                        if 'References' in line or 'REFERENCES' in line:
                            break

            fout.close()


def train_test(json_name='Marks.json'):
    """
    Splitting documents into train and test, saving documents in vowpal_wabbit format and markup in json format
            Parameters:
                    json_name (str): The name of the file to load markup in json format in 'Dataset/Terms/'
    """
    name = 'Dataset/Terms/' + json_name
    with open(name, 'r') as fp:
        data = json.load(fp)
    vw_train_output = open('Dataset/Train_test/Train/Train_1.vw.txt', 'w')
    vw_test_output = open('Dataset/Train_test/Test/Test_1.vw.txt', 'w')
    count = 0
    count_train = 0
    count_test = 0
    data_train = {}
    data_test = {}

    for k in data.keys():
        number = k[1:3]
        input_path = 'Dataset/Stem_texts/' + number + '/' + k + '.txt'
        with open(input_path, 'r') as fin:
            words = fin.read()
            if count % 10 == 9:
                data_test[k] = data[k]
                vw_test_output.write('doc_{} {}\n'.format(count_test, words))
                count_test += 1
            else:
                data_train[k] = data[k]
                vw_train_output.write('doc_{} {}\n'.format(count_train, words))
                count_train += 1
        count += 1

    vw_train_output.close()
    vw_test_output.close()

    with open('Dataset/Train_test/Train_1.json', 'w') as fp:
        json.dump(data_train, fp)

    with open('Dataset/Train_test/Test_1.json', 'w') as fp:
        json.dump(data_test, fp)