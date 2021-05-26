import string

from collections import deque

# https://en.wikipedia.org/wiki/Damerau%E2%80%93Levenshtein_distance
# -> 80% of typos are 1 insertion, deletion, substitution, or (adjacent) transposition (swap)
# https://dl.acm.org/doi/10.1145/363958.363994 -> https://sci-hub.se/10.1145/363958.363994
# Survey: https://ijcttjournal.org/Volume4/issue-3/IJCTT-V4I3P134.pdf (probabilistic from corpus, etc)
# consider common typo index: https://www.dcs.bbk.ac.uk/~ROGER/corpora.html
# https://stackoverflow.com/questions/29233888/edit-distance-such-as-levenshtein-taking-into-account-proximity-on-keyboard
# Example of a post: https://towardsdatascience.com/symspell-vs-bk-tree-100x-faster-fuzzy-string-search-spell-checking-c4f10d80a078
# https://norvig.com/spell-correct.html - similar to this, but im not using probability

# Also try common things for test passphrase:
# https://github.com/danielmiessler/SecLists/tree/master/Passwords/Common-Credentials
# https://thehacktoday.com/password-cracking-dictionarys-download-for-free/

# Blog idea:
# https://github.com/danielmiessler/SecLists/blob/master/Passwords/Common-Credentials/four-digit-pin-codes-sorted-by-frequency-withcount.csv
# Create de bruijn sequence that maximizes the probability

# TODO:
# map-reduce to derive keys and addresses?
# Make it work in a distributed way
# make it work in a way that can accept new requests (a service)
# make it work with GPU
# make it work in a way that can scale to have more workers
# develop pipeline to save partial work
# optimize it so most common typos go to the top
# add checking for wordlists
# add combination of 1password words
# profile and optimize
# find substrings and chunk their typos


def insertions(a, b):
    return string.ascii_lowercase


def substitutions(x):
    return string.ascii_lowercase


def concat(*tokens):
    return "".join(tokens)


def generate_insertions(s):
    # for every position, insert a character
    for i in range(len(s)):
        # make a way to weight these...
        xs = insertions(s[i-1:i], s[i:i+1])
        yield from (concat(s[:i], x, s[i:]) for x in xs)


def generate_substitutions(s):
    for i in range(len(s)):
        xs = substitutions(s[i])
        yield from (concat(s[:i], x, s[i+1:]) for x in xs)


def generate_transpositions(s):
    return (concat(s[:i], s[i+1], s[i], s[i+2:]) for i in range(len(s) - 1))


def generate_deletions(s):
    for i in range(len(s)):
        yield concat(s[:i], s[i+1:])


class Typos(object):
    def __init__(self, root, max_edit_distance=None, visited=None):
        self.root = root
        self.visited = visited or set()
        self.frontier = deque([(0, root)])
        self.max_edit_distance = max_edit_distance

    def __iter__(self):
        if self.visited and not self.frontier:
            return iter(self.visited)

        def neighbors(s):
            yield from generate_deletions(s)
            yield from generate_insertions(s)
            yield from generate_substitutions(s)
            yield from generate_transpositions(s)

        def prune(d, s):
            if self.max_edit_distance and d > self.max_edit_distance:
                return True

            if s in self.visited:
                return True

            return False

        while self.frontier:
            d, s = self.frontier.popleft()

            self.visited.add(s)
            yield s

            self.frontier.extend((d+1, n) for n in neighbors(s) if not prune(d+1,n))

