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

from typing import Optional, List, Union, Tuple


class MutableString:
    def __init__(self, content: str) -> None:
        self._content = content

    def __repr__(self) -> str:
        return f"<MutableString content={repr(self._content)}>"

    def __str__(self) -> str:
        return self._content

    def to_string(self) -> str:
        return str(self)

    def __getitem__(self, index: Union[int, Tuple[int, int]]) -> str:
        if isinstance(index, tuple):
            return self._content[index[0] : index[1] + 1]
        if index < 0 or index >= len(self._content):
            return ""
        return self._content[index]

    def insert(self, *, text: str, index: int) -> "MutableString":
        index = max(index, 0)
        if index <= len(self._content):
            before = self._content[:index]
            after = self._content[index:]
            self._content = before + text + after
        else:
            self._content = self._content + text
        return self

    def append(self, *, text: str) -> "MutableString":
        if not isinstance(text, str):
            raise TypeError("text parameter must be a str object")
        self._content = self._content + text
        return self

    def prepend(self, *, text: str) -> "MutableString":
        if not isinstance(text, str):
            raise TypeError("text parameter must be a str object")
        self._content = text + self._content
        return self

    def delete(
        self,
        *,
        start: int = 0,
        end: Optional[int] = None,
        length: Optional[int] = None,
    ) -> "MutableString":
        if not self._content:
            return self
        if not isinstance(start, int):
            raise TypeError("start parameter must be an int object")
        start = start % len(self._content)
        if end is not None and not isinstance(end, int):
            raise TypeError("end parameter must be an int object")
        if length is not None and not isinstance(length, int):
            raise TypeError("length parameter must be an int object")
        if length is not None and end is not None:
            raise ValueError(
                "cannot pass values for both end and length parameters"
            )
        if end is not None:
            end = end % len(self._content)
        elif length is None:
            end = len(self._content) - 1
        elif length == 0:
            return self
        elif length < 0:
            raise ValueError("length parameter must be at least zero")
        else:
            end = start + length - 1
            end = min(end, len(self._content))
        if end < start:
            raise ValueError("the end must be greater than the start")
        end = end + 1
        before = self._content[:start]
        after = self._content[end:]
        self._content = before + after
        return self

    def search(self, *, needle: str, case_sensitive: bool = True) -> List[int]:
        result: List[int] = []
        if not needle:
            return result
        content = self._content
        if not case_sensitive:
            content = content.lower()
            needle = needle.lower()
        current = content.find(needle)
        while current != -1:
            result.append(current)
            current = self._content.find(needle, current + 1)
        return result


MutableString.__init__.__doc__ = """
    Initializes a MutableString object.
    >>> MutableString("the rain in spain")
    <MutableString content='the rain in spain'>
"""

MutableString.__str__.__doc__ = """
    Returns the contents of the MutableString as a str
    >>> str(MutableString("a b c d e f g"))
    'a b c d e f g'
"""

MutableString.to_string.__doc__ = """
    Equivalent to str(self).  Helpful for method chaining.
    >>> MutableString("a b c d e f g").to_string()
    'a b c d e f g'
"""

MutableString.append.__doc__ = """
    Appends the given text to the underlying text value.
    Return a reference to self to support method chaining.

    >>> MutableString("I eat").append(text=" red meat")
    <MutableString content='I eat red meat'>

    This will raise a TypeError if the text parameter is not a string

    >>> MutableString("seven eight").append(text=9)
    Traceback (most recent call last):
    TypeError: text parameter must be a str object
"""

MutableString.prepend.__doc__ = """
    Prepends the given text to the underlying text value.
    Return a reference to self to support method chaining.

    >>> MutableString("the greatest teacher").prepend(text="failure is ")
    <MutableString content='failure is the greatest teacher'>

    This will raise a TypeError if the text parameter is not a string

    >>> MutableString("seven eight").prepend(text=9)
    Traceback (most recent call last):
    TypeError: text parameter must be a str object
"""

MutableString.delete.__doc__ = """
    Deletes the text between the given indices (inclusively).

    >>> MutableString("I am funny and smart").delete(start=8, end=9)
    <MutableString content='I am fun and smart'>

    >>> MutableString("I am funny, and smart").delete(start=10, end=10)
    <MutableString content='I am funny and smart'>

    >>> MutableString("").delete(start=8, end=9)
    <MutableString content=''>

    Instead of providing the end parameter, passing a length is also
    acceptable.

    >>> MutableString("I am funny and smart").delete(start=8, length=2)
    <MutableString content='I am fun and smart'>

    >>> MutableString("I am funny, and smart").delete(start=10, length=1)
    <MutableString content='I am funny and smart'>

    Passing length=0 results in no change to the string

    >>> MutableString("I am funny and smart").delete(start=5, length=0)
    <MutableString content='I am funny and smart'>

    But length has to be at least zero.

    >>> MutableString("I am funny and smart").delete(start=5, length=-1)
    Traceback (most recent call last):
    ValueError: length parameter must be at least zero

    Passing start by itself removes all trailing text from the string.

    >>> MutableString("I am funny, and smart").delete(start=8)
    <MutableString content='I am fun'>

    The starting index actually used is the requested starting index
    modulo the length of the string, so negative numbers are allowed.

    >>> MutableString("I am funny and smart").delete(start=-10)
    <MutableString content='I am funny'>

    >>> MutableString("I am funny, and smart").delete(start=-11, end=10)
    <MutableString content='I am funny and smart'>

    This lets you use rather crazy values for the starting index.

    >>> assert 1900 % 21 == 10
    >>> MutableString("I am funny, and smart").delete(start=1900)
    <MutableString content='I am funny'>

    Note that the ending index we use is also the requested ending index
    moduleo the length of hte string.

    >>> MutableString("I am funny, and smart").delete(start=-11, end=-11)
    <MutableString content='I am funny and smart'>

    >>> MutableString("I am funny, and smart").delete(start=-11, end=1900)
    <MutableString content='I am funny and smart'>

    However, The start parameter is optional and defaults to 0 (zero).

    >>> MutableString("I am funny and smart").delete(end=14)
    <MutableString content='smart'>

    Passing length by itself also works.

    >>> MutableString("I am funny and smart").delete(length=15)
    <MutableString content='smart'>

    By now you may have noticed that end = start + length - 1.
    This is because I wanted "end" to be inclusive, which is
    contrary to how slicing normally works in python.

    As a result, passing length=0 results in no change to the string

    >>> MutableString("I am funny and smart").delete(start=5, length=0)
    <MutableString content='I am funny and smart'>

    To truncate the entire string, simply call delete without any arguments.

    >>> MutableString("I am funny and smart").delete()
    <MutableString content=''>

    Naturally, start, end, and length, if provided must all be int objects.

    >>> MutableString("Well shucks").delete(start="moose")
    Traceback (most recent call last):
    TypeError: start parameter must be an int object

    >>> MutableString("Well shucks").delete(end="")
    Traceback (most recent call last):
    TypeError: end parameter must be an int object

    >>> MutableString("Well shucks").delete(length="moose")
    Traceback (most recent call last):
    TypeError: length parameter must be an int object


    Also, end and length cannot both be specified simultaneously

    >>> MutableString("I am funny and smart").delete(start=5, end=7, length=4)
    Traceback (most recent call last):
    ValueError: cannot pass values for both end and length parameters

    Also, the end cannot be less than the start

    >>> MutableString("I am funny and smart").delete(start=5, end=3)
    Traceback (most recent call last):
    ValueError: the end must be greater than the start


    Tired of hearing how funny and smart I am?   So is my wife hahaha.
"""

MutableString.search.__doc__ = r"""
    Search the text for the string contained in the needle parameter.

    Returns a list containing the the starting positions where the string
    is found.

    >>> haystack = "the rain\nin west\tspain\nmainly\ndrains in the plain."
    >>> mut = MutableString(haystack)

    >>> mut.search(needle="ain")
    [5, 19, 24, 32, 46]

    >>> mut.search(needle="goober")
    []

"""
