from __future__ import annotations

from io import StringIO
from locale import localeconv
from math import isclose, modf
from re import compile  # pylint: disable=redefined-builtin
from typing import Any, List, Optional, cast

from vinculum.log import log
from vinculum.math import greatest_common_divisor, int_to_buffer, string_to_int

DECIMAL_POINT = str(localeconv()["decimal_point"])

DECIMAL_PATTERN = compile(rf"^(-?\d+)(?:\{DECIMAL_POINT}(\d+))?$")
FRACTION_PATTERN = compile(r"^(\d+)/(\d+)$")


class Rational:
    """
    A rational number.

    For example, to describe the rational number 3/2 (decimal 1.5), the
    `numerator` is 3 and `denominator` is 2.
    """

    def __init__(self, numerator: int, denominator: int = 1) -> None:
        self._numerator = numerator
        self._denominator = denominator

        if self._denominator < 0:
            self._denominator = abs(self._denominator)
            self._numerator = self._numerator * -1

    def __add__(self, right: Any) -> Rational:
        if right == 0:
            log.debug("__add__ taking a shortcut to self")
            return self

        if isinstance(right, int):
            log.debug("__add__ adding integer %i", right)
            return Rational(
                self._numerator + (right * self._denominator),
                self._denominator,
            )

        if isinstance(right, Rational):
            log.debug("__add__ adding Rational %s", right)

            if self._denominator == right._denominator:
                return Rational(
                    self._numerator + right._numerator,
                    self._denominator,
                )

            new_self_numerator = self._numerator * right._denominator
            new_right_numerator = right._numerator * self._denominator

            return Rational(
                new_self_numerator + new_right_numerator,
                self._denominator * right._denominator,
            )

        a, b = self.comparable_with_self(right)
        f = Rational(a.numerator + b.numerator, a.denominator)
        return f.reduced

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, float):
            return isclose(float(self), other)

        a, b = self.comparable_with_self(other)
        return a.numerator == b.numerator

    def __float__(self) -> float:
        return self._numerator / self._denominator

    def __floordiv__(self, other: Any) -> Rational:
        a, b = self.comparable_with_self(other)
        true_result = a * b.reciprocal
        return Rational(true_result.integral)

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, float):
            return float(self) >= other

        a, b = self.comparable_with_self(other)
        return a.numerator >= b.numerator

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, float):
            return float(self) > other

        a, b = self.comparable_with_self(other)
        return a.numerator > b.numerator

    def __int__(self) -> int:
        return self.integral

    def __le__(self, other: Any) -> bool:
        if isinstance(other, float):
            return float(self) <= other

        a, b = self.comparable_with_self(other)
        return a.numerator <= b.numerator

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, float):
            return float(self) < other

        a, b = self.comparable_with_self(other)
        return a.numerator < b.numerator

    def __mul__(self, other: Any) -> Rational:
        if other == 0:
            log.debug("__mul__ taking a shortcut to 0")
            return ZERO

        if other == 1:
            log.debug("__mul__ taking a shortcut to self")
            return self

        if isinstance(other, int):
            log.debug("__mul__ multiplying by integer %i", other)
            return Rational(
                self._numerator * other,
                self._denominator,
            )

        if isinstance(other, Rational):
            log.debug("__mul__ multiplying by Rational %s", other)
            return Rational(
                self._numerator * other._numerator,
                self._denominator * other._denominator,
            )

        other = Rational.from_any(other)
        result = Rational(
            self.numerator * other.numerator,
            self.denominator * other.denominator,
        )
        return result.reduced

    def __radd__(self, other: Any) -> Rational:
        if other == 0:
            log.debug("__radd__ taking a shortcut to self")
            return self

        if isinstance(other, int):
            log.debug("__radd__ adding integer %i", other)
            return Rational(
                self._numerator + (other * self._denominator),
                self._denominator,
            )

        a, b = self.comparable_with_self(other)
        f = Rational(b.numerator + a.numerator, a.denominator)
        return f.reduced

    def __repr__(self) -> str:
        try:
            return f"{self._numerator}/{self._denominator}"
        except ValueError:
            # Raised if CVE-2020-10735
            # https://github.com/python/cpython/issues/95778 is violated.

            result = StringIO()

            int_to_buffer(
                self._numerator,
                result,
            )

            result.write("/")

            int_to_buffer(
                self._denominator,
                result,
            )

            return result.getvalue()

    def __rfloordiv__(self, other: Any) -> Rational:
        a, b = self.comparable_with_self(other)
        true_result = b * a.reciprocal
        return Rational(true_result.integral)

    def __rmul__(self, other: Any) -> Rational:
        if other == 0:
            log.debug("__rmul__ taking a shortcut to 0")
            return ZERO

        if other == 1:
            log.debug("__rmul__ taking a shortcut to self")
            return self

        if isinstance(other, int):
            log.debug("__rmul__ multiplying by integer %i", other)
            return Rational(
                self._numerator * other,
                self._denominator,
            )

        other = Rational.from_any(other)
        result = Rational(
            other.numerator * self.numerator,
            other.denominator * self.denominator,
        )
        return result.reduced

    def __rsub__(self, left: Any) -> Rational:
        a, b = self.comparable_with_self(left)
        f = Rational(b.numerator - a.numerator, a.denominator)
        return f.reduced

    def __rtruediv__(self, other: Any) -> Rational:
        a, b = self.comparable_with_self(other)
        return b * a.reciprocal

    def __sub__(self, right: Any) -> Rational:
        if right == 0:
            log.debug("__sub__ taking a shortcut to 0")
            return self

        if isinstance(right, Rational):
            log.debug("__sub__ subtracting Rational %s", right)

            if self._denominator == right._denominator:
                return Rational(
                    self._numerator - right._numerator,
                    self._denominator,
                )

            new_left_numerator = self._numerator * right._denominator
            new_right_numerator = right._numerator * self._denominator

            return Rational(
                new_left_numerator - new_right_numerator,
                self._denominator * right._denominator,
            )

        a, b = self.comparable_with_self(right)
        f = Rational(a.numerator - b.numerator, a.denominator)
        return f.reduced

    def __truediv__(self, other: Any) -> Rational:
        a, b = self.comparable_with_self(other)
        return a * b.reciprocal

    @staticmethod
    def comparable(a: Rational, b: Rational) -> tuple[Rational, Rational]:
        """
        Converts rational numbers `a` and `b` to the same denominator.
        """

        if a.denominator == b.denominator:
            return a, b

        d = a.denominator * b.denominator

        return (
            Rational(
                a.numerator * b.denominator,
                d,
            ),
            Rational(
                b.numerator * a.denominator,
                d,
            ),
        )

    def comparable_with_self(self, value: Any) -> tuple[Rational, Rational]:
        """
        Converts this and `value` to rational numbers of the same denominator.
        """

        value = Rational.from_any(value)
        return Rational.comparable(self, value)

    def decimal(
        self,
        max_dp: int = 100,
        recursion: bool = True,
        recurring_prefix: Optional[str] = "\u0307",
    ) -> str:
        """
        Gets a decimal string that describes this rational number. For example,
        3/2 in a British English locale is rendered as "1.5".

        Recurring digits are styled with overhead dots. For example, 1/3
        returns "0.̇3".

        This function is aware of and avoids CVE-2020-10735:
        https://github.com/python/cpython/issues/95778

        `max_dp` describes the maximum number of decimal places to render. This
        is limited only by your available memory and patience.

        `recursion` describes whether or not to track recursion. There is a
        slight performance benefit to disabling this if you don't care.

        `recurring_prefix` describes the string with which to prefix each
        recurring digit. This is \u0307 (the Unicode "Dot Above" character) by
        default, but you might prefer \u0305 ("Combining Overline").
        """

        log.debug("Rendering %s to a decimal string", self)

        result = StringIO()

        positive = self._numerator >= 0

        integral = abs(self._numerator) // self._denominator
        if not positive:
            integral *= -1

        result = StringIO()

        int_to_buffer(integral, result)

        result.write(DECIMAL_POINT)

        recursion_track: Optional[List[int]] = [] if recursion else None
        remainder = (abs(self._numerator) % self._denominator) * 10

        added_non_zero = False
        decimal_places = 0
        fractional = 0
        leading_zeros = 0
        recurring_count = 0

        while True:
            i = remainder // self._denominator
            remainder = (remainder % self._denominator) * 10

            if recursion_track is not None and (remainder in recursion_track):
                index_of = recursion_track.index(remainder)
                recurring_count = len(recursion_track) - index_of
                break

            fractional *= 10
            fractional += i

            if i > 0:
                added_non_zero = True
            elif not added_non_zero:
                leading_zeros += 1

            decimal_places += 1

            if remainder == 0 or decimal_places >= max_dp:
                break

            if recursion_track is not None:
                recursion_track.append(remainder)

        int_to_buffer(
            fractional,
            result,
            leading_zeros=leading_zeros,
            recurring_count=recurring_count,
            recurring_prefix=recurring_prefix,
        )

        return result.getvalue()

    @property
    def denominator(self) -> int:
        """
        Denominator.

        For example, given the rational number 3/2, the denominator is "2".
        """

        return self._denominator

    @property
    def fractional(self) -> Rational:
        """
        The fractional part of this rational number.

        For example, for 3/2, the integral part is 1 (2/2) and the fractional
        part is 1/2.
        """

        return self - self.integral

    @classmethod
    def from_any(cls, value: Any) -> Rational:
        """
        Converts `value` to a rational number.

        Raises `TypeError` if `value` cannot be converted to a rational number.
        """

        if isinstance(value, int):
            return Rational(value)

        if isinstance(value, float):
            return Rational.from_float(value)

        if isinstance(value, str):
            return Rational.from_string(value)

        if isinstance(value, Rational):
            return value

        raise TypeError(
            f"Cannot create a {cls.__name__} from {repr(value)} "
            f"({value.__class__.__name__})"
        )

    @classmethod
    def from_float(cls, f: float) -> Rational:
        log.debug("Parsing float %s", f)

        positive = f >= 0
        f = abs(f)

        fractional, i = modf(f)

        result = Rational(int(i))
        over = 10

        while fractional != 0:
            f *= 10
            fractional, i = modf(f)
            digit = int(i) % 10
            result += Rational(digit, over)
            over *= 10

        if not positive:
            result *= -1

        return result

    @classmethod
    def from_string(cls, string: str) -> Rational:
        """
        Parses `string` as either a decimal or fraction.
        """

        match = DECIMAL_PATTERN.match(string)
        if match is not None:
            log.debug('Parsing "%s" as a decimal', string)

            groups = match.groups(0)

            integral_str = cast(str, groups[0])

            if negative := string.startswith("-"):
                integral_str = integral_str[1:]

            integral_int = string_to_int(integral_str)
            integral = Rational(integral_int)

            decimal_group = groups[1]

            log.debug(
                'The decimal group of "%s" is %s (%s)',
                string,
                decimal_group,
                decimal_group.__class__.__name__,
            )

            if decimal_group == 0:
                decimal = Rational.ZERO()
            else:
                d = cast(str, decimal_group)
                decimal = Rational(string_to_int(d), 10 ** len(d))

            absolute = integral + decimal
            multiplier = -1 if negative else 1

            return (absolute * multiplier).reduced

        match = FRACTION_PATTERN.match(string)
        if match is not None:
            log.debug('Parsing "%s" as a fraction', string)

            groups = match.groups(0)
            numerator_group = groups[0]

            log.debug(
                'The numerator group of "%s" is %s (%s)',
                string,
                numerator_group,
                numerator_group.__class__.__name__,
            )

            denominator_group = groups[1]

            log.debug(
                'The denominator group of "%s" is %s (%s)',
                string,
                denominator_group,
                denominator_group.__class__.__name__,
            )

            return Rational(
                string_to_int(cast(str, numerator_group)),
                string_to_int(cast(str, denominator_group)),
            )

        raise ValueError(f'Cannot parse "{string}" as decimal or fraction')

    @property
    def integral(self) -> int:
        """
        The integral part of this rational number.

        For example, for 3/2, the integral part is 1 (2/2) and the fractional
        part is 1/2.
        """

        return self._numerator // self._denominator

    @property
    def numerator(self) -> int:
        """
        Numerator.

        For example, given the rational number 3/2, the numerator is "3".
        """

        return self._numerator

    @property
    def reciprocal(self) -> Rational:
        """
        Gets the reciprocal of the rational number.

        For example, the reciprocal of 2/3 is 3/2.
        """

        return Rational(self.denominator, self.numerator)

    @property
    def reduced(self) -> Rational:
        """
        Gets the rational number in its reduced form.

        For example, 15/30 reduces to 1/2.
        """

        gcf = greatest_common_divisor(self._numerator, self._denominator)

        if gcf in (0, 1):
            return self

        return Rational(
            self._numerator // gcf,
            self._denominator // gcf,
        )

    @staticmethod
    def ZERO() -> Rational:
        """
        Zero.
        """

        return ZERO


ZERO = Rational(0)
"""
Zero.
"""
