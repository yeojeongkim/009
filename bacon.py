#!/usr/bin/env python3

import pickle


def transform_data(raw_data):
    """
    dict where key is film_id and value is a set of all actors in the film
    dict where key is actor and value is a set of all actors that have acted with them

    raw_data in the form of a list of tuples (actor_id_1, actor_id_2, film_id)
    """
    film_dict = {}
    actor_dict = {}
    for tup in raw_data:
        # makes dict with key film_id & value all actors in film
        if tup[2] in film_dict:
            film_dict[tup[2]].update({tup[0], tup[1]})
        else:
            film_dict[tup[2]] = {tup[0], tup[1]}

        # makes dict with key actor & all actors that acted with the actor
        if tup[0] in actor_dict:
            actor_dict[tup[0]].update({tup[1]})
        else:
            actor_dict[tup[0]] = {tup[0], tup[1]}
        if tup[1] in actor_dict:
            actor_dict[tup[1]].update({tup[0]})
        else:
            actor_dict[tup[1]] = {tup[0], tup[1]}
    return film_dict, actor_dict


def acted_together(transformed_data, actor_id_1, actor_id_2):
    if actor_id_2 in transformed_data[1][actor_id_1]:
        return True
    else:
        return False


def actors_with_bacon_number(transformed_data, n):
    if n == 0:
        return {4724}
    if n > 1000:
        return set()

    to_visit = {4724}
    visited = {4724}

    for i in range(n):
        n_set = set()
        for actor in to_visit:
            for neighbor in transformed_data[1][actor]:
                if neighbor in visited:
                    continue
                n_set.add(neighbor)
                visited.add(neighbor)
        to_visit = n_set

    return to_visit


def bacon_path(transformed_data, actor_id):
    return actor_to_actor_path(transformed_data, 4724, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    return actor_path(transformed_data, actor_id_1, lambda p: p == actor_id_2)


def movie_path(transformed_data, actor_id_1, actor_id_2):
    act_path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    film_list = []
    for i in range(len(act_path)):
        for film in transformed_data[0].keys():
            if i == len(act_path) - 1:
                continue
            if (
                act_path[i] in transformed_data[0][film]
                and act_path[i + 1] in transformed_data[0][film]
            ):
                film_list.append(film)
    return film_list


def actor_path(transformed_data, actor_id_1, goal_test_function):
    if actor_id_1 not in transformed_data[1]:
        return None
    
    to_visit = {actor_id_1}
    visited = {actor_id_1}

    if goal_test_function(actor_id_1):
        return [actor_id_1]
    to_visit = [(actor_id_1, [actor_id_1])]
    visited = {actor_id_1}
    while to_visit:
        (actor, path) = to_visit.pop(0)
        for coactor in transformed_data[1][actor] - visited:
            if coactor in visited:
                continue
            visited.add(coactor)
            if goal_test_function(coactor):
                return path + [coactor]
            to_visit.append((coactor, path + [coactor]))
    return None

    ### less efficient, but another way to do the same thing ###
    # if actor_id_1 not in transformed_data[1]:
    #     return None

    # to_visit = {actor_id_1}
    # visited = {actor_id_1}
    # parent = {actor_id_1: None}

    # current_actor = actor_id_1

    # while not goal_test_function(current_actor):
    #     n_set = set()
    #     for actor in to_visit:
    #         for child in transformed_data[1][actor]:
    #             if child in visited:
    #                 continue
    #             n_set.add(child)
    #             visited.add(child)
    #             parent[child] = actor
    #             current_actor = child
    #             if goal_test_function(current_actor):
    #                 break
    #         if goal_test_function(current_actor):
    #             break
    #     if len(to_visit) == 0:
    #         return None

    #     to_visit = n_set
    # result = []
    # while current_actor != None:
    #     result.append(current_actor)
    #     current_actor = parent[current_actor]

    # return result[::-1]


def actors_connecting_films(transformed_data, film1, film2):
    actor_set1 = transformed_data[0][film1]
    actor_set2 = transformed_data[0][film2]

    path_list = []

    for actor1 in actor_set1:
        for actor2 in actor_set2:
            path_list.append(
                actor_path(transformed_data, actor1, lambda p: p == actor2)
            )

    return min(path_list, key=len)


if __name__ == "__main__":
    # with open("resources/small.pickle", "rb") as f:
    #     smalldb = pickle.load(f)

    # with open("resources/names.pickle", "rb") as f:
    #     namesdb = pickle.load(f)

    # print(namesdb)
    # print(namesdb["Tom Hoover"])
    # print(namesdb)
    # for key, val in namesdb.items():
    #     if val == 35753:
    #         print(key)

    # with open("resources/tiny.pickle", "rb") as f:
    #     tinydb = pickle.load(f)

    # actor1 = namesdb["Tom Amandes"]
    # actor2 = namesdb["Johan Akerblom"]
    # print(acted_together(transform_data(smalldb), actor1, actor2))

    # actor1 = namesdb["Robert Viharo"]
    # actor2 = namesdb["David Clennon"]
    # print(acted_together(transform_data(smalldb), actor1, actor2))

    # with open("resources/large.pickle", "rb") as f:
    #     largedb = pickle.load(f)

    # ids = actors_with_bacon_number(transform_data(largedb), 6)
    # actor_set = set()
    # for actors in ids:
    #     for key, val in namesdb.items():
    #         if val == actors:
    #             actor_set.add(key)
    # print(actor_set)

    # print(bacon_path(transform_data(tinydb), 1640))

    # path = bacon_path(transform_data(largedb), namesdb["Isabelle Aring"])
    # names = []
    # for actor in path:
    #     for key, val in namesdb.items():
    #         if val == actor:
    #             names.append(key)
    # print(names)

    # path = actor_to_actor_path(transform_data(largedb), namesdb["Fern Emmett"], namesdb["Willie Adams"])
    # names = []
    # for actor in path:
    #     for key, val in namesdb.items():
    #         if val == actor:
    #             names.append(key)
    # print(names)

    with open("resources/movies.pickle", "rb") as f:
        moviesdb = pickle.load(f)

    # path = movie_path(transform_data(largedb), namesdb["Emily Ann Lloyd"], namesdb["Anton Radacic"])
    # movies = []
    # for film in path:
    #     for key, val in moviesdb.items():
    #         if val == film:
    #             movies.append(key)
    # print(movies)

    pass
