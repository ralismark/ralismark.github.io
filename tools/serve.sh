#!/usr/bin/env bash
set -eu

# fix for NixOS
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

name=${1:-kwellig.garden}

builddir=$(mktemp -dt heron.XXXXXXXXX)
trap 'kill -- $(jobs -p); wait; rm -rf "$builddir"' EXIT

ln -s "$PWD/wrangler.jsonc" "$builddir/wrangler.jsonc"

HERON_ENV=development heron dev --no-serve --out="$builddir/dist" "$name/_heron.py" "$@" &

# setup databases
wrangler d1 execute --local --persist-to="$builddir/.wrangler/state" \
	kwellig-garden_dovecote --file=dovecote/schema.sql

# wait for initial build to complete
while ! [ -e "$builddir/dist/_worker.js" ]; do
	sleep 1
done

echo "$builddir"
wrangler dev --cwd "$builddir" &

wait -n
