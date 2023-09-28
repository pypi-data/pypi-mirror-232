from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable
from typing import Iterable
from typing import TypeVar

if TYPE_CHECKING:
    from pathlib import Path

    from pymarks.bookmark import Bookmark

T = TypeVar("T")

def generic_prompt(
    items: Iterable[T] | list[str],
    prompt: Callable[[Iterable[T] | list[str]], tuple[T, int]],
) -> tuple[T, int]:
    item, code = prompt(items)
    return item, code

def items(
    items: Iterable[Bookmark] | list[str],
    prompt: Callable[[Iterable[Bookmark] | list[str]], tuple[Bookmark, int]],
) -> tuple[Bookmark, int]:
    return generic_prompt(items, prompt)

def paths(
    items: Iterable[Path] | list[str],
    prompt: Callable[[Iterable[Path] | list[str]], tuple[Path, int]],
) -> tuple[Path, int]:
    return generic_prompt(items, prompt)
