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

import logging
from typing import Optional, Union, Tuple, List

from . import selection
from .coordinate import Coordinate
from .lined_text_grid import LinedTextGrid

logger = logging.getLogger(__name__)


class TabExpandingTextGrid:
    def __init__(
        self, lined_text_grid: LinedTextGrid, tab_size: int = 4
    ) -> None:
        self._lined_text_grid = lined_text_grid
        self._tab_size = tab_size

    def __repr__(self) -> str:
        return f"<TabExpandingTextGrid content={repr(str(self))}>"

    def __str__(self) -> str:
        return self.get_expanded_text()

    def get_expanded_text(self) -> str:
        text = self.get_unexpanded_text()
        return text.replace("\t", "\t" * self._tab_size)

    def get_unexpanded_text(self) -> str:
        return str(self._lined_text_grid)

    def _get_underlying_coordinate(
        self, *, coordinate: Coordinate
    ) -> Coordinate:
        y = coordinate.y
        line = self._lined_text_grid.lines(start=y, end=y)[0]
        ending = self._lined_text_grid.line_ending
        line = line.replace("\t", "\t" * self._tab_size) + ending
        x = min(max(0, coordinate.x), len(line) - 1)
        line = line[:x]
        splitup = line.split("\t" * self._tab_size)
        last = splitup.pop().rstrip("\t")
        splitup.append(last)
        line = "\t".join(splitup)
        return Coordinate(y=y, x=len(line))

    def _get_coordinate_from_underlying(
        self, *, underlying: Coordinate
    ) -> Coordinate:
        y = underlying.y
        line = self._lined_text_grid.lines(start=y, end=y)[0]
        line = line[: underlying.x]
        line = line.replace("\t", "\t" * self._tab_size)
        x = len(line)
        return Coordinate(x=x, y=y)

    def __getitem__(
        self,
        coordinate_or_tuple: Union[Coordinate, Tuple[Coordinate, Coordinate]],
    ) -> str:
        if isinstance(coordinate_or_tuple, Coordinate):
            coord = coordinate_or_tuple
            underlying = self._get_underlying_coordinate(coordinate=coord)
            return self._lined_text_grid[underlying]
        start, end = coordinate_or_tuple
        start = self._get_underlying_coordinate(coordinate=start)
        end = self._get_underlying_coordinate(coordinate=end)
        return self._lined_text_grid[start, end]

    def insert(
        self, *, text: str, coordinate: Coordinate
    ) -> "TabExpandingTextGrid":
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        self._lined_text_grid.insert(text=text, coordinate=underlying)
        return self

    def append(self, *, text: str) -> "TabExpandingTextGrid":
        self._lined_text_grid.append(text=text)
        return self

    def delete(
        self, *, start: Coordinate, end: Coordinate
    ) -> "TabExpandingTextGrid":
        start_index = self._get_underlying_coordinate(coordinate=start)
        end_index = self._get_underlying_coordinate(coordinate=end)
        self._lined_text_grid.delete(start=start_index, end=end_index)
        return self

    def lines(
        self, *, start: Optional[int] = None, end: Optional[int] = None
    ) -> List[str]:
        return selection.text_lines(
            text=str(self),
            line_ending=self._lined_text_grid.line_ending,
            start=start,
            end=end,
        )

    def get_moved_coordinate(
        self,
        *,
        coordinate: Coordinate,
        new_x: Optional[int] = None,
        new_y: Optional[int] = None,
        up: int = 0,
        down: int = 0,
        left: int = 0,
        right: int = 0,
    ) -> Coordinate:
        underlying = self._get_underlying_coordinate(coordinate=coordinate)
        if new_y is None:
            new_y = underlying.y
        new_y = new_y + down - up
        new_y = min(max(0, new_y), len(self._lined_text_grid.lines()) - 1)
        current_line = self._lined_text_grid.lines(start=new_y, end=new_y)[0]
        if new_x is None:
            new_x = underlying.x
        elif new_x == -1:
            new_x = len(current_line)
        new_x = new_x + right - left
        new_x = min(max(0, new_x), len(current_line))
        new_underlying = Coordinate(x=new_x, y=new_y)
        return self._get_coordinate_from_underlying(underlying=new_underlying)

    def search(
        self, *, needle: str, case_sensitive: bool = True
    ) -> List[Coordinate]:
        result = []
        for underlying in self._lined_text_grid.search(
            needle=needle, case_sensitive=case_sensitive
        ):
            coord = self._get_coordinate_from_underlying(underlying=underlying)
            result.append(coord)
        return result


TabExpandingTextGrid.__init__.__doc__ = r"""
    Create a new TabExpandingTextGrid by providing a LinedTextGrid
    and the tab_size (which defaults to four).

    >>> TabExpandingTextGrid(LinedTextGrid("\thello"))
    <TabExpandingTextGrid content='\t\t\t\thello'>

    >>> TabExpandingTextGrid(LinedTextGrid("\thello"), tab_size=2)
    <TabExpandingTextGrid content='\t\thello'>
"""

TabExpandingTextGrid.__getitem__.__doc__ = r"""
    >>> text = "\tone\n\t\ttwo\n\t\tthree"
    >>> grid = TabExpandingTextGrid(LinedTextGrid(text), tab_size=2)
    >>> grid[Coordinate(x=5, y=1)]
    'w'

    >>> grid[Coordinate(x=2, y=1), Coordinate(x=7, y=2)]
    '\ttwo\n\t\tthre'
"""

TabExpandingTextGrid.get_moved_coordinate.__doc__ = r"""
    >>> grid = TabExpandingTextGrid(LinedTextGrid("I\thave\t\tlots of\ttabs"))
    >>> start = Coordinate(x=0, y=0)
    >>> end = grid.get_moved_coordinate(coordinate=start, right=1)
    >>> end
    <Coordinate x=1, y=0>

    >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
    >>> end
    <Coordinate x=5, y=0>

    >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
    >>> end
    <Coordinate x=6, y=0>

    >>> end = grid.get_moved_coordinate(coordinate=end, right=2)
    >>> end
    <Coordinate x=8, y=0>

    >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
    >>> end
    <Coordinate x=9, y=0>

    >>> end = grid.get_moved_coordinate(coordinate=end, right=1)
    >>> end
    <Coordinate x=13, y=0>

    >>> grid.get_moved_coordinate(coordinate=Coordinate(x=10, y=0))
    <Coordinate x=9, y=0>
"""

TabExpandingTextGrid.search.__doc__ = r"""
    Search the text for the string contained in the needle parameter.

    Returns a list containing the the Coordiante of the starting positions
    where the string is found.

    >>> haystack = "the rain\nin west\tspain\nmainly\ndrains in the plain."
    >>> grid = TabExpandingTextGrid(LinedTextGrid(haystack))

    >>> grid.search(needle="goober")
    []

    >>> result = grid.search(needle="ain")
    >>> for item in result:
    ...    print(item)
    <Coordinate x=5, y=0>
    <Coordinate x=13, y=1>
    <Coordinate x=1, y=2>
    <Coordinate x=2, y=3>
    <Coordinate x=16, y=3>
"""

TabExpandingTextGrid.append.__doc__ = r"""
    Appends the given text to the underlying value.
    Return a reference to self to support method chaining.

    >>> grid = TabExpandingTextGrid(LinedTextGrid("I eat\n"))
    >>> grid.append(text="red meat")
    <TabExpandingTextGrid content='I eat\nred meat'>

    This will raise a ValueError if the text is not a string

    >>> grid.append(text=8)
    Traceback (most recent call last):
    TypeError: text parameter must be a str object
"""

TabExpandingTextGrid.delete.__doc__ = r"""
    Deletes text between the given coordinates (inclusive).

    >>> grid = TabExpandingTextGrid(LinedTextGrid("first\n\tsecond\n\tthird"))
    >>> grid.delete(start=Coordinate(x=2, y=1), end=Coordinate(x=1, y=2))
    <TabExpandingTextGrid content='first\nthird'>

    >>> grid = TabExpandingTextGrid(LinedTextGrid("first\n\tsecond\n\tthird"))
    >>> grid
    <TabExpandingTextGrid content='first\n\t\t\t\tsecond\n\t\t\t\tthird'>

    >>> grid.delete(start=Coordinate(x=2, y=1), end=Coordinate(x=2, y=1))
    <TabExpandingTextGrid content='first\nsecond\n\t\t\t\tthird'>

    >>> grid = TabExpandingTextGrid(LinedTextGrid("\tthis\thas\tlots"))
    >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
    <TabExpandingTextGrid content='\t\t\t\tthishas\t\t\t\tlots'>

    >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
    <TabExpandingTextGrid content='\t\t\t\tthishs\t\t\t\tlots'>

    >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
    <TabExpandingTextGrid content='\t\t\t\tthish\t\t\t\tlots'>

    >>> grid.delete(start=Coordinate(x=9, y=0), end=Coordinate(x=9, y=0))
    <TabExpandingTextGrid content='\t\t\t\tthishlots'>
"""
