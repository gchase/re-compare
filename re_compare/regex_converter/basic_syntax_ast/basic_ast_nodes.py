from ..generic_ast import Ast


class BasicAstNode(Ast):
    def __init__(self, sons=None):
        super(BasicAstNode, self).__init__(sons)

    def to_basic_string(self):
        return ''.join(s.to_basic_string() for s in self.sons)


class BasicEscapedCharacterNode(Ast):
    def __init__(self, escaped_char):
        super(BasicEscapedCharacterNode, self).__init__()
        self.escaped_char = escaped_char

    def to_re2_string(self):
        return '%s' % self.escaped_char

    def to_basic_string(self):
        return '%s' % self.escaped_char


class BasicTermNode(BasicAstNode):
    def __init__(self, term):
        super(BasicTermNode, self).__init__()
        self.term = term

    def to_re2_string(self):
        return self.term

    def to_basic_string(self):
        return self.term


class EmptyNode(BasicAstNode):
    def __init__(self):
        super(EmptyNode, self).__init__()

    def to_re2_string(self):
        return ''

    def to_basic_string(self):
        return ''


class BasicDotNode(BasicAstNode):
    def __init__(self):
        super(BasicAstNode, self).__init__()

    def to_re2_string(self):
        return '.'

    def to_basic_string(self):
        return '.'


class BasicExpressionConcatNode(BasicAstNode):
    def __init__(self, son, term):
        super(BasicExpressionConcatNode, self).__init__()
        self.sons = [son]
        self.term = term

    def to_re2_string(self):
        return '%s%s' % (self.sons[0].to_re2_string(), self.term)

    def to_basic_string(self):
        return '%s%s' % (self.sons[0].to_basic_string(), self.term)


class BasicExpressionGroupNode(Ast):
    def __init__(self, expression_ast, group_ast):
        super(BasicExpressionGroupNode, self).__init__()
        self.sons = [expression_ast, group_ast]

    def to_re2_string(self):
        return '%s(%s)' % (self.sons[0].to_re2_string(),
                           self.sons[1].to_re2_string())

    def to_basic_string(self):
        return self.to_re2_string()


class BasicOrNode(BasicAstNode):
    def __init__(self, left_son, right_son):
        super(BasicOrNode, self).__init__()
        self.sons = [left_son, right_son]

    def to_re2_string(self):
        return '%s|%s' % (self.sons[0].to_re2_string(),
                          self.sons[1].to_re2_string())

    def to_basic_string(self):
        return self.to_re2_string()


class BasicGroupNode(BasicAstNode):
    def __init__(self, left_son):
        super(BasicGroupNode, self).__init__()
        self.sons = [left_son]

    def to_re2_string(self):
        return '(%s)' % self.sons[0].to_re2_string()

    def to_basic_string(self):
        return self.to_re2_string()


class BasicStarNode(BasicAstNode):
    def __init__(self, left_son):
        super(BasicStarNode, self).__init__()
        self.sons = [left_son]

    def to_re2_string(self):
        return '%s*' % self.sons[0].to_re2_string()

    def to_basic_string(self):
        return self.to_re2_string()
