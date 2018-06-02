import re
import random

# use case
#x = generate_random_regex(alphabet, operations, max_depth, min_depth, oper_percent)


# these are probably too premisive
operations = ["%s%s", "%s|%s", "%s?", "%s+", "%s*", "(%s)"]
alphabet = ["A", "C", "G", "T", "."]

#operations = ["%s%s", "(%s)+"]
#alphabet = ["A", "C", "G", "T"]


#recursivly generates a regex over alphabet using operations whose tree has the property that every branch is between min depth and max depth
# Params:   alphabet - a list of strings signifying the atoms of the regex
#           operations - a list of strings signifying the operations possible on the atoms, %s mean an inpu tof said operation
#           max_depth - maximum depth of a branch in the regex formula tree
#           min depth - minimal depth
#           oper_percent - percentage of times an operation will be chosen when it is possible to choose either an operation or a letter from the alphabet
#           recursive_call - the recursive call that generates the subtree, will be the same function by default
#           key, key for recursive calls
# returns:  a tree in the form of recursive lists which when collapsed will be the  regex
def generate_random_regex_aux(alphabet,
                              operations,
                              max_depth,
                              min_depth,
                              oper_percent,
                              recursive_call,
                              key=None):

    if (max_depth < min_depth) or (max_depth < 0) or (min_depth < 0):
        raise ValueError("min is bigger then max")

    # whether we generate an atom or a subtree
    atom_flag = True

    if max_depth == 0:
        atom_flag = True
    elif min_depth > 0:
        atom_flag = False
    elif max_depth > 0 and min_depth == 0:
        # false with probability oper_percent
        atom_flag = (random.uniform(0, 1) > (float(oper_percent) / 100))
    else:  # shouldnt get here
        raise ValueError("sanity check failed, YOU ARE INSANE")

    if atom_flag == True:  #generate atom
        return random.choice(alphabet)

    else:  # generate operations
        chosen_oper = random.choice(operations)
        token_list = tokenize_expression(chosen_oper)
        token_list = [
            recursive_call(alphabet, operations, max_depth - 1,
                           max(min_depth - 1, 0), oper_percent, recursive_call,
                           key) if token == '%s' else token
            for token in token_list
        ]

        return token_list


def tokenize_expression(string):

    token_list = re.split('(\%s)', string)
    token_list = filter(None, token_list)
    return token_list


#recursivly flattens an expression tree into a string, in our case a regex
#param:     expr_tree - and expression tree in the form of a list of either strings or lists where the strings form the syntax of the operation and the sub_lists are the sub expression
def flatten_expression_tree(expr_tree):
    if isinstance(expr_tree, str):
        return expr_tree

    if isinstance(expr_tree, list):
        string_list = [flatten_expression_tree(exp) for exp in expr_tree]
        string = ''.join(string_list)
        return string

    raise TypeError("INSANE")


def generate_random_regex(alphabet, operations, max_depth, min_depth,
                          oper_percent):
    return generate_random_regex_aux(alphabet, operations, max_depth,
                                     min_depth, oper_percent,
                                     generate_random_regex_aux, None)
