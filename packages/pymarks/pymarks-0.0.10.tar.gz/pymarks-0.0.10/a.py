from typing import Dict, Callable


def select_option(
    options: Dict[str, Callable], prompt: PromptFn, message: str
) -> str | None:
    selected = display.options(
        tuple(options.keys()),
        prompt=prompt,
        mesg=message,
    )

    if selected is None or selected not in options:
        return None

    return selected


def execute_option(
    selected: str | None,
    options: Dict[str, Callable],
    cursor: Cursor,
    prompt: PromptFn,
    bookmark: Bookmark,
) -> tuple[Bookmark | None, KeyCode]:
    if selected is None:
        return None, KeyCode(1)

    func = options[selected]
    func(cursor, prompt, bookmark)
    return bookmark, KeyCode(0)


def options_selector(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> tuple[Bookmark | None, KeyCode]:
    kwargs['menu'].keybind.toggle_all()
    bookmark: Bookmark = kwargs['bookmark']

    options_fn: Dict[str, Callable] = {
        f'{BULLET} Edit': update_bookmark,
        f'{BULLET} Delete': delete_bookmark,
    }

    selected = select_option(
        options=options_fn,
        prompt=prompt,
        message=f'{BULLET} Actions for <{bookmark.url}>',
    )

    return execute_option(selected, options_fn, cursor, prompt, bookmark)


def update_bookmark(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> tuple[Bookmark | None, KeyCode]:
    options_fn: Dict[str, Callable] = {
        f'{BULLET} Title': update_title,
        f'{BULLET} Description': update_desc,
        f'{BULLET} Tags': update_tags,
        f'{BULLET} URL': update_url,
        f'{BULLET} Fetch Title/Desc': fetch_and_update,
    }

    selected = select_option(
        options=options_fn,
        prompt=prompt,
        message=f'Options for <{b.url}>',
    )

    return execute_option(selected, options_fn, cursor, prompt, b)


##############################################


from typing import Callable, Dict, Tuple
from display import options
from bookmark import Bookmark

BULLET = "•"


def execute_action(
    cursor: Cursor,
    prompt: PromptFn,
    actions: Dict[str, Callable],
    item: Bookmark,
    action_message: str,
) -> Tuple[Bookmark | None, KeyCode]:
    selected = options(
        tuple(actions.keys()),
        prompt=prompt,
        mesg=f'{BULLET} {action_message} for <{item.url}>',
    )

    if selected is None or selected not in actions:
        return None, KeyCode(1)

    func = actions[selected]
    func(cursor, prompt, item)
    return item, KeyCode(0)


def options_selector(
    cursor: Cursor, prompt: PromptFn, **kwargs
) -> Tuple[Bookmark | None, KeyCode]:
    kwargs['menu'].keybind.toggle_all()
    bookmark: Bookmark = kwargs['bookmark']

    actions = {
        f'{BULLET} Edit': update_bookmark,
        f'{BULLET} Delete': delete_bookmark,
    }

    return execute_action(
        cursor, prompt, actions, bookmark, f'Actions for <{bookmark.url}>'
    )


def update_bookmark(
    cursor: Cursor, prompt: PromptFn, b: Bookmark
) -> Tuple[Bookmark | None, KeyCode]:
    actions = {
        f'{BULLET} Title': update_title,
        f'{BULLET} Description': update_desc,
        f'{BULLET} Tags': update_tags,
        f'{BULLET} URL': update_url,
        f'{BULLET} Fetch Title/Desc': fetch_and_update,
    }

    return execute_action(cursor, prompt, actions, b, f'Options for <{b.url}>')
