from exceptions import InputError
from ftplib import FTP
from measurement import Measurement
from os import makedirs
from os.path import isdir, isfile, basename, join as path
from regex_converter.proteins_ast.protein_parser import ProteinParser
from regex_converter.re2_ast.re2_parser import Re2Parser
from tqdm import tqdm
from urllib.parse import urlparse
import config
import csv
import itertools
import logging
import os
import importlib
import shutil
import subprocess
import urllib.request


class Collector:
    def __init__(self, task):
        self.task = task
        self.text_files_dir = None
        self.regex_files_dir = None
        self.metafile_path = path(config.DEFAULT_LOG_FILE_DIR, 'metafile.csv')

    def _download_texts(self, urls):
        """TODO: Docstring for _download_textfile.
        """

        if urls.__class__ is not list:
            urls = [urls]

        for url in urls:
            parsed_url = urlparse(url)
            if parsed_url.scheme == 'ftp':
                self._download_ftp(parsed_url)
            elif parsed_url.scheme in ['http', 'https']:
                self._download_http(parsed_url)
            else:
                raise ValueError("Task has %s text url scheme, \
                can only process ftp and http/s urls in tasks." %
                                 parsed_url.scheme)

    def _download_http(self, parsed_url):
        file_name = os.path.basename(parsed_url.path)
        new_file_path = path(self.text_files_dir, file_name)
        new_file_size = urllib.request.urlopen(parsed_url.geturl()).length

        with tqdm(
                total=new_file_size, unit_scale=True, leave=True,
                miniters=1) as pbar:

            def update_to(b=1, bsize=1, tsize=None):
                pbar.update(b)

            urllib.request.urlretrieve(
                parsed_url.geturl(),
                filename=new_file_path,
                reporthook=update_to)

    def _download_ftp(self, parsed_url):
        ftp = FTP(parsed_url.netloc)
        ftp.login()
        text_file_name = basename(parsed_url.path)
        ftp.cwd(parsed_url.path[:-len(text_file_name)])
        total = ftp.size(text_file_name)

        logging.debug("downloading textfile via ftp")

        new_file_path = path(self.text_files_dir, text_file_name)
        with open(new_file_path, 'wb') as f:
            with tqdm(
                    total=total, unit_scale=True, leave=True,
                    miniters=1) as pbar:

                def cb(data):
                    pbar.update(len(data))
                    f.write(data)

                ftp.retrbinary("RETR %s" % text_file_name, cb)
        ftp.quit()

    def _metafile_header_params(self):
        """TODO: Docstring for _metafile_header_fieldnames.
        :returns: TODO

        """
        return [
            "%s.%s" % (space.split("_")[0], param[0])
            for space, params in config.PARAMETER_SPACE.items()
            for param in params
        ]

    def collect(self):
        logging.debug('collecting tasks')
        self._get_task()

        logging.debug('converting regex to canonical form')
        self._convert_regex_to_canonical_form()

        logging.debug('running algs on regexes and data')
        self._perform_measurements()

    def _perform_measurements(self):
        """TODO: Docstring for _perform_measurements.
        :returns: TODO

        """
        shutil.rmtree(config.DEFAULT_LOG_FILE_DIR, ignore_errors=True)
        makedirs(config.DEFAULT_LOG_FILE_DIR)
        with open(self.metafile_path, 'w') as mf:
            meta_writer = csv.writer(mf)
            meta_writer.writerow(['filename', 'taskname', 'alg'] +
                                 self._metafile_header_params())
            for alg_executable in config.ALGORITHMS:
                for point in Collector.parameter_space():
                    measurement = Measurement(alg_executable)
                    measurement.run(self.text_files_dir, self.regex_files_dir,
                                    point, meta_writer, self.task)

    @staticmethod
    def parameter_space():
        """TODO: Docstring for parameter_space.
        :returns: TODO

        """
        flattened_params = [
            param[1] for space in config.PARAMETER_SPACE.values()
            for param in space
        ]

        return itertools.product(*flattened_params)

    def _get_task(self):
        """TODO: Docstring for _get_task.
        :returns: TODO

        """
        os.makedirs("text", exist_ok=True)
        os.makedirs("regex", exist_ok=True)
        self.regex_files_dir = path(self.task, 'regex')
        self.text_files_dir = path(self.task, 'text')
        os.makedirs(self.regex_files_dir, exist_ok=True)
        os.makedirs(self.text_files_dir, exist_ok=True)
        if not all(
                isdir(d) for d in (self.regex_files_dir, self.text_files_dir)):
            raise InputError("should have 'regex' and 'text' \
                subdirectories inside the task directory")

        if isfile(path(self.task, "_config.py")):
            self.config = open(path(self.task, "_config.py"))

        if not os.listdir(self.text_files_dir):
            task_config = importlib.import_module(".".join(
                path(self.task, "_config").split("/")))
            if hasattr(task_config, "TEXT_URLS"):
                self._download_texts(task_config.TEXT_URLS)
                self._preprocess_text()
            elif hasattr(task_config, "TEXT_SCRIPT"):
                subprocess.call(task_config.TEXT_SCRIPT)

    def _preprocess_text(self):
        if isfile(path(self.task, "_pre_processing.sh")):
            logging.debug("preprocessing text")

            subprocess.call(
                [path(self.task, "_pre_processing.sh"), self.text_files_dir])

    def _convert_regex_to_canonical_form(self):
        canonical_regex_directory_path = os.path.join(
            self.task, 'tmp', "canonical_form_regex_files")

        regex_type = importlib.import_module(".".join(
            path(self.task, "_config").split("/"))).regex_type

        if regex_type == "extended":
            return

        protein_parser = ProteinParser()
        re2_parser = Re2Parser()

        shutil.rmtree(canonical_regex_directory_path, ignore_errors=True)
        os.makedirs(canonical_regex_directory_path)

        for f in os.scandir(self.regex_files_dir):
            with open(path(canonical_regex_directory_path, f.name),
                      'w+') as canon_f, open(
                          path(self.regex_files_dir, f.name), 'r') as pat_f:
                for pattern in pat_f:
                    pattern = pattern.strip()

                    if regex_type == 'protein_patterns':
                        pattern = protein_parser.parse(pattern).to_re2_string()

                    tree, groups, named_groups = re2_parser.parse(pattern)
                    basic_form = re2_parser.convert_re2_tree_to_basic_syntax(
                        tree, groups, named_groups).to_basic_string()

                    canon_f.write("%s\n" % basic_form)
        self.regex_files_dir = canonical_regex_directory_path
        # subprocess.call('./re_compare/regex_converter/removeTempFiles.sh')
