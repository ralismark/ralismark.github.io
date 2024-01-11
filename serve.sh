#!/bin/sh
set -eu

builddir=$(mktemp -d)
trap 'rm -rf "$builddir"' EXIT

direnv exec . python -m heron dev --out="$builddir" site/main.py "$@"
