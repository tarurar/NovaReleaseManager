"""
File system helper functions.
"""

import os

def search_file(root_dir, filename):
    """
    Searches for a file in a directory tree.
    :param root_dir: root directory to start search from
    :param filename: file name to search for
    :return: full path to the first file if found, None otherwise
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file == filename:
                return os.path.join(dirpath, file)
    return None

def search_files_with_ext(root_dir, extension):
    """
    Searches for files with a given extension in a directory tree.
    :param root_dir: root directory to start search from
    :param extension: file extension to search for
    :return: list of full paths to the files if found, empty list otherwise
    """
    result = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(extension):
                result.append(os.path.join(dirpath, file))
    return result

def search_files_with_content(file_paths, search_string):
    """
    Searches for a string in a list of files.
    :param file_paths: list of file paths to search in
    :param search_string: string to search for
    :return: list of file paths where the string was found
    """
    result = []
    for file_path in file_paths:
        if not os.path.isfile(file_path):
            continue
        with open(file_path, 'r', encoding='utf-8') as file_handle:
            if search_string in file_handle.read():
                result.append(file_path)
    return result
