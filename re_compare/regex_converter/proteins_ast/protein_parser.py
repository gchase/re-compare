from ply import lex, yacc

from ..re2_ast.re2_ast_nodes import *


class ProteinParser(object):
    def __init__(self):
        super(object, self)

    AMINO_ACIDS = 'ACDEFGHIKLMNPQRSTVWY'
    tokens = ('AMINO_ACID', 'ANY', 'HYPHEN', 'NTERMINAL', 'CTERMINAL',
              'BRACKETS_EXPRESSION', 'CURLY_EXPRESSION', 'COMMA', 'NUMBER',
              'LEFT_PAREN', 'RIGHT_PAREN', 'STAR')

    t_AMINO_ACID = r'[%s]' % AMINO_ACIDS
    t_ANY = r'x'
    t_HYPHEN = r'\-'
    t_BRACKETS_EXPRESSION = r'\[([A-Z<>])+\]'
    t_CURLY_EXPRESSION = r'\{([A-Z<>])+\}'
    t_NTERMINAL = r'<'
    t_CTERMINAL = r'>'
    t_COMMA = r','
    t_LEFT_PAREN = r'\('
    t_RIGHT_PAREN = r'\)'
    t_STAR = r'\*'

    precedence = (('left', 'NTERMINAL', 'HYPHEN'), )

    def t_NUMBER(self, t):
        r"""\d+"""
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def p_amino_acid(self, p):
        """expression : AMINO_ACID"""
        p[0] = Re2TermNode(p[1])

    def p_amino_any(self, p):
        """expression : ANY"""
        p[0] = Re2DotNode()

    def p_star_expression(self, p):
        """expression : expression STAR """
        p[0] = Re2StarNode(p[1])

    def p_C_teminal_expression(self, p):
        """expression : expression CTERMINAL"""
        p[0] = Ast([p[1], Re2DollarNode()])

    def p_N_teminal_expression(self, p):
        """expression : NTERMINAL expression """
        p[0] = Ast([Re2CaretNode(), p[2]])

    def p_brackets_expression(self, p):
        """expression : BRACKETS_EXPRESSION"""
        p[0] = Re2BracketsExpressionNode(p[1].replace('>', '$').replace(
            '<', '^'))

    def p_expression_brackets_expression(self, p):
        """expression : expression BRACKETS_EXPRESSION"""
        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2BracketsExpressionNode(
                                           p[2].replace('>', '$').replace(
                                               '<', '^')).to_re2_string())

    def p_expression_hyphen_brackets_expression(self, p):
        """expression : expression HYPHEN BRACKETS_EXPRESSION"""
        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2BracketsExpressionNode(
                                           p[3].replace('>', '$').replace(
                                               '<', '^')).to_re2_string())

    def build_brackets_from_curly(self, curly_expression):
        unique_characters = set(curly_expression[1:-1])
        complement_acids = []
        for a in self.AMINO_ACIDS:
            if a not in unique_characters:
                complement_acids.append(a)
        if '<' in unique_characters:
            complement_acids.insert(0, '<')
        if '>' in unique_characters:
            complement_acids.append('>')

        return '[%s]' % ''.join(complement_acids)

    def p_curly_expression(self, p):
        """expression : CURLY_EXPRESSION"""

        p[0] = Re2BracketsExpressionNode(
            self.build_brackets_from_curly(p[1]).replace('>', '$').replace(
                '<', '^'))

    def p_expression_curly_expression(self, p):
        """expression : expression CURLY_EXPRESSION"""
        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2BracketsExpressionNode(
                                           self.build_brackets_from_curly(
                                               p[2]).replace('>', '$').replace(
                                                   '<', '^')).to_re2_string())

    def p_expression_hyphen_curly_expression(self, p):
        """expression : expression HYPHEN CURLY_EXPRESSION"""
        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2BracketsExpressionNode(
                                           self.build_brackets_from_curly(
                                               p[3]).replace('>', '$').replace(
                                                   '<', '^')).to_re2_string())

    def p_repetition(self, p):
        """expression : ANY LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2RepeatNode(Re2DotNode(), p[3])

    def p_expression_repetition(self, p):
        """expression : expression ANY LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2RepeatNode(Re2DotNode(),
                                                     p[4]).to_re2_string())

    def p_expression_hyphen_repetition(self, p):
        """expression : expression HYPHEN ANY LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2RepeatNode(Re2DotNode(),
                                                     p[5]).to_re2_string())

    def p_brackets_repetition(self, p):
        """expression : BRACKETS_EXPRESSION LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2RepeatNode(
            Re2BracketsExpressionNode(p[1].replace('>', '$').replace(
                '<', '^')), p[3])

    def p_expression_brackets_repetition(self, p):
        """expression : expression BRACKETS_EXPRESSION LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Ast([
            p[1],
            Re2RepeatNode(
                Re2BracketsExpressionNode(p[2].replace('>', '$').replace(
                    '<', '^')), p[4])
        ])

    def p_expression_hyphen_brackets_repetition(self, p):
        """expression : expression HYPHEN BRACKETS_EXPRESSION LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Ast([
            p[1],
            Re2RepeatNode(
                Re2BracketsExpressionNode(p[3].replace('>', '$').replace(
                    '<', '^')), p[5])
        ])

    def p_curly_repetition(self, p):
        """expression : CURLY_EXPRESSION LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2RepeatNode(
            Re2BracketsExpressionNode(
                self.build_brackets_from_curly(p[1]).replace('>', '$').replace(
                    '<', '^')), p[3])

    def p_expression_curly_repetition(self, p):
        """expression : expression CURLY_EXPRESSION LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Ast([
            p[1],
            Re2RepeatNode(
                Re2BracketsExpressionNode(
                    self.build_brackets_from_curly(p[2]).replace(
                        '>', '$').replace('<', '^')), p[4])
        ])

    def p_expression_hyphen_curly_repetition(self, p):
        """expression : expression HYPHEN CURLY_EXPRESSION LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Ast([
            p[1],
            Re2RepeatNode(
                Re2BracketsExpressionNode(
                    self.build_brackets_from_curly(p[3]).replace(
                        '>', '$').replace('<', '^')), p[5])
        ])

    def p_repetition_amino_acid(self, p):
        """expression : AMINO_ACID LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2RepeatNode(Re2TermNode(p[1]), p[3])

    def p_expression_repetition_amino_acid(self, p):
        """expression : expression AMINO_ACID LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2RepeatNode(Re2TermNode(p[2]),
                                                     p[4]).to_re2_string())

    def p_expression_hyphen_repetition_amino_acid(self, p):
        """expression : expression HYPHEN AMINO_ACID LEFT_PAREN NUMBER RIGHT_PAREN"""

        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2RepeatNode(Re2TermNode(p[3]),
                                                     p[5]).to_re2_string())

    def p_any_range(self, p):
        """expression : ANY LEFT_PAREN NUMBER COMMA NUMBER RIGHT_PAREN"""

        p[0] = Re2RepeatRangeNode(Re2DotNode(), p[3], p[5])

    def p_expression_any_range(self, p):
        """expression : expression ANY LEFT_PAREN NUMBER COMMA NUMBER RIGHT_PAREN"""

        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2RepeatRangeNode(
                                           Re2DotNode(), p[4],
                                           p[6]).to_re2_string())

    def p_expression_hyphen_any_range(self, p):
        """expression : expression HYPHEN ANY LEFT_PAREN NUMBER COMMA NUMBER RIGHT_PAREN"""

        p[0] = Re2ExpressionConcatNode(p[1],
                                       Re2RepeatRangeNode(
                                           Re2DotNode(), p[5],
                                           p[7]).to_re2_string())

    def p_expression_amino_acid(self, p):
        """expression : expression AMINO_ACID
                      | expression ANY
                      | expression HYPHEN AMINO_ACID
                      | expression HYPHEN ANY"""

        amino_acid = p[2] if p[2] is not '-' else p[3]
        if 'x' == amino_acid:
            amino_acid = '.'
        p[0] = Re2ExpressionConcatNode(p[1], amino_acid)

    def p_error(self, p):
        print('yacc error: %s' % p)

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
        return ast


def main():
    parser = ProteinParser()
    print(parser.parse('<{C}*>', debug=True))


if '__main__' == __name__:
    main()
