from __future__ import annotations

import hashlib
import itertools as it
import os
import re
import string
from pathlib import Path
from typing import (
    Any,
    AnyStr,
    DefaultDict,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
    TypeAlias,
)


def get_hash(item: str | bytes, method: str = "sha512"):
    if isinstance(item, str):
        item = item.encode()
    if method == "md5":
        return hashlib.md5(item).hexdigest()
    elif method == "sha512":
        return hashlib.sha512(item).hexdigest()
    else:
        raise TypeError(f"method '{method}' is not a valid hash method")


HashableContainer: TypeAlias = "dict[Hashable, HashableContainer] | set[HashableContainer] | tuple[HashableContainer, ...] | list[HashableContainer] | Hashable"


def hash_container(obj: HashableContainer) -> str:
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """

    if isinstance(obj, (set, tuple, list)):
        return get_hash(str(tuple([hash_container(e) for e in obj])))

    elif not isinstance(obj, dict):
        return get_hash(str(obj))

    result: dict[Hashable, str] = {}
    for k, v in obj.items():
        result[k] = hash_container(v)

    return get_hash(str(tuple(sorted(result.items()))))


WalkTuple: TypeAlias = "tuple[AnyStr, list[AnyStr], list[AnyStr]]"


class oswalk:
    cache: dict[str, tuple[str]] = {}

    def __init__(self, dirname: str | Path):
        self.dirname = str(dirname)
        if str(self.dirname) in self.cache:
            self.iter = iter(self.cache[str(self.dirname)])
            return
        paths: list[str] = []
        for root, dirs, files in os.walk(self.dirname):
            for file in it.chain(files, dirs):
                paths.append(str(os.path.join(root, file)))
            for i, d in enumerate(reversed(dirs)):
                if str(d) in self.cache:
                    paths.extend(self.cache[str(d)])
                    dirs.pop(i - 1)
        _paths = tuple(paths)
        self.cache[str(self.dirname)] = _paths
        self.iter = iter(_paths)

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self):
        return next(self.iter)


def listfiles(
    pattern: str | Path,
    restriction: dict[str, Sequence[str]] | None = None,
    omit_value: str | None = None,
    dirs: Sequence[str | Path] | None = None,
) -> Iterable[tuple[str, dict[str, str]]]:
    """Yield a tuple of existing filepaths for the given pattern.

    Wildcard values are yielded as the second tuple item.

    Args:
        pattern (str):       a filepattern. Wildcards are specified in snakemake syntax, e.g. "{id}.txt"
        restriction (dict):  restrict to wildcard values given in this dictionary
        omit_value (str):    wildcard value to omit
        dirs:                Specified directories to search

    Yields:
        tuple: The next file matching the pattern, and the corresponding wildcards object
    """
    pattern = os.path.normpath(pattern)
    first_wildcard = re.search("{[^{]", pattern)
    if first_wildcard:
        dirname = os.path.dirname(pattern[: first_wildcard.start()])
        if not dirname:
            dirname = "."
    else:
        dirname = os.path.dirname(pattern)

    re_patterns: dict[str, str] = {}
    for wildcard, restrictions in (restriction or {}).items():
        re_patterns[wildcard] = (
            "(" + "|".join(re.escape(restr) for restr in restrictions) + ")"
        )
    pattern_regex = re.compile(regex(pattern, re_patterns), re.VERBOSE)

    for dir in dirs or [dirname]:
        if (
            Path(dir).resolve() != Path(dirname).resolve()
            and Path(dirname) not in Path(dir).parents
        ):
            continue
        for path in oswalk(str(dir)):
            match = re.match(pattern_regex, path)
            if match:
                yield path, dict(match.groupdict())


class MissingDict(dict):
    def __missing__(self, key):
        try:
            return self[key[: key.index(",")]]
        except (KeyError, ValueError):
            return "{" + key + "}"


formatter = string.Formatter()

WILDCARD_REGEX = re.compile(
    r"""
\{
    (?=(                                      # Use lookahead for performance 
        (?:
            (?: \s*(?P<name>[a-zA-Z]\w*) ) |  # Either a wildcard name
            (?= \s*: )                        # or a future colon
        )
        (?:
            (?:
                (?: (?<!:)  \s*, ) |  # either a comma with no preceding colon
                (?: (?<=\{) \s*: )    # or a colon immediately following the brace
            )
            \s*
            (?P<constraint>
                (?: 
                    \\\{ | \\\}  |   # Escaped braces
                    [^{}] |          # Non-brace characters
                    \{\d+(,\d+)?\}   # or at nested braces at most 1 level (for quant)
                )* 
            ) 
        )?
        \s*
    ))\1
(?<!\\)\}
    """,
    re.VERBOSE,
)


def regex(filepattern: str, constraints: dict[str, str] | None = None):
    f: list[str] = []
    last = 0
    wildcards: set[str] = set()
    _constraints: dict[str, str] = DefaultDict(lambda: ".+")
    _constraints.update(constraints or {})
    for match in WILDCARD_REGEX.finditer(filepattern):
        f.append(re.escape(filepattern[last : match.start()]))
        wildcard = match.group("name")
        constraint = match.group("constraint")
        if wildcard is None:
            if constraint:
                f.append(rf"(?:{constraint})")
            last = match.end()
            continue
        if wildcard in wildcards:
            if constraint:
                if wildcard in _constraints and _constraints[wildcard] != constraint:
                    raise ValueError(
                        "Constraints must all be identical:\n"
                        f"\tIn filepattern: '{filepattern}'\n"
                        f"\tIn wildcard:    '{wildcard}'\n"
                        f"\tGot:            '{_constraints[wildcard]}' and '{constraint}'"
                    )
            f.append(f"(?P={wildcard})")
        else:
            wildcards.add(wildcard)
            f.append(f"(?P<{wildcard}>{{{wildcard}}})")
            if constraint:
                _constraints[wildcard] = constraint
        last = match.end()
    f.append(re.escape(filepattern[last:]))
    f.append("$")  # ensure that the match spans the whole file
    return "".join(f).format_map(_constraints)


def dict_merge(d1: Mapping[Any, Any], d2: Mapping[Any, Any]) -> Mapping[Any, Any]:
    return {
        k: (
            dict_merge(d1[k], d2[k])
            if isinstance(d1.get(k), dict) and isinstance(d2.get(k), dict)
            else d2[k]
            if k in d2
            else d1[k]
        )
        for k in d2.keys() | d1.keys()
    }
