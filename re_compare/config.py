""" out of all algorithms located in the algorithms dir, which ones should
be used in the analysis
"""
ALGORITHMS = ("algorithms/python_pattern_recog",
              "algorithms/re2_pattern_recog")
""" configure the parameters used during the collection and analysis.
1) The 'regex_space'/'text_space' keys shouldn't be changed or re-ordered,
only their values should be configured.
2) The single value of 'regex_space' is a list of pairs, where each pair
has the parameter name in the left side, and a list of possible values for that
param in the right side.
3) The value of 'text_space' is similar.
4) Unless denoted in the SKIP_CUT list above, each parameter in a right side of
a pair will be tested as a dependent variable against all combinations of
values from other import lists, and vice versa.
5) the naming of the files placed in the 'regex'/'text' directories
correponds with this configuration, see README
"""

PARAMETER_SPACE = __import__("collections").OrderedDict({
    'regex_space': [('hardness',
                     ["easy-protein-patterns", "harder-protein-patterns"])],
    # ["dna_translated"])],
    'text_space': [('length', ['10e3', '10e5', '10e7'])]
})
""" log-files outputted in the collection phase will be generated here,
and also collected during the analysis phase"""
DEFAULT_LOG_FILE_DIR = 'logs'
""" Denote which types of graphs should be outputted
at the end of the Analysis stage. The default tests are:
OUTPUT_TYPES = ['consecutive_matches', 'all_matches', 'first_match']
"""
OUTPUT_TYPES = ['consecutive_matches', 'all_matches', 'first_match']
""" skip analysis of specified cuts, for example:
SKIP_CUTS = ('hardness')
will skip analyzing cuts in the parameter cube whose dependent variable
, as stated in the PARAMETER_SPACE in this config, is 'hardness'
"""
SKIP_CUTS = ()
""" how many regexes, out of the total number in each file in the
'regex' directory, should be used. If the regex file has more
than NUMBER_OF_REGEXES_IN_TASK regexes
(where each regex is a line in the file),
then only the first NUMBER_OF_REGEXES_IN_TASK are collected.
NUMBER_OF_REGEXES_IN_TASK should not be larger than the number of regexes
in any of these files
"""
NUMBER_OF_REGEXES_IN_TASK = 30
""" maximum runtime of algorithm per pattern, in seconds """
ALGORITHM_TIMEOUT = 1000

MAX_MATCHES_PER_PATTERN = 100
""" Influences how many boxes whould be outputted in the boxchart output.
The number of boxes outputted is calculated in the following way:
total_number_of_boxes = NUMBER_OF_REGEXES_IN_TASK *
                        BOXCHART_MATCH_LIMIT_PERCENTAGE
Therefore, this should be a number between 0 and 1
"""
BOXCHART_MATCH_LIMIT_PERCENTAGE = 1
""" output debugging information during runtime """
DEBUG = True
