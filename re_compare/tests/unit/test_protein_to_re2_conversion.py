from re_compare.regex_converter.proteins_ast.protein_parser import ProteinParser


def test_single_amino_acid():
    parser = ProteinParser()
    tree = parser.parse('C')
    assert 'C' == tree.to_re2_string()


def test_two_amino_acids():
    parser = ProteinParser()
    tree = parser.parse('CC')
    assert 'CC' == tree.to_re2_string()


def test_any_acid():
    parser = ProteinParser()
    tree = parser.parse('x')
    assert '.' == tree.to_re2_string()


def test_acid_any_acid():
    parser = ProteinParser()
    tree = parser.parse('Cx')
    assert 'C.' == tree.to_re2_string()


def test_repeat_acid():
    parser = ProteinParser()
    tree = parser.parse('C(3)')
    assert 'C{3}' == tree.to_re2_string()


def test_repeat_any():
    parser = ProteinParser()
    tree = parser.parse('x(3)')
    assert '.{3}' == tree.to_re2_string()


def test_acid_repeat_any():
    parser = ProteinParser()
    tree = parser.parse('Cx(3)')
    assert 'C.{3}' == tree.to_re2_string()


def test_repeat_range_any():
    parser = ProteinParser()
    tree = parser.parse('x(1,3)')
    assert '.{1,3}' == tree.to_re2_string()


def test_brackets():
    parser = ProteinParser()
    tree = parser.parse('[ALT]')
    assert '[ALT]' == tree.to_re2_string()


def test_hyphen():
    parser = ProteinParser()
    tree = parser.parse('A-A-A')
    assert 'AAA' == tree.to_re2_string()


def test_acid_brackets():
    parser = ProteinParser()
    tree = parser.parse('C[ALT]')
    assert 'C[ALT]' == tree.to_re2_string()


def test_acid_hyphen_brackets():
    parser = ProteinParser()
    tree = parser.parse('C-[ALT]')
    assert 'C[ALT]' == tree.to_re2_string()


def test_nterminal_acid():
    parser = ProteinParser()
    tree = parser.parse('<C')
    assert '^C' == tree.to_re2_string()


def test_acid_cterminal():
    parser = ProteinParser()
    tree = parser.parse('C>')
    assert 'C$' == tree.to_re2_string()


def test_curly():
    parser = ProteinParser()
    tree = parser.parse('{C}')
    assert '[ADEFGHIKLMNPQRSTVWY]' == tree.to_re2_string()


def test_curly_complex():
    parser = ProteinParser()
    tree = parser.parse('{ACDEF}')
    assert '[GHIKLMNPQRSTVWY]' == tree.to_re2_string()


def test_not_containing_c():
    parser = ProteinParser()
    tree = parser.parse('<{C}*>')
    assert '^[ADEFGHIKLMNPQRSTVWY]*$' == tree.to_re2_string()


def test_brackets_repetition():
    parser = ProteinParser()
    tree = parser.parse('[AC](2)')
    assert '[AC]{2}' == tree.to_re2_string()


def test_curly_repetition():
    parser = ProteinParser()
    tree = parser.parse('{AC}(2)')
    assert '[DEFGHIKLMNPQRSTVWY]{2}' == tree.to_re2_string()
