import os
import csv
from config import DEFAULT_LOG_FILE_DIR
from os.path import basename


class LogGenerator:
    """ Generates a logfile that can be consumed by the Analyzer,
        given results from Test.
    """
    FIELD_NAMES = ['regex', 'matchtype', 'matchnumber', 'time(ms)', 'span']

    def __init__(self, params, alg):
        self.open_file = LogGenerator.new_logfile(params, alg)
        self.writer = csv.writer(self.open_file)

    def writeheader(self):
        """TODO: Docstring for writeheader.
        :returns: TODO

        """
        self.writer.writerow(LogGenerator.FIELD_NAMES)

    def log_path(self):
        return self.open_file.name

    def close(self):
        self.open_file.close()

    @staticmethod
    def new_logfile(params, alg):
        filename = "_".join([basename(alg)] + list(params))
        path_name = "{}/{}.csv".format(DEFAULT_LOG_FILE_DIR, filename)
        path = os.path.normpath(path_name)
        return open(path, "w")

    def writerow(self, row=[]):
        self.writer.writerow(row)
