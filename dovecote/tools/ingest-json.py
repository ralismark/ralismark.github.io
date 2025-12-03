#!/usr/bin/env python3

import datetime as dt
import json

with open("export-from-webmention-io.json") as f:
    data = json.load(f)

KEYS = [
    "source",
    "resolved_source",
    "target",
    "resolved_target",

    "entered_ts",
    "updated_ts",
    "valid",

    "type",
    "published_ts",
    "author_name",
    "author_photo",
    "content_html",
]


def repr_sql(value):
    match value:
        case None:
            return "NULL"
        case int():
            return str(value)
        case str() as s:
            return "'" + s.replace("'", "''") + "'"
    raise ValueError(value)


print(f"INSERT INTO Webmention({",".join(KEYS)}) VALUES")

first = True
for wm in data["links"]:
    try:
        # our old testing data
        if "banksia.ralismark.xyz" in wm["source"]:
            continue

        source = wm["source"]
        source = source.replace("https://brid-gy.appspot.com/", "https://brid.gy/")

        target = wm["target"]
        if "brid.gy" in source:
            target = target.replace("www.ralismark.xyz", "kwellig.garden")
            target = target.replace("ralismark.xyz", "kwellig.garden")

        rtarget = target
        rtarget = rtarget.replace("www.ralismark.xyz", "kwellig.garden")
        rtarget = rtarget.replace("ralismark.xyz", "kwellig.garden")

        kind = wm["activity"]["type"]
        if kind == "link":
            kind = None

        row = {
            "source": source,
            "resolved_source": source,
            "target": target,
            "resolved_target": rtarget,

            "entered_ts": int(dt.datetime.fromisoformat(wm["verified_date"]).timestamp()),
            "updated_ts": int(dt.datetime.now().timestamp()),
            "valid": 1,

            "type": kind,
            "published_ts": wm["data"]["published_ts"],
            "author_name": wm["data"].get("author", {}).get("name"),
            "author_photo": wm["data"].get("author", {}).get("photo"),
            "content_html": wm["data"]["content"],
        }
        assert set(row.keys()) == set(KEYS)
        print(f"\t{" " if first else ","}({", ".join(repr_sql(row[col]) for col in KEYS)})")
        first = False

    except Exception as e:
        raise ValueError(wm) from e

print("\t;")
