import argparse
import datetime
import itertools
import multiprocessing
import os
import pathlib
import shlex
import subprocess
import sys
import typing

import psutil

from . import slurm_utils
from .parser_utils import Options, add_runexp_args, RunExpState


_PREFIX_SWEEP_ARG = "sweep-"
_PREFIX_SWEEP_DST = "sweep_"


def prohibit_prefix(action: argparse.Action, prefix: str):
    if action.dest.startswith(prefix):
        raise argparse.ArgumentError(
            action,
            f"prefix {prefix!r} is reserved by runexp",
        )


def check_action(action: argparse.Action):
    if action.dest == "help":
        return

    # make sure there are no reserved prefixes used in the parser
    for prefix in Options.all_prefixes():
        prohibit_prefix(action, prefix)
    prohibit_prefix(action, _PREFIX_SWEEP_ARG)


def add_sweep(parser: argparse.ArgumentParser, action: argparse.Action):
    label = argparse._get_action_name(action)
    parser.add_argument(
        f"--{_PREFIX_SWEEP_ARG}{action.dest}",
        type=str,  # list to split
        required=False,
        help=f"Sweep comma separated list of values for {label}",
        dest=f"{_PREFIX_SWEEP_DST}{action.dest}",
    )


def make_runexp_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    "create a new RunExp parser with appropriate sweep options"
    runexp_parser = argparse.ArgumentParser(parser.prog + "-runexp", add_help=False)

    for act in parser._actions:
        check_action(act)
        add_sweep(runexp_parser, act)
    add_runexp_args(runexp_parser)

    return runexp_parser


def sweep_as_dict(runexp_ns: argparse.Namespace) -> dict[str, list[str]]:
    "compute the sweep parameters for each relevant argument"
    sweep_dict = {}
    for attr, csl in vars(runexp_ns).items():
        if attr == _PREFIX_SWEEP_DST:
            raise RuntimeError(
                f"empty sweep parameter: {attr=!r}: this should not happen"
            )

        # not swept : the original parser should produce an error if no value are given
        if csl is None:
            continue

        if not attr.startswith(_PREFIX_SWEEP_DST):
            raise RuntimeError(
                f"parameter {attr!r} non recognized: this should not happen"
            )

        parameter_start = len(_PREFIX_SWEEP_DST)
        parameter = attr[parameter_start:]
        values = str(csl).split(",")
        sweep_dict[parameter] = values

    return sweep_dict


def iter_sweep(sweep_dict: dict[str, list[str]]):
    "iterate all sweep configuration from dictionary of configurations per parameter"
    choices_len = map(len, sweep_dict.values())
    choices_idx_iter = itertools.product(*map(range, choices_len))

    def idx_to_param(indices: tuple[int, ...]):
        return {
            dest: value[idx]
            for ((dest, value), idx) in zip(sweep_dict.items(), indices)
        }

    yield from map(idx_to_param, choices_idx_iter)


def build_param(action: argparse.Action, param_value: typing.Any) -> list[str]:
    "compute the parts for '--name [val0 [val1 [...]]]'"
    key = action.option_strings[0]
    nargs = action.nargs

    # simple boolean options: --set-opt
    if nargs == 0:
        if param_value is True:
            return [key]
        return []

    # Omitting 'nargs' is only supported for simple actions
    if nargs is None:
        if not isinstance(action, argparse._StoreAction):
            raise NotImplementedError(
                "only 'store' action with no 'nargs' are currently supported"
            )

    # length checking
    if isinstance(nargs, int):
        # input should be a list of adequate length
        if not hasattr(param_value, "__len__") or len(param_value) != nargs:
            raise ValueError(f"expected {nargs} values for {action}: {param_value!r}")
    elif nargs == "+":
        if not hasattr(param_value, "__len__") or len(param_value) < 1:
            raise ValueError(
                f"expected at least one value for {action}: {param_value!r}"
            )

    # --key val0 [val1 [...]]
    if nargs in ["+", "*"] or isinstance(nargs, int):
        return [key] + [str(v) for v in param_value]
    elif nargs == "?" or nargs is None:
        return [key, str(param_value)]
    else:
        raise ValueError(f"unexpected value for nargs ({nargs!r}): {action=!r}")


def build_command(parser: argparse.ArgumentParser, namespace: dict[str, typing.Any]):
    "inverse of ArgumentParser.parse: produce a command from a parser and a namespace"

    # NOTE This is simplistic and will likely need updates when the workflow gets more complex

    parts: list[str] = []
    done_keys: list[str] = []

    for action in parser._actions:
        # skip help
        if action.dest == "help":
            continue

        param_value = namespace.get(action.dest, None)

        # this is considered: even if it's not written
        done_keys.append(action.dest)

        # skip omitted optional values : it is not possible to pass None
        if param_value is None:
            if action.required:
                raise ValueError(f"missing a value for {action}")
            continue

        # print shorter command by removing the defaults
        if param_value == action.default:
            continue

        if action.option_strings:
            parts.extend(build_param(action, param_value))
        else:
            parts.append(str(param_value))

    if sorted(done_keys) != sorted(namespace.keys()):
        done = set(done_keys)
        ns = set(namespace.keys())
        raise ValueError(f"no done: {sorted(ns-done)}\nwtf: {sorted(done-ns)}")

    return parts


def run_no_sweep(
    cmd: list[str],
    caller_file: pathlib.Path,
    name: str,
    state: RunExpState,
):
    if not state.use_slurm:
        # we can reach here by specifying the number of processors
        if state.no_dry_run:
            subprocess.run(cmd)
            return
        else:
            print(shlex.join(cmd))
            return

    now = datetime.datetime.now()

    if state.template_file is not None:
        command = shlex.join(cmd)
        destination_path = slurm_utils.job_path(caller_file, now.isoformat())

        slurm_utils.run_from_template(
            state.template_file,
            destination_path,
            state.no_dry_run,
            name,
            command,
            state.slurm_args,
        )
        return

    # srun invocation
    srun_command = ["srun"] + state.slurm_args + cmd
    if state.no_dry_run:
        subprocess.run(srun_command)
    else:
        print(shlex.join(srun_command))

    return


def run_sweep(
    sweep_cmd_list: list[list[str]],
    caller_file: pathlib.Path,
    name: str,
    state: RunExpState,
):
    now = datetime.datetime.now()

    def _run_once(cmd: list[str]):
        return subprocess.run(cmd)

    def format_cmd(cmd: list[str]):
        return shlex.quote(shlex.join(cmd))

    if not state.use_slurm:
        if state.no_dry_run:
            with multiprocessing.Pool(state.max_concurrent_proc) as pool:
                pool.map(_run_once, sweep_cmd_list)
        else:
            for arg in sweep_cmd_list:
                print(format_cmd(arg))
        return

    if state.template_file is None:
        raise ValueError("slurm sweep are only implemented with template files")

    # add each configuration as its own command
    bash_array = "commands=(\n  "
    bash_array += "\n  ".join(format_cmd(cmd) for cmd in sweep_cmd_list)
    bash_array += "\n)"

    sbatch_options = [
        f"#SBATCH --array=1-{len(sweep_cmd_list)}%{state.max_concurrent_proc}",
        "",  # newline before the args,
        bash_array,
    ]

    slurm_utils.run_from_template(
        state.template_file,
        slurm_utils.job_path(caller_file, now.isoformat()),
        state.no_dry_run,
        name,
        "${commands[%a]}",
        state.slurm_args,
        sbatch_options=sbatch_options,
    )

    return


def get_python_head_flags() -> list[str]:
    "necessary flags for the system executable before any arguments"
    sys_args = sys.argv[1:]
    argc = len(sys_args)
    ps_args = psutil.Process(os.getpid()).cmdline()[1:]

    assert ps_args[-argc:] == sys_args
    return ps_args[:-argc]


def parse(parser: argparse.ArgumentParser) -> argparse.Namespace | typing.NoReturn:
    # Using custom args is not allowed: we need to find the command that
    # initiated this process to reuse the right arguments
    args = sys.argv[1:]

    # used for module, optimization, ..., target
    python_flags = get_python_head_flags()

    # detect if any RunExp options were used (slurm or sweep)
    runexp_parser = make_runexp_parser(parser)
    runexp_ns, remaining_args = runexp_parser.parse_known_args(args)
    runexp_state = RunExpState.pop_state(runexp_ns)  # removes specific fields as well

    # no runexp options, don't interfere with the program
    base_args = parser.parse_args(remaining_args)
    if len(remaining_args) == len(args):
        return base_args
    base_cfg = vars(base_args)

    def _make_command(ns_: dict[str, typing.Any]):
        return [sys.executable] + python_flags + build_command(parser, ns_)

    # executed file
    filename = pathlib.Path(sys.argv[0])
    name = parser.prog or filename.stem

    # build configs one by one
    sweep_dict = sweep_as_dict(runexp_ns)

    # simpler no-sweep config
    if not sweep_dict:
        run_no_sweep(
            _make_command(base_cfg),
            filename,
            name,
            runexp_state,
        )
        exit(0)

    # build 1 command per config
    all_commands: list[list[str]] = []
    for param in iter_sweep(sweep_dict):
        # update the namespace
        new_cfg = {**base_cfg, **param}
        # rebuild the CLI command
        all_commands.append(_make_command(new_cfg))

    run_sweep(all_commands, filename, name, runexp_state)
    exit(0)
