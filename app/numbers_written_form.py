import json


NUMBER_COMPONENTS = {int(k): v for k, v in json.load(open("numbers.json")).items()}


def number_written_form(x):
    if x in NUMBER_COMPONENTS and x < 100:
        return NUMBER_COMPONENTS[x]
    if 20 < x < 100:
        from_twenty_to_hundred = NUMBER_COMPONENTS[x // 10 * 10], NUMBER_COMPONENTS[x % 10]
        return " ".join(from_twenty_to_hundred)
    raise NotImplementedError(f"number_written_form is not implemented for x={x}")
