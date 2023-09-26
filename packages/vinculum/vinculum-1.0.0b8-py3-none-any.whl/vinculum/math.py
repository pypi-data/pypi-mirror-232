from io import StringIO
from typing import List, Optional


def greatest_common_divisor(a: int, b: int) -> int:
    """
    Gets the greatest common divisor of `a` and `b`.
    """

    biggest = max(a, b)
    smallest = min(a, b)

    if smallest in (0, biggest):
        return smallest

    while True:
        remainder = biggest % smallest

        if remainder == 0:
            return smallest

        biggest = smallest
        smallest = remainder


def int_to_buffer(
    number: int,
    buffer: StringIO,
    leading_zeros: int = 0,
    recurring_count: int = 0,
    recurring_prefix: Optional[str] = "\u0307",
) -> None:
    """
    Writes the integer `number` to string `buffer`.

    Avoids CVE-2020-10735: https://github.com/python/cpython/issues/95778

    `leading_zeros` describes the number of leading zeros to prefix before
    `number`.

    `recurring_count` describes the count of least-significant digits that
    should be formatted as recurring.

    `recurring_prefix` describes the string with which to prefix each recurring
    digit. This is \u0307 (the Unicode "Dot Above" character) by default, but
    you might prefer \u0305 ("Combining Overline").
    """

    positive = number >= 0
    number = abs(number)

    wip: List[str] = []

    min_leading_zeros = 1 if number == 0 else leading_zeros
    leading_zeros = max(leading_zeros, min_leading_zeros)

    e = 0
    while (10**e) <= number:
        digit = int(number // 10**e) % 10
        wip.append(str(digit))
        e += 1

    if not positive:
        buffer.write("-")

    for _ in range(leading_zeros):
        buffer.write("0")

    recur_from = len(wip) - recurring_count

    for index, c in enumerate(reversed(wip)):
        if recurring_prefix is not None and index >= recur_from:
            buffer.write(recurring_prefix)

        buffer.write(c)


def string_to_int(string: str) -> int:
    """
    Converts `string` to an integer.

    Avoids CVE-2020-10735: https://github.com/python/cpython/issues/95778
    """

    result = 0
    string_len = len(string)

    for index, digit in enumerate(string):
        e = string_len - (index + 1)
        result += int(digit) * (10**e)

    return result
