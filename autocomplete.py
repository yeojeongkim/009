import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError
        for letter in key:
            if letter not in self.children:
                self.children[letter] = PrefixTree()
            self = self.children[letter]
        self.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        if len(key) == 1:
            if key not in self.children or self.children[key] is None:
                raise KeyError
            return self.children[key].value
        return self.children[key[0]].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if key not in self:
            raise KeyError
        # elif not isinstance(key, str):
        #     raise TypeError
        else:
            self.__setitem__(key, None)

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError

        if not key:  # len(key) == 0:
            if self.value is not None:
                return True
        # elif len(key) == 1:
        #     if key in self.children and self.children[key].value is not None:
        #         return True
        elif key[0] in self.children:
            return self.children[key[0]].__contains__(key[1:])
        return False

    def __iter__(self, curr_key=""):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        if self.value is not None:
            yield (curr_key, self.value)
        for letter, child in self.children.items():
            yield from child.__iter__(curr_key + letter)

    def __getsubtree__(self, key):
        """
        Given a key, returns a subtree that all include the key.
        """
        if not isinstance(key, str):
            return []

        if not key:  # len(key) == 0:
            return self
        elif key[0] in self.children:
            return self.children[key[0]].__getsubtree__(key[1:])


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    prefix_tree = PrefixTree()
    sentence_strings = tokenize_sentences(text)

    for sentence in sentence_strings:
        for word in sentence.split(" "):
            if word not in prefix_tree:
                prefix_tree[word] = 1
            else:
                prefix_tree[word] += 1

    return prefix_tree


def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError

    subtree = tree.__getsubtree__(prefix)

    if not subtree or max_count == 0:
        return []

    pair_subtree = subtree.__iter__()  # get list of (key,value) in the subtree

    if not max_count:  # return all words with prefix in list
        return [prefix + pair[0] for pair in pair_subtree]

    list_pair_subtree = list(pair_subtree)  # turn generator into a list
    list_pair_subtree.sort(key=lambda x: x[1], reverse=True)  # reverse sort it

    return [prefix + pair[0] for pair in list_pair_subtree[:max_count]]
    # return_list = []
    # for pair in list_pair_subtree[:max_count]:
    #     return_list.append(prefix + pair[0])


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    if not isinstance(prefix, str):
        raise TypeError

    if max_count == 0:
        return []

    autocomplete_set, autocorrect_set = all_results(tree, prefix, max_count)

    # if max_count is None or its greater than all possible corrections
    if max_count is None or max_count > (len(autocomplete_set) + len(autocorrect_set)):
        return list(autocorrect_set) + list(autocomplete_set)

    # if autocomplete result is longer than the max_count
    if len(autocomplete_set) >= max_count:
        return list(autocomplete_set)

    # if autocomplete result is shorter than max_count but max_count is
    # less than all possible corrections
    pair_autocorrect_list = []
    for word in autocorrect_set:
        pair_autocorrect_list.append((word, tree.__getitem__(word)))

    pair_autocorrect_list.sort(key=lambda x: x[1], reverse=True)
    return [
        pair[0] for pair in pair_autocorrect_list[: max_count - len(autocomplete_set)]
    ] + list(autocomplete_set)


def all_results(tree, prefix, max_count):
    """
    Given a tree, prefix, and a max_count, returns the autocomplete_set
    and the autocorect_set

    autocomplete_set = result of calling autocomplete function,
                        turned into a set
    autocorrect_set = all the edits made
    """
    autocomplete_set = set(autocomplete(tree, prefix, max_count))
    autocorrect_set = set()

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for i in range(len(prefix)):
        ##insertion
        for letter in alphabet:
            insertion_word = prefix[:i] + letter + prefix[i:]
            if (
                tree.__contains__(insertion_word)
                and insertion_word not in autocomplete_set
            ):
                autocorrect_set.add(insertion_word)
        ##deletion
        deletion_word = prefix[:i] + prefix[i + 1 :]
        if tree.__contains__(deletion_word) and deletion_word not in autocomplete_set:
            autocorrect_set.add(deletion_word)
        ##replacement
        for letter in alphabet:
            replacement_word = prefix[:i] + letter + prefix[i + 1 :]
            if (
                tree.__contains__(replacement_word)
                and replacement_word not in autocomplete_set
            ):
                autocorrect_set.add(replacement_word)
        ##transpose
        if i < len(prefix[:-2]):
            transpose_word = prefix[:i] + prefix[i + 1] + prefix[i] + prefix[i + 2 :]
            if (
                tree.__contains__(transpose_word)
                and transpose_word not in autocomplete_set
            ):
                autocorrect_set.add(transpose_word)

    return autocomplete_set, autocorrect_set


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    return_set = set()

    def word_filter_helper(tree, pattern, prefix=""):
        if not pattern:
            if tree.value:
                return_set.add((prefix, tree.value))
        else:
            char = pattern[0]
            rest_char = pattern[1:]
            children = tree.children
            ##matches the next unmatched character in word no matter what it is
            if char == "?":
                for letter, child in children.items():
                    word_filter_helper(child, rest_char, prefix + letter)
            ##sequence of zero or more of the next unmatched characters in word
            elif char == "*":
                for letter, child in children.items():
                    word_filter_helper(child, pattern, prefix + letter)
                word_filter_helper(tree, rest_char, prefix)
            ##character in the pattern must exactly match the next unmatched character in the word
            elif char in children:
                subtree = tree.__getsubtree__(char)
                word_filter_helper(subtree, rest_char, prefix + char)

    word_filter_helper(tree, pattern)

    return list(return_set)


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    # t = PrefixTree()
    # # t['bat'] = 2
    # # t['bar'] = 1
    # # t['bark'] = 1
    # # print(word_filter(t, "bat"))
    # with open("metamorphosis.txt", encoding="utf-8") as f:
    #     metamorphosis = f.read()
    # with open("taleoftwocities.txt", encoding="utf-8") as f:
    #     tale = f.read()
    # with open("aliceinwonderland.txt", encoding="utf-8") as f:
    #     alice = f.read()
    # with open("pride.txt", encoding="utf-8") as f:
    #     pride = f.read()
    # with open("dracula.txt", encoding="utf-8") as f:
    #     dracula = f.read()
    # tree = word_frequencies(pride)
    # # print(autocomplete(tree, 'gre', 6))
    # # print(word_filter(tree, 'c*h'))
    # # print(word_filter(tree, 'r?c*t'))
    # # print(autocorrect(tree, 'hear', 12))
    # print(autocorrect(tree, 'hear'))
    # # print(len(list(tree)))
    # # words = word_filter(tree,'*')
    # # count = 0
    # # for word in words:
    # #     count += word[1]
    # print(count)
