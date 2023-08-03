import json
import typing


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    new_description = {
        "wall": set(),
        "player": set(),
        "computer": set(),
        "target": set(),
    }
    num_row = len(level_description)
    num_col = len(level_description[0])

    for row in range(num_row):
        for col in range(num_col):
            current_pixel = level_description[row][col]
            for element in current_pixel:
                new_description[element].add((row, col))

    return new_description


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    # get position of target
    target_copy = game["target"].copy()

    if not game["target"]:
        return False

    for tar in target_copy:
        if tar not in game["computer"]:
            return False

    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    for user in game["player"]:
        current_user = user

    # new player position without edge cases
    new_user = add_tuple(direction_vector[direction], current_user)

    # if player hits wall
    if new_user in game["wall"]:
        return game

    # get the neighbors of player & computer
    computer_copy = game["computer"].copy()
    neighbor = None

    if new_user in computer_copy:
        neighbor = add_tuple(direction_vector[direction], new_user)
        if neighbor in computer_copy or neighbor in game["wall"]:
            return game
        else:
            computer_copy.remove(new_user)
            computer_copy.add(neighbor)

    new_game = {
        "wall": game["wall"].copy(),
        "computer": computer_copy,
        "target": game["target"].copy(),
        "player": {new_user},
    }
    return new_game


def add_tuple(t1, t2):
    """
    given 2 tuples, returns a tuple of them added together
    """
    new_list = []
    for i in range(len(t1)):
        new_list.append(t1[i] + t2[i])
    return tuple(new_list)


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    game_copy = game.copy()

    first_col = 0
    first_row = 0
    for tup in game_copy["wall"]:
        first_col = max(tup[1], first_col)
        first_row = max(tup[0], first_row)

    reverted_game = []

    # empty shell of 2D list of list of list
    for y in range(first_row + 1):
        reverted_game.append([])
        for x in range(first_col + 1):
            reverted_game[y].append([])

    # add to shell of 2D list
    for tup in game_copy["wall"]:
        reverted_game[tup[0]][tup[1]].append("wall")
    for tup in game_copy["computer"]:
        reverted_game[tup[0]][tup[1]].append("computer")
    for tup in game_copy["player"]:
        reverted_game[tup[0]][tup[1]].append("player")
    for tup in game_copy["target"]:
        reverted_game[tup[0]][tup[1]].append("target")

    return reverted_game


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    hashable_game = hashable(game)
    visited = {hashable_game}
    agenda = [(game, [])]

    if victory_check(game):
        return []

    while agenda:
        current_state, moves = agenda.pop(0)
        for dir in direction_vector:
            current_game = step_game(current_state, dir)
            hashable_game = hashable(current_game)
            if hashable_game in visited:
                continue
            visited.add(hashable_game)
            agenda.append((current_game, moves + [dir]))
            if victory_check(current_game):
                return agenda[-1][1]

    return None


def hashable(dictionary):
    return (frozenset(dictionary["computer"]), frozenset(dictionary["player"]))


if __name__ == "__main__":
    # game = [
    #     [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
    #     [["wall"], ["target"], ["wall"], [], [], [], ["wall"]],
    #     [["wall"], ["target"], ["player"], ["computer"], ["computer"], [], ["wall"]],
    #     [["wall"], [], ["computer"], [], [], [], ["wall"]],
    #     [["wall"], ["target"], [], [], [], [], ["wall"]],
    #     [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"], ["wall"]],
    # ]
    # print(new_game(game))
    # # print(step_game(new_game(game), "down"))
    # # print(victory_check(new_game(game)))
    # # print("new")
    # hello = dump_game(new_game(game))
    # print(hello)
    # if hello == game:
    #     print("true")

    # print(add_tuple((1,2),(-1,-1)))
    pass
