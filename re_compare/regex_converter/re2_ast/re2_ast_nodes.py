from ..generic_ast import Ast


class Re2TermNode(Ast):
    def __init__(self, term):
        super(Re2TermNode, self).__init__()
        self.term = term

    def to_re2_string(self):
        return self.term


class Re2DotNode(Ast):
    def __init__(self):
        super(Re2DotNode, self).__init__()

    def to_re2_string(self):
        return '.'


class Re2ExpressionConcatNode(Ast):
    def __init__(self, son, term):
        super(Re2ExpressionConcatNode, self).__init__()
        self.sons = [son]
        self.term = term

    def to_re2_string(self):
        return '%s%s' % (self.sons[0].to_re2_string(), self.term)


class Re2BracketsExpressionNode(Ast):
    def __init__(self, brackets_expression):
        super(Re2BracketsExpressionNode, self).__init__()
        self.brackets_expression = brackets_expression

    def to_re2_string(self):
        return self.brackets_expression


class Re2ExpressionBracketsExpressionNode(Ast):
    def __init__(self, son, brackets_expression):
        super(Re2ExpressionBracketsExpressionNode, self).__init__()
        self.sons = [son]
        self.brackets_expression = brackets_expression

    def to_re2_string(self):
        return '%s%s' % (self.sons[0].to_re2_string(),
                         self.brackets_expression)


class Re2OrNode(Ast):
    def __init__(self, left_son, right_son):
        super(Re2OrNode, self).__init__()
        self.sons = [left_son, right_son]

    def to_re2_string(self):
        return '%s|%s' % (self.sons[0].to_re2_string(),
                          self.sons[1].to_re2_string())


class Re2OptionalNode(Ast):
    def __init__(self, left_son):
        super(Re2OptionalNode, self).__init__()
        self.sons = [left_son]

    def to_re2_string(self):
        return '%s?' % self.sons[0].to_re2_string()


class Re2ExpressionOptionalNode(Ast):
    def __init__(self, expression_son, optional_son):
        super(Re2ExpressionOptionalNode, self).__init__()
        self.sons = [expression_son, optional_son]

    def to_re2_string(self):
        return '%s(%s)?' % (self.sons[0].to_re2_string(),
                            self.sons[1].to_re2_string())


class Re2StarNode(Ast):
    def __init__(self, left_son):
        super(Re2StarNode, self).__init__()
        self.sons = [left_son]

    def to_re2_string(self):
        return '%s*' % self.sons[0].to_re2_string()


class Re2ExpressionStarNode(Ast):
    def __init__(self, expression_son, star_son):
        super(Re2ExpressionStarNode, self).__init__()
        self.sons = [expression_son, star_son]

    def to_re2_string(self):
        return '%s(%s*)' % (self.sons[0].to_re2_string(),
                            self.sons[1].to_re2_string())


class Re2PlusNode(Ast):
    def __init__(self, left_son):
        super(Re2PlusNode, self).__init__()
        self.sons = [left_son]

    def to_re2_string(self):
        return '%s+' % self.sons[0].to_re2_string()


class Re2ExpressionPlusNode(Ast):
    def __init__(self, expression_son, plus_son):
        super(Re2ExpressionPlusNode, self).__init__()
        self.sons = [expression_son, plus_son]

    def to_re2_string(self):
        return '%s(%s+)' % (self.sons[0].to_re2_string(),
                            self.sons[1].to_re2_string())


class Re2GroupNode(Ast):
    def __init__(self, left_son):
        super(Re2GroupNode, self).__init__()
        self.sons = [left_son]

    def to_re2_string(self):
        return '(%s)' % self.sons[0].to_re2_string()


class Re2CaretNode(Ast):
    def __init__(self):
        super(Re2CaretNode, self).__init__()

    def to_re2_string(self):
        return '^'


class Re2DollarNode(Ast):
    def __init__(self):
        super(Re2DollarNode, self).__init__()

    def to_re2_string(self):
        return '$'


class Re2ExpressionGroupNode(Ast):
    def __init__(self, expression_ast, group_ast):
        super(Re2ExpressionGroupNode, self).__init__()
        self.sons = [expression_ast, group_ast]

    def to_re2_string(self):
        return '%s(%s)' % (self.sons[0].to_re2_string(),
                           self.sons[1].to_re2_string())


class Re2NumericGroupNode(Ast):
    def __init__(self, left_son, group_number):
        super(Re2NumericGroupNode, self).__init__()
        self.sons = [left_son]
        self.group_number = group_number

    def to_re2_string(self):
        return '%s\\%s' % (self.sons[0].to_re2_string(), self.group_number)


class Re2EscapedCharacterNode(Ast):
    def __init__(self, escaped_char):
        super(Re2EscapedCharacterNode, self).__init__()
        self.escaped_char = escaped_char

    def to_re2_string(self):
        return '%s' % self.escaped_char


class Re2RepeatNode(Ast):
    def __init__(self, left_son, number):
        super(Re2RepeatNode, self).__init__()
        self.sons = [left_son]
        self.number = number

    def to_re2_string(self):
        return '%s{%d}' % (self.sons[0].to_re2_string(), self.number)


class Re2RepeatRangeNode(Ast):
    def __init__(self, left_son, range_low, range_high):
        super(Re2RepeatRangeNode, self).__init__()
        self.sons = [left_son]
        self.range_low = range_low
        self.range_high = range_high

    def to_re2_string(self):
        return '%s{%d,%d}' % (self.sons[0].to_re2_string(), self.range_low,
                              self.range_high)
