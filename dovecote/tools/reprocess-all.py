#!/usr/bin/env nix-shell
#!nix-shell -p "python3.withPackages (p: with p; [ requests tqdm ])" -i python3

import requests
import tqdm

ENDPOINT = "http://localhost/_dovecote"

r = requests.get(ENDPOINT)
r.raise_for_status()
data = r.json()

for row in tqdm.tqdm(data["entries"]):
    source = row["source"]
    target = row["target"]
    r = requests.post(ENDPOINT, data={"source": source, "target": target})
