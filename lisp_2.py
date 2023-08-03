#!/usr/bin/env python3
import sys

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
        else:
            raise SchemeNameError

    def __setitem__(self, var, val):
        self.children[var] = val

    def set_parent(self, var, val):
        if var in self.children:
            self.children[var] = val
        elif self.parent:
            try:
                self.parent.set_parent(var, val)
            except AttributeError:  # if its parent is scheme_builtins
                raise SchemeNameError
        else:
            raise SchemeNameError


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


class Pair:
    """
    class to represent pairs
    """

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


######################
# Built-in Functions #
######################


def mul(args):
    """
    Given a list of arguments, return the result of multiplying all together.
    """
    result = 1
    for num in args:
        result *= num
    return result


def div(args):
    """
    Given a list of arguments, return the result of dividing all together.
    """
    if not args:
        raise ValueError
    result = args[0]
    if len(args) == 1:
        return 1 / result
    for num in args[1:]:
        result /= num
    return result


def equal(args):
    """
    Given a list of arguments, returns True if all are equal, False otherwise.
    """
    return len(set(args)) == 1


def greater(args):
    """
    Given a list of arguments, returns True if in decreasing order, False otherwise.
    """
    iscorrect = True
    for i in range(len(args) - 1):
        if args[i] <= args[i + 1]:
            iscorrect = False
    return iscorrect


def ge(args):
    """
    Given a list of arguments, returns True if in nonincreasing order, False otherwise.
    """
    iscorrect = True
    for i in range(len(args) - 1):
        if args[i] < args[i + 1]:
            iscorrect = False
    return iscorrect


def less(args):
    """
    Given a list of arguments, returns True if in increasing order, False otherwise.
    """
    iscorrect = True
    for i in range(len(args) - 1):
        if args[i] >= args[i + 1]:
            iscorrect = False
    return iscorrect


def le(args):
    """
    Given a list of arguments, returns True if in nondecreasing order, False otherwise.
    """
    iscorrect = True
    for i in range(len(args) - 1):
        if args[i] > args[i + 1]:
            iscorrect = False
    return iscorrect


def not_func(args):
    """
    Given a list of one argument, returns the opposite of the argument.

    If there is not just one argument, raises SchemeEvaluationError.
    """
    if len(args) != 1:
        raise SchemeEvaluationError
    return not (args[0])


# def abs_func(args):
#     value = args[0]
#     if value >= 0:
#         return value
#     return -value

# def factorial_func(args):
#     value = args[0]
#     if value > 0:
#         return value * factorial_func([value - 1])
#     elif value == 1:
#         return 1


def cons(args):
    """
    Given 2 values, returns a Pair object of them.

    If there is not just 2 values, raises SchemeEvaluationError.
    """
    if len(args) != 2:
        raise SchemeEvaluationError
    return Pair(args[0], args[1])


def car(args):
    """
    Given a Pair object, returns the car (left side).

    If there is not just 1 value or is not a Pair object,
    raises SchemeEvaluationError.
    """
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].car


def cdr(args):
    """
    Given a Pair object, returns the cdr (right side).

    If there is not just 1 value or is not a Pair object,
    raises SchemeEvaluationError.
    """
    if len(args) != 1 or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].cdr


def list_func(args):
    """
    Given a list of arguments, returns a nested list of Pair
    objects.

    If there are no arguments, returns None.
    """
    if not args:
        return None
    return Pair(args[0], list_func(args[1:]))


def check_list(args):
    """
    Given an arbitrary argument, returns #t if that object is a linked
    list, and #f otherwise.
    """
    if args[0] is None:
        return True
    if not isinstance(args[0], Pair):
        return False
    return check_list([args[0].cdr])


def len_list(args):
    """
    Given a linkedd list, return the length of that list.

    When called on any object that is not a linked list,
    raises a SchemeEvaluationError
    """
    current = args[0]
    if not check_list([current]):
        raise SchemeEvaluationError
    count = 0
    while current is not None:
        count += 1
        current = current.cdr
    return count


def list_index(args):
    """
    Given a list of a linked list and a nonnegative index, return the
    element at the given index in the given linked list.

    If the argument is a cons cell (but not a list), then asking for index 0 should
    produce the car of that cons cell, and asking for any other index should
    raise a SchemeEvaluationError.
    """
    current = args[0]
    index = args[1]
    if not check_list([current]) and isinstance(current, Pair):
        if index != 0:
            raise SchemeEvaluationError
        return args[0].car
    if index >= len_list([current]):
        raise SchemeEvaluationError
    for i in range(index):
        current = current.cdr
    return current.car


def list_append(args):
    """
    Given an arbitrary number of lists, return a new linked list representing
    the concatenation of these lists.

    If exactly one list is passed in, it should return a copy of that list.

    If append is called with no arguments, it should produce an empty list.

    Calling append on any elements that are not lists should result in a SchemeEvaluationError.
    """
    head = None
    tail = None
    for arg in args:
        if not check_list([arg]):
            raise SchemeEvaluationError
        current = arg
        while current:
            if not head:
                head = Pair(current.car, None)
                tail = head
            else:
                tail.cdr = Pair(current.car, None)
                tail = tail.cdr
            current = current.cdr
    return head


def map_func(args):
    """
    Given a list of a function and a linked list, returns a new list containing the
    results of applying the given function to each element of the given list.
    """
    func = args[0]
    LL = args[1]
    if not callable(func) or not check_list([LL]):
        raise SchemeEvaluationError
    result = None
    for i in range(len_list([LL])):
        current = list_index([LL, i])
        curr_val = func([current])
        result = list_append([result, Pair(curr_val, None)])
    return result


def filter_func(args):
    """
    Given a list of a function and a linked list, returns a new linked list containing only
    the elements of the given linked list for which the given function returns true.
    """
    func = args[0]
    LL = args[1]
    if not callable(func) or not check_list([LL]):
        raise SchemeEvaluationError
    result = None
    for i in range(len_list([LL])):
        current = list_index([LL, i])
        if func([current]):
            result = list_append([result, Pair(current, None)])
    return result


def reduce_func(args):
    """
    Given a list of a function, a linked list, and an initial value, returns the result of
    successively applying the given function to the elements in the linked list.
    """
    func = args[0]
    LL = args[1]
    initial = args[2]
    if not callable(func) or not check_list([LL]):
        raise SchemeEvaluationError
    for i in range(len_list([LL])):
        initial = func([initial, list_index([LL, i])])
    return initial


def begin(args):
    """
    Given some arguments, return its last argument.
    """
    return args[-1]


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div,
    "#t": True,
    "#f": False,
    "equal?": equal,
    ">": greater,
    ">=": ge,
    "<": less,
    "<=": le,
    "not": not_func,
    # "abs": abs_func,
    # "factorial": factorial_func,
    "cons": cons,
    "car": car,
    "cdr": cdr,
    "list": list_func,
    "list?": check_list,
    "length": len_list,
    "list-ref": list_index,
    "append": list_append,
    "map": map_func,
    "filter": filter_func,
    "reduce": reduce_func,
    "begin": begin,
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
    if tree == "nil":
        return None
    if isinstance(tree, str):
        return frame[tree]
    if isinstance(tree, (int, float)):
        return tree
    if isinstance(tree, list) and len(tree) > 0:
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
        if tree[0] == "if":
            if evaluate(tree[1], frame):
                return evaluate(tree[2], frame)
            return evaluate(tree[3], frame)
        if tree[0] == "and":
            for item in tree[1:]:
                if not evaluate(item, frame):
                    return False
            return True
        if tree[0] == "or":
            for item in tree[1:]:
                if evaluate(item, frame):
                    return True
            return False
        if tree[0] == "del":
            if tree[1] not in frame.children:
                raise SchemeNameError
            return frame.children.pop(tree[1])
        if tree[0] == "let":
            new_frame = Frames(frame)
            for exp in tree[1]:
                current_value = evaluate(exp[1], new_frame)
                new_frame[exp[0]] = current_value
            return evaluate(tree[2], new_frame)
        if tree[0] == "set!":
            current_value = evaluate(tree[2], frame)
            frame.set_parent(tree[1], current_value)
            return current_value
        maybe_func = evaluate(tree[0], frame)
        if not callable(maybe_func):
            raise SchemeEvaluationError("first element is not a valid function")
        return maybe_func([evaluate(subtree, frame) for subtree in tree[1:]])
    raise SchemeEvaluationError


def result_and_frame(tree, frame=None):
    """
    Given a tree, returns a tuple with two elements: the result of the
    evaluation and the frame in which the expression was evaluated.
    """
    if not frame:
        frame = Frames()
    return evaluate(tree, frame), frame


def evaluate_file(file_name, frame=None):
    """
    Given a file name and an optional variable, frame, returns the evaluated
    expression contained in the file.
    """
    with open(file_name) as f:
        current_file = f.read()
    return evaluate(parse(tokenize(current_file)), frame)


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
    for item in sys.argv[1:]:
        evaluate_file(item, frame)
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