#!/usr/bin/env python3

import sys
import doctest

sys.setrecursionlimit(20_000)


#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    line_list = source.splitlines()
    return_list = []
    for line in line_list:
        expression, symbol, comment = line.partition(";")
        if ")" in comment:
            expression += ")"
        new_exp = expression.replace("(", " ( ")
        new_exp = new_exp.replace(")", " ) ")
        return_list.extend(item for item in new_exp.split())
    return return_list


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens

    >>> parse(['(', 'cat', '(', 'dog', '(', 'tomato', ')', ')', ')'])
    ['cat', ['dog', ['tomato']]]
    >>> parse(['2'])
    2
    >>> parse(['x'])
    'x'
    >>> parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')'])
    ['+', 2, ['-', 5, 3], 7, 8]
    """
    num_char = len(tokens)

    def parse_expression(index):
        token = number_or_symbol(tokens[index])
        if isinstance(token, (int, float)):
            return token, index + 1
        if token == "(":
            expression_list = []
            curr_index = index + 1
            if curr_index > num_char - 1:
                raise SchemeSyntaxError
            while tokens[curr_index] != ")":
                curr_exp, upcoming_index = parse_expression(curr_index)
                expression_list.append(curr_exp)
                curr_index = upcoming_index
                if curr_index > num_char - 1:
                    raise SchemeSyntaxError
            return expression_list, curr_index + 1
        if token == ")":  # if there's an extra parenthesis
            raise SchemeSyntaxError
        return token, index + 1

    parsed_expression, next_index = parse_expression(0)

    if next_index < num_char:  # if there are extra items not in ()
        raise SchemeSyntaxError

    return parsed_expression


####################
# Class Definition #
####################


class Frames:
    """
    class to represent frames
    """

    def __init__(self, grandparent=None):
        if grandparent:
            self.parent = grandparent
        else:
            self.parent = scheme_builtins
        self.children = {}  # variable: value

    def __getitem__(self, var):
        if var in self.children:
            return self.children[var]
        elif self.parent:
            try:
                return self.parent.__getitem__(var)
            except KeyError:
                raise SchemeNameError
        raise SchemeNameError

    def __setitem__(self, var, val):
        self.children[var] = val


class Functions:
    """
    class to represent functions
    """

    def __init__(self, body, param, frame):
        self.body = body
        self.param = param
        self.frame = frame

    def __call__(self, args):
        if len(args) != len(self.param):
            raise SchemeEvaluationError
        frame = Frames(self.frame)
        for i, value in enumerate(args):
            frame.children[self.param[i]] = value
        return evaluate(self.body, frame)


######################
# Built-in Functions #
######################


def mul(args):
    """
    Given a list of values, return the result of multiplying all together.
    """
    result = 1
    for num in args:
        result *= num
    return result


def div(args):
    """
    Given a list of values, return the result of dividing all together.
    """
    if not args:
        raise ValueError
    result = args[0]
    if len(args) == 1:
        return 1 / result
    for num in args[1:]:
        result /= num
    return result


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div,
}


##############
# Evaluation #
##############


def evaluate(tree, frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    >>> evaluate(3.14)
    3.14
    >>> evaluate(['+', 3, 7, 2])
    12
    >>> evaluate(['+', 3, ['-', 7, 5]])
    5
    """
    if not frame:
        frame = Frames()
    if isinstance(tree, str):
        return frame[tree]
    if isinstance(tree, (int, float)):
        return tree
    if isinstance(tree, list):
        if tree[0] == "define":
            if isinstance(tree[1], str):
                current_value = evaluate(tree[2], frame)
                frame[tree[1]] = current_value
                return current_value
            if isinstance(tree[1], list):
                param = tree[1][1:]
                body = tree[2]
                current_func = Functions(body, param, frame)
                frame[tree[1][0]] = current_func
                return current_func
            raise SchemeSyntaxError
        if tree[0] == "lambda":
            param = tree[1]
            body = tree[2]
            return Functions(body, param, frame)
        maybe_func = evaluate(tree[0], frame)
        if not callable(maybe_func):
            raise SchemeEvaluationError("first element is not a valid function")
        return maybe_func([evaluate(subtree, frame) for subtree in tree[1:]])


def result_and_frame(tree, frame=None):
    """
    Given a tree, returns a tuple with two elements: the result of the
    evaluation and the frame in which the expression was evaluated.
    """
    if not frame:
        frame = Frames()
    return evaluate(tree, frame), frame


def repl(verbose=False):
    """
    Read in a single line of user input, evaluate the expression, and print
    out the result. Repeat until user inputs "QUIT"

    Arguments:
        verbose: optional argument, if True will display tokens and parsed
            expression in addition to more detailed error output.
    """
    import traceback

    frame = Frames()
    while True:
        input_str = input("in> ")
        if input_str == "QUIT":
            return
        try:
            token_list = tokenize(input_str)
            if verbose:
                print("tokens>", token_list)
            expression = parse(token_list)
            if verbose:
                print("expression>", expression)
            output = evaluate(expression, frame)
            print("  out>", output)
        except SchemeError as e:
            if verbose:
                traceback.print_tb(e.__traceback__)
            print("Error>", repr(e))


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    repl(True)
    # print(tokenize("(cat (dog (tomato)))"))
    # print(tokenize(';add the numbers\n (+ ; this expression\n2     ; spans multiple\n3  ; lines)'))
    # print(tokenize('(adam adam chris duane))'))
