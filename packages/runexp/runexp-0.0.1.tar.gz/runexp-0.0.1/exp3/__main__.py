import dataclasses
import typing

from pydantic import dataclasses as py_dataclasses

from runexp.config_file import runexp_main


@dataclasses.dataclass
class ParamsDC:
    num_epochs: int
    learning_rate: float


class ParamsTD(typing.TypedDict):
    num_epochs: int
    learning_rate: float


class ParamsNT(typing.NamedTuple):
    num_epochs: int
    learning_rate: float


@py_dataclasses.dataclass
class ParamsPydantic:
    num_epochs: int
    learning_rate: float
    train_modalities: typing.Literal["all"] | list[str]


# @runexp_main
# def main_dc(p: ParamsDC):
#     pass


# @runexp_main
# def main_td(p: ParamsTD):
#     pass


@runexp_main()
def main_nt(p: ParamsNT):
    print(f"{p.num_epochs=!r}")
    print(f"{p.learning_rate=!r}")
    pass


# @runexp_main
# def main_pydantic(p: ParamsPydantic):
#     "a toy function to make sure everything works fine !"
#     # pydantic enables validation by default !
#     print(f"{p.num_epochs=!r}")
#     print(f"{p.learning_rate=!r}")
