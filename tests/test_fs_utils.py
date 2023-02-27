"""
File system helper function tests
"""

import tempfile
import os
import pytest
import fs_utils as fs

@pytest.fixture
def create_test_files():
    root_dir = tempfile.TemporaryDirectory()
    sub_dir = os.path.join(root_dir.name, 'subdir')
    os.mkdir(sub_dir)
    file_path = os.path.join(sub_dir, 'test_file.txt')
    with open(file_path, 'w', encoding='utf-8') as file_handle:
        file_handle.write('test')
    yield root_dir.name, sub_dir, file_path
    root_dir.cleanup()

@pytest.fixture
def create_test_files_ext():
    root_dir = tempfile.TemporaryDirectory()
    sub_dir = os.path.join(root_dir.name, 'subdir')
    os.mkdir(sub_dir)
    file_path_1 = os.path.join(sub_dir, 'test_file_1.txt')
    with open(file_path_1, 'w', encoding='utf-8') as file_handle:
        file_handle.write('test')
    file_path_2 = os.path.join(sub_dir, 'test_file_2.doc')
    with open(file_path_2, 'w', encoding='utf-8') as file_handle:
        file_handle.write('test')
    file_path_3 = os.path.join(sub_dir, 'test_file_3.txt')
    with open(file_path_3, 'w', encoding='utf-8') as file_handle:
        file_handle.write('test')
    yield root_dir.name, sub_dir, file_path_1, file_path_2, file_path_3
    root_dir.cleanup()

@pytest.fixture
def create_test_files_content():
    root_dir = tempfile.TemporaryDirectory()
    file_path_1 = os.path.join(root_dir.name, 'test_file_1.txt')
    with open(file_path_1, 'w', encoding='utf-8') as file_handle:
        file_handle.write('this is a test\nline 2\nline 3')
    file_path_2 = os.path.join(root_dir.name, 'test_file_2.txt')
    with open(file_path_2, 'w', encoding='utf-8') as file_handle:
        file_handle.write('another test\nwith some example text\nand more lines')
    file_path_3 = os.path.join(root_dir.name, 'test_file_3.txt')
    with open(file_path_3, 'w', encoding='utf-8') as file_handle:
        file_handle.write('no matches\nin this file')
    yield [file_path_1, file_path_2, file_path_3], root_dir.name
    root_dir.cleanup()

def test_search_file_found(create_test_files):
    root_dir, sub_dir, file_path = create_test_files
    assert fs.search_file(root_dir, 'test_file.txt') == file_path

def test_search_file_not_found(create_test_files):
    root_dir, sub_dir, file_path = create_test_files
    assert fs.search_file(root_dir, 'nonexistent_file.txt') is None

def test_search_file_ignore_directories(create_test_files):
    root_dir, sub_dir, file_path = create_test_files
    assert fs.search_file(root_dir, 'subdir') != sub_dir

def test_search_files_with_ext(create_test_files_ext):
    root_dir, sub_dir, file_path_1, file_path_2, file_path_3 = create_test_files_ext
    assert set(fs.search_files_with_ext(root_dir, '.txt')) == set([file_path_1, file_path_3])
    assert set(fs.search_files_with_ext(sub_dir, '.doc')) == set([file_path_2])

def test_search_files_with_ext_no_files_found(create_test_files_ext):
    root_dir, sub_dir, file_path_1, file_path_2, file_path_3 = create_test_files_ext
    assert not fs.search_files_with_ext(root_dir, '.md')

def test_search_files_with_content(create_test_files_content):
    file_paths, root_dir = create_test_files_content
    assert set(fs.search_files_with_content(file_paths, 'example')) == set([os.path.join(root_dir, 'test_file_2.txt')])
    assert set(fs.search_files_with_content(file_paths, 'test')) == set([os.path.join(root_dir, 'test_file_1.txt'), os.path.join(root_dir, 'test_file_2.txt')])

def test_no_test_search_files_with_content_not_found(create_test_files_content):
    file_paths, root_dir = create_test_files_content
    assert fs.search_files_with_content(file_paths, 'not_found') == []