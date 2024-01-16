---
layout: post
title: "Fortune Was So Broken"
excerpt: "All the bugs and quirks that didn't make into the previous post"
date: 2023-10-24
tags:
reason: wip
---

While testing out the various fortune versions for the previous post, I found so, _so_ many interesting bugs, issues, and just general oddities in the code.
So much that it was starting to bloat up that post!

I've taken them out of that article to keep it a bit tidier, but they're still really interesting (plus I don't want my research to go to waste), so I'll be covering them here.

# 4BSD's Empty Final Fortune

First up is 4BSD, whose `fortune` implementation straight up ignores the last fortune of the datafile.
I originally thought this was an off-by-one error, but it's actually intentional -- [this is a line from fortune.c](https://github.com/ralismark/fortune-history/blob/868398d2f3f338e7b8130973cf2dc6f0bd0f3e65/fortune.c#L52C34-L52C71):

```c
	numforts = tbl.str_numstr - 1;	 /* always a null string at the end */
```

And accordingly, the provided fortune collection has the last fortune be empty -- the final line is `%%`.

My guess as to why is that, in addition to finding where the text of each fortune is, the offsets in the datafile also get used to quickly figure out the length of each fortune.
`fortune` would read into the pair `long seekpts[2]`, then use the difference between them to determine whether to skip it when filtering for short/long fortunes.
This means that if `fortune` could pick the last fortune, `seekpts[1]` would be read from the actual text of the first fortune, which is basically meaningless in this context.

However, `strfile` doesn't know about this assumption, and processes the last fortune as normal, and won't be upset if it's not empty.
So, if you're curating a list of fortunes and correctly have the last entry be none, `str_numstr` will be "off by one", and more importantly, `str_shortlen` will always be zero.
Which means that if you're using `-s` (for short fortunes only) and you don't actually have any short fortunes, fortune will simply never terminate!

4.3BSD would fix this whole thing by having `strfile` write an extra offset after all the others, pointing just past the last fortune.
This removed the need for the last fortune to be empty and ignored by `fortune`.

Anyways, difference-of-`seekpts` couldn't be used with `strfile`'s new shuffling and sorting features, since they were implemented by simply changing the order that the offsets were stored.
The order of the strings didn't change, so offsets would be all over the place making `seekpts[1]` meaningless.
Ken also recognised this problem while making the 4.3BSD version, and so `fortune` only uses it for the length if neither flag was used when generating the datafile, falling back to counting non-null bytes if they were.

# 4.3BSD Can't Sort Empty Fortunes

While comparing the results of `strfile` between 4BSD and 4.3BSD, I found I was getting the completely wrong but oddly specific `0xbebebebe` as one of the offsets sometimes.
Turns out, there's a bug when populating the data structure used for `-o`, where a part doesn't get populated if the fortune is empty
...
and coincidentally, fortune files for 4BSD always have an empty fortune (at the end).

# 4.3BSD Can't Randomize Either

The random choice code seem incredibly broken in [the copy of the code I found](https://minnie.tuhs.org/cgi-bin/utree.pl?file=4.3BSD/usr/src/games/fortune/fortune.c).
It only ever gives the first fortune in the file.
The 4BSD version was fine so I'm not really sure what happened...

<!-- Loose End: getfort has a bunch of stuff for validating str_delims, what is that for? -->

<!-- Loose End: the 4.3BSD code I have in fortune-history is different from the one at https://minnie.tuhs.org/cgi-bin/utree.pl?file=4.3BSD/usr/src/games/fortune/fortune.c. So which one is correct, and where did I get the 4.3 code from? -->

# Long Got Bigger

In an attempt to be more portable, the 4.3BSD-Reno version started using `htonl` and `ntohl` to make integers stored in the datafile always be in big endian.
Problem is, those functions operate on 32-bit integers, while `long` on my machine is 64 bits wide.
So the datafile I got from `strfile` would have a bunch of `0x00'00'00'00` or `0xff'ff'ff'ff`, the latter being from sign-extending a 32-bit negative number to 64 bits.

I'm sure it was fine on the original systems though.

# Amy Lewis is mad a strfile

The 4.3BSD-Reno version

- wouldn't consistently ignore empty fortunes (Amy's version always ignores them)
- fails to sort the fortunes, since the sort routine thinks that there are no fortunes at all (Amy's version correctly gets the number of fortunes)
