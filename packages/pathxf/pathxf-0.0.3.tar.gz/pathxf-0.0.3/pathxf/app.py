from __future__ import annotations

import copy
import itertools as it
import json
import os
from pathlib import Path
import re
from typing import Optional, Sequence

import more_itertools as itx
import typer
import yaml
from appdirs import user_cache_dir
from typer import Option, Typer

from pathxf.bids import bids
from pathxf.spec import CompSpec, Spec
from pathxf.utils import dict_merge, hash_container, listfiles, oswalk

app = Typer()


def _merge_conditionals(compspec: CompSpec | list[CompSpec]) -> list[CompSpec]:
    if isinstance(compspec, list):
        return _merge_conditionals(CompSpec(conditions=compspec))
    if not "conditions" in compspec:
        return [compspec]
    mergables = copy.copy(compspec)
    conditions = mergables.pop("conditions")
    return [
        CompSpec(**dict_merge(mergables, s))
        for spec in conditions
        for s in _merge_conditionals(spec)
    ] + [mergables]


class IndexCache(dict[Spec, dict[str, str]]):
    dir: Path = Path(user_cache_dir("file_renamer", "pvandyken"))

    def __init__(self):
        if not self.dir.exists():
            self.dir.mkdir(parents=True)
        if not self.dir.joinpath("index").exists():
            self.dir.joinpath("index").mkdir()

    def contains(self, hash: str):
        if self.dir.joinpath(hash).exists():
            return True
        return False

    def index(self, hash: str):
        return self.dir / "index" / hash

    def purge(self):
        for file in self.dir.joinpath("index").iterdir():
            os.remove(file)

    def rm(self, spec: Spec):
        name = hash_container(spec)
        if self.contains(name):
            os.remove(self.index(name))

    def __getitem__(self, spec: Spec):
        name = hash_container(spec)
        if self.contains(name):
            with open(self.index(name), "r") as f:
                return json.load(f)["maps"]
        raise KeyError(name)

    def __setitem__(self, __key: Spec, __value: dict[str, str]) -> None:
        name = hash_container(__key)
        with open(self.index(name), "w") as f:
            json.dump({"version": "0.0.0", "maps": __value}, f)

    def __contains__(self, __key: object) -> bool:
        if not isinstance(__key, dict):
            return False
        name = hash_container(__key)
        return self.contains(name)


def index(config: Spec, limit: Sequence[Path] | None = None):
    maps: dict[str, str] = {}
    for group in config["maps"]:
        if not "comps" in group:
            for inp, wcards in listfiles(
                Path(config["input"], group["root"]), dirs=limit
            ):
                wcards = dict(wcards.items())
                try:
                    maps[group["out"].format(**wcards)] = inp
                except KeyError:
                    raise Exception(
                        f"Not all wildcards found in input '{inp}'\n"
                        f"Found: {wcards}\n"
                    )
            continue
        for root, (path, _entityspecs) in it.product(
            itx.always_iterable(group["root"]), list(group["comps"].items())
        ):
            entityspecs = _merge_conditionals(_entityspecs)
            for inp, wcards in listfiles(
                Path(config["input"], root + path), dirs=limit
            ):
                wcards = dict(wcards.items())
                spec = None
                for _spec in entityspecs:
                    good = True
                    if not "when" in _spec:
                        spec = _spec
                        break
                    for ent, values in _spec["when"].items():
                        if wcards[ent] not in itx.always_iterable(values):
                            good = False
                            break
                    if good:
                        spec = _spec
                        break
                if spec is None:
                    raise Exception(f"No valid entityspec found for {inp}")
                for ent, _m in spec.get("map", {}).items():
                    wcards[ent] = _m.get(wcards[ent], wcards[ent])

                outroot = os.path.join(config.get("output", ""), group.get("out", ""))
                assert "bids" in spec
                outtemplate = bids(
                    root=outroot,
                    **{
                        **config.get("all", {}).get("bids", {}),
                        **group.get("all", {}),
                        **spec["bids"],
                    },
                )
                try:
                    maps[inp] = outtemplate.format(
                        **{
                            **config.get("all", {}).get("bids", {}),
                            **wcards
                        }
                    )
                except KeyError:
                    raise Exception(
                        f"Not all wildcards found in input '{inp}'\n"
                        f"Template: {outtemplate}\n",
                        f"Found: {wcards}\n"
                        f"Expected: {spec['bids']}"
                    )
    return maps


def _normalize_limit(limits: Sequence[Path]):
    viewed: set[Path] = set()
    result: list[Path] = []
    for limit in limits:
        resolved = limit.resolve()
        discard = False
        for view in viewed:
            if view in resolved.parents:
                discard = True
                break
        if not discard:
            result.append(limit)
            viewed.add(resolved)
    return result

def _bids_callback(value: list[str] | None):
    if value is None:
        return value
    mapping_re = re.compile(r'\w+=\w+')
    if len(
        bad_vals := [s for s in value if re.match(mapping_re, s) is None]
    ):
        raise TypeError(
            "bids entities must be specified as 'entity=value' strings, got:\n\t" + 
            "\n\t".join(bad_vals)
        )


def main(
    config: Path,
    input: Optional[Path] = Option(
        None, "-i", help="Override the input field in the config"
    ),
    output: Optional[Path] = Option(
        None, "-o", help="Override the ouptut field in the config"
    ),
    do_index: bool = Option(
        False, "--index", help="Force reindexing of the filesystem"
    ),
    limit: Optional[list[Path]] = Option(
        None, help="limit fs search to specific directories"
    ),
    purge: bool = Option(False, help="Remove all cached indexes"),
    _print: bool = Option(
        False,
        "--print",
        "-p",
        help="Print the file mapping as json, without doing any renaming",
    ),
    inverse: bool = Option(
        False,
        "-v",
        help="Print list of files in the input directory not indexed, formatted as json",
    ),
    _bids: Optional[list[str]] = Option(
        None,
        "--bids",
        help="Provide entity=value pairs to be provided as defaults to every output "
        "made with bids",
    )
):
    _bids_callback(_bids)
    cache = IndexCache()
    if purge:
        cache.purge()
        return
    with config.open() as f:
        config_obj: Spec = yaml.safe_load(f)
    if input is not None:
        config_obj["input"] = str(input)
    if output is not None:
        config_obj["output"] = str(output)
    if _bids is not None:
        if not "all" in config_obj:
            config_obj["all"] = {}
        config_obj["all"]["bids"] = dict(field.split("=") for field in _bids)
    if do_index or config_obj not in cache:
        maps = index(config_obj, limit=_normalize_limit(limit) if limit else None)
        cache[config_obj] = maps
    else:
        maps = cache[config_obj]
    if _print:
        print(json.dumps(maps))
        return
    if inverse:
        unused: list[str] = []
        for d in limit or [config_obj["input"]]:
            for f in oswalk(d):
                if Path(f).is_dir():
                    continue
                if f in maps:
                    continue
                unused.append(f)
        print(json.dumps(unused))
        return

    for src, dest in maps.items():
        if Path(src).exists() and not Path(dest).exists():
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(
                os.path.relpath(Path(src).resolve(), Path(dest).resolve().parent), dest
            )
    cache.rm(config_obj)


def run():
    typer.run(main)
