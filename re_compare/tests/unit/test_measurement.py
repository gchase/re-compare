from itertools import islice
import importlib
from log_generator import LogGenerator
import sys
import pytest

config = sys.modules['config'] = importlib.import_module('tests.mock_config')
from measurement import Measurement

REGEX_FILE = 'tests/functional/protein/regex/_easy-protein-patterns'
REGEX_FILE_LENGTH = sum(1 for line in open(REGEX_FILE))


@pytest.mark.parametrize(
    "requested_regex,expected_regex_tested",
    [
        (0, 0),
        (10, 10),
        (REGEX_FILE_LENGTH + 10, REGEX_FILE_LENGTH
         )  # can't read more regex then there are in file
    ])
# test that NUMBER_OF_REGEXES_IN_TASK controlls how many regexes are measured
def test_run_measurement_according_to_config(mocker, requested_regex,
                                             expected_regex_tested):
    config.NUMBER_OF_REGEXES_IN_TASK = requested_regex
    f = open('tests/functional/protein/regex/_easy-protein-patterns')

    measurement = Measurement('')
    mocker.patch.object(
        measurement, '_find_file_by_params', return_value=f.name)
    mocker.patch('csv.writer')
    stub = mocker.stub(name='file')
    stub.__dict__.update({
        'name': 'asd',
        'close': lambda: None,
        'writerow': lambda x: None
    })

    mocker.patch.object(LogGenerator, "new_logfile", return_value=stub)
    mocker.patch.object(measurement, "_write_results_for_pattern")
    measurement.run(None, None, (), stub, '')
    for pattern in islice(f, expected_regex_tested):
        measurement._write_results_for_pattern.assert_any_call(
            pattern.rstrip())
