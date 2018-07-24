from os.path import basename
import pytest
import csv
import sys
import importlib
config = sys.modules['config'] = importlib.import_module('tests.mock_config')
from re_compare.analysis import Analysis

EXPECTED_OUTPUT = 'tests/functional/expected_output/'


@pytest.fixture
def analysis(monkeypatch):
    a = Analysis(EXPECTED_OUTPUT + 'logs')
    monkeypatch.setattr(a, '_plot_graphs', lambda: None)
    monkeypatch.setattr(a, '_add_statistical_information_to_parameter_cube',
                        lambda: None)
    a.analyze_logs()
    return a


def test_create_cube_with_correct_dim(analysis):
    assert len(config.ALGORITHMS) == 2
    assert len(config.PARAMETER_SPACE['regex_space'][0][1]) == 2
    assert len(config.PARAMETER_SPACE['text_space'][0][1]) == 3
    assert analysis.cube.data.shape == (2, 2, 3)


def test_log_stats_added_to_parameter_cube(monkeypatch):
    a = Analysis(EXPECTED_OUTPUT + 'logs')
    monkeypatch.setattr(a, '_plot_graphs', lambda: None)
    a.analyze_logs()
    stats = open(EXPECTED_OUTPUT + "expected_stats")
    for cell in a.cube.data.flat:
        list(cell.keys()) == [
            'results', 'consecutive_matches', 'all_matches', 'first_match'
        ]
        assert len(cell['consecutive_matches']
                   ['stats']) <= config.MAX_MATCHES_PER_PATTERN

        for stat in cell['consecutive_matches']['stats']:
            assert str(list(stat.values())) == next(stats).rstrip()


def test_logs_mapped_to_parameter_cube_points(analysis):
    results_file_for_point = analysis.cube.data[1, 0, 1]['results']
    assert results_file_for_point == EXPECTED_OUTPUT + "logs/re2_pattern_recog_easy-protein-patterns_10e5.csv"

    # show that (2,0,1) corresponds to the third ordered alg,
    # the first val in the first regex space parameters,
    # and the second value in the first text space parameters
    with open(EXPECTED_OUTPUT + "logs//metafile.csv") as mf:
        reader = csv.DictReader(mf)
        for row in reader:
            if row['filename'] == basename(results_file_for_point):
                assert row['alg'] == basename(config.ALGORITHMS[1])
                regex_hardness_values = [
                    reg_param
                    for reg_param in config.PARAMETER_SPACE['regex_space']
                    if reg_param[0] == 'hardness'
                ][0][1]
                assert row['regex.hardness'] == regex_hardness_values[0]

                text_length_values = [
                    reg_param
                    for reg_param in config.PARAMETER_SPACE['text_space']
                    if reg_param[0] == 'length'
                ][0][1]
                assert row['text.length'] == text_length_values[1]
