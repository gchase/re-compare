from collections import OrderedDict

#TODO - remove duplication between this and TEST_TYPES
OUTPUT_TYPES = ['consecutive_matches', 'all_matches', 'first_match']
# OUTPUT_TYPES = []

DEBUG = True

SKIP_CUTS = ()

DEFAULT_LOG_FILE_DIR = 'tests/functional/protein/logs'

REGEX_TYPE = "dna_patterns"

TEXT_TYPE = "dna_sequence"

ALGORITHMS = ("algorithms/python_pattern_recog",
              "algorithms/re2_pattern_recog", "algorithms/modified_grep")

# Don't change order of spaces in the PARAMETER_SPACE, regex should
# be first, text second
PARAMETER_SPACE = OrderedDict({
    'regex_space': [('hardness',
                     ["easy-protein-patterns", "harder-protein-patterns"])],
    'text_space': [('length', ['10e3', '10e5', '10e7'])]
})

# how many runs to do for each slice
# (and then average them) TODO - describe this better
NUMBER_OF_REGEXES_IN_TASK = 10

ALGORITHM_TIMEOUT = 1000  # seconds until algo times out on a specific pattern and continues

MAX_MATCHES_PER_PATTERN = 2

BOXCHART_MATCH_LIMIT_PERCENTAGE = 1

#TODO - make this work
# DELETE_RAW_TEXT_FILES_AFTER_PRE_PROCESSING = True
