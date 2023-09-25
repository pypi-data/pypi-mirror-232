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

from typing import Optional
from enum import Enum

from .window import Window
from .file_handlers import BaseFileHandler
from .configuration import Config
from .coordinate import Coordinate
from .mutable_string import MutableString
from .lined_text_grid import LinedTextGrid
from .tabbed_text_grid import TabExpandingTextGrid


logger = logging.getLogger(__name__)


class Editor:
    def __init__(
        self,
        file_handler: BaseFileHandler,
        config: Config = Config(),
    ) -> None:
        self._config = config
        self._file_handler = file_handler
        self._mutable_string = MutableString(file_handler.read())
        self._text_grid = LinedTextGrid(
            self._mutable_string, line_ending=config.line_ending
        )
        self._tab_text_grid = TabExpandingTextGrid(
            self._text_grid, tab_size=config.tab_display_width
        )
        self.cursor = Coordinate(x=0, y=0)
        self._undo_redo = UndoRedo()

    def handle_delete(self, length: int = 1, add_event: bool = True) -> None:
        start = self.cursor
        end = Coordinate(y=start.y, x=start.x + length - 1)
        text = self._tab_text_grid[start, end]
        self._tab_text_grid.delete(start=start, end=end)
        if add_event and text is not None:
            self._undo_redo.add_deletion_event(position=self.cursor, text=text)

    def undo(self) -> None:
        self._undo_redo.undo(self)

    def redo(self) -> None:
        self._undo_redo.redo(self)

    def handle_backspace(self, add_event: bool = True) -> None:
        if self.cursor.x == 0:
            self._handle_backspace_on_first_column(add_event=add_event)
        else:
            self._handle_backspace_on_nonfirst_column(add_event=add_event)

    def _handle_backspace_on_first_column(self, add_event: bool = True) -> None:
        if self.cursor.y > 0:
            self.move_cursor(up=1, x=-1)
            self.handle_delete(add_event=add_event)

    def _handle_backspace_on_nonfirst_column(
        self, add_event: bool = True
    ) -> None:
        length = 1
        if self._config.expand_tabs:
            logger.info("handling expand_tabs for backspace")
            start_x = self.cursor.x - 1
            mod = start_x % self._config.expand_tabs
            if mod == 0:
                mod = 3
            start_x = max(start_x - mod, 0)
            start = Coordinate(x=start_x, y=self.cursor.y)
            end = Coordinate(x=self.cursor.x - 1, y=self.cursor.y)
            text = set(self._tab_text_grid[start, end])
            logger.info(f"{start=} {end=} {text=}")
            if text == set(" "):
                length = mod + 1
        self.move_cursor(left=length)
        self.handle_delete(length=length, add_event=add_event)

    def insert(self, character_to_add: str, add_event: bool = True) -> None:
        if character_to_add == "\n":
            character_to_add = self._config.line_ending
        if character_to_add == "\t" and self._config.expand_tabs:
            mod = (
                self._config.expand_tabs - self.cursor.x
            ) % self._config.expand_tabs
            if not mod:
                mod = self._config.expand_tabs
            logger.info(f"inserting {mod} spaces")
            character_to_add = " " * mod
            logger.info(f"inserting {mod} spaces {character_to_add=!r}")
        self._tab_text_grid.insert(
            text=character_to_add, coordinate=self.cursor
        )
        if add_event:
            self._undo_redo.add_insertion_event(
                position=self.cursor, text=character_to_add
            )
        if character_to_add == self._config.line_ending:
            self.move_cursor(down=1, x=0)
        else:
            self.move_cursor(right=len(character_to_add))

    def move_cursor(
        self,
        *,
        x: Optional[int] = None,
        y: Optional[int] = None,
        up: int = 0,
        down: int = 0,
        left: int = 0,
        right: int = 0,
    ) -> None:
        logger.info(f"moving: {x=} {y=} {up=} {down=} {left=} {right=}")
        new_coordinate = self._tab_text_grid.get_moved_coordinate(
            coordinate=self.cursor,
            new_x=x,
            new_y=y,
            up=up,
            down=down,
            left=left,
            right=right,
        )
        logger.info(f"moving from {self.cursor} to {new_coordinate}")
        self.cursor = new_coordinate

    def cell_under_cursor(self) -> Optional[str]:
        return self._tab_text_grid[self.cursor]

    def get_text_for_window(self, window: Window) -> str:
        top = window.top
        bottom = window.bottom
        lines = self._tab_text_grid.lines(start=top, end=bottom)
        final_lines = []
        for line in lines:
            line_segment = line[window.left : window.right]
            final_lines.append("".join(cell for cell in line_segment))
        return self._config.line_ending.join(final_lines)

    def incremental_search(
        self,
        search_string: str,
        mode: str = "normal",
        case_sensitive: bool = True,
    ) -> None:
        positions = self._tab_text_grid.search(
            needle=search_string, case_sensitive=case_sensitive
        )
        if mode == "reverse":
            positions.reverse()
        move_to = None
        for position in positions:
            if mode == "reverse" and position < self.cursor:
                move_to = position
                break
            if mode == "normal" and position > self.cursor:
                move_to = position
                break
            if mode == "same" and position >= self.cursor:
                move_to = position
                break
        if move_to is None and positions:
            move_to = positions[0]
        if move_to is not None:
            self.move_cursor(x=move_to.x, y=move_to.y)

    def get_full_text(self) -> str:
        return self._tab_text_grid.get_unexpanded_text()

    def save(self) -> None:
        self._file_handler.save(self.get_full_text())


class EventType(Enum):
    FIRST = "first"
    INSERTION = "insertion"
    DELETION = "deletion"


class Event:
    def __init__(
        self,
        event_type: EventType,
        *,
        position: Coordinate = Coordinate(x=0, y=0),
        text: str = "",
    ) -> None:
        self.next: Optional[Event] = None
        self.previous: Optional[Event] = None
        self.text = text
        self.position = position
        self.event_type = event_type

    def __repr__(self) -> str:
        has_next = self.next is not None
        has_previous = self.previous is not None
        event_type = self.event_type
        text = self.text
        position = self.position
        return (
            f"<Event {event_type=} {text=} {position=} "
            f"{has_next=} {has_previous=}>"
        )


class UndoRedo:
    def __init__(self) -> None:
        self.last_event = Event(EventType.FIRST)

    def add_insertion_event(self, *, position: Coordinate, text: str) -> None:
        new = Event(EventType.INSERTION, position=position, text=text)
        self._add_event(new)

    def add_deletion_event(self, *, position: Coordinate, text: str) -> None:
        new = Event(EventType.DELETION, position=position, text=text)
        self._add_event(new)

    def _add_event(self, new: Event) -> None:
        logger.info(f"adding event {new}")
        self.last_event.next = new
        new.previous = self.last_event
        self.last_event = new

    def undo(self, editor: Editor) -> None:
        logger.info(f"undoing event: {self.last_event}")
        if self.last_event.event_type == EventType.INSERTION:
            self._apply_delete(self.last_event, editor)
        elif self.last_event.event_type == EventType.DELETION:
            self._apply_insert(self.last_event, editor)
        if self.last_event.previous is not None:
            self.last_event = self.last_event.previous

    def _apply_delete(self, event: Event, editor: Editor) -> None:
        editor.cursor = event.position
        editor.handle_delete(length=len(event.text), add_event=False)

    def _apply_insert(self, event: Event, editor: Editor) -> None:
        editor.cursor = event.position
        editor.insert(self.last_event.text, add_event=False)

    def redo(self, editor: Editor) -> None:
        event = self.last_event
        if self.last_event.next is None:
            logger.info("nothing to redo")
        else:
            self.last_event = self.last_event.next
            logger.info(f"redoing event: {event}")
            if self.last_event.event_type == EventType.INSERTION:
                self._apply_insert(self.last_event, editor)
            else:
                self._apply_delete(self.last_event, editor)
