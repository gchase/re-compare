from re_compare.regex_converter.re2_ast.re2_parser import Re2Parser


def test_term_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a')
    assert 'a' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_2term_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('ab')
    assert 'ab' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_2term_or_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a|b')
    assert 'a|b' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_dot_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('.')
    assert '.' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_star_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a*')
    assert 'a*' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_term_star_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('ab*')
    assert 'ab*' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_term_optional_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('ab?')
    assert 'a|ab' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_brackets_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[a-c]')
    assert 'a|b|c' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_brackets_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a[a-c]')
    assert 'a(a|b|c)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_group_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('(abc)')
    assert '(abc)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_group_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('x(abc)')
    assert 'x(abc)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_group_with_reference_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('(abc)\\1')
    assert '(abc)(abc)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_group_with_two_references_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('(abc)\\1\\1')
    assert '(abc)(abc)(abc)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_multiple_group_references_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('(abc)(def)\\1\\2')
    assert '(abc)(def)(abc)(def)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_complex_group_with_references_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('([abc])\\1')
    assert '(a|b|c)(a|b|c)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_range_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a{3}')
    assert 'aaa' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_repeat_range_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a{3,5}')
    assert 'aaa|aaaa|aaaaa' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_plus_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a+')
    assert 'aa*' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_plus_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('ab+')
    assert 'abb*' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_empty_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('')
    assert '' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_range_in_group_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('(a{3})\\1')
    assert '(aaa)(aaa)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_or_with_brackets_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a|[cd]')
    assert 'a|c|d' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_two_terms_plus_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('b(aa)+')
    assert 'b(aa)(aa)*' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_two_stars_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('(a*)*')
    assert '(a*)*' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_two_brackets_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[a-b][c-d]')
    assert '(a|b)(c|d)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()


def test_term_optional_term_conversion():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a?b')
    assert '(a|)b' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_brackets_range():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[ab]{1,2}')
    assert '(a|b)|(a|b)(a|b)' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_single_char_escaping():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a\\n')
    assert 'a\\n' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_single_char_escaping_in_brackets():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[a\\t]')
    assert 'a|\\t' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_hex_escaping_in_brackets():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[a\\x01]')
    assert 'a|\\x01' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_hex_escaping_in_brackets():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a\\x01')
    assert 'a\\x01' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_hex_escaping_range():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a\\x01{2}')
    assert 'a\\x01\\x01' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_caret_ignore():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('^a')
    assert 'a' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_dollar_ignore():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('a$')
    assert 'a' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_special_chars():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('!@#&=')
    assert '!@#&=' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_special_chars_in_brackets():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[!@#&=]')
    assert '!|@|#|&|=' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_number():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('123')
    assert '123' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_number_in_brackets():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('[123]')
    assert '1|2|3' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_expression_number():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('aaa123')
    assert 'aaa123' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()

def test_multiple_escaped_hex():
    parser = Re2Parser()
    tree, groups, named_groups = parser.parse('\\x01\\x02')
    assert '\\x01\\x02' == parser.convert_re2_tree_to_basic_syntax(
        tree, groups, named_groups).to_basic_string()
