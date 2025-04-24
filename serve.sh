#!/bin/sh
set -eu

builddir=$(mktemp -d)
trap 'rm -rf "$builddir"' EXIT

name=$1
shift

HERON_ENV=development nix run . -- dev --out="$builddir" "$name/_heron.py" "$@"
