from clipstick._parse import tokenize
from clipstick._tokens import Subcommand, TPydanticModel
import sys


def parse(model: type[TPydanticModel], args: list[str] | None = None) -> TPydanticModel:
    if args is None:
        args = sys.argv[1:]

    args = [model.__name__] + args
    root_node = Subcommand("__main_entry__", model.__name__, model)
    tokenize(model=model, sub_command=root_node)

    success, _ = root_node.match(0, args)
    if success:
        parsed = root_node.parse(args)
    else:
        raise ValueError("No matching pattern found.")
    return parsed["__main_entry__"]
