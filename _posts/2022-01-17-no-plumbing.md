---
layout: post
title: Don't Plumb For The Programmer
tags: opinion
excerpt: A sort of follow-up to "Write Libraries, Not Frameworks"
---

I was recently linked this article by a coworker: [Write Libraries, Not Frameworks](https://www.brandons.me/blog/libraries-not-frameworks).
It's a great article and I very much recommend that you read it, but the gist of it is to write code that can interop with other libraries and leverage the underlying language as much as possible, rather than adding domain-specific ways of doing things that don't compose easily.

A sort of corollary of this I've seen, particularly with Python, is when scripts get written just to call some function and print the outputs -- essentially just a lot of "plumbing" to parse user input into actual datatypes, then converting the output back to some neater format, such as a table.

Here's something that I've seen python beginners write, particularly people who aren't primarily programmers (recently, mostly finance people).

```python
#!/usr/bin/env python3

import sys
import pandas as pd

df = pd.read_csv("some-data.csv")
locations = df["location"].values

if len(sys.argv) < 2:
    print("Usage: main.py <locations>")
    exit()

for loc in sys.argv[1:]:
    if loc not in locations:
        print(f"{loc} is not a valid location")
        exit()

    df[df.location == loc].plot(x="date", y="count")
```

Now, stylistically there's nothing with that code.
It does do its job well -- taking in location names and plotting data for them -- and in under 20 lines.
However, if this is the kind of one-off script to just plot data, much of this is extraneous and completely unnecessary.
The python interpreter, especially when improved with [IPython](https://ipython.org/), is perfectly usable, even if it does take a bit to get over the unfamiliarity of repl interfaces.
Or, if that's not your taste, you can use jupyter, or even a python script that you keep open in an editor and run.
All these cases are the same: directly use python, instead of adding an intermediate translation step.
It also allows easier exploration -- you can immediately "ask" the API for whatever information you want.

The main issue with this kind of thing is that this only exposes a tiny portion of the API surface, and if the person interacting with the API wants anything different, or wants to compose bits, they'll have to open up the script and either make temporary changes, or directly interface with the API via the above things.
Even with a collection of scripts, you can only ever expose a subset of the API.

Now, there still are some valid reasons from doing this.
The main one is to hook up a bunch of API calls and extra post-processing and cleanup to present a more complete overview -- something like a status summary, though in some cases it's arguable better to add these plumbing functions to a library so they don't get repeated re-implemented and duplicated.
Another is if the users aren't familiar with Python, or there's value in hiding the complexity of the API, such as if there's a lot of concepts that need to be understood to.
