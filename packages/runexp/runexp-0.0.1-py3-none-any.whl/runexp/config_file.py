import argparse
import contextlib
import dataclasses
import datetime
import json
import multiprocessing
import os
import pathlib
import shlex
import subprocess
import sys
import typing
import psutil

import yaml
from pydantic import ValidationError
from pydantic import dataclasses as py_dataclasses

from . import slurm_utils
from .parser_utils import RunExpState, add_runexp_args, remove_runexp_args


class TypedDictLike(typing.Protocol):
    "something that can be constructed with kwargs"


Fun: typing.TypeAlias = typing.Callable[[TypedDictLike], None]


def typed_dict_like(cls: type) -> typing.TypeGuard[type[TypedDictLike]]:
    if py_dataclasses.is_pydantic_dataclass(cls):
        return True
    if dataclasses.is_dataclass(cls):
        return True
    if issubclass(cls, dict | tuple):
        return bool(typing.get_type_hints(cls))
    return False


def to_dict(item: TypedDictLike) -> dict[str, typing.Any]:
    if dataclasses.is_dataclass(item):
        return dataclasses.asdict(item)
    if isinstance(item, dict):
        return item
    if isinstance(item, tuple):
        hints = typing.get_type_hints(type(item))
        return {key: getattr(item, key) for key in hints}
    raise TypeError(f"{type(item)=!r} not supported")


def sanitize(fun) -> tuple[Fun, type[TypedDictLike], str | None]:
    "sanitize function and return data type and documentation"

    hints = typing.get_type_hints(fun)
    arg_hints = {k: v for k, v in hints.items() if k != "return"}
    if len(arg_hints) != 1:
        raise ValueError(f"{fun} should take exactly 1 parameters (hints: {hints})")
    dtype: type = next(iter(arg_hints.values()))

    if not typed_dict_like(dtype):
        raise TypeError(f"{dtype} is not a supported type")

    doc: str | None = fun.__doc__

    def _tp_check(fn) -> typing.TypeGuard[Fun]:
        return True

    assert _tp_check(fun)

    return fun, dtype, doc


def read_config(config: str):
    "read the config file at the given path"

    config_path = pathlib.Path(config)
    if not config_path.is_file():
        raise ValueError(f"{config_path=!r} must be a file")

    with open(config_path, "r", encoding="utf8") as config_file:
        match config_path.suffix.lower():
            case ".yml":
                return yaml.safe_load(config_file)
            case ".yaml":
                return yaml.safe_load(config_file)
            case ".json":
                return json.load(config_file)
            case _:
                raise ValueError(f"unrecognized format: {config_path.suffix!r}")


def write_config(value: TypedDictLike, path: pathlib.Path):
    if path.exists():
        raise ValueError(f"will not override {path!r}")

    # correct format
    value = {"base_config": to_dict(value)}

    with open(path, "w", encoding="utf8") as config_file:
        match path.suffix.lower():
            case ".yml":
                yaml.safe_dump(value, config_file)
            case ".yaml":
                yaml.safe_dump(value, config_file)
            case ".json":
                json.dump(value, config_file)
            case _:
                raise ValueError(f"unrecognized format: {path.suffix!r}")


def get_args(doc: str | None, cli: list[str] | None = None):
    # build CLI to run this function
    parser = argparse.ArgumentParser(
        description=doc,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("config_file", type=str, help="JSON/YAML file with the config")
    add_runexp_args(parser)
    return parser.parse_args(cli)


def get_sweeps(
    base_config: dict[str, typing.Any], sweep_options: dict[str, typing.Any] | None
):
    if not sweep_options:  # non empty dict
        return None

    config_lst: list[dict[str, typing.Any]] = []

    # check for length and prohibit overriding
    common_length = 0
    for key, val in sweep_options.items():
        if key in base_config:
            raise ValueError(f"overriding base_config.{key} is not allowed")
        if not isinstance(val, (list, tuple)):
            raise ValueError(f"sweep.{key} should be a list or tuple, found: {val!r}")

        if not common_length:
            common_length = len(val)
        elif len(val) != common_length:
            raise ValueError(
                f"len(sweep.{key})={len(val)} mismatch with previous "
                f"sweep options (len(prev)={common_length})"
            )

    if not common_length:
        raise ValueError("empty sweep are not allowed")

    # build sweep item
    for idx in range(common_length):
        copy = {**base_config}
        for key, val_lst in sweep_options.items():
            copy[key] = val_lst[idx]
        config_lst.append(copy)

    return config_lst


def _print_call(fun: Fun, config: TypedDictLike):
    print(f"calling {fun.__name__}({config!r})")


def run_no_sweep(
    fun: Fun,
    config: TypedDictLike,
    config_path: str,
    state: RunExpState,
):
    if not state.use_slurm:
        if state.no_dry_run:
            fun(config)
        else:
            _print_call(fun, config)
        return

    now = datetime.datetime.now()

    command_list = [sys.executable] + remove_runexp_args(
        psutil.Process(os.getpid()).cmdline()[1:]
    )
    if state.template_file is not None:
        command = shlex.join(command_list)
        slurm_utils.run_from_template(
            state.template_file,
            slurm_utils.job_path(config_path, now.isoformat()),
            state.no_dry_run,
            fun.__name__,
            command,
            state.slurm_args,
        )
        return

    # srun invocation
    srun_command = ["srun"] + state.slurm_args + command_list
    if state.no_dry_run:
        subprocess.run(srun_command)
        return
    else:
        print(shlex.join(srun_command))
        return


def run_sweep(
    fun: Fun,
    config_list: list[TypedDictLike],
    config_path: str,
    state: RunExpState,
):
    now = datetime.datetime.now()

    if not state.use_slurm:
        if state.no_dry_run:
            with multiprocessing.Pool(state.max_concurrent_proc) as pool:
                pool.map(fun, config_list)
        else:
            for cfg in config_list:
                _print_call(fun, cfg)
        return

    if state.template_file is None:
        raise ValueError("slurm sweep are only implemented with template files")

    command_list = [sys.executable] + remove_runexp_args(
        psutil.Process(os.getpid()).cmdline()[1:]
    )
    path_idx = command_list.index(config_path)

    with contextlib.ExitStack() as stack:
        # create all config-now-\d.yml for \d=1-10 (make sure this format is exact)
        config_path_ = pathlib.Path(config_path)
        config_prefix = config_path_.stem + f"_{now.isoformat()}"
        for idx, config in enumerate(config_list):
            path_ = config_path_.with_stem(config_prefix + f"-{1 + idx}")
            write_config(config, path_)

            # remove in dry-run
            if not state.no_dry_run:
                stack.callback(path_.unlink)

        command_list[path_idx] = str(config_path_.with_stem(config_prefix + r"-%a"))
        command = shlex.join(command_list)

        slurm_utils.run_from_template(
            state.template_file,
            slurm_utils.job_path(config_path, now.isoformat()),
            state.no_dry_run,
            fun.__name__,
            command,
            state.slurm_args,
            sbatch_options=[
                f"#SBATCH --array=1-{len(config_list)}%{state.max_concurrent_proc}"
            ],
        )
        return


def try_cast(value: dict[str, typing.Any], dtype: typing.Type[TypedDictLike]):
    try:
        return dtype(**value)
    except (TypeError, ValidationError) as exc:
        raise ValueError("invalid config") from exc


T = typing.TypeVar("T")


def _runexp_dec(fun_: T) -> T:
    """Use `fun`: as an entry point

    - fun: (python dataclass | pydantic dataclass | NamedTuple | TypedDict) -> None
    """
    fun, dtype, doc = sanitize(fun_)

    args = get_args(doc)
    runexp_state = RunExpState.pop_state(args)

    # read config
    config_data = read_config(args.config_file)
    try:
        base_config: dict[str, typing.Any] = config_data["base_config"]
    except KeyError:
        raise ValueError(f"config at {args.config_file} should have a 'base_config'")

    # find sweep options
    sweep_opt: dict[str, typing.Any] | None = config_data.get("sweep", None)
    config_lst = get_sweeps(base_config, sweep_opt)

    if config_lst is None:
        config = try_cast(base_config, dtype)
        run_no_sweep(fun, config, args.config_file, runexp_state)
    else:
        run_sweep(
            fun,
            [try_cast(item, dtype) for item in config_lst],
            args.config_file,
            runexp_state,
        )

    return fun_


@typing.overload
def runexp_main() -> typing.Callable[[T], T]:
    ...


@typing.overload
def runexp_main(fun: T) -> T:
    ...


def runexp_main(fun: T | None = None) -> T | typing.Callable[[T], T]:
    """Use `fun`: as an entry point

    - fun: (python dataclass | pydantic dataclass | NamedTuple | TypedDict) -> None
    """

    if fun is None:
        return _runexp_dec
    return _runexp_dec(fun)
