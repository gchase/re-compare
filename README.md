![Thanks to logomaker with the help on the logo](doc/Logo.png)


Re-Compare
=====

A modular configurable platform for comparing regex matching algorithms with state-of-the-art baseline algorithms.

## Features

[comment]: # (TODO link mathematical documentation)

* Runs user defined workloads on state of the art algorithms and tracks their performance
* Analyzes algorithm performance across user defined parameter space [See Problem space documnetation](./doc/Problem_Space.pdf)
* Parses regexes in multiple regex syntaxes and converts them
* Random regex generator with user defined operation syntax, alphabet and depth

## Contents
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Output example](#output-example)
- [Directory structure](#directory-structure)
- [Usage](#usage)
- [Translator syntaxes](#translator-syntaxes)
- [Changing-the-parameters-of-the-cube](#changing-the-parameters-of-the-cube)
- [Adding algorithms](#adding-algorithms)
- [Adding datasets](#adding-datasets)
- [Output structure](#output-structure)
- [Log format](#log-format)
- [Regex translation](#regex-translation)
- [Random regex generator](#random-regex-generator)
- [Default datasets](#default-datasets)
- [Default Algorithms](#default-algorithms)
- [Future work](#future-work)
- [Contributing](#contributing)
- [License](#license)


## Installation

Install python 3.6.5 (and pip3), then clone the repo and cd into it:
```bash
$ git clone https://github.com/gchase/re-compare
$ cd re-compare
```

add the directory into PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

Install dependincies with the following script (it'll require sudo for installing the baseline algorithms)
```bash
sudo bash utils/install.sh
```

Change directory into the main module, where the main execution file `re_compare.py` and the tests dir are located.
```bash
cd re_compare
```

In order to check that the installation went smoothly, you can run:
```bash
pytest tests
```

## Getting Started
Suppose we'd like to compare some regex pattern matching algorithm to other known baselines.

For convenience and familiarity, our running example for this README will use Grep as this "new" regex matching algorithm we'd like to test, and the built-in "Protien" task.
A task is a set of calculations of the type "match regex_x to text_y" (to learn more about how to configure and add your own tasks to re-compare, see [Adding datasets](#adding-datasets))

Our first step will be to modify Grep's output so that it adhers to Re-Compare's format, and rename Grep to "modified_grep" (in order to avoid confusion):
```bash
$ echo "test \n bloop \n test" > test.txt
$ ./modified_grep test test.txt
>>>>{"match": "test", "span": [0,3], "time": 726}
>>>>{"match": "test", "span": [15,18], "time": 15}
>>>>{"match": "EOF", "span":  [-1,-1], "time": 323}
```
Note that the "time" field denotes the time between the last match (or program start) until current one.

Next, we need to add it as input to Re-Compare by:

- moving the executable to the "algorithms" executible folder (which already stores the baseline algorithms built-in in
Re-Compare plus any other baselines added by a user)

```bash
mv ./modified_grep re-compare/re_compare/algorithms/
```
- Registering the algorithm in the global config file:
```
  #re-compare/re_compare/config.py
  ALGORITHMS = (
                "algorithms/python_pattern_recog", # Baseline 1
                "algorithms/re2_pattern_recog", # Baseline 2
                "algorithms/modified_grep" # ADDED THIS LINE
                )
```

And finally, run the algorithm on the protein task:
```bash
$ cd re-compare/re_compare
$ ./re_compare.py --task tasks/protein
# output is being generated!
```

And we're done.

To see the types of different output we created, see [Output example](#output-example).

## Output example
There are two types of output, *logs* that detail all the measurements made on all algorithms on the given task during the testing stage, and *plots* that show various statistical comparisons between the new algorithm ("modified_grep" in this running example) and the baseline algorithms. The logs are located in the 'logs' directory, and the plots in the 'output' directory — see [Directory structure](#directory-structure) to see exactly where these directories are located.

- logfile example
  ```text
  regex,matchtype,matchnumber,time(ms),span
  G|S|T|A|D|N|E|K|R,first_match,1,781,"[2, 2]"
  G|S|T|A|D|N|E|K|R,consecutive,1,781,"[2, 2]"
  G|S|T|A|D|N|E|K|R,consecutive,2,4,"[3, 3]"
  G|S|T|A|D|N|E|K|R,all_matches,2,785,"[-1, -1]"

  ```

Where match time is one of {first_match,consecutive,all_matches} and they signal the following time calculations.
-   first_match - time until first match was recieved. match number is always 1
-   consecutive - ith delay time. The time between the i-1 to the ith match, match number is i.
-   all_matches - total elapse time of the algorithm, match number is the number of matches across the entire file.

- Example plots

The y axis is in ms and the x axis is in [user defined](#changing-the-parameters-of-the-cube) categories.

  ![consecutive graph](doc/consecutive%20matches%20-%20(2%2C%201%2C%202).png)

  ![non consecutive graph](output/all_matches_cut_4.png)

## Directory structure
Directory structure in Re-Compare is *important*, because the program assumes some files are located in particular locations. All files/directories not mentioned in this section are not important for the user.

```
re-compare/
|--- re_compare/        # cd into this directory to run program/tests
|    |--- re_compare.py # main executable
|    |--- algorithms/   # put all algorithms here, baselines and the algorithms to test against them
|--- logs/              # algorithm measurements are generated and placed here
|--- output/            # plots generated from the logs placed in the logs directory are placed here
|--- tasks/             # place tasks here, using the same directory format
```

## Usage

re-compare is comprised of 3 major modules
* Regex translator
* Collector
* Cube-Analyzer

The **Regex translator** builds an [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree) for a regex pattern and allows converting multiple regex syntaxes to a common basic syntax (See [Translator syntaxes](#Translator-syntaxes))
For usage see [Regex translation](#regex-translation)


The **Collector** takes datasets in a a user friendly format (see [Adding datasets](#Adding-datasets))and Regex matching algorithms executables (see [Adding Algorithms](#Adding-Algorithms)). It translates the regexes to a syntax that each Alg supports, using **Regex translator**, runs the regexs tasks on each Alg and records the timing of each algorithm.

The **Cube-Analyzer** takes the logs of the **Collecter**, and outputs graphs and logs of statistical comparisons of the algorithm across every parameter in the user defined [Parameter Space](link to math viggentes).
[//]: # (fix link )


-  To perform measurements and analysis, run

```
$ ./re_compare/re_compare --task <path_to_task>
```

Note that the task folder must match re-compares task structure format (see [Adding datasets](#Adding-datasets))

Our built in [Default](#Default-datasets) tasks, can be found in the tasks directory
```
$ ./re_compare/re_compare --task re_compare/tasks/<dir_name>
```

- Assuming you want to add your own external log files, or to alter re-compare log files prior to plot generation, you can change the logs manually and perform only the cube-analysis (See [Log format](#log-format)).

```
$ ./re_compare/re_compare --log_files   <path/to/logfiles/>
```

This is it for the intro to re-compare. The next sections are for power users that want to costumize or get the most out of re-compare.

Power users (beware, code ahead)
===============

## Changing the parameters of the cube

See documentation inside [config.py](re_compare/config.py)

## Translator Syntaxes
Our in house regex tranlator uses python's [extended regex format](https://docs.python.org/2/library/re.html) as an intermidiate representation of all other syntaxes (and is itself supported as a regex syntax in re-compare).

These are the syntaxes currently supported in re-compare

**Basic syntax:**
The basic regex syntax supports the following operations:
`terminals` - letters digits and all printable characters.
also supports escaped characters in both `\\n` or `\\t` format or `\\x00` format with two hex digits.
`|` - Or operator
`()` - Group operator, useful for defining precedence, etc...
`*` - Star operator. matches a concatenation of the regex 0 or more times.
`?` - optional operator. matches either the regex or the empty string.

**Python's extended syntax**
Also used as our intermidiate language as it is the most expressive. Full description can be found [here](https://docs.python.org/2/library/re.html)

**Proteins:**
Full description of the proteins regex syntax can be found [here](http://www.hpa-bioinfotools.org.uk/ps_scan/PS_SCAN_PATTERN_SYNTAX.html).

## Adding algorithms
<!--[//]: # ( TODO change the word pattern to regex globally)-->
All regex matching algorithms tested in this library have the following signature:
<!--[//]: # ( TODO explain that each alg will run on all regexes and text pairs in the given task)-->
```bash
 algorithm_executable regex_string path/to/textfile
```
The collector ignores all lines that are not prefixed by `>>>>`.
The output format for returning spans is a [json string](https://www.w3schools.com/js/js_json_syntax.asp), with keys `match,span,time` that correspond with each match's string-match, its span in the text, and the __delta__ from the previous match. When the algorithm reaches EOF, it must output a last match, with the match "EOF", span `[-1,-1]` and the delta time from the previous match (or begining of run, if there were not matches). For example:
```
# in file example.txt
abc is easy as 123
abc

$ ./modified_grep "abc|123" example.txt
>>>>{"match": "abc", "span": [0,2], "time": 840}
>>>>{"match": "123", "span": [15,17], "time": 63}
some_output_that_doesn't_start_with '>>>>' hence is ignored
>>>>{"match": "abc", "span": [19,21], "time": 5}
>>>>{"match": "EOF", "span":  [-1,-1], "time": 21}

$ ./modified_grep "mooooooooo" example.txt
>>>>{"match": "EOF", "span":  [-1,-1], "time": 888}
```

## Adding datasets
A task dataset is a directory with the following structure:

```
task_name/
|--- text/                        # subdir for all text files
|    |--- textfile_10e3           # examples of textfiles
|    |--- textfile_10e3           #
|--- regex/                       # subdirs for all regex patterns
|    |--- regexfile_easy-patterns # example of a file of regex patterns
|    |--- regexfile_hard-patterns #
|--- _config.py                   # the task confdig file. not to be confused with the global re-compare config file.
|--- _pre_processing.sh           # a pre processing script. usefull for dynamically loading and pre processing big data files.
```
The regex and text file names are dependant on the **ordered** values in `_config.PARAMETER_SPACE`. This dependency is what the section explains.

### Param space configuration

Here is an example of a definition of a **parameter space**:
<!--[//]: # ( TODO explain generalisability of the param space, do this with both a general case and the example from the running example)-->
```python
# task_name/_config.py
PARAMETER_SPACE = OrderedDict({
	'regex_space': [
		('hardness',["easy", "hard"]),
		('depth',["shallow","deep"])
	],
	'text_space': [
		('length', ['10e3', '10e5', '10e7'])
	]
})
```
Note that these parameters are completly user configureable. Here is a more general parameter space configuration:
```python
# task_name/_config.py
PARAMETER_SPACE = OrderedDict({
	'regex_space': [
		('r_param1',["val_a", "val_b"]),
		('r_param2',["val_c","val_d"])
		('r_param3',["val_e","val_f","val_g"])
	],
	'text_space': [
		('t_param1',["val_z", "val_y"]),
		('t_param2',["val_x","val_w"])
		('t_param3_new_and_imporved',["val_e","val_f"])
	]
})
```
The beauty of re-compare is that it can run on whatever parameterisation of the param space the user wants.



<!--[//]: # ( TODO explain whose name correspond to what maybe view of the configfiles)-->
<!--[//]: # ( TODO make sure each config file is given a different name)-->
Both subdirectories have files with names that correspond to a selection of values from their space. Each such file start with either a `_` char, or `<some_prefix>_` as displayed below
- The regex subdirectory has files whose names correspond with the `regex_space` in the `PARAMETER_SPACE`. So for the example above, the `regex` subdirectory will hold files with names
```bash
$ ls task_name/regex
_easy_shallow
<some_prefix>_easy_deep
_hard_shallow
_hard_deep
```
Each file holds one regex pattern per line. These patterns can be either in exteded regex patterns, or with any pattern that the `regex_converter` module can convert to extended regex patterns
- The text subdirectory has a similar structure to the regex dir. However, the text subdirectory can either be empty, in which case the text files will be downloaded from a url specified in the local config file and proccessed using the `_pre_processing.sh` script. In our example the text sub dir might look like this:
```bash
$ ls task_name/text
_10e3
_10e5
<dont_care>_10e7
```
Each file holds a textfile that all patterns from all of the files in the regex dir will be tested on.
- The task specific `_config.py` file must assign a value to a `regex_type` constant. This constant is used by the `regex-converter` module in order to convert all the patterns from their own grammar to a simplified regular expression grammar. Adding parsers to this convertion process will add support to more regex types.
Here is an example of the `_config.py` :

```python
#task_name/_config.py
TEXT_URLS = "https://www.my_sweet_texts.com/text1.txt"
regex_type = "protein_patterns"

```


## Output structure

[//]: # ( TODO explain what canonical form is or change the wordings)
[//]: # ( TODO explain what cannonical form is with figure)

- The extended form regular expressions, converted from the task's patterns, are stored at `path/to/task/tmp/converted_regex_files`
- Logs from the collection stage (in format [Log Format](#log-format)) are stored at `./logs`
- Output plots are located at `./output`, where plot types are specified in `config.OUTPUT_TYPES`

[//]: # ( TODO change dot to point add reference to running example)
[//]: # ( TODO reword the the term index and explain with example)
[//]: # ( TODO show example of the dot file to explain the meta data header line)
	For each point in the parameter space, a consecutive matches file will be created, with its parameters listed inside. It's index in the parameter cube is part of the title.

	For each possible cut in the parameter space, a `first_match` and `all_matches` plot is created, where its parameters are specified at `detailed_output.csv`

## Log format
  This section explains the output format of the collection module, which is also the input of the cube analyzer.

  - For each selection of algorithm from `config.ALGORITHMS` and parameters from all lists specified in `config.PARAMETER_SPACE`, a log file __must__ be supplied with the following csv format:
	```csv
	regex,matchtype,matchnumber,time(ms),span
	```
        where `regex` is an __extended form regular expression__, matchtype is one of `consecutive, first_match, all_matches`, and span is in format `[n,n + <size_of_match>]`. This csv format is ment to ease querying the log files.

    The log file must be ordered such that matches of any one regex form a continuous block with the first_match line first, the all_match line last and the consecutive lines in chronological order.

- A file called `metafile.csv` must also be supplied, where the parameters of each logfile in the previous bullet is specified in the following format:
	```csv
	filename,taskname,alg_name,regex.param_name_1,regex.param_name_2,...regex.param_name_n,text.param_name_1,text.param_name_2,...,text.param_name_n
	<file_path>,<task_name>,<regex_param_1_value>,<regex_param_2_value>,...
	```
	For example, for a parameter space:
	```python
	PARAMETER_SPACE = OrderedDict({
			'regex_space': [('hardness',["easy", "hard"])],
			'text_space': [('length', ['10e3', '10e5', '10e7'])]
	})
	```
	and algorithm list
	```python
	ALGORITHMS=("grep","egrep")
	```
	the metafile will look like this (note that file names are named appropriately for convenience, but their names are not part of the analysis, just the param columns):
	```csv
	filename,taskname,alg,regex.hardness,text.length
	grep_easy_10e3.csv,path/to/task,grep,easy,10e3
	grep_easy_10e5.csv,path/to/task,grep,easy,10e5
	grep_hard_10e3.csv,path/to/task,grep,hard,10e3
	grep_hard_10e5.csv,path/to/task,grep,hard,10e5
	egrep_easy_10e3.csv,path/to/task,egrep,easy,10e3
	.
	.
	.
	```

## Regex translation
Currently, we have 3 different parsers for the 3 supported syntaxes: `BasicAstParser`, `Re2Parser` and `ProteinParser`.
Description of the syntaxes can be found in the [Translator syntaxes](#translator-syntaxes) section.

The regex parsers are using the python [ply library](http://www.dabeaz.com/ply/).
ply is a python lex/yacc library which allows building [lalr1](https://en.wikipedia.org/wiki/LALR_parser) grammars.

The parsing is doen automatically during the collection step.

**usage:**
The following are the manual instructions for the parsers (useful if you want to preprocess your own datasets).

In the project's root directory run the following commands:
```
python
from re_compare.regex_converter.re2_ast.re2_parser import *
p = Re2Parser()
tree, groups, named_groups = p.parse('a|b') # Could be any valid re2 pattern pattern
basic_syntax_tree = p.convert_re2_tree_to_basic_syntax(tree, groups, named_groups)
basic_syntax_pattern = basic_syntax_tree.to_basic_string()
print(basic_syntax_pattern)
```

First, we import the re2 parser. Then we create an instance of an re2 parser.
The parse method gets a pattern and return a tuple containing the build AST, groups and named groups (named groups are not yet supported, but referring groups by their index in the list of groups works)
Here, it's possible to print the tree with the `to_re2_string()` method.
To convert the tree use the `convert_re2_tree_to_basic_syntax` method with the same tuple elements that parse returned.
This method returns an AST in the basic syntax, which supports the `to_basic_string()` method in order to print it.

**Building your own parser:**
First step is to define the tokens for the syntax.
Easiest  way to do so is using literal strings.
In some complex situation there's a need for regular expressions.
At first, define the logical name of each token in a 'tokens' variable.
For example:

    tokens = (
    'DIGIT',
    'PLUS',
    'MULT'
    )

Now define regular expression patterns to match each token using t_<TOKEN_NAME> convention:

    t_MULT = r'\*'
    t_PLUS = r'\+'
    t_DIGIT = r'[0-9]'

If needed you can also create a function instead of a single regex.
An error handler can be defined like this:

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

After you got your lexer working you need to define the grammar rules.
ply allows generic LALR grammars which should be ok for most reasonable syntaxes
Some grammars may have conflicts regarding which rule should be used in the case where multiple rules can derive the same expression.
For example we want a calculator to use multiplication before addition in an expression like '1+2*3'
In order to solve these conflicts use the 'precedence' table

    precedence = (
    ('left', 'MULTIPLY'),
    ('left', 'PLUS'),
    )

The precedence table specifies the order between operators and the correct way in which to derive the expressions.

In this example multiplication will precede addition and the left argument would be calculated first.
Finally, its time to define the actual grammar rules.
Use the convention `p_<RULE_NAME>`
I suggest using a class for the parser but it's not necessary.
Rules are defined like the following example:

    def p_star(self, p):
        """expression : expression STAR"""
        p[0] = Re2StarNode(p[1])
[//]: # ( TODO explain the Re2starnode generates the syntax tree)


The docstring is mandatory and tells ply exactly which expressions to match for this rule.
In our case we match any expression followed by a STAR token ('\*') in re2 syntax.

p is an array of the tokens of the expression we are currently deriving.
After the method ends p[0] holds the result of the current expression, in our case an ast.
We create an ast node for a star token using the ast of the sub-expression in p[1] which was already calculated.
Ast nodes all inherit from the base class Ast in generic_ast.py
They all have a member names sons containing a list of the sub-tree's (can be empty).
They also implement a basic `to_re2_string()` method (can be overriden by an inheriting class)
They all have a similar structure.
Here's an example of an OR ast node for re2 grammar:

    class Re2OrNode(Ast):
      def __init__(self, left_son, right_son):
          super(Re2OrNode, self).__init__()
          self.sons = [left_son, right_son]

      def to_re2_string(self):
          return '%s|%s' % (self.sons[0].to_re2_string(), self.sons[1].to_re2_string())
The or node has two sons (AST's of two expressions).
It implements the `to_re2_string()` method which prints the expression in re2 syntax, using the `to_re2_string()` method of the two sons.

For more information and examples see the official [documentation](http://www.dabeaz.com/ply) of ply.
The ply [calculator](http://www.dabeaz.com/ply/example.html) covers all common features pretty well.

**Editing a parser:**
The parsers here are written in optimized mode.
While much faster when parsing multiple strings, optimized mode also creates temporary files.
These files contain the state machine for the created parser (and some implementation)
Note that changing the python parser and running again will **NOT** change the state machine saved in the file.
Use `./removeTempFiles.sh` from the regex converter directory or remove them manually.

## Random regex generator
We build an in house random regex generator to test re-compare.
Its quite extendible and very easy to use.
The random regex generator can be found in the re_compare/random_generator/random_gen.py module.
Here is an example of our random regex generator
```python
>>> operations = ["%s%s", "%s|%s", "%s?", "%s+", "%s*", "(%s)"]
>>> alphabet = ["A", "C", "G", "T", "."]
>>> (min_depth,max_depth,oper_percent)=(3,5,50)
>>> reg=generate_random_regex(alphabet, operations, max_depth, min_depth, oper_percent)
>>> reg
[[['C', '|', [['(', 'G', ')'], '*']], ['A', '+']], '?']
>>> flatten_expression_tree(reg)
'C|(G)*A+?'
```
Regex relations and terminals are currently chosen uniformly from operations and alphabet respectivly.
Operations can have any arity and use printf like syntax where '%s' marks a sub-expression.
max_depth and_min depth limit the depth of the regex as a syntax tree.
oper_precent is the liklyhood that an operation will be chosen when depth is within bounds.

The resulting expression is given in a recursive list formula as shown above. Allowing easy manipulation and post processing of the generated regex.
flatten_expression_tree can be called to flatten the regex into string format.

## Default datasets
All datasets are available at '/re_compare/tasks/'


Currently we provide the following default datasets

* **Protein motifs**
Regexes are protein motifs taken from the [prosite](https://prosite.expasy.org) protein database. The regexes where extracted by a crawler and translated to extended regex format via our in house syntax [Translator](#Translator-syntaxes)
The text for this dataset is a file containing all protein sequences in the [PDB](https://www.rcsb.org/) protein database.

The motivation for this dataset came from the [paper](https://ink.library.smu.edu.sg/cgi/viewcontent.cgi?article=4157&context=sis_research) "Negative Factor: Improving Regular-Expression Matching in Strings"  by Yang et al.

* **DNA promoter sequences**
Regxes nucleotide Yeast promoter sequences taken via a crawler from the Yeast promotor sequence [database](http://rulai.cshl.edu/cgi-bin/SCPD/getfactorlist) Regexes were translated by a short script based on the [fasta](https://en.wikipedia.org/wiki/FASTA_format) format specification. These regexes are of the '.[]' form over [AGCT], meaning they are a concatenation of bracket sets or terminals over the nucleotide alphabet.
The text is the entire Saccharomyces cerevisiae (Baker's yeast) [Chromosome](https://downloads.yeastgenome.org/sequence/S288C_reference/chromosomes/fasta/)

The addition of this dataset was inspired by the [paper](https://ieeexplore.ieee.org/document/4359878/) "DNA Motif Representation with Nucleotide Dependency" by Chin et al.

* **Web packet analysis**
The web analysis tasks are composed of two regex sets that are matched on the same text.
Regexes are regexes extracted from the [Bro](https://www.bro.org/) and [Snort](https://www.snort.org/) web inspection systems. The regexes were manually extracted from the source code of the systems.
Texts are taken from the MIT [Darpa](https://www.ll.mit.edu//ideval/data/) project
TODO say which dataset specifically
These datasets were collected based on the [paper](https://ieeexplore.ieee.org/document/4579527/) "Fast and memory-efficient regular expression matching for deep packet inspection" by Yu et al.

* **English text**
Regexes for english text filtering tasks were manually picked from [regexlib](http://www.regexlib.com/Default.aspx).
Texts are a concatenation of all abstracts found on the [DBLP-Citation-network](https://aminer.org/citation).


## Future work
TODO this should be filled after the project is done and after consulting Benny
talk about signals
talk about itegration of classifiers and random generators
talk about random bison
talk about checkling regex params such as case sensitive etc
talk about constrained random text generators  (or genrerators by regex fit)



## Contributing
To contribute to the devlopment of re-compare, please contact Dean Light at light.skep@gmail.com

## License
	re-compare is released under the [MIT License](http://www.opensource.org/licenses/MIT).
  Project dependancies include:
  <!--TODO put dependancies here-->
