#!/usr/bin/env python3

import typing
import doctest



def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    # board = []
    # hidden = []
    # for r in range(num_rows):
    #     board_row = []
    #     hidden_row = []
    #     for c in range(num_cols):
    #         hidden_row.append(True)
    #         if (r, c) in bombs:
    #             board_row.append(".")
    #         else:
    #             board_row.append(0)
    #     board.append(board_row)
    #     hidden.append(hidden_row)

    # neighbor_key = [-1,0,1]

    # for r in range(num_rows):
    #     for c in range(num_cols):
    #         if board[r][c] == 0:
    #             neighbor_bombs = 0

    #             for key_r in neighbor_key:
    #                 for key_c in neighbor_key:
    #                     if 0 <= r + key_r < num_rows:
    #                         if 0<= c + key_c < num_cols:
    #                             if board[r + key_r][c + key_c] == ".":
    #                                 neighbor_bombs += 1
    #             board[r][c] = neighbor_bombs
    # return {
    #     "dimensions": (num_rows, num_cols),
    #     "board": board,
    #     "hidden": hidden,
    #     "state": "ongoing",
    # }
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """
    # if game["state"] == "defeat" or game["state"] == "victory":
    #     return 0

    # if game["board"][row][col] == ".":
    #     game["hidden"][row][col] = False
    #     game["state"] = "defeat"
    #     return 1

    # bombs = 0
    # hidden_squares = 0
    # for r in range(game["dimensions"][0]):
    #     for c in range(game["dimensions"][1]):
    #         if game["board"][r][c] == ".":
    #             if not game["hidden"][r][c]:
    #                 bombs += 1
    #         elif game["hidden"][r][c]:
    #             hidden_squares += 1
    # if bombs != 0:
    #     # if bombs is not equal to zero, set the game state to defeat and
    #     # return 0
    #     game["state"] = "defeat"
    #     return 0

    # if hidden_squares == 0:
    #     game["state"] = "victory"
    #     return 0

    # if game["hidden"][row][col]:
    #     game["hidden"][row][col] = False
    #     revealed = 1
    # else:
    #     return 0

    # neighbor_key = [-1,0,1]

    # if game["board"][row][col] == 0:
    #     num_rows, num_cols = game["dimensions"]
    #     for key_r in neighbor_key:
    #         for key_c in neighbor_key:
    #             current_row = row + neighbor_key[key_r]
    #             current_col = col + neighbor_key[key_c]
    #             if 0 <= current_row < num_rows:
    #                 if 0 <= current_col < num_cols:
    #                     if game["board"][current_row][current_col] != ".":
    #                         if game["hidden"][current_row][current_col]:
    #                             revealed += dig_2d(game, current_row, current_col)

    # bombs = 0  # set number of bombs to 0
    # hidden_squares = 0
    # for r in range(game["dimensions"][0]):
    #     # for each r,
    #     for c in range(game["dimensions"][1]):
    #         # for each c,
    #         if game["board"][r][c] == ".":
    #             if not game["hidden"][r][c]:
    #                 # if the game hidden is False, and the board is '.', add 1 to
    #                 # bombs
    #                 bombs += 1
    #         elif game["hidden"][r][c]:
    #             hidden_squares += 1
    # bad_squares = bombs + hidden_squares
    # if bad_squares > 0:
    #     game["state"] = "ongoing"
    # else:
    #     game["state"] = "victory"
    # return revealed
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    # result_board = game["board"].copy()
    # hidden_copy = game["hidden"].copy()
    # num_row = game["dimensions"][0]
    # num_col = game["dimensions"][1]

    # for row in range(num_row):
    #     for col in range(num_col):
    #         current_pix = result_board[row][col]
    #         if current_pix == 0:
    #             result_board[row][col] = ' '
    #         else:
    #             result_board[row][col] = str(current_pix)
    #         if not xray:
    #             if hidden_copy[row][col]:
    #                 result_board[row][col] = '_'

    # return result_board
    return render_nd(game, xray)


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    # num_row = game["dimensions"][0]
    # num_col = game["dimensions"][1]
    # locations_list = render_2d_locations(game, xray)
    # return_string = ''
    # for row in range(num_row):
    #     for col in range(num_col):
    #         return_string = return_string + locations_list[row][col]
    #     if row != num_row - 1: #to not ad \n at the very end of the string
    #         return_string = return_string + '\n'
    # return return_string

    locations_list = render_nd(game, xray)
    return_string = ""
    for x in range(game["dimensions"][0]):
        new_string = "".join(locations_list[x])
        return_string += new_string
        if x != game["dimensions"][0] - 1:
            return_string += "\n"
    return return_string


# N-D IMPLEMENTATION


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    """
    board = empty_board(dimensions, 0)
    hidden = empty_board(dimensions, True)
    # bombs = set(bombs)
    for coord in bombs:
        set_value(coord, board, ".")
        for neighbor in get_neighbors(coord, dimensions):
            curr_val = get_value(neighbor, board)
            if isinstance(curr_val, int):
                set_value(neighbor, board, curr_val + 1)

    return {
        "dimensions": dimensions,
        "board": board,
        "hidden": hidden,
        "state": "ongoing",
    }


# new_game_nd helper functions:


def empty_board(dimensions, value):
    """
    Given the dimensioins of a board and a value, returns a board filled
    with the value given in every coordinate of the board.
    """
    nd = len(dimensions)
    result_board = []
    if nd == 1:
        return [value for x in range(dimensions[0])]
    for x in range(dimensions[0]):
        result_board.append(empty_board(dimensions[1:], value))
    return result_board


def get_neighbors(coord, dimensions):
    """
    Given a coordinate and the dimensions of a board, returns all
    the neighbors of that given coordinate in a set of tuples.
    """
    all_neighbors = set()
    if len(coord) == 1:
        for x in range(coord[0] - 1, coord[0] + 2):
            if 0 <= x < dimensions[0]:
                all_neighbors.add((x,))
    else:
        for x in range(coord[0] - 1, coord[0] + 2):
            if 0 <= x < dimensions[0]:
                for i in get_neighbors(coord[1:], dimensions[1:]):
                    all_neighbors.add((x,) + i)
    return all_neighbors


def get_all_coords(dimensions):
    """
    Given the dimensions of a board, returns all possible coordinates
    of the board in a set of tuples.
    """
    all_coords = set()
    if len(dimensions) == 1:
        for coord in range(dimensions[0]):
            all_coords.add((coord,))
    else:
        for x in get_all_coords((dimensions[0],)):
            for i in get_all_coords(dimensions[1:]):
                all_coords.add(x + i)
    return all_coords


def get_value(coord, board):
    """
    Given a coordinate and a board, returns the current value of that
    coordinate on the board.
    """
    if len(coord) == 1:
        return board[coord[0]]
    return get_value(coord[1:], board[coord[0]])


def set_value(coord, board, value):
    """
    Given a coordinate, a board, and a value, modifies the board to set
    the coordinate given to the value given.
    """
    if len(coord) == 1:
        board[coord[0]] = value
    else:
        set_value(coord[1:], board[coord[0]], value)


def dig_nd(game, coordinates, curr_state=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    """
    if not get_value(coordinates, game["hidden"]) or game["state"] != "ongoing":
        return 0

    set_value(coordinates, game["hidden"], False)
    current_value = get_value(coordinates, game["board"])
    revealed = 1

    if current_value == ".":
        game["state"] = "defeat"
        return revealed

    if current_value == 0:
        neighbors = get_neighbors(coordinates, game["dimensions"])
        for coord in neighbors:
            revealed += dig_nd(game, coord, False)

    if curr_state:
        if victory_check(game, get_all_coords(game["dimensions"])):
            game["state"] = "victory"

    return revealed


# dig_nd helper function:


def victory_check(game, coords):
    """
    Given a game and a list of all the coordinates, returns the current
    state of the game, victory, defeat, or ongoing.
    """
    curr_state = False
    for val in coords:
        board_val = get_value(val, game["board"])
        hid_val = get_value(val, game["hidden"])
        if (not hid_val and board_val == ".") or (hid_val and board_val != "."):
            return curr_state
    return True


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    all_coords = get_all_coords(game["dimensions"])
    result_board = empty_board(game["dimensions"], "_")

    for coord in all_coords:
        current_pix = get_value(coord, game["board"])
        if current_pix == 0:
            set_value(coord, result_board, " ")
        else:
            set_value(coord, result_board, str(current_pix))
        if not xray:
            if get_value(coord, game["hidden"]):
                set_value(coord, result_board, "_")

    return result_board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # # )
    # doctest.run_docstring_examples(
    #    render_2d_board,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # doctest.run_docstring_examples(
    #    new_game_2d,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # doctest.run_docstring_examples(
    #    dig_2d,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # # print(get_neighbors((1,1,1),(4,4,4)))
    # # print(get_all_coords((2,2,2)))
    # doctest.run_docstring_examples(
    #    new_game_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # doctest.run_docstring_examples(
    #    dig_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # doctest.run_docstring_examples(
    #    render_nd,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # print(get_neighbors((5,13,0),(10,20,3)))
    pass