import pytest
import importlib
import sys
config = sys.modules['config'] = importlib.import_module('tests.mock_config')
from re_compare.analysis import Cut


def test_all_cuts(mocker):
    stub = mocker.stub(name='fff')
    cols = {
        'regex_hardness': ['easy', 'hard'],
        'regex_depth': ['1', '2', '3'],
        'text_length': ['10e3']
    }
    stub.cols = cols

    Cut.all_cuts(stub)
    cuts = set()
    for cut in Cut.all_cuts(stub):
        new_cut = (cut.dep, str(list(cut.parameters.items())))
        print(new_cut, cuts)
        assert new_cut not in cuts
        assert cut.dep not in cut.parameters.keys()
        cuts.add(new_cut)
