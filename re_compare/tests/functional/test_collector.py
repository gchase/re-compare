import os
from decimal import Decimal
import csv
import pytest
from regex_converter.re2_ast.re2_parser import Re2Parser
import shutil
import importlib
import sys

config = sys.modules['config'] = importlib.import_module('tests.mock_config')
from re_compare.collector import Collector

DUMMY_TASK_PATH = "tests/functional/dummy_task"
PROTEIN_TASK_PATH = "tests/functional/protein"


@pytest.fixture
def collector(mocker):
    c = Collector(DUMMY_TASK_PATH)
    mocker.patch.object(c, '_perform_measurements')
    mocker.patch.object(c, '_download_texts')
    return c


def test_downloads_texts(collector, mocker):
    mocker.patch.object(collector, '_convert_regex_to_canonical_form')
    collector.collect()
    url = importlib.import_module(
        ".".join(DUMMY_TASK_PATH.split("/")) + "._config").TEXT_URLS
    collector._download_texts.assert_called_once_with(url)


def test_converts_regexes(collector, mocker, tmpdir, monkeypatch):
    canonical_regex_path = DUMMY_TASK_PATH + "/tmp/converted_regex_files"
    shutil.rmtree(canonical_regex_path, ignore_errors=True)
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse(
        open(DUMMY_TASK_PATH + "/regex/reg_file").readline().rstrip())
    expected_regex = parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

    collector.collect()
    assert open(next(os.scandir(canonical_regex_path))
                .path).read().rstrip() == expected_regex


def test_creates_logs_for_all_points(collector):
    shutil.rmtree(config.DEFAULT_LOG_FILE_DIR, ignore_errors=True)
    c = Collector(PROTEIN_TASK_PATH)
    c.collect()
    for log in os.scandir(config.DEFAULT_LOG_FILE_DIR):
        expected_file = open(
            'tests/functional/expected_output/logs/%s' % log.name)
        if log.name == 'metafile.csv':
            assert open(log).read() == expected_file.read()
            continue
        f_reader = csv.DictReader(open(log))
        exp_reader = csv.DictReader(expected_file)
        for row, exp_row in zip(f_reader, exp_reader):
            assert Decimal(row.pop('time(ms)'))
            assert Decimal(exp_row.pop('time(ms)'))
            assert row == exp_row
