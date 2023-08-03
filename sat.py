#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)


def updating_expressions(formula, assignment):
    """
    Given a CNF formula, returns an updated formula.
    assignment: ('a', True)
    """
    result_formula = []
    if not formula or not assignment:
        return formula
    for clause in formula:
        if assignment in clause:
            continue
        elif (
            assignment[0],
            not assignment[1],
        ) in clause:  # if the opposite assignment is in the formula
            temporary_clause = clause.copy()
            while (assignment[0], not assignment[1]) in temporary_clause:
                temporary_clause.remove((assignment[0], not assignment[1]))
            result_formula.append(temporary_clause)
        else:  # i isn't in the formula
            result_formula.append(clause)
    return result_formula


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or
                                        x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """

    def satisfying_helper(f, a={}):
        if not f:  # if there's no unit clause, need these base cases
            return a
        if [] in f:
            return None
        while f:  # simplify the formula as much as possible by finding unit clauses
            done = True
            for clause in f:
                if len(clause) == 1:  # f is a unit clause
                    unit_clause = clause  # in the form of [('a', True)]
                    f = updating_expressions(f, unit_clause[0])
                    a[unit_clause[0][0]] = unit_clause[0][1]
                    done = False
                    break
            if not f:  # for efficiency, faster to do inside
                return a
            if [] in f:
                return None
            if done:
                break
        random_clause = [
            l[0] for c in f for l in c
        ]  # if no more unit clause, pick a random clause
        for x in (True, False):
            a[random_clause[0]] = x  # add it to the return dict
            possible_formula = satisfying_helper(
                updating_expressions(f, (random_clause[0], x)), a
            )
            if possible_formula != None:
                return a
            del a[random_clause[0]]  # remove it if it doesn't work
        return None

    return satisfying_helper(formula)


def possible_values(n, start=1):
    """
    Given the n dimension of the sudoku board, returns a list of tuples of all
    possible values of a cell in the board. The parameter start tells us at what
    number to start the indexing at (0 or 1)

    output:
    make_board(3,0): [(0, 1), (0, 2), (1, 2)]
    make_board(3,1): [(1, 2), (1, 3), (2, 3)]
    """
    new_board = [
        (row, col)
        for row in range(start, n + start)
        for col in range(row + start, n + start)
        if row != col
    ]
    return new_board


def make_cell_formula(sudoku_board, n):
    """
    Given a sudoku board and the dimension, returns a formula that satisfy the
    cell rules: each cell must contain one of the numbers between 1 and n, inclusive
    """
    cell_formula = []
    board_values = possible_values(n)
    for row in range(n):
        for col in range(n):
            if sudoku_board[row][col] == 0:  # if there isn't a number assigned yet
                cell_formula.append(
                    [(((row, col), digit + 1), True) for digit in range(n)]
                )
            else:  # if there is a number assigned, add it to the formula w the curr val
                cell_formula.append([(((row, col), sudoku_board[row][col]), True)])
            for (
                value
            ) in board_values:  # add rules that it can't be any other possible value
                cell_formula.append(
                    [(((row, col), value[0]), False), (((row, col), value[1]), False)]
                )
    return cell_formula


def make_rowcol_formula(n):
    """
    Given the dimension, returns a formula that satisfy the row/col rules:
    each row/col must contain one of the numbers from 1 and n exactly once
    """
    row_formula = []
    col_formula = []
    board_index = possible_values(n, 0)
    for x in range(n):
        for digit in range(n):
            col_formula.append([(((row, x), digit + 1), True) for row in range(n)])
            row_formula.append([(((x, col), digit + 1), True) for col in range(n)])

            for value in board_index:  # apply row/col rule of exactly once
                col_formula.append(
                    [
                        (((value[0], x), digit + 1), False),
                        (((value[1], x), digit + 1), False),
                    ]
                )
                row_formula.append(
                    [
                        (((x, value[0]), digit + 1), False),
                        (((x, value[1]), digit + 1), False),
                    ]
                )

    return row_formula + col_formula


def make_subgrid_formula(n, sub_n):
    """
    Given the dimension and the subgrid dimension, returns a formula that satisfy the
    subgrid rules: each subgrid must contain one of the numbers from 1 and n exactly once
    """
    subgrid_formula = []
    for row in range(0, n, sub_n):
        for col in range(0, n, sub_n):

            subgrid = [
                (r, c) for r in range(row, row + sub_n) for c in range(col, col + sub_n)
            ]  # make the subgrid

            for digit in range(n):  # apply the subgrid rules
                subgrid_formula.append([((cell, digit + 1), True) for cell in subgrid])
                additional_subgrid_formula = [
                    [
                        ((subgrid[rr], digit + 1), False),
                        ((subgrid[cc], digit + 1), False),
                    ]
                    for rr in range(n)
                    for cc in range(rr + 1, n)
                ]
                subgrid_formula += additional_subgrid_formula

    return subgrid_formula


def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.

    representation: [[(((row, col), digit), True), (((row, col), digit), False)]]
    """
    n = len(sudoku_board)
    sub_n = int(n ** (1 / 2))

    # 1) each cell must contain one of the numbers between 1 and n, inclusive
    cell_formula = make_cell_formula(sudoku_board, n)

    # 2) each row must contain one of the numbers from 1 and n exactly once
    # 3) each col must contain one of the numbers from 1 and n exactly once
    rowcol_formula = make_rowcol_formula(n)

    # 4) each subgrid must contain one of the numbers from 1 and n exactly once
    subgrid_formula = make_subgrid_formula(n, sub_n)

    return cell_formula + rowcol_formula + subgrid_formula


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    if not assignments:
        return None

    sudoku_board = []
    for row in range(n):
        sudoku_board.append([0])
        for col in range(n - 1):
            sudoku_board[row].append(0)

    for clause in assignments:
        if assignments[clause]:
            sudoku_board[clause[0][0]][clause[0][1]] = clause[1]

    return sudoku_board


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    # sudoku_board = []
    # for row in range(2):
    #     sudoku_board.append([0])
    #     for col in range(1):
    #         sudoku_board[row].append(0)
    # print(sudoku_board)
