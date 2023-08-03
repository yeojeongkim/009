import doctest

class Symbol:
    """
    super class
    initializes class variables for the subclasses to use
    defines dunder methods
    """
    precedence = 0
    right_parens = False
    left_parens = False

    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __rsub__(self, other):
        return Sub(other, self)

    def __rmul__(self, other):
        return Mul(other, self)

    def __rtruediv__(self, other):
        return Div(other, self)

    def simplify(self):
        return self

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)


class Var(Symbol):
    """
    subclass of Symbol for the variables
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Var('{self.name}')"

    def eval(self, mapping):
        if self.name not in mapping:
            raise NameError
        return mapping[self.name]

    def __eq__(self, other):
        if isinstance(other, Var):
            return self.name == other.name
        return False

    def deriv(self, var):
        if self.name == var:  # derivative of x with respect to x
            return Num(1)
        return Num(0)  # derivative of x with respect to y, return 0


class Num(Symbol):
    """
    subclass of Symbol for the numbers
    """
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return f"Num({self.n})"

    def eval(self, mapping):
        return self.n

    def __eq__(self, other):
        if isinstance(other, Num):
            return self.n == other.n
        return False

    def deriv(self, var):
        return Num(0)


class BinOp(Symbol):
    """
    subclass of Symbol for the binary operations
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

        if isinstance(left, int) or isinstance(left, float):
            self.left = Num(left)
        elif isinstance(left, str):
            self.left = Var(left)

        if isinstance(right, int) or isinstance(right, float):
            self.right = Num(right)
        elif isinstance(right, str):
            self.right = Var(right)

    def __str__(self):
        new_left = str(self.left)
        new_right = str(self.right)
        if self.left.precedence != 0 and (
            self.left.precedence < self.precedence
            or (self.left.precedence == self.precedence and self.left_parens)
        ):
            new_left = f"({new_left})"
        if self.right.precedence != 0 and (
            self.right.precedence < self.precedence
            or (self.right.precedence == self.precedence and self.right_parens)
        ):
            new_right = f"({new_right})"
        return f"{new_left} {self.operation} {new_right}"

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.left)}, {repr(self.right)})"

    def eval(self, mapping):
        return self.perform_operation(self.left.eval(mapping), self.right.eval(mapping))

    def __eq__(self, other):
        if isinstance(other, BinOp):
            return (
                (self.left == other.left)
                and (self.right == other.right)
                and (self.operation == other.operation)
            )
        return False


class Add(BinOp):
    """
    subclass of BinOp to define the addition operation
    """
    def perform_operation(self, l, r):
        return l + r

    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)

    def simplify(self):
        new_left = self.left.simplify()
        new_right = self.right.simplify()
        if new_left == Num(0):
            return new_right
        elif new_right == Num(0):
            return new_left
        if isinstance(new_left, Num) and isinstance(new_right, Num):
            return Num(new_left.n + new_right.n)
        return Add(new_left, new_right)

    operation = "+"
    precedence = 1


class Sub(BinOp):
    """
    subclass of BinOp to define the subtraction operation
    """
    def perform_operation(self, l, r):
        return l - r

    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)

    def simplify(self):
        new_left = self.left.simplify()
        new_right = self.right.simplify()
        if new_right == Num(0):
            return new_left
        if isinstance(new_left, Num) and isinstance(new_right, Num):
            return Num(new_left.n - new_right.n)
        return Sub(new_left, new_right)

    operation = "-"
    precedence = 1
    right_parens = True


class Mul(BinOp):
    """
    subclass of BinOp to define the multiplication operation
    """
    def perform_operation(self, l, r):
        return l * r

    def deriv(self, var):
        return (self.right * self.left.deriv(var)) + (self.left * self.right.deriv(var))

    def simplify(self):
        new_left = self.left.simplify()
        new_right = self.right.simplify()
        if new_left == Num(0):
            return Num(0)
        elif new_right == Num(0):
            return Num(0)
        if new_left == Num(1):
            return new_right
        elif new_right == Num(1):
            return new_left
        if isinstance(new_left, Num) and isinstance(new_right, Num):
            return Num(new_left.n * new_right.n)
        return Mul(new_left, new_right)

    operation = "*"
    precedence = 2


class Div(BinOp):
    """
    subclass of BinOp to define the division operation
    """
    def perform_operation(self, l, r):
        return l / r

    def deriv(self, var):
        return (
            (self.right * self.left.deriv(var)) - (self.left * self.right.deriv(var))
        ) / (self.right * self.right)

    def simplify(self):
        new_left = self.left.simplify()
        new_right = self.right.simplify()
        if new_left == Num(0):
            return Num(0)
        if new_right == Num(1):
            return new_left
        if isinstance(new_left, Num) and isinstance(new_right, Num):
            return Num(new_left.n / new_right.n)
        return Div(new_left, new_right)

    operation = "/"
    precedence = 2
    right_parens = True


class Pow(BinOp):
    """
    subclass of BinOp to define the power operation
    """
    def perform_operation(self, l, r):
        return l**r

    def deriv(self, var):
        if not isinstance(self.right, Num):
            raise TypeError
        return (self.right * (self.left ** (self.right - 1))) * self.left.deriv(var)

    def simplify(self):
        new_left = self.left.simplify()
        new_right = self.right.simplify()
        if new_right == Num(0):
            return Num(1)
        elif new_right == Num(1):
            return new_left
        elif new_left == Num(0):
            return Num(0)
        return Pow(new_left, new_right)

    operation = "**"
    precedence = 3
    left_parens = True


def tokenize(formula):
    """
    Given a formula of string type, returns a list containing different
    strings in that formula.

    Example: 
    tokenize("(x * (2 + 3))")
    ['(', 'x', '*', '(', '2', '+', '3', ')', ')']
    """
    new_formula = formula.replace("(", " ( ")
    new_formula = new_formula.replace(")", " ) ")
    return new_formula.split()


def parse(tokens):
    """
    Given tokens, a form in the result of the tokenize function, returns
    a tuple of the parsed expression and the next index

    Example:
    tokens = tokenize("(x * (2 + 3))")
    parse(tokens)
    Mul(Var('x'), Add(Num(2), Num(3)))
    """
    def parse_expression(index):
        try:
            return Num(float(tokens[index])), index + 1
        except ValueError:
            if tokens[index] == "(":
                left_exp, left_index = parse_expression(index + 1)
                right_exp, final_index = parse_expression(left_index + 1)
                if tokens[left_index] == "+":
                    return left_exp + right_exp, final_index + 1
                elif tokens[left_index] == "-":
                    return left_exp - right_exp, final_index + 1
                elif tokens[left_index] == "*":
                    return left_exp * right_exp, final_index + 1
                elif tokens[left_index] == "/":
                    return left_exp / right_exp, final_index + 1
                elif tokens[left_index] == "**":
                    return left_exp**right_exp, final_index + 1
            return Var(tokens[index]), index + 1

    parsed_expression, next_index = parse_expression(0)
    return parsed_expression


def expression(formula):
    """
    Given a formula, returns the parsed formula.
    """
    tokenized_formula = tokenize(formula)
    return parse(tokenized_formula)


if __name__ == "__main__":
    doctest.testmod()
    # print(tokenize("(-101 * x)"))
    # print(parse(tokenize("(-101 * x)")))
