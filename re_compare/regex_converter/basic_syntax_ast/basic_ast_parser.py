import ply.lex as lex
import ply.yacc as yacc

from basic_syntax_ast.basic_ast_nodes import *


class BasicAstParser(object):
    def __init__(self):
        super(object, self)

    tokens = (
        'TERM',
        'OR',
        'STAR',
        'DOT',
        'LEFT_PAREN',
        'RIGHT_PAREN',
    )

    t_TERM = r'\w'
    t_OR = r'\|'
    t_STAR = r'\*'
    t_DOT = r'\.'
    t_LEFT_PAREN = r'\('
    t_RIGHT_PAREN = r'\)'

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    precedence = (
        ('left', 'OR'),
        ('right', 'STAR', ),
    )

    def p_expression_group(self, p):
        """
       expression : expression LEFT_PAREN expression RIGHT_PAREN
       """
        p[0] = BasicExpressionGroupNode(p[1], p[3])


    def p_expression_or(self, p):
        """
        expression : expression OR expression
        """
        p[0] = BasicOrNode(p[1], p[3])

    def p_term(self, p):
        """expression : TERM"""
        p[0] = BasicTermNode(p[1])

    def p_star(self, p):
        """expression : expression STAR"""
        p[0] = BasicStarNode(p[1])

    def p_dot(self, p):
        """expression : DOT"""
        p[0] = BasicDotNode()

    def p_expression_dot(self, p):
        """expression : expression DOT"""
        p[0] = BasicExpressionConcatNode(p[1], p[2])

    def p_expression_term(self, p):
        """expression : expression TERM"""
        p[0] = BasicExpressionConcatNode(p[1], p[2])

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
        return ast.to_re2_string()


def main():
    parser = BasicAstParser()
    print(parser.parse('^a|b$', debug=True))


if '__main__' == __name__:
    main()
