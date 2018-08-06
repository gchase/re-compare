#!/usr/bin/env python3

import logging
import argparse
import traceback
import os
import sys
from analysis import Analysis
from collector import Collector

from config import DEBUG, DEFAULT_LOG_FILE_DIR


def is_dir(dirname):
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname


def main():

    if DEBUG:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.INFO,
            format=
            '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
            datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=lambda x: is_dir(x))
    parser.add_argument(
        '--test_types',
        nargs="+",
        choices=['first_match', 'all_matches', 'consecutive_matches'])
    parser.add_argument('--log_files', nargs='+', type=argparse.FileType())
    parser.set_defaults(
        test_types=['first_match', 'all_matches', 'consecutive_matches'])

    args = parser.parse_args()

    if args.log_files:
        logging.info('starting analysis')

        Analysis(files=args.log_files).analyze_logs()

        logging.info('finished analysis')
    else:
        logging.info('starting collection')

        Collector(args.task).collect()

        logging.info('finished collection')
        logging.info('starting analysis')

        Analysis(logs_dir=DEFAULT_LOG_FILE_DIR).analyze_logs()


if __name__ == '__main__':
    main()
