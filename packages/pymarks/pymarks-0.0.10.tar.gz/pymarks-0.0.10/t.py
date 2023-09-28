from __future__ import annotations

import functools
import sys

from pyselector import Menu
from pyselector import key_manager

from pymarks import constants
from pymarks.constants import ExitCode


def testing_fn() -> tuple[str, int]:
    return 'aja', 0


menu = Menu.get('rofi')

menu.keybind.add(
    key='alt-a',
    description='testing...',
    callback=testing_fn,
)

prompt = functools.partial(
    menu.prompt,
    lines=15,
    prompt=f'{constants.APP_NAME}> ',
    width='75%',
    height='50%',
    markup=False,
    mesg=f'Welcome to {constants.APP_NAME}',
)


url, _ = prompt(
    prompt='New bookmark>',
    mesg='Reading <url> from clipboard',
    filter='this item',
)

selected, keycode = prompt(items=['a', 'b', 'c'])


while keycode != ExitCode(0):
    try:
        keybind = menu.keybind.get_keybind_by_code(keycode)
        bookmark, keycode = keybind.callback()
    except key_manager.KeybindError as err:
        print(err)
        sys.exit(1)


def new_execute(args: list[str], items: list[Any] | tuple[Any]) -> tuple[Any | None, int]:
    logger.debug("executing: %s", args)

    input_items = "\n".join(map(str, items))

    result = subprocess.run(
        args,
        input=input_items,
        text=True,
        capture_output=True,
        check=False,
    )

    print('CantItems:', len(items))
    print("ReturnCode:", result.returncode)

    if result.returncode == UserCancelSelection(1):
        return None, result.returncode

    reconverted = input_items.split("\n")
    selected = result.stdout.replace("\n", "")

    idx = reconverted.index(selected)
    selected_item = items[idx]

    return selected_item, result.returncode


def prompt(
    self,
    items: list[Any] | tuple[Any] | None = None,
    case_sensitive: bool = False,
    multi_select: bool = False,
    prompt: str = "PySelector> ",
    **kwargs,
) -> PromptReturn:
    """Prompts the user with a rofi window containing the given items
        and returns the selected item and code.

    Args:
        items (Iterable[str, int], optional):  The items to display in the rofi window
        case_sensitive (bool, optional):       Whether or not to perform a case-sensitive search
        multi_select (bool, optional):         Whether or not to allow the user to select multiple items
        prompt (str, optional):                The prompt to display in the rofi window
        **kwargs:                              Additional keyword arguments.

    Keyword Args:
        lines    (int): The number of lines to display in the selection window.
        mesg     (str): A message to display at the top of the selection window.
        filter   (str): Filter the list by setting text in input bar to filter.
        location (str): The location of the selection window (e.g. "upper-left", "center" or "bottom-right").
        width    (str): The width of the selection window (e.g. 60%).
        height   (str): The height of the selection window (e.g. 50%).
        theme    (str): The path of the rofi theme to use.

    Returns:
        A tuple containing the selected item (str or list of str if `multi_select` enabled) and the return code (int).

    Return Code Value
        0: Row has been selected accepted by user.
        1: User cancelled the selection.
        10-28: Row accepted by custom keybinding.
    """
    if items is None:
        items = []

    args = self._build_command(case_sensitive, multi_select, prompt, **kwargs)
    selection, returncode = helpers._execute(args, items)

    if returncode == UserCancelSelection(1):
        return None, returncode

    return selection, returncode
