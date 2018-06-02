from contextlib import contextmanager
from exceptions import Timeout
from itertools import islice
from log_generator import LogGenerator
from os.path import join as path, basename
import config
import glob
import json
import logging
import signal
import subprocess


class Measurement:
    MATCH_PREFIX = ">>>>"

    def __init__(self, alg_executable_path):
        self.alg = alg_executable_path
        self.regex_file = None
        self.regex_params = None
        self.text_params = None
        self.text_file = None
        self.log_generator = None
        Measurement.register_timeout()

    def _do_measurement(self):
        self._write_header()
        self._write_body()

    def _write_body(self):
        with open(self.regex_file, "r") as pat_f:
            for i, pattern in enumerate(
                    islice(pat_f, config.NUMBER_OF_REGEXES_IN_TASK)):
                pattern = pattern.rstrip()
                logging.debug(
                    "pattern num: %d/%s, algorithm: %s, text: %s, pattern_file: %s,  pattern: %s"
                    % (i, config.NUMBER_OF_REGEXES_IN_TASK, self.alg,
                       self.text_file, pat_f.name, pattern))
                with self._timeout_alarm():
                    self._write_results_for_pattern(pattern.rstrip())

    def _valid_matches(self, pattern):
        """TODO: Docstring for get_va.

        :pattern: TODO
        :returns: TODO

        """
        matches_for_pattern = -1
        with self._run_alg(pattern) as pipe:
            for match in pipe.stdout:

                # not a match, don't care
                if not match.startswith(Measurement.MATCH_PREFIX):
                    continue
                matches_for_pattern += 1

                if matches_for_pattern >= config.MAX_MATCHES_PER_PATTERN:
                    pipe.kill()
                    break

                formatted_match = match[len(Measurement.MATCH_PREFIX):].strip()
                yield json.loads(formatted_match)

    def _write_results_for_pattern(self, pattern):
        total_time_delta = 0
        for num_matches, match in enumerate(self._valid_matches(pattern)):
            match.pop('match')
            total_time_delta += match['time']

            if not num_matches:
                first_match_row = [
                    pattern, 'first_match', num_matches, match['time'],
                    match['span']
                ]
                if not Measurement.is_EOF(match):
                    first_match_row[2] = 1
                self.log_generator.writerow(first_match_row)

            if not Measurement.is_EOF(match):
                consecutive_match_row = [
                    pattern, 'consecutive', num_matches + 1, match['time'],
                    match['span']
                ]
                self.log_generator.writerow(consecutive_match_row)
        last_match_row = [
            pattern, 'all_matches', num_matches, total_time_delta, [-1, -1]
        ]
        if not Measurement.is_EOF(match):
            last_match_row[2] += 1
        self.log_generator.writerow(last_match_row)

    @staticmethod
    def is_EOF(match):
        return match['span'] == [-1, -1]

    def _write_header(self):
        self.log_generator.writeheader()

    def run(self, text_dir, regex_dir, point, meta_writer, task_name):
        regex_space_len = len(config.PARAMETER_SPACE['regex_space'])
        self.regex_params = point[:regex_space_len]
        self.text_params = point[regex_space_len:]

        self.regex_file = self._find_file_by_params(regex_dir,
                                                    self.regex_params)
        self.text_file = self._find_file_by_params(text_dir, self.text_params)

        self.log_generator = LogGenerator(point, self.alg)

        meta_writer.writerow(
            (basename(self.log_generator.log_path()), task_name,
             basename(self.alg)) + point)  # extract to own calss

        self._do_measurement()
        self.log_generator.close()

    def _find_file_by_params(self, directory, point):
        """TODO: Docstring for _find_file_by_params(file_directory.
        :returns: TODO

        """
        file_pattern = path(directory, "*_%s" % '_'.join(point))
        files = glob.glob(file_pattern)
        if len(files) == 1:
            return files[0]
        else:
            raise ValueError("should have exactly one file of format \
            %s in the %s directory" % (file_pattern, directory))

    @contextmanager
    def _run_alg(self, pattern):
        with subprocess.Popen(
            [self.alg, pattern, self.text_file],
                stdout=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True) as pipe:
            try:
                yield pipe
            except Exception as e:
                pipe.kill()
                raise e

    @contextmanager
    def _timeout_alarm(self):
        signal.alarm(config.ALGORITHM_TIMEOUT)
        try:
            yield
        except Timeout:
            logging.debug("timeout reached for pattern")

        finally:
            signal.alarm(0)  # cancel timeout alarm

    @staticmethod
    def register_timeout():
        signal.signal(signal.SIGALRM, Measurement.raise_timeout)

    @staticmethod
    def raise_timeout(signum, frame):
        raise Timeout
