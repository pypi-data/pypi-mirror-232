import argparse
import pprint

from runexp import parse

query_strategies_name = ["flexmatch", "fixmatch", "freematch", "rand"]

parser = argparse.ArgumentParser("exp1", description="first experiment")

parser.add_argument(
    "--strategy",
    help="acquisition algorithm",
    type=str,
    choices=query_strategies_name,
    default="rand",
)
parser.add_argument(
    "--query_strategy",
    type=str,
    default=None,
    help="(opt.) other strategy to query: must be compatible with strategy",
    choices=query_strategies_name,
)
parser.add_argument(
    "--nQuery", type=float, default=5, help="number of points to query in a batch (%%)"
)
parser.add_argument(
    "--probRemoveGland",
    type=float,
    default=0.4,
    help="probability that a gland annotation will be removed an used as an unsupervized label initialy [0,1]",
)
parser.add_argument(
    "--doFullySupervized",
    type=bool,
    default=False,
    help="Set to True if you want to run the code as if the processed dataset was fully supervized (but still applying the gland annotation removal parameter)",
)
parser.add_argument(
    "--nEnd", type=float, default=100, help="total number of points to query (%%)"
)
parser.add_argument(
    "--nEmb", type=int, default=256, help="number of embedding dims (mlp)"
)
parser.add_argument(
    "--seed", type=int, default=1, help="the index of the repeated experiments"
)
parser.add_argument(
    "--device",
    type=str,
    default="0",
    help="GPU device",
)
parser.add_argument("--batch_size", type=int, default=4, help="the batch size")
parser.add_argument(
    "--save-image-freq",
    type=int,
    default=30,
    help="save images after every N epochs. Skip saving with -1",
)
parser.add_argument(
    "--allow_no_tensorboard",
    action="store_false",
    dest="tensorboard",
    help="if False or unset, tensorboard must be installed for the script to run",
)
parser.set_defaults(tensorboard=True)

# model and data
parser.add_argument("--model", help="model - resnet, vgg, or mlp", type=str)
parser.add_argument("--dataset", help="dataset (non-openML)", type=str, default="")
parser.add_argument("--data_path", help="data path", type=str, default="./datasets")
parser.add_argument("--save_path", help="result save save_dir", default="./save")
parser.add_argument("--save_file", help="result save save_dir", default="result.csv")

# for gcn, designed for uncertainGCN and coreGCN
parser.add_argument(
    "-n",
    "--hidden_units",
    type=int,
    default=128,
    help="Number of hidden units of the graph",
)
parser.add_argument(
    "-r",
    "--dropout_rate",
    type=float,
    default=0.3,
    help="Dropout rate of the graph neural network",
)
parser.add_argument(
    "-l",
    "--lambda_loss",
    type=float,
    default=1.2,
    help="Adjustment graph loss parameter between the labeled and unlabeled",
)
parser.add_argument(
    "-s", "--s_margin", type=float, default=0.1, help="Confidence margin of graph"
)

# for ensemble based methods
parser.add_argument("--n_ensembles", type=int, default=1, help="number of ensemble")

# for proxy based selection
parser.add_argument(
    "--proxy_model", type=str, default=None, help="the architecture of the proxy model"
)

# training hyperparameters
parser.add_argument(
    "--optimizer", type=str, default="SGD", choices=["SGD", "Adam", "YF"]
)
parser.add_argument(
    "--n_epoch",
    type=int,
    default=200,
    help="number of training epochs in each iteration",
)
parser.add_argument(
    "--schedule",
    type=int,
    nargs="+",
    default=[80, 120],
    help="Decrease learning rate at these epochs.",
)
parser.add_argument("--momentum", type=float, default=0.9, help="Momentum.")
parser.add_argument(
    "--lr", type=float, default=0.1, help="learning rate. 0.01 for semi"
)
parser.add_argument(
    "--gammas",
    type=float,
    nargs="+",
    default=[0.1, 0.1],
    help="LR is multiplied by gamma on schedule, number of gammas should be equal to schedule",
)
parser.add_argument(
    "--save_model", action="store_true", default=False, help="save model every steps"
)
parser.add_argument(
    "--load_ckpt", action="store_true", help="load model from memory, True or False"
)
parser.add_argument(
    "--add_imagenet", action="store_true", help="load model from memory, True or False"
)

# args = parser.parse_args(sys.argv[1:])
args = parse(parser)

pprint.pprint(vars(args))
