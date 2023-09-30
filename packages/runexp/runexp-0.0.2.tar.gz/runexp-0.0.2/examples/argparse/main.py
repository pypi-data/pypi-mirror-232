import argparse
import pprint
import time

from runexp import parse

choices = ["first", "second", "third"]

parser = argparse.ArgumentParser(
    "exp1",
    description="first experiment",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument("target", type=str)
parser.add_argument("--choice", type=str, choices=choices, default=choices[0])
parser.add_argument("--float", type=float, default=5.0)
parser.add_argument("--flag", action="store_true")

parser.add_argument("--no-option", action="store_false", dest="option",)
parser.set_defaults(option=True)

parser.add_argument("--sf", action="store_false")
parser.add_argument("--sc", action="store_const", const=3.14, default=2.72)

parser.add_argument("--string", type=str, default="")
parser.add_argument("--other-string", type=str, default="a value")

parser.add_argument("--lst", type=int, nargs="+", default=[80, 120])

# args = parser.parse_args()
args = parse(parser)

# this is where you would use the values
pprint.pprint(vars(args))
time.sleep(1.0)
