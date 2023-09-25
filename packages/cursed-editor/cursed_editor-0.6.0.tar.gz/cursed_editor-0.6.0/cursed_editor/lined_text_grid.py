#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2023 Philip Zerull

# This file is part of "The Cursed Editor"

# "The Cursed Editor" is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from typing import Union, Tuple, Optional, List

from . import selection
from .coordinate import Coordinate
from .mutable_string import MutableString


class LinedTextGrid:
    def __init__(
        self, mutable_string: Union[MutableString, str], line_ending: str = "\n"
    ) -> None:
        if isinstance(mutable_string, str):
            mutable_string = MutableString(mutable_string)
        self._mutable_string: MutableString = mutable_string
        self._line_ending: str = line_ending

    def __repr__(self) -> str:
        return f"<LinedTextGrid content={repr(str(self))}>"

    def __str__(self) -> str:
        return str(self._mutable_string)

    def to_string(self) -> str:
        return str(self)

    @property
    def line_ending(self) -> str:
        return self._line_ending

    def _get_underlying_index(self, *, coordinate: Coordinate) -> int:
        text = str(self)
        lines = text.split(self._line_ending)
        y = max(0, coordinate.y)
        if y >= len(lines):
            return len(text)
        prior_lines = lines[:y]
        current_line = lines[y] + self._line_ending
        x = min(max(0, coordinate.x), len(current_line) - 1)
        current_line = current_line[:x]
        lines = prior_lines + [current_line]
        combined = self._line_ending.join(lines)
        underlying_index = len(combined)
        return underlying_index

    def coordinate_in_bounds(self, *, coordinate: Coordinate) -> bool:
        if not self._y_coordinate_in_bounds(coordinate=coordinate):
            return False
        if coordinate.x < 0:
            return False
        text = str(self)
        lines = text.split(self._line_ending)
        line = lines[coordinate.y]
        return coordinate.x < len(line)

    def _y_coordinate_in_bounds(self, *, coordinate: Coordinate) -> bool:
        text = str(self)
        lines = text.split(self._line_ending)
        return 0 <= coordinate.y < len(lines)

    def __getitem__(
        self,
        coordinate_or_tuple: Union[Coordinate, Tuple[Coordinate, Coordinate]],
    ) -> str:
        if isinstance(coordinate_or_tuple, Coordinate):
            index = self._get_underlying_index(coordinate=coordinate_or_tuple)
            return self._mutable_string[index]
        text = str(self)
        start, end = coordinate_or_tuple
        return selection.linear(
            text=text, start=start, end=end, line_break=self.line_ending
        )

    def delete(self, *, start: Coordinate, end: Coordinate) -> "LinedTextGrid":
        text = str(self)
        result = selection.except_linear(
            text=text, start=start, end=end, line_break=self.line_ending
        )
        self._mutable_string.delete()
        self.append(text=result)
        return self

    def insert(self, *, text: str, coordinate: Coordinate) -> "LinedTextGrid":
        index = self._get_underlying_index(coordinate=coordinate)
        self._mutable_string.insert(text=text, index=index)
        return self

    def append(self, *, text: str) -> "LinedTextGrid":
        self._mutable_string.append(text=text)
        return self

    def prepend(self, *, text: str) -> "LinedTextGrid":
        self._mutable_string.prepend(text=text)
        return self

    def lines(
        self, *, start: Optional[int] = None, end: Optional[int] = None
    ) -> List[str]:
        return selection.text_lines(
            text=str(self),
            line_ending=self._line_ending,
            start=start,
            end=end,
        )

    def search(
        self, *, needle: str, case_sensitive: bool = True
    ) -> List[Coordinate]:
        result = []
        for index in self._mutable_string.search(
            needle=needle, case_sensitive=case_sensitive
        ):
            result.append(self._coordinate_from_index(index=index))
        return result

    def _coordinate_from_index(self, *, index: int) -> Coordinate:
        filtered_content = str(self)[:index]
        lines = filtered_content.split(self.line_ending)
        y = len(lines) - 1
        x = len(lines[-1])
        return Coordinate(x=x, y=y)


LinedTextGrid.__init__.__doc__ = """
    Create a new LinedTextGrid by either providing a str or MutableString.
    >>> LinedTextGrid("hello")
    <LinedTextGrid content='hello'>

    >>> LinedTextGrid(MutableString("hello"))
    <LinedTextGrid content='hello'>
"""

LinedTextGrid.__str__.__doc__ = """
    Returns the contents of the LinedTextGrid as a str
    >>> str(LinedTextGrid("a b c d e f g"))
    'a b c d e f g'
"""

LinedTextGrid.__getitem__.__doc__ = r"""
    Returns the string between teh provided positions
    >>> grid = LinedTextGrid("first\nsecond\nthird")
    >>> grid[Coordinate(x=1, y=1)]
    'e'

    >>> grid[Coordinate(x=2, y=0), Coordinate(x=10, y=1)]
    'rst\nsecond\n'
"""

LinedTextGrid.to_string.__doc__ = """
    Equivalent to str(self).  Helpful for method chaining.
    >>> LinedTextGrid("a b c d e f g").to_string()
    'a b c d e f g'
"""

LinedTextGrid.coordinate_in_bounds.__doc__ = r"""
    Checks to see if the coordinate is in the bounds of the string.

    >>> grid = LinedTextGrid("first\nsecond\nthird")
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=1, y=1))
    True
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=-1, y=1))
    False
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=5, y=1))
    True
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=6, y=1))
    False
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=7000, y=1))
    False
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=3, y=-1))
    False
    >>> grid.coordinate_in_bounds(coordinate=Coordinate(x=3, y=10))
    False
"""

LinedTextGrid.line_ending.__doc__ = r"""
    Returns the LinedTextGrid's line ending sequence.

    >>> LinedTextGrid("first\nsecond\nthird\n").line_ending
    '\n'
"""

LinedTextGrid.lines.__doc__ = r"""
    Returns a list of strings containing the text of lines between
    start and end (inclusive).

    >>> grid = LinedTextGrid("zero\none\ntwo\nthree\nfour\nfive\nsix")
    >>> grid.lines(start=2, end=4)
    ['two', 'three', 'four']

    >>> grid.lines(start=5, end=5)
    ['five']

    If end is not provided, then this will return all lines starting
    at start and proceeding to the end of the string

    >>> grid.lines(start=3)
    ['three', 'four', 'five', 'six']

    Similarly, if start is not provided, then this will return all
    lines from the beginning of the string through end.

    >>> grid.lines(end=3)
    ['zero', 'one', 'two', 'three']

    If both start and end are ommitted, then all lines are returned.

    >>> grid.lines()
    ['zero', 'one', 'two', 'three', 'four', 'five', 'six']

    Naturally, start and end, must be ints

    >>> grid.lines(start="moose")
    Traceback (most recent call last):
    TypeError: start parameter must be either None or an int

    >>> grid.lines(end="moose")
    Traceback (most recent call last):
    TypeError: end parameter must be either None or an int

    The start and end parameters are automatically capped to be at
    least zero and at most the number of lines minus one.

    >>> grid.lines(start=-1)
    ['zero', 'one', 'two', 'three', 'four', 'five', 'six']

    >>> grid.lines(start=7)
    ['six']

    And end must be greater than or equal to start and less than
    the number of lines in the string.

    >>> grid.lines(start=4, end=3)
    Traceback (most recent call last):
    ValueError: end must be greater than start

    >>> grid.lines(start=4, end=7)
    ['four', 'five', 'six']
"""

LinedTextGrid.delete.__doc__ = r"""
    Deletes text between the given coordinates (inclusive).

    >>> grid = LinedTextGrid("first\nsecond\nthird")
    >>> grid.delete(start=Coordinate(x=0, y=1), end=Coordinate(x=0, y=2))
    <LinedTextGrid content='first\nhird'>

    >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
    >>> grid.delete(start=Coordinate(x=0, y=3), end=Coordinate(x=100, y=3))
    <LinedTextGrid content='first\nsecond\nthird\nfifth\n'>

    >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
    >>> grid.delete(start=Coordinate(x=-8, y=3), end=Coordinate(x=100, y=3))
    <LinedTextGrid content='first\nsecond\nthird\nfifth\n'>

    >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
    >>> grid.delete(start=Coordinate(x=99, y=2), end=Coordinate(x=99, y=3))
    <LinedTextGrid content='first\nsecond\nthird\nfifth\n'>

    >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
    >>> grid.delete(start=Coordinate(x=-100, y=3), end=Coordinate(x=2, y=3))
    <LinedTextGrid content='first\nsecond\nthird\nrth\nfifth\n'>

    >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
    >>> grid.delete(start=Coordinate(x=0, y=2), end=Coordinate(x=100, y=100))
    <LinedTextGrid content='first\nsecond\n'>

    >>> grid = LinedTextGrid("first\nsecond\nthird\nfourth\nfifth\n")
    >>> grid.delete(start=Coordinate(x=8, y=-1), end=Coordinate(x=5, y=2))
    <LinedTextGrid content='fourth\nfifth\n'>
"""

LinedTextGrid.append.__doc__ = r"""
    Appends the given text to the underlying value.
    Returns a reference to self to support method chaining.

    >>> LinedTextGrid("I eat\n").append(text="red meat")
    <LinedTextGrid content='I eat\nred meat'>

    This will raise a ValueError if the text is not a string

    >>> LinedTextGrid("I eat\n").append(text=8)
    Traceback (most recent call last):
    TypeError: text parameter must be a str object
"""

LinedTextGrid.prepend.__doc__ = r"""
    Prepends the gien text to the underlying value.
    Returns a reference to self to support method chaining.

    >>> LinedTextGrid("red meat\n").prepend(text="I eat ")
    <LinedTextGrid content='I eat red meat\n'>

    This will raise a ValueError if the text is not a string

    >>> LinedTextGrid("I eat\n").prepend(text=8)
    Traceback (most recent call last):
    TypeError: text parameter must be a str object
"""
