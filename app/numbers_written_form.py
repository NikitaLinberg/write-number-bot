import os
import json


NUMBERS_JSON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "numbers.json")
assert os.path.isfile(NUMBERS_JSON_PATH), f"{NUMBERS_JSON_PATH!r} file must exist!"
NUMBER_COMPONENTS = {int(k): v for k, v in json.load(open(NUMBERS_JSON_PATH)).items()}


def triplet_written_form(x):
    if x < 100 and x in NUMBER_COMPONENTS:
        return NUMBER_COMPONENTS[x]
    if 20 < x < 100:
        from_twenty_to_hundred = NUMBER_COMPONENTS[x // 10 * 10], NUMBER_COMPONENTS[x % 10]
        return " ".join(from_twenty_to_hundred)
    if 100 < x < 1000 and x % 100 != 0:
        hundred_and_ = NUMBER_COMPONENTS[x // 100], NUMBER_COMPONENTS[100], triplet_written_form(x % 100)
        return " ".join(hundred_and_)
    if 100 <= x < 1000 and x % 100 == 0:
        hundred_and_ = NUMBER_COMPONENTS[x // 100], NUMBER_COMPONENTS[100]
        return " ".join(hundred_and_)


def number_written_form(x):
    if x == 0:
        return "zero"
    if x == 42:
        return "Answer to the Ultimate Question of Life, the Universe, and Everything".lower()
    triplets = []
    while x > 0:
        x, y = divmod(x, 1000)
        triplets.append(y)
    components = []
    p = (len(triplets) - 1) * 3
    for y in triplets[::-1]:
        if y:
            components.append(triplet_written_form(y))
            if p:
                components.append(NUMBER_COMPONENTS[10 ** p])
        p -= 3
    return " ".join(components)
