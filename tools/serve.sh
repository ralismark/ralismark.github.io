#!/usr/bin/env bash
set -eu

name=${1:-kwellig.garden}

builddir=$(mktemp -dt heron.XXXXXXXXX)
trap 'kill -- $(jobs -p); wait; rm -rf "$builddir"' EXIT

ln -s "$PWD/wrangler.jsonc" "$builddir/wrangler.jsonc"

HERON_ENV=development heron dev --no-serve --out="$builddir/dist" "$name/_heron.py" "$@" &

# wait for initial build to complete
while ! [ -e "$builddir/dist/_worker.js" ]; do
	sleep 1
done

echo "$builddir"
wrangler dev --cwd "$builddir" &

wait -n
