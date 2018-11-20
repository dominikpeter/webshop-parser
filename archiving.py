
# coding: utf-8

import os
import shutil
import re
import datetime
import itertools


def walk(top):
    filepaths = []
    for path, subdir, files in os.walk(top):
        for file in files:
            filepaths.append(
                os.path.join(path, file))
    return filepaths



def get_all_files(top, regex=".*"):
    filepaths = walk(top)
    filtered = [i for i in filepaths if re.match(regex, i)]
    filtered = [i for i in filtered if not re.match(".*Archiv.*", i)]
    return filtered


def check_nested(x):
    for i in x:
        if isinstance(i, (list, tuple)):
            return True
    else:
        return False

def flatten(x):
    if check_nested(x):
        new_x = []
        for i in x:
            if isinstance(i, (list, tuple)):
                for j in i:
                    new_x.append(j)
            else:
                new_x.append(i)
        return flatten(new_x)
    else:
        return x

def path_join_list(list_of_files, path=""):
    list_of_files = flatten(list_of_files)
    if isinstance(list_of_files, (tuple, set)):
        list_of_files = list(list_of_files)
    if list_of_files:
        path = os.path.join(path, list_of_files[0])
        list_of_files.pop(0)
        return path_join_list(list_of_files, path)
    else:
        return path


def create_folder_if_not(path):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return dirname


def create_archiv(files):
    now = datetime.datetime.now(
        ).strftime("%Y%m%d_%H%M")
    for file in files:
        splitted = os.path.split(file)
        new_path = path_join_list(
            flatten([splitted[:-1],
                     "Archiv",
                     now +"_"+ splitted[1]]))
        create_folder_if_not(new_path)
        shutil.copyfile(file, new_path)


if __name__ == '__main__':
    files = get_all_files(".", ".*\.(json|xml)$")
    create_archiv(files)
