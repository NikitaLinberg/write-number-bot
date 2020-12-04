import json
import os
import random


NUMBERS_JSON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "numbers.json")
assert os.path.isfile(NUMBERS_JSON_PATH), f"{NUMBERS_JSON_PATH!r} file must exist!"
NUMBER_COMPONENTS = {int(k): v for k, v in json.load(open(NUMBERS_JSON_PATH)).items()}
WORD_COMPONENTS = {k: int(v) for v, k in json.load(open("numbers.json")).items()}
MAX_RANK = max(NUMBER_COMPONENTS.items())

MEANING_OF_LIFE = "Answer to the Ultimate Question of Life, the Universe, and Everything"


def _parse_number_group(nums, source_string):
    """ Combine a group of numbers into a single integer, from 1 up to 999.
        source_string - The source string of the numbers, for detailed exceptions.
    """
    hundreds = 0
    if nums[0] == 100:
        raise Exception(f"A number can't start on a \"hundred\", please use \"one hundred\"")
    if len(nums) >= 2 and nums[1] == 100:
        if 0 <= nums[0] <= 9:
            hundreds = nums[0] * 100
            nums = nums[2:]
            source_string = " ".join(source_string.split()[-2:])
        else:
            raise Exception(f"Expected a number of hundreds from 1 up to 9, instead got: {source_string!r}")
    if len(nums) == 0:
        return hundreds
    if len(nums) == 1:
        ones = nums[0]
        if 1 <= ones <= 90:
            return hundreds + ones
        raise Exception(f"Expected a one-word number from range [1;90], instead got {source_string!r}")
    if len(nums) == 2:
        tens, ones = nums
        if 20 <= tens <= 90 and 1 <= ones <= 9:
            return hundreds + tens + ones
        raise Exception(f"Expected a valid two-digit number, instead got: {source_string!r}")
    raise Exception(f"Expected a valid quantity from range [1;999], instead got: {source_string!r}")


def parse_number_written_form(s):
    """ Inverse of the number_written_form function - parse the number string into an integer.
    """
    assert isinstance(s, str)
    s = s.lower().strip()
    if not s:
        raise Exception(f"Expected a string of words, instead got an empty string")
    if s == "zero":
        return 0
    if s == MEANING_OF_LIFE.lower() or s == MEANING_OF_LIFE.lower().replace(",", ""):
        return 42
    num_group, word_group, previous_rank, res = [], [], None, 0
    for w in s.split():
        if w == "zero":
            raise Exception(f"\"Zero\" can only be used if it's alone")
        if w not in WORD_COMPONENTS:
            if w.endswith("illion"):
                raise Exception(f"Unknown rank: {w!r}, this program only knows ranks up to " +
                                f"{MAX_RANK[1]!r} ({MAX_RANK[0]:.0e})")
            raise Exception(f"This program can only handle numbers. It expected number word, instead got: {w!r}")
        x = WORD_COMPONENTS[w]
        if x and x % 1000 == 0:
            if previous_rank is not None and x >= previous_rank:
                raise Exception(f"Expected each number rank to be less than the previous rank, instead got rank {w!r}" +
                                f" ({x:.0e}) after rank {NUMBER_COMPONENTS[previous_rank]!r} ({previous_rank:.0e})")
            if not num_group:
                raise Exception(f"Expected to get quantity before each rank, instead got rank {w!r} without a quantity")
            quantity = _parse_number_group(num_group, source_string=" ".join(word_group))
            assert 1 <= quantity < 1000
            res += quantity * x
            num_group, word_group = [], []
            previous_rank = x
        else:
            num_group.append(x)
            word_group.append(w)
    if num_group:
        res += _parse_number_group(num_group, source_string=" ".join(word_group))
    return res


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
        return MEANING_OF_LIFE
    if x >= MAX_RANK[0] * 1000:
        raise Exception(f"Sorry, can't write number {x}. This program only knows ranks up to " +
                        f"{MAX_RANK[1]!r} ({MAX_RANK[0]:.0e})")
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


if __name__ == "__main__":
    print("running some parse_number_written_form tests...")
    for test_num in range(1001):
        test_s = number_written_form(test_num)
        res_num = parse_number_written_form(test_s)
        assert res_num == test_num, f"Expected to parse {test_s!r} into {test_num} instead got {res_num}"
    for rank in range(3, 37):
        start = 10 ** rank
        test_num = random.randrange(start, start * 10)
        test_s = number_written_form(test_num)
        res_num = parse_number_written_form(test_s)
        assert res_num == test_num, f"Expected to parse {test_s!r} into {test_num} instead got {res_num}"
    print("passed all tests!")
