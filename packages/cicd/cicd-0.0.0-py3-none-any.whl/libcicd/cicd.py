import os
import glob
import json
from pathlib import Path
import time
import datetime
from queue import Queue
import traceback
import subprocess
import re
from IPython.display import clear_output
import functools as ft
import random
import pwd
from contextlib import contextmanager

subprocess.check_output('pip install watchdog python-gitlab pyyaml'.split())

import shlex
import yaml
import gitlab

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SysUtils():
    
    @classmethod
    def run_cmd(cls, cmd):
        return subprocess.call(cmd, shell=True)
        
    @classmethod
    def yield_parent_folder_items(cls, parent_folder = '.', expr = '*', recursive = True):
        items = Path(parent_folder).rglob(expr) if recursive else Path(parent_folder).glob(expr)
        for item in items:
            yield item.as_posix()

    @classmethod
    def yield_parent_folder_subfolders(cls, parent_folder = '.', expr = '*', recursive = True):
        items = cls.yield_parent_folder_items(parent_folder = parent_folder, expr = expr, recursive = recursive)
        for item in items:
            if os.path.isdir(item):
                yield item

    @classmethod
    @contextmanager
    def chdir(cls, path):
        origin = Path().absolute()
        
        try:
            os.chdir(path)
            yield
        finally:
            os.chdir(origin)

class NbToPy():

    def __init__(self, 
        nb_folder_path = 'src/notebook', py_folder_path = 'src/python',
        beg_prefix_package = '#### beg from',
        end_prefix_package = '#### end from',
        suffix_ignore = ' #',
    ):
        self.nb_folder_path = nb_folder_path
        self.py_folder_path = py_folder_path

        self.beg_prefix_package = beg_prefix_package
        self.end_prefix_package = end_prefix_package
        self.suffix_ignore = suffix_ignore

    def format_nb_json(self, nb_json):
        for cell in nb_json['cells']:
            if('outputs' in cell):
                cell['outputs'] = []
                
    def format_nb_file(self, nb_path):
        nb_json = json.load(open(nb_path))
        self.format_nb_json(nb_json)
        
        with open(nb_path, "w") as outfile:
            json.dump(nb_json, outfile)

    def yield_nb_file_paths(self):
        for p in SysUtils.yield_parent_folder_items(self.nb_folder_path, '*.ipynb'):
            if('.ipynb_checkpoints' not in p):
                yield p
        
    def format_nb_files(self):
        for nb_path in self.yield_nb_file_paths():
            self.format_nb_file(nb_path)

    def get_py_path_from_nb_path(self, nb_path):
        return nb_path.replace(self.nb_folder_path, self.py_folder_path).replace('.ipynb', '.py')

    def yield_py_lines_from_nb_cell_code_source(self, nb_cell_code_source):
        prefix = ''
        last_stripped_line = ''
        for line in nb_cell_code_source:
            stripped_line = line.strip()
        
            if(line.startswith(self.beg_prefix_package)) : 
                prefix = line[len(self.beg_prefix_package):].strip().split(' ')[0] + '.'
            
            elif(line.startswith(self.end_prefix_package)):
                prefix = ''
                
            elif(not stripped_line.endswith(self.suffix_ignore)): 
                if(stripped_line or last_stripped_line):
                    yield line.replace('from ', f'from {prefix}')
                    last_stripped_line = stripped_line

    def yield_py_lines_from_nb_cell_markdown_source(self, nb_cell_markdown_source):
        for line in nb_cell_markdown_source:
            if line.strip():
                yield('#' + line)

    def yield_py_lines_from_nb_cell(self, nb_cell):
        if nb_cell['cell_type'] == 'code':
            return self.yield_py_lines_from_nb_cell_code_source(nb_cell['source'])

        elif nb_cell['cell_type'] == 'markdown':
            return self.yield_py_lines_from_nb_cell_markdown_source(nb_cell['source'])

    def yield_py_lines_from_nb_json(self, nb_json):
        for nb_cell in nb_json['cells']:
            for line in self.yield_py_lines_from_nb_cell(nb_cell):
                yield line
            yield '\n\n'
            
    def convert_nb_file_to_py_file(self, nb_path):
        nb_json = json.load(open(nb_path))
        py_path = self.get_py_path_from_nb_path(nb_path)
        py_dir_path = os.path.dirname(py_path)
        Path(py_dir_path).mkdir(parents = True, exist_ok = True)

        with open(py_path, 'w+') as py_file:
            for line in self.yield_py_lines_from_nb_json(nb_json):
                py_file.write(line)
                
    def convert_nb_files_to_py_files(self):
        for nb_file_path in self.yield_nb_file_paths():
            self.convert_nb_file_to_py_file(nb_file_path)

    def format_convert_nb_files_to_py_files(self):
        self.format_nb_files()
        self.convert_nb_files_to_py_files()

class PyBuild():

    def __init__(self, 
    project_folder_path = '.', 
    lib_subfolder_path = 'src/python/lib',
    ):
        self.project_folder_path = Path(project_folder_path).absolute().as_posix()
        self.project_name = self.project_folder_path.strip('/').split('/')[-1]
        self.lib_subfolder_path = lib_subfolder_path

    def get_package_folders(self):
        folders = [
            folder[len(self.lib_subfolder_path):].strip('/') 
            for folder in SysUtils.yield_parent_folder_subfolders(self.lib_subfolder_path, recursive = False)
            if not folder.endswith('.egg-info')
        ]
        return folders
        
    def generate_setup_py_lines(self):
        content = [
            'from distutils.core import setup',
            'setup(',
            f'name="{self.project_name}",',
            'version="0.0.0",',
            f'packages={list(self.get_package_folders())},',
            'package_dir={"":"' + self.lib_subfolder_path + '"}',
            ')',
        ]
        return content

    def generate_setup_py_file(self, replace_if_exists = False):   
        with SysUtils.chdir(self.project_folder_path):
            if(replace_if_exists or (not os.path.exists('setup.py'))):
                with open('setup.py', 'w') as fw:
                    fw.write('\n'.join(self.generate_setup_py_lines()))   

    def generate_readme_content(self):
        content = [
            f'#### {self.project_name} ####'
        ]
        return content

    def generate_readme_file(self, replace_if_exists = False):
        with SysUtils.chdir(self.project_folder_path):
            if(replace_if_exists or (not os.path.exists('README.md'))):
                with open('README.md', 'w') as fw:
                    fw.write('\n'.join(self.generate_readme_content()))   
                     
    def generate_requirements_file(self):
        with SysUtils.chdir(self.project_folder_path):
            SysUtils.run_cmd('pip freeze > requirements.txt')

    def build_wheel_from_setup_py_file(self):
        with SysUtils.chdir(self.project_folder_path):
            SysUtils.run_cmd('python -m build')

    def generate_setup_py_readme_requirement_files_build(self):
        PyBuild().generate_setup_py_file(replace_if_exists=True)
        PyBuild().generate_readme_file()
        PyBuild().generate_requirements_file()
        PyBuild().build_wheel_from_setup_py_file()

    def upload_to_pypi(self):
        with SysUtils.chdir(self.project_folder_path):
            SysUtils.run_cmd('twine upload dist/*.whl')











