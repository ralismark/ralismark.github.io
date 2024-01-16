#!/usr/bin/env python3

import argparse
import sys

import mistune

from . import create_md


def ast_print(ast, indent=0):
    ind = "    "

    if isinstance(ast, list):
        if not ast:
            print("[]", end="")
        else:
            print("[")
            for v in ast:
                print(ind * (indent + 1), end="")
                ast_print(v, indent=indent + 1)
                print(",")
            print(ind * indent, end="")
            print("]", end="")
    elif isinstance(ast, dict):
        if not ast:
            print("{}", end="")
        else:
            print("{")
            for k, v in ast.items():
                print(ind * (indent + 1), end="")
                print(f'"{k}": ', end="")
                ast_print(v, indent=indent + 1)
                print(",")
            print(ind * indent, end="")
            print("}", end="")
    else:
        print(repr(ast), end="")


parser = argparse.ArgumentParser(
    prog="heron.md",
    description="Parse markdown using heron's parser",
)
parser.add_argument(
    "--ast",
    action="store_true",
)
args = parser.parse_args()

if args.ast:
    ast_print(create_md(None)(sys.stdin.read()))
else:
    print(create_md(mistune.HTMLRenderer(escape=False))(sys.stdin.read()))
