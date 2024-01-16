#!/bin/sh
set -eu

builddir=$(mktemp -d)
trap 'rm -rf "$builddir"' EXIT

HERON_ENV=development nix run . -- dev --out="$builddir" site/main.py "$@"
