import numpy as np
import csv
import config
from os.path import join as path, basename, dirname
from config import PARAMETER_SPACE, ALGORITHMS, NUMBER_OF_REGEXES_IN_TASK
import itertools

# TODO - first stage - save the entire list in each point. second stage
# (intermediate) - turn  the list into statistical shit: (first match-
# take first cell, last match - take last cell, consecutive - do the same
# as first/last match but for each column, then present them in a graph
# with y being time, and x being [first_match,second_match...] this will
# be a monotone increasing func. Also write in the intermediate which
# matches had how many regexes reach. for example, all regexes reach first
# match, some reach the tenth, only one reaches the 1000. Later, we use
# lines and colors to show the user in the graph which x coordinate is
# sifnificant.


class ParameterCube:
    def __init__(self):
        self.cols = dict([
            param for space in list(PARAMETER_SPACE.values())
            for param in space
        ])

    #  init n-dim array, such that each cell is filled with a
    #  dimensions being the number of columns + 1 more for algorithms.
    #  each cell is a pointer to python object, which will be a N-sized
    # array, representing a matching task
    #  where N is number of regexes in the task
    def init_table_data_from_cols(self):
        dimention = [len(ALGORITHMS)] + [len(v) for _, v in self.cols.items()]

        self.data = np.ndarray(dimention, dtype=object)

    # TODO explain the format of cut (should fit mathematical form somewhat)
    def populate_cut(self, cut):
        col_names = list(self.cols.keys())
        index_of_log_in_cube = [slice(None)] * len(col_names)

        for param_name, param_value in cut.parameters.items():
            index_of_log_in_cube[col_names.index(param_name)] = self.cols[
                param_name].index(param_value)
        index_of_log_in_cube.insert(0, slice(None))
        cut.data = self.data[tuple(index_of_log_in_cube)]

    def add_point_from_log(self, log):

        #  n-dim index (written as an array)
        #  of the NUMBER_OF_REGEXES_IN_TASK res array in the cube
        #  first dim is the algorithm, the others are dimensions,
        #  and the last is the ending # TODO WHAT?? what is the ending?
        index_of_log_in_cube = self.get_cube_index_from_log(log)

        self.data[index_of_log_in_cube] = {'results': log}

    def get_cube_index_from_log(self, log):
        """TODO: Docstring for get_cube_index_from_log.

        :log: TODO
        :returns: TODO

        """
        col_names = [a for a in (self.cols.keys())]
        log_meta = {}
        alg = ""
        index_of_log_in_cube = [None] * len(col_names)

        with open(path(dirname(log), 'metafile.csv')) as mf:
            reader = csv.DictReader(mf)
            for row in reader:
                if row['filename'] == basename(log):
                    row.pop('filename')
                    row.pop('taskname')
                    alg = row.pop('alg')
                    log_meta = row
                    break

        for param_name, param_value in log_meta.items():
            param_name = param_name.split(".")[1]
            index_of_log_in_cube[col_names.index(param_name)] = self.cols[
                param_name].index(param_value)

        for alg_path in ALGORITHMS:
            if basename(alg_path) == alg:
                index_of_log_in_cube.insert(0, ALGORITHMS.index(alg_path))
                return tuple(index_of_log_in_cube)
