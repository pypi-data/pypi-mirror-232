import dataclasses
import typing

from pydantic import dataclasses as py_dataclasses

from runexp.config_file import runexp_main


if __name__ != "__main__":
    raise RuntimeError("scripts should not be imported")


@dataclasses.dataclass
class ParamsDC:
    num_epochs: int
    learning_rate: float
    tags: list[str]


class ParamsTD(typing.TypedDict):
    num_epochs: int
    learning_rate: float
    tags: list[str]


class ParamsNT(typing.NamedTuple):
    num_epochs: int
    learning_rate: float
    tags: list[str]


@py_dataclasses.dataclass
class ParamsPydantic:
    num_epochs: int
    learning_rate: float
    tags: list[str]


def main_dc(p: ParamsDC):
    "a toy function to make sure everything works fine !"

    print(f"{p.num_epochs=!r}")
    print(f"{p.learning_rate=!r}")
    print(f"{p.tags=!r}")


def main_td(p: ParamsTD):
    "a toy function to make sure everything works fine !"

    print(f"{p['num_epochs']=!r}")
    print(f"{p['learning_rate']=!r}")
    print(f"{p['tags']=!r}")


def main_nt(p: ParamsNT):
    "a toy function to make sure everything works fine !"

    print(f"{p.num_epochs=!r}")
    print(f"{p.learning_rate=!r}")
    print(f"{p.tags=!r}")


def main_pydantic(p: ParamsPydantic):
    "a toy function to make sure everything works fine !"

    print(f"{p.num_epochs=!r}")
    print(f"{p.learning_rate=!r}")
    print(f"{p.tags=!r}")


# run any of those !
runexp_main([main_dc, main_td, main_nt, main_pydantic][-1])
