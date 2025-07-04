#!/bin/sh
set -eu

builddir=$(mktemp -d)
trap 'rm -rf "$builddir"' EXIT

name=${1:-kwellig.garden}

HERON_ENV=development heron dev --out="$builddir" "$name/_heron.py" "$@"
