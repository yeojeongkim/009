import pickle
import sys

sys.setrecursionlimit(20_000)


def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    recipe_dict = {}
    for tup in recipes:
        if tup[0] == "compound":
            recipe_dict[tup[1]] = []
    for tup in recipes:
        if tup[1] not in recipe_dict:
            continue
        recipe_dict[tup[1]].append(list(tup[2]))
    return recipe_dict


def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    atomic_cost_dict = {}
    for tup in recipes:
        if tup[0] == "atomic":
            atomic_cost_dict[tup[1]] = tup[2]
    return atomic_cost_dict


def lowest_cost(recipes, food_item, forbidden_items=[]):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    atomic_cost_dict = make_atomic_costs(recipes)
    recipe_dict = make_recipe_book(recipes)

    def lowest_helper(food):
        if food not in atomic_cost_dict and food not in recipe_dict:
            return None
        elif food in forbidden_items:
            return None
        elif food in atomic_cost_dict:
            return atomic_cost_dict[food]
        min_cost = float("inf")
        for recipe in recipe_dict[food]:
            no_ingredient = False
            current_cost = 0
            for ingredient in recipe:
                if lowest_helper(ingredient[0]) is None:
                    no_ingredient = True
                    break
                else:
                    current_cost += ingredient[1] * (lowest_helper(ingredient[0]))
            if not no_ingredient:
                min_cost = min(min_cost, current_cost)
        if min_cost == float("inf"):
            return None
        return min_cost

    return lowest_helper(food_item)


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled_dict = {}
    for ingredient, quantity in flat_recipe.items():
        scaled_dict[ingredient] = quantity * n
    return scaled_dict


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    grocery_dict = {}
    for recipe in flat_recipes:
        for ingredient, quantity in recipe.items():
            if ingredient in grocery_dict:
                grocery_dict[ingredient] += quantity
            else:
                grocery_dict[ingredient] = quantity
    return grocery_dict


def cheapest_flat_recipe(recipes, food_item, forbidden_items=[]):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomic_cost_dict = make_atomic_costs(recipes)
    recipe_dict = make_recipe_book(recipes)

    def cheapest_helper(food):
        if food not in atomic_cost_dict and food not in recipe_dict:
            return None
        elif food in forbidden_items:
            return None
        elif food in atomic_cost_dict:
            return {food: 1}
        minimum_cost = float("inf")
        minimum_recipe = {}
        for recipe in recipe_dict[food]:
            no_ingredient = False
            current_recipe = {}
            recipe_cost = 0
            for ingredient in recipe:
                if cheapest_helper(ingredient[0]) is None:
                    no_ingredient = True
                    break
                else:
                    current_recipe = make_grocery_list(
                        [
                            current_recipe,
                            scale_recipe(cheapest_helper(ingredient[0]), ingredient[1]),
                        ]
                    )
            if not no_ingredient:
                for ingredient in current_recipe:
                    recipe_cost += (
                        atomic_cost_dict[ingredient] * current_recipe[ingredient]
                    )
                if recipe_cost < minimum_cost:
                    minimum_cost = recipe_cost
                    minimum_recipe = current_recipe
        if not minimum_recipe:
            return None
        return minimum_recipe

    return cheapest_helper(food_item)


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes make a certain ingredient as part of a recipe, compute all
    combinations of the flat recipes.
    """
    if not flat_recipes:
        return [{}]

    final_recipe = []
    first_flat_recipe = flat_recipes[0]

    for ingredient in first_flat_recipe:
        for item in ingredient_mixes(flat_recipes[1:]):
            final_recipe.append(make_grocery_list([ingredient, item]))

    return final_recipe


def all_flat_recipes(recipes, food_item, forbidden_items=[]):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_cost_dict = make_atomic_costs(recipes)
    recipe_dict = make_recipe_book(recipes)

    def all_flat_helper(food):
        if food not in atomic_cost_dict and food not in recipe_dict:
            return []
        elif food in forbidden_items:
            return []
        elif food in atomic_cost_dict:
            return [{food: 1}]
        all_recipes = []
        for recipe in recipe_dict[food]:
            no_ingredient = False
            current_recipe = {}
            recipe_list = []
            for ingredient in recipe:
                all_current_recipes = []
                helper_result = all_flat_helper(ingredient[0])
                if not helper_result:
                    no_ingredient = True
                    break
                else:
                    for x in helper_result:
                        current_recipe = scale_recipe(x, ingredient[1])
                        all_current_recipes.append(current_recipe)
                if not recipe_list:
                    recipe_list = all_current_recipes
                else:
                    recipe_list = ingredient_mixes([recipe_list, all_current_recipes])
            if not no_ingredient:
                all_recipes += recipe_list
        return all_recipes

    return all_flat_helper(food_item)


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
    # print(len([x[0] for x in example_recipes if x[0] == "atomic"]))
    # print(make_recipe_book(example_recipes))
    # print(make_atomic_costs(example_recipes))

    # atomic_cost_dict = make_atomic_costs(example_recipes)
    # result = 0
    # for atomic in atomic_cost_dict.values():
    #     result += atomic
    # print(result)

    # recipe_dict = make_recipe_book(example_recipes)
    # result = 0
    # for recipe in recipe_dict.values():
    #     if len(recipe)>1:
    #         result+=1
    # print(result)

    # dairy_recipes = [
    #     ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    #     ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    #     ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    #     ('atomic', 'milking stool', 5),
    #     ('atomic', 'cutting-edge laboratory', 1000),
    #     ('atomic', 'time', 10000),
    #     ('atomic', 'cow', 100),
    # ]
    # # print(lowest_cost(dairy_recipes, "milk"))
    # # print(lowest_cost(example_recipes, "burger"))

    # cookie_recipes = cookie_recipes = [
    #     ('compound', 'cookie sandwich', [('cookie', 2), ('ice cream scoop', 3)]),
    #     ('compound', 'cookie', [('chocolate chips', 3)]),
    #     ('compound', 'cookie', [('sugar', 10)]),
    #     ('atomic', 'chocolate chips', 200),
    #     ('atomic', 'sugar', 5),
    #     ('compound', 'ice cream scoop', [('vanilla ice cream', 1)]),
    #     ('compound', 'ice cream scoop', [('chocolate ice cream', 1)]),
    #     ('atomic', 'vanilla ice cream', 20),
    #     ('atomic', 'chocolate ice cream', 30),
    # ]
    # # print(lowest_cost(cookie_recipes, "cookie sandwich"))

    # dairy_recipes_2 = [
    #     ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
    #     ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    #     ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    #     ('atomic', 'milking stool', 5),
    #     ('atomic', 'cutting-edge laboratory', 1000),
    #     ('atomic', 'time', 10000),
    # ]
    # # print(lowest_cost(dairy_recipes_2, 'cheese'))

    # soup = {"carrots": 5, "celery": 3, "broth": 2,
    # "noodles": 1, "chicken": 3, "salt": 10}
    # # print(scale_recipe(soup,3))

    # carrot_cake = {"carrots": 5, "flour": 8, "sugar": 10,
    # "oil": 5, "eggs": 4, "salt": 3}
    # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # grocery_list = [soup, carrot_cake, bread]
    # # print(make_grocery_list(grocery_list))
    # print(all_flat_recipes(example_recipes,"burger"))
