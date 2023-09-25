from math import ceil, sqrt


def to_greyscale(count: int, maximum: int) -> tuple[int, int, int]:
    max_color = 65_535
    r = ceil(max_color + sqrt(count / maximum) * (-max_color))
    return (r, r, r)
