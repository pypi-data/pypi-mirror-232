import os
from typing import Union, Any, Iterable

from lawnmowerlatte.logger import log

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def read(filename: str) -> str:
    filename = os.path.expanduser(filename)

    with open(filename, "rb") as f:
        return f.read().decode("utf-8")


def tomlrc(
    *path: Union[str, list[str]], filename: str = "~/.tomlrc"
) -> tuple[dict[str, Any], str]:
    """
    Fetch the users .tomlrc and return the section specified.
    Sections can either be specified as:
        - individual strings (ie. `tomlrc("tool", "example", "table")`)
        - a dotted string (ie. `tomlrc("tool.example.table"`)
        - a list of strings (ie. `tomlrc(["tool", "example", "table"])`)
        - combinations of the above
    >>> tomlrc("tool", filename=None)
    ({'example': {'first': 1, 'second': 2, 'table': {'lorem': 'ipsum'}, 'deeply': {'nested': {'table': {'ie': 'ex'}}}, 'empty': {'table': {}}}}, 'tool')
    >>> tomlrc(["tool"], filename=None)
    ({'example': {'first': 1, 'second': 2, 'table': {'lorem': 'ipsum'}, 'deeply': {'nested': {'table': {'ie': 'ex'}}}, 'empty': {'table': {}}}}, 'tool')
    >>> tomlrc("tool", "example", filename=None)
    ({'first': 1, 'second': 2, 'table': {'lorem': 'ipsum'}, 'deeply': {'nested': {'table': {'ie': 'ex'}}}, 'empty': {'table': {}}}, 'tool.example')
    >>> tomlrc(["tool", "example"], filename=None)
    ({'first': 1, 'second': 2, 'table': {'lorem': 'ipsum'}, 'deeply': {'nested': {'table': {'ie': 'ex'}}}, 'empty': {'table': {}}}, 'tool.example')
    >>> tomlrc(["tool"], "example", filename=None)
    ({'first': 1, 'second': 2, 'table': {'lorem': 'ipsum'}, 'deeply': {'nested': {'table': {'ie': 'ex'}}}, 'empty': {'table': {}}}, 'tool.example')
    >>> tomlrc(["tool.example"], "deeply", "nested", filename=None)
    ({'table': {'ie': 'ex'}}, 'tool.example.deeply.nested')
    >>> tomlrc(["tool.example"], ["deeply", "nested"], filename=None)
    ({'table': {'ie': 'ex'}}, 'tool.example.deeply.nested')
    >>> tomlrc(["tool.example"], ["deeply.nested"], filename=None)
    ({'table': {'ie': 'ex'}}, 'tool.example.deeply.nested')
    >>> tomlrc(["tool.example.deeply.nested"], filename=None)
    ({'table': {'ie': 'ex'}}, 'tool.example.deeply.nested')
    >>> tomlrc(["tool.example"], ["deeply"], "nested", filename=None)
    ({'table': {'ie': 'ex'}}, 'tool.example.deeply.nested')
    >>> tomlrc(["tool.example"], ["table"], filename=None)
    ({'lorem': 'ipsum'}, 'tool.example.table')
    >>> tomlrc(["tool.example"], ["table.lorem"], filename=None)
    Traceback (most recent call last):
    ...
    KeyError: "Key provided corresponds to a value, not a table: tool.example.table.lorem = 'ipsum'"
    >>> tomlrc(["tool.example.empty.table"], filename=None)
    ({}, 'tool.example.empty.table')
    >>> tomlrc(["tool.sample"], filename=None)
    ({}, 'tool.sample')
    >>> tomlrc(["tool.sample.even.deeper"], filename=None)
    ({}, 'tool.sample.even.deeper')
    """

    def flatten_path(path: Iterable[Union[str, list[str]]]) -> list[str]:
        flattened: list[str] = []
        for key in path:
            if isinstance(key, tuple) or isinstance(key, list):
                flattened.extend(flatten_path(key))
            elif isinstance(key, str):
                if "." in key:
                    flattened.extend(flatten_path(key.split(".")))
                else:
                    flattened.append(key)

        return flattened

    contents: str
    if filename is None:
        contents = """
            [tool.example]
            first = 1
            second = 2
            
            [tool.example.table]
            lorem = "ipsum"
            
            [tool.example.deeply.nested.table]
            ie = "ex"
            
            [tool.example.empty.table]
        """
    else:
        contents = read(filename)

    toml: dict[str, Any] = tomllib.loads(contents)
    flattened: list[str] = flatten_path(path)

    for key, index in indexed(flattened):
        if toml:
            try:
                toml = toml[key]
            except KeyError:
                log.warning(
                    f"The table '{'.'.join(flattened[:index+1])}' does not exist in the TOML file"
                )
                toml = {}

    if not isinstance(toml, dict):
        raise KeyError(
            f"Key provided corresponds to a value, not a table: {'.'.join(flattened)} = '{toml}'"
        )

    return toml, ".".join(flattened)


def indexed(iterable, start_at=0):
    return zip(iterable, range(start_at, len(iterable) + start_at))


def progress(iterable, on_change_only=True, precision=1):
    percentages = [
        percentage(_, len(iterable), precision) for _ in range(len(iterable))
    ]

    if on_change_only:
        percentages = [
            value if value != percentages[index - 1] else None
            for value, index in indexed(percentages)
        ]

    return zip(iterable, percentages)


def percentage(part, whole, precision=1):
    percentage = round(part / whole * 100, precision)
    return f"{percentage}%"


def progress_bar(part, whole, width=10, frame="[{bar}]", complete="|", incomplete=" "):
    complete_count = round(part / whole * width)
    bar = "".join(
        [complete if complete_count > index else incomplete for index in range(width)]
    )

    return frame.format(bar=bar)
