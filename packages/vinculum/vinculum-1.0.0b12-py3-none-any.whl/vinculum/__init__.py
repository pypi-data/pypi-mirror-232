"""
&copy; 2022-2023 Cariad Eccleston and released under the MIT License.

For usage and support, see https://github.com/cariad/vinculum.
"""

from importlib.resources import files

from vinculum.math import greatest_common_divisor, int_to_buffer, string_to_int
from vinculum.rational import Rational


def version() -> str:
    """
    Gets the package's version.
    """

    with files(__package__).joinpath("VERSION").open("r") as t:
        return t.readline().strip()


__all__ = [
    "Rational",
    "greatest_common_divisor",
    "int_to_buffer",
    "string_to_int",
    "version",
]
