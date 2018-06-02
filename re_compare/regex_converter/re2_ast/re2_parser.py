import functools

import ply.lex as lex
import ply.yacc as yacc
import sre_parse

from ..basic_syntax_ast.basic_ast_nodes import *
from .re2_ast_nodes import *
import re


class Re2Parser(object):
    def __init__(self):
        self.groups = []
        self.named_groups = {}

    tokens = ('TERM', 'OR', 'OPTIONAL', 'CARET', 'DOLLAR', 'STAR', 'PLUS',
              'LEFT_CURLY', 'RIGHT_CURLY', 'COMMA', 'NUMBER', 'DOT',
              'BRACKETS_EXPRESSION', 'LEFT_PAREN', 'RIGHT_PAREN',
              'NUMERIC_GROUP', 'ESCAPED_CHARACTER')

    t_TERM = r'[a-zA-Z\w<>!@&#=]'
    t_OR = r'\|'
    t_OPTIONAL = r'\?'
    t_STAR = r'\*'
    t_PLUS = r'\+'
    t_LEFT_CURLY = r'\{'
    t_RIGHT_CURLY = r'\}'
    t_CARET = r'\^'
    t_DOLLAR = r'\$'
    t_COMMA = r','
    t_DOT = r'\.'
    t_NUMERIC_GROUP = r'\\\d+'
    t_LEFT_PAREN = r'\('
    t_RIGHT_PAREN = r'\)'
    t_BRACKETS_EXPRESSION = r'\[([\w\-\\!@#&=]|\[\:|\:\])+\]'  # allowing digits, letters and some
    # special characters
    t_ESCAPED_CHARACTER = r'\\[Xx][a-fA-F0-9]{2}|\\[a-zA-Z] '

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    precedence = (
        ('right', 'RIGHT_PAREN'),
        ('right', 'LEFT_CURLY'),
        ('right', 'BRACKETS_EXPRESSION'),
        ('left', 'CARET'),
        ('right', 'STAR', 'PLUS', 'OPTIONAL'),
        ('left', 'OR'),
    )

    def t_NUMBER(self, t):
        r"""\d+"""
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        return t

    def p_expression_or(self, p):
        """
        expression : expression OR expression
        """
        p[0] = Re2OrNode(p[1], p[3])

    def p_group(self, p):
        """
        expression : LEFT_PAREN expression RIGHT_PAREN
        """
        self.groups.append(p[2])
        p[0] = Re2GroupNode(p[2])

    # TODO need to change so that
    # expressions -> expressions expression
    # expression -> (expressions)
    def p_expression_group(self, p):
        """
        expression : expression LEFT_PAREN expression RIGHT_PAREN
        """
        self.groups.append(p[3])
        p[0] = Re2ExpressionGroupNode(p[1], p[3])

    def p_brackets_expression(self, p):
        """
        expression : BRACKETS_EXPRESSION
        """
        p[0] = Re2BracketsExpressionNode(p[1])

    #TODO after the modification you can cut htis out
    def p_expression_brackets_expression(self, p):
        """
        expression : expression BRACKETS_EXPRESSION
        """
        p[0] = Re2ExpressionBracketsExpressionNode(p[1], p[2])

    def p_term(self, p):
        """expression : TERM"""
        p[0] = Re2TermNode(p[1])

    def p_dot(self, p):
        """expression : DOT"""
        p[0] = Re2DotNode()

    def p_escaped_character(self, p):
        """expression : ESCAPED_CHARACTER"""
        p[0] = Re2EscapedCharacterNode(p[1])

    #TODO also cut
    def p_expression_dot(self, p):
        """expression : expression DOT"""
        p[0] = Re2ExpressionConcatNode(p[1], p[2])

    #TODO can remove last 2 cases
    def p_expression_term_dot_optional(self, p):
        """expression : DOT OPTIONAL
                        | TERM OPTIONAL
                        | ESCAPED_CHARACTER OPTIONAL
                        | expression DOT OPTIONAL
                        | expression TERM OPTIONAL
                        | expression ESCAPED_CHARACTER OPTIONAL"""
        if len(p) == 3:
            if '.' == p[1]:
                under_optional_expression = Re2DotNode()
            elif '\\' == p[1][0]:
                under_optional_expression = Re2EscapedCharacterNode(p[1])
            else:
                under_optional_expression = Re2TermNode(p[1])
            p[0] = Re2OptionalNode(under_optional_expression)
            return

        if '.' == p[2]:
            under_optional_expression = Re2DotNode()
        elif '\\' == p[2][0]:
            under_optional_expression = Re2EscapedCharacterNode(p[2])
        else:
            under_optional_expression = Re2TermNode(p[2])
        p[0] = Re2ExpressionOptionalNode(p[1], under_optional_expression)

    #TODO you can add a
    #expression -> BRACKET_EXPRESSION
    # rule and then not have to add a specific case for BRACKET_EXPRESSION everytime
    #TODO can remove last 2 cases
    def p_brackets_group_optional(self, p):
        """expression : BRACKETS_EXPRESSION OPTIONAL
                        | LEFT_PAREN expression RIGHT_PAREN OPTIONAL
                        | expression BRACKETS_EXPRESSION OPTIONAL
                        | expression LEFT_PAREN expression RIGHT_PAREN OPTIONAL"""
        under_optional_expression = None
        if type(p[1]) is str and p[1][0] == '[':
            under_optional_expression = Re2BracketsExpressionNode(p[1])
        elif type(p[1]) == str and p[1] == '(':
            under_optional_expression = Re2GroupNode(p[2])

        if under_optional_expression is not None:
            p[0] = Re2OptionalNode(under_optional_expression)
            return

        if type(p[2]) is str and p[2][0] == '[':
            under_optional_expression = Re2BracketsExpressionNode(p[2])
        else:
            under_optional_expression = Re2GroupNode(p[3])
        p[0] = Re2ExpressionOptionalNode(p[1], under_optional_expression)

    #TODO can remove last 2 cases
    def p_expression_term_dot_star(self, p):
        """expression : DOT STAR
                        | TERM STAR
                        | ESCAPED_CHARACTER STAR
                        | expression DOT STAR
                        | expression TERM STAR
                        | expression ESCAPED_CHARACTER STAR"""
        if len(p) == 3:
            if '.' == p[1]:
                under_star_expression = Re2DotNode()
            elif '\\' == p[1][0]:
                under_star_expression = Re2EscapedCharacterNode(p[1])
            else:
                under_star_expression = Re2TermNode(p[1])
            p[0] = Re2StarNode(under_star_expression)
            return

        if '.' == p[2]:
            under_star_expression = Re2DotNode()
        elif '\\' == p[2][0]:
            under_star_expression = Re2EscapedCharacterNode(p[2])
        else:
            under_star_expression = Re2TermNode(p[2])
        p[0] = Re2ExpressionStarNode(p[1], under_star_expression)

    #TODO can remove last 2 cases
    #TODO second law can be reduced to
    #TODO expression -> expression star
    def p_brackets_group_star(self, p):
        """expression : BRACKETS_EXPRESSION STAR
                        | LEFT_PAREN expression RIGHT_PAREN STAR
                        | expression BRACKETS_EXPRESSION STAR
                        | expression LEFT_PAREN expression RIGHT_PAREN STAR"""
        under_star_expression = None
        if type(p[1]) is str and p[1][0] == '[':
            under_star_expression = Re2BracketsExpressionNode(p[1])
        elif type(p[1]) == str and p[1] == '(':
            under_star_expression = Re2GroupNode(p[2])

        if under_star_expression is not None:
            p[0] = Re2StarNode(under_star_expression)
            return

        if type(p[2]) is str and p[2][0] == '[':
            under_star_expression = Re2BracketsExpressionNode(p[2])
        else:
            under_star_expression = Re2GroupNode(p[3])
        p[0] = Re2ExpressionStarNode(p[1], under_star_expression)

    #TODO can remove last 2 cases
    def p_expression_term_dot_plus(self, p):
        """expression : DOT PLUS
                        | TERM PLUS
                        | ESCAPED_CHARACTER PLUS
                        | expression DOT PLUS
                        | expression TERM PLUS
                        | expression ESCAPED_CHARACTER PLUS"""
        if len(p) == 3:
            if '.' == p[1]:
                under_plus_expression = Re2DotNode()
            elif '\\' == p[1][0]:
                under_plus_expression = Re2EscapedCharacterNode(p[1])
            else:
                under_plus_expression = Re2TermNode(p[1])
            p[0] = Re2PlusNode(under_plus_expression)
            return

        if '.' == p[2]:
            under_plus_expression = Re2DotNode()
        elif '\\' == p[2][0]:
            under_plus_expression = Re2EscapedCharacterNode(p[2])
        else:
            under_plus_expression = Re2TermNode(p[2])
        p[0] = Re2ExpressionPlusNode(p[1], under_plus_expression)

    #TODO can remove last 2 cases
    def p_brackets_group_plus(self, p):
        """expression : BRACKETS_EXPRESSION PLUS
                        | LEFT_PAREN expression RIGHT_PAREN PLUS
                        | expression BRACKETS_EXPRESSION PLUS
                        | expression LEFT_PAREN expression RIGHT_PAREN PLUS"""
        under_plus_expression = None
        if type(p[1]) is str and p[1][0] == '[':
            under_plus_expression = Re2BracketsExpressionNode(p[1])
        elif type(p[1]) == str and p[1] == '(':
            under_plus_expression = Re2GroupNode(p[2])

        if under_plus_expression is not None:
            p[0] = Re2PlusNode(under_plus_expression)
            return

        if type(p[2]) is str and p[2][0] == '[':
            under_plus_expression = Re2BracketsExpressionNode(p[2])
        else:
            under_plus_expression = Re2GroupNode(p[3])
        p[0] = Re2ExpressionPlusNode(p[1], under_plus_expression)

    def p_caret(self, p):
        """expression : CARET """
        p[0] = Re2CaretNode()

    #TODO no need to put left recursion here. make it into
    # expression -> DOLLAR
    def p_dollar(self, p):
        """expression : expression DOLLAR"""
        p[0] = Ast([p[1], Re2DollarNode()])

    def p_expression_term_dot_repeat(self, p):
        """expression : DOT LEFT_CURLY NUMBER RIGHT_CURLY
                        | TERM LEFT_CURLY NUMBER RIGHT_CURLY
                        | ESCAPED_CHARACTER LEFT_CURLY NUMBER RIGHT_CURLY
                        | expression DOT LEFT_CURLY NUMBER RIGHT_CURLY
                        | expression TERM LEFT_CURLY NUMBER RIGHT_CURLY
                        | expression ESCAPED_CHARACTER LEFT_CURLY NUMBER RIGHT_CURLY"""
        if len(p) == 5:
            if '.' == p[1]:
                under_repeat_expression = Re2DotNode()
            elif '\\' == p[1][0]:
                under_repeat_expression = Re2EscapedCharacterNode(p[1])
            else:
                under_repeat_expression = Re2TermNode(p[1])
            p[0] = Re2RepeatNode(under_repeat_expression, p[3])
            return

        if '.' == p[2]:
            under_repeat_expression = Re2DotNode()
        elif '\\' == p[2][0]:
            under_repeat_expression = Re2EscapedCharacterNode(p[2])
        else:
            under_repeat_expression = Re2TermNode(p[2])
        p[0] = Ast([p[1], Re2RepeatNode(under_repeat_expression, p[4])])

    def p_brackets_group_repeat(self, p):
        """expression : BRACKETS_EXPRESSION LEFT_CURLY NUMBER RIGHT_CURLY
                        | LEFT_PAREN expression RIGHT_PAREN LEFT_CURLY NUMBER RIGHT_CURLY
                        | expression BRACKETS_EXPRESSION LEFT_CURLY NUMBER RIGHT_CURLY
                        | expression LEFT_PAREN expression RIGHT_PAREN LEFT_CURLY NUMBER RIGHT_CURLY"""
        under_repeat_expression = None
        range_index = None
        if type(p[1]) is str and p[1][0] == '[':
            range_index = 3
            under_repeat_expression = Re2BracketsExpressionNode(p[1])
        elif type(p[1]) == str and p[1] == '(':
            range_index = 4
            under_repeat_expression = Re2GroupNode(p[2])

        if under_repeat_expression  is not None:
            p[0] = Re2RepeatNode(under_repeat_expression, p[range_index])
            return

        if type(p[2]) is str and p[2][0] == '[':
            range_index = 4
            under_repeat_expression = Re2BracketsExpressionNode(p[2])
        else:
            range_index = 6
            under_repeat_expression = Re2GroupNode(p[3])
        p[0] = Ast([p[1], Re2RepeatNode(under_repeat_expression, p[range_index])])

    def p_expression_term_dot_repeat_range(self, p):
        """expression : DOT LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | TERM LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | ESCAPED_CHARACTER LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | expression DOT LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | expression TERM LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | expression ESCAPED_CHARACTER LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY"""
        if len(p) == 7:
            if '.' == p[1]:
                under_repeat_expression = Re2DotNode()
            elif '\\' == p[1][0]:
                under_repeat_expression = Re2EscapedCharacterNode(p[1])
            else:
                under_repeat_expression = Re2TermNode(p[1])
            p[0] = Re2RepeatRangeNode(under_repeat_expression, p[3], p[5])
            return

        if '.' == p[2]:
            under_repeat_expression = Re2DotNode()
        elif '\\' == p[2][0]:
            under_repeat_expression = Re2EscapedCharacterNode(p[2])
        else:
            under_repeat_expression = Re2TermNode(p[2])
        p[0] = Ast([p[1], Re2RepeatRangeNode(under_repeat_expression, p[4], p[6])])

    def p_brackets_group_repeat_range(self, p):
        """expression : BRACKETS_EXPRESSION LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | LEFT_PAREN expression RIGHT_PAREN LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | expression BRACKETS_EXPRESSION LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY
                        | expression LEFT_PAREN expression RIGHT_PAREN LEFT_CURLY NUMBER COMMA NUMBER RIGHT_CURLY"""
        under_repeat_expression = None
        range_index = None
        if type(p[1]) is str and p[1][0] == '[':
            range_index = 3
            under_repeat_expression = Re2BracketsExpressionNode(p[1])
        elif type(p[1]) == str and p[1] == '(':
            range_index = 4
            under_repeat_expression = Re2GroupNode(p[2])

        if under_repeat_expression  is not None:
            p[0] = Re2RepeatRangeNode(under_repeat_expression, p[range_index], p[2 + range_index])
            return

        if type(p[2]) is str and p[2][0] == '[':
            range_index = 4
            under_repeat_expression = Re2BracketsExpressionNode(p[2])
        else:
            range_index = 6
            under_repeat_expression = Re2GroupNode(p[3])
        p[0] = Ast([p[1], Re2RepeatRangeNode(under_repeat_expression, p[range_index], p[2 + range_index])])

    #TODO like the dollar case just make it into
    # expression -> TERM
    def p_expression_term(self, p):
        """expression : expression TERM"""
        p[0] = Re2ExpressionConcatNode(p[1], p[2])

    def p_expression_NUMBER(self, p):
        """expression : expression NUMBER"""
        num = str(p[2])
        term_nodes = [Re2TermNode(c) for c in num]
        term_nodes.insert(0, p[1])
        p[0] = Ast(term_nodes)

    def p_NUMBER(self, p):
        """expression : NUMBER"""
        num = str(p[1])
        term_nodes = [Re2TermNode(c) for c in num]
        p[0] = Ast(term_nodes)

    #TODO like the dollar case
    def p_numeric_group(self, p):
        """expression : expression NUMERIC_GROUP"""
        # Find and extract the group number from the second operator
        group_number = int(re.search('(\d+)$', p[2]).group(0))
        p[0] = Re2NumericGroupNode(p[1], group_number)

    #TODO like the dollar case
    def p_expression_escaped_character(self, p):
        """expression : expression ESCAPED_CHARACTER"""
        p[0] = Ast([p[1], Re2EscapedCharacterNode(p[2])])

    def p_error(self, p):
        print('error %s' % p)

    def parse(self, expression, debug=False):
        lexer = lex.lex(optimize=True, module=self)

        if debug:
            lexer.input(expression)
            # Tokenize
            while True:
                tok = lexer.token()
                if not tok:
                    break  # No more input
                print(tok)

        y = yacc.yacc(optimize=True, module=self, debug=debug)
        ast = y.parse(expression)
        return (ast, self.groups, self.named_groups)

    @staticmethod
    def convert_re2_tree_to_basic_syntax(tree,
                                         numeric_groups,
                                         named_groups,
                                         convert_caret_and_dollar=False):
        if tree is None:
            return BasicAstNode()
        basic_tree = Re2Parser._convert_re2_tree_to_basic_syntax(
            tree, numeric_groups, named_groups)
        # convert caret '^' on the leftmost node to .*
        found_caret = False
        leftmost_node = basic_tree
        while leftmost_node.sons:
            if type(leftmost_node.sons[0]) is Re2CaretNode:
                leftmost_node.sons[0] = EmptyNode()
                found_caret = True
                break
            leftmost_node = leftmost_node.sons[0]
        if convert_caret_and_dollar and not found_caret:
            basic_tree = BasicAstNode(
                [BasicStarNode(BasicDotNode()), basic_tree])

        # convert dollar '$' on the rightmost node to .*
        found_dollar = False
        rightmost_node = basic_tree
        while rightmost_node.sons:
            if type(rightmost_node.sons[-1]) is Re2DollarNode:
                rightmost_node.sons[-1] = EmptyNode()
                found_dollar = True
                break
            rightmost_node = rightmost_node.sons[-1]

        if convert_caret_and_dollar and not found_dollar:
            basic_tree = BasicAstNode(
                [basic_tree, BasicStarNode(BasicDotNode())])
        return basic_tree

    @staticmethod
    def _convert_re2_tree_to_basic_syntax(tree, numeric_groups, named_groups):
        son_trees = [
            Re2Parser._convert_re2_tree_to_basic_syntax(
                son, numeric_groups, named_groups) for son in tree.sons
        ]
        if type(tree) is Re2TermNode:
            return BasicTermNode(tree.term)
        elif type(tree) is Re2ExpressionConcatNode:
            return BasicExpressionConcatNode(son_trees[0], tree.term)
        elif type(tree) is Re2EscapedCharacterNode:
            return BasicEscapedCharacterNode(tree.escaped_char)
        elif type(tree) is Re2GroupNode:
            return BasicGroupNode(son_trees[0])
        elif type(tree) is Re2OptionalNode:
            return BasicGroupNode(BasicOrNode(son_trees[0], BasicAstNode()))
        elif type(tree) is Re2ExpressionGroupNode:
            return BasicExpressionGroupNode(son_trees[0], son_trees[1])
        elif type(tree) is Re2NumericGroupNode:
            return BasicExpressionGroupNode(
                son_trees[0],
                Re2Parser._convert_re2_tree_to_basic_syntax(
                    numeric_groups[tree.group_number - 1], None, None))
        elif type(tree) is Re2DotNode:
            return BasicDotNode()
        elif type(tree) is Re2CaretNode:
            return Re2CaretNode()
        elif type(tree) is Re2DollarNode:
            return Re2DollarNode()
        elif type(tree) is Re2OrNode:
            return BasicOrNode(son_trees[0], son_trees[1])
        elif type(tree) is Re2StarNode:
            return BasicStarNode(son_trees[0])
        elif type(tree) is Re2ExpressionStarNode:
            return BasicAstNode([son_trees[0], BasicStarNode(son_trees[1])])
        elif type(tree) is Re2ExpressionPlusNode:
            return BasicAstNode(
                [son_trees[0], son_trees[1],
                 BasicStarNode(son_trees[1])])
        elif type(tree) is Re2ExpressionOptionalNode:
            return BasicOrNode(son_trees[0],
                               BasicAstNode([son_trees[0], son_trees[1]]))
        elif type(tree) is Re2BracketsExpressionNode:
            possible_values = Re2Parser.get_brackets_values(
                tree.to_re2_string())
            if 1 == len(possible_values):
                return BasicTermNode(possible_values[0])
            possible_values = [BasicTermNode(x) for x in possible_values]
            return functools.reduce(lambda t1, t2: BasicOrNode(t1, t2),
                                    possible_values)
        elif type(tree) is Re2ExpressionBracketsExpressionNode:
            possible_values = Re2Parser.get_brackets_values(
                tree.brackets_expression)
            if 1 == len(possible_values):
                return BasicExpressionConcatNode(son_trees[0],
                                                 possible_values[0])

            possible_values = [BasicTermNode(x) for x in possible_values]
            return BasicAstNode([
                Re2Parser.group_tree_if_needed(son_trees[0]),
                BasicGroupNode(
                    functools.reduce(lambda t1, t2: BasicOrNode(t1, t2),
                                     possible_values))
            ])
        elif type(tree) is Re2RepeatRangeNode:
            possible_repeat_values = []
            for x in range(tree.range_low, 1 + tree.range_high):
                possible_repeat_values.append(
                    BasicAstNode(Re2Parser.create_range_list(son_trees[0], x)))
            if 1 == len(possible_repeat_values):
                return possible_repeat_values[0]
            else:
                return functools.reduce(lambda t1, t2: BasicOrNode(t1, t2),
                                        possible_repeat_values)
        elif type(tree) is Re2PlusNode:
            return BasicAstNode(
                sons=[BasicAstNode(son_trees[0]),
                      BasicStarNode(son_trees[0])])
        elif type(tree) is Re2RepeatNode:
            repeat_list = Re2Parser.create_range_list(son_trees[0],
                                                      tree.number)
            return BasicAstNode(repeat_list)
        elif type(tree) is Ast:
            return BasicAstNode(son_trees)

    @staticmethod
    def group_tree_if_needed(tree):
        if tree.sons != [] and type(tree) is not Re2GroupNode:
            return BasicGroupNode(tree)

        return tree

    @staticmethod
    def create_range_list(node, number):
        if len(node.sons) > 0 and type(node) is not BasicGroupNode:
            node = BasicGroupNode(node)
        repeat_list = []
        for x in range(number):
            repeat_list.append(node)
        return repeat_list

    @staticmethod
    def get_brackets_values(pattern):
        replace_perl_regex_dict = {
            '[:alnum:]': 'a-zA-Z0-9',
            '[:alpha:]': 'a-zA-Z',
            '[:ascii:]': '\\x00-\\x7f',
            '[:blank:]': ' \\t',
            '[:cntrl:]': '\\x00-\\x1f\\x7f',
            '[:digit:]': '0-9',
            '[:graph:]': '\\x21-\\x7e',
            '[:lower:]': 'a-z',
            '[:print:]': '\\x20-\\x7e',
            '[:punct:]': '!"\\#$%&\'()*+,\\-./:;<=>?@\\[\\\\\\]^_`{|}~',
            '[:space:]': ' \\t\\r\\n\\v\\f',
            '[:upper:]': 'A-Z',
            '[:word:]': 'A-Za-z0-9_',
            '[:xdigit:]': 'A-Fa-f0-9'
        }

        for perl_pattern in replace_perl_regex_dict:
            pattern = pattern.replace(perl_pattern, replace_perl_regex_dict[perl_pattern])
        matches = []
        sre_parsed_data = sre_parse.parse(pattern).data
        if type(sre_parsed_data[0][1]) is int:
            return [chr(sre_parsed_data[0][1]).encode('unicode_escape').decode("utf-8")]
        for m in sre_parsed_data[0][1]:
            if type(m) is int:
                return [chr(m).encode('unicode_escape').decode("utf-8")]
            if sre_parse.LITERAL == m[0]:
                matches.append(chr(m[1]).encode('unicode_escape').decode("utf-8"))
            elif sre_parse.RANGE == m[0]:
                range_chars = [chr(x).encode('unicode_escape').decode("utf-8") for x in range(m[1][0], 1 + m[1][1])]
                matches += range_chars
        return matches

    def parse_file(self, path):
        # iterate over the lines in in the file ant try to convert each line to basic syntax
        basic_strings = []
        with open(path, 'r') as f:
            for line in f:
                try:
                    tree, groups, named_groups = self.parse(line)
                    basic_tree = self.convert_re2_tree_to_basic_syntax(
                        tree, groups, named_groups)
                    basic_strings.append(basic_tree.to_basic_string())
                except Exception as e:
                    print(
                        'failed to convert regex expression %s, exception: %s'
                        % (line, e))

        return basic_strings


def main():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse(
        '[a-b][c-d]',
        debug=True,
    )
    print(
        parser.convert_re2_tree_to_basic_syntax(
            tree, groups, named_groups).to_basic_string())


if '__main__' == __name__:
    main()
