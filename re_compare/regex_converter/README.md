Regex Converter
===============

A tool to convert regexes from one regex syntax to a common basic syntax.

## Features
* Convert python re2 regexes to the basicy regex syntax
* Convert protein regexes to re2 syntax
* Build an AST (abstract syntax tree) for a regex pattern
* Fairly easy to expand

## Contents
- [Installation](#installation)
- [Usage](#usage)
- [Output](#output)
- [Contributing](#contributing)
- [License](#license)


## Installation
```bash
$ git clone https://github.com/gzohari/re-compare
```

install ply library (python lex-yacc) from [here](http://www.dabeaz.com/ply)

## Usage


-  In the projects root directory:
```
python
from re_compare.regex_converter.re2_ast.re2_parser import *
p = Re2Parser()
tree, groups, named_groups = p.parse('abc') # Could be any valid re2 pattern pattern
basic_syntax_tree = p.convert_re2_tree_to_basic_syntax(tree, groups, named_groups)
basic_syntax_patern = basic_syntax_tree.to_basic_string()
```
In a similar way it's possible to convert proteins patterns to re2 patterns

## Output
The library implements a way to build an abstract syntax tree from a given patter in any supported regex syntax
All trees support the to\_re2\_string() method to convert to re2 syntax.
The basic syntax tree has a to\_basic\_string\() method 


## Contributing


## License
	re-compare is released under the [MIT License](http://www.opensource.org/licenses/MIT).


