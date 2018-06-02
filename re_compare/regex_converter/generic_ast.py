

class Ast(object):

    def __init__(self, sons=None):
        if sons is None:
            sons = []
        if type(sons) is not list:
            self.sons = [sons]
        else:
            self.sons = sons

    def to_re2_string(self):
        return ''.join(s.to_re2_string() for s in self.sons)

