import os
import json


NUMBERS_JSON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "numbers.json")
assert os.path.isfile(NUMBERS_JSON_PATH), f"{NUMBERS_JSON_PATH!r} file must exist!"
NUMBER_COMPONENTS = {int(k): v for k, v in json.load(open(NUMBERS_JSON_PATH)).items()}
WORD_COMPONENTS = {k: int(v) for v, k in json.load(open("numbers.json")).items()}


def word_pars_form(words):
    count = 0
    ints = []
    for word in words:
        if word in WORD_COMPONENTS:
            ints.append(WORD_COMPONENTS[word])
    if "hundred" in words:
        if ints[0] < 10:
            count = ints[0] * 100
            ints = ints[2:]
            words = words[2:]
        else:
            raise Exception("Error. I can work with hundreds up to 9")
    if len(ints) >= 3:
        raise Exception(f"Error. I expected at most two words, instead got: {words!r}")
    if len(ints) == 2:
        if 20 <= ints[0] <= 90:
            count += ints[0]
            ints.pop(0)
        else:
            raise Exception(f"Error. I expected a valid two-digit number, instead got: {words!r}")
    if len(ints) == 1:
        ones = ints[0]
        if 1 <= ones <= 9 or count % 100 == 0 and 10 <= ones <= 99:
            count += ones
        else:
            raise Exception(f"Error. I expected a valid number, insted got {words!r}")
    return count


def pars_number_written_form(words):
    digits = ["thousand", "million", "billion", "trillion", "quadrillion", "quintillion", "sextillion", "septillion",
              "octillion", "nonillion", "decillion", "undecillion"]
    words = words.lower().split()
    if words == ["zero"]:
        return 0
    if "zero" in words:
        raise Exception(f"Error. 'Zero' can only be usedif it's alone")
    triple_words = []
    triple_nums = []
    components = []
    digit_values = 0
    if len(words) == 0:
        return "I expected words, but have empty str"
    for v in words:
        if v not in WORD_COMPONENTS:
            raise Exception(f"Error. This program can only handle numbers. It expected number word, instead got: {v!r}")
        if v in digits:
            triple_nums.append(word_pars_form(triple_words))
            triple_nums.append(WORD_COMPONENTS[v])
            if WORD_COMPONENTS[v] >= digit_values and digit_values != 0 or len(triple_words) == 0:
                raise Exception("Logic error in the text")
            triple_words.clear()
            digit_values = WORD_COMPONENTS[v]
        else:
            triple_words.append(v)
    if len(triple_words) > 0:
        triple_nums.append(word_pars_form(triple_words))
        triple_words.clear()
    for i in range(0, len(triple_nums) - 1, 2):
        triple_nums_val = triple_nums[i] * triple_nums[i + 1]
        components.append(triple_nums_val)
    if len(triple_nums) % 2 != 0:
        components.append(triple_nums[-1])
    return sum(components)


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
