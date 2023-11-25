---
layout: post
title: Stiching Together the Story of Fortune
excerpt: Doing some archeology on 40+ year old software
date: 2023-10-22
tags:
reason: wip
---

On Linux and BSDs, there's a cute little program you can install known as `fortune` (or `fortune-mod`) that has a single purpose -- it acts like a fortune cookie, picking a random fortune from a number of files and printing it.
However, this humble program has quite the history, having multiple forks over its over 40 year long history.
There's bits and pieces of it all over the internet, but nothing covering the whole history from start to end.
So that's what this post is[^why] -- stitching the pieces I could find together into one single story.

[^why]: This blog post is the product of several levels of yak shaving:

	1. I originally wanted to add [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) support to [fortune-mod](https://github.com/shlomif/fortune-mod), so that I could have it search for fortunes in more directories.
		This is particularly pertinent on NixOS, which I use, where you can't add fortunes to the default directory without a decent amount of work.

	2. But, in order to make that change, I had to understand how the code works first.
		Unfortunately, it's quite unclear and nothing close to straightforward, likely because of its long history, and there was quite a lack of comments explaining _why_ the code did things a certain way.

	3. So, I resorted to digging through the commit history and the blame.
		However, [fortune-mod](https://github.com/shlomif/fortune-mod)'s commit history only goes up to the start of this fork, which was after the changes I was interested in.

	4. To get as complete a history as I could, I decided to dig through archives of old BSD versions to get the start, and spelunking through the internet to find other snapshots of intermediate versions.
		With this, I assembled <https://github.com/ralismark/fortune-history>.

	5. Digging up the history left me with a sense that there was a story to tell here -- especially the individual contributions between NetBSD and the current (shlomif's) [fortune-mod](https://github.com/shlomif/fortune-mod).

	(I also felt like writing somewhat.
	Though there was a considerable gap between when I started this -- early 2023 -- and when I actually finished it)

In researching this, I've managed to assemble a pretty comprehensive code history in <https://github.com/ralismark/fortune-history>.
So have a look if you wanna have a look around!

.. admonition:: aside

	I'm also going to be focusing on just the fortune *programs* here -- mainly `fortune` and `strfile`.
	The actual fortunes strings that come bundled with it have their own story, but that's mostly for another time.

# In The Beginning

The lineage of `fortune` can be traced back all the way to at least 4BSD, where Ken Arnold is attributed.
However, Wikipedia claims that it has its origins a bit earlier, in Version 7 Unix in 1979.
And indeed, Unix V7 does have a fortune, but the behaviour and implementation is sufficiently different that I wouldn't be confident in saying they're related.
It simply picks a random line from the file at `/usr/games/lib/fortunes`.
It's actually really short -- this is the [entire source code](https://minnie.tuhs.org/cgi-bin/utree.pl?file=V7/usr/src/games/fortune.c)!

```c
#include <stdio.h>

char line[500];
char bline[500];

main()
{
	double p;
	register char * l;
	long t;
	FILE *f;

	f = fopen("/usr/games/lib/fortunes", "r");
	if (f == NULL) {
		printf("Memory fault -- core dumped\n");
		exit(1);
	}
	time(&t);
	srand(getpid() + (int)((t>>16) + t));
	p = 1.;
	for(;;) {
		l = fgets(line, 500, f);
		if(l == NULL)
			break;
		if(rand() < 32768./p)
			strcpy(bline, line);
		p += 1.;
	}
	fputs(bline, stdout);
	return(0);
}
```

I was actually quite surprised at how much this looks like C that people would write today.
Sure there's differences -- `main` is missing the return type and they're using the `register` keyword -- but this *still compiles with today's compilers*.
That's pretty amazing given that this is only 1979 -- Brian Kernighan and Dennis Ritchie just released their *The C Programming Language* book a year prior, and C would not become standardised for another decade!

Another thing I want to point out is that it's highly unlikely that this was written by Ken Arnold either.
Unix V7 was developed at Bell Labs, while Arnold was at Berkeley.
His BSD fortune would end up becoming the "canonical" version through its inclusion in BSD, but before that there were a variety of fortune implementations, likely in addition to the one above (I'm not really sure who the author of that even is).
Wikipedia supports this, saying that ["Arnold's quote-displaying program was not the first in history"](https://en.wikipedia.org/wiki/Ken_Arnold), though without a specific citation to back it up.

Still, this version would also be included in Unix/32V as well as 3BSD (which Ken might've been involved in? I'm not sure), just with expanded sets of fortunes.
But let's move on, to the first version that is recognisably the same program as the modern `fortune-mod`!

# 4BSD's Fortune

4BSD, released in late 1980, would include a full rewrite of fortune, and it is this version that would be the common ancestor of the modern implementations.
There were two main things of note that we got from this:

1. The `%%`-separated format for fortunes and the datafile it got processed into.
2. A distinction between non-offensive files.

This version also had command-line flags, to select between offensive/non-offensive fortunes among other things:

|Option|Description
|-
|-o|Only pick from offensive fortunes.|
|-a|Pick from both offensive and non-offensive fortunes. (The default is to only pick non-offensive fortunes.)|
|-s|Short fortunes (under 160 bytes) only.|
|-l|Long fortunes (over 160 bytes) only.|
|-w[^why-w]|Sleep a bit after printing the message, to give the user some time to read it.|

<!--TODO this is explicitly mentioned in the manual at some point-->
[^why-w]: My guess as to why `-w` exists is if you're running `fortune` in your logout script, so you have time to read it before the screen got cleared.
	You could probably achieve something similar just with `sleep`, but the time fortune waits before exiting is proportional to the fortune length, which would be tricky to replicate otherwise.

Interestingly, help is printed by running `fortune -` (that's a single dash), so I'm guessing we're right between when dash became the standard option syntax, and when `-h` or `--help` would be the standard help option.

And Ken Arnold's name is in a lot of places here:

- `strfile.c` contains the line `Ken Arnold      Sept. 7, 1978`
- `unstr.c` is similarly dated to `Aug 13, 1978`
- The man page (`fortune.6`, rather than in section 7) also includes the line "Mail suggested fortunes to arnold"

So yep, definitely him this time.

## 4BSD's Datafile

If you're familiar with fortune, you'll notice one key difference: modern fortune uses a single `%` to separate fortunes, while this version uses `%%`.
The main reason for this is that, unlike modern fortune implementations, both offensive and non-offensive fortunes were stored in the same file.
`%-` was used to partition them, so you'd have a sequence of non-offensive fortunes separated by `%%`, then a `%-`, then offensive fortunes similarly separated by `%%`.

Where this delimiter is is included in the datafile, which has a format like this:

- A header, which is a C struct with the fields:
	- `int str_numstr`, the total number of strings.
	- `int str_longlen`, the length of the longest string.
	- `int str_shortlen`, the length of the shortest string.
	- `long str_delims[3]`, the number of strings in each section -- this is what `%-` affects!
	- `int str_unused` padding.
- A list of `long` offsets into this this file, pointing to the start of each fortune.
- All the fortunes, null terminated, one after another.

Yep, this format is pretty non-portable between systems.
I'm not really sure why some fields are `int`s while others are `long`s, or whether there even is a difference on the systems that 4BSD was run on.
Anyways, when making the datafile, `strfile` would keep a counter of the number of fortunes, and when it saw a `%-`, it would put that counter into one of the `str_delims` fields.

.. admonition:: aside

	4BSD `strfile` also had two bugs in the delimiter processing code -- a _guaranteed_ null dereference, and an uninitialised variable -- that causes it to always crash on my system.
	The first was fixed in 4.2BSD as the only change to any of C code <!--REWORD-->, and the second in 4.3BSD by converting it into a global variable.

Ken Arnold would add shuffling (`-r`) and sorting (`-o`) to `strfile` in November 1984 as part of 4.3BSD.
This also turned `str_unused` in the datafile header into `str_flags`, which had bits indicating whether the input was shuffled or sorted or neither.

(This version would also be the origin of the "scene"/"obscene" terminology for correspondingly, non-offensive and offensive fortunes -- they were split up into two files with those names, and only joined together when building.)

# Luck of the Draw

The next major change to fortune would come in 4.3BSD-Reno, which got rid of the delimiters in favour of having multiple files of fortunes.
Now, offensive fortunes are in their own files that have the `-o` suffix, separate from the non-offensive ones.

> Fortunes are split into potentially offensive and not potentially
> offensive parts.  The offensive version of a file has the same name as the
> non-offensive version with "-o" concatenated, i.e. "fort" is the standard
> fortune database, and "fort-o" is the standard offensive database.  The
> fortune program automatically assumes that any file with a name ending in
> "-o" is potentially offensive, and should therefore only be displayed if
> explicitly requested, either with the -o option or by specifying a file name
> on the command line.
>
> --- [*Notes*](https://github.com/ralismark/fortune-history/blob/6bf93783e212a153c48e0c5ddfefd1790dd3a364/Notes#L22-L29)

<!-- TODO now _searching_ in /usr/share/games/fortune/ by default, instead of just reading /usr/games/lib/fortunes.dat -->

This also came with being able to specify multiple files and give them different weightings, allowing more control over what kind of fortunes you got!
So for example, you could run `fortune 90% funny 10% not-funny` to get fortunes from `funny` 9 times out of 10, and `not-funny` the remaining 10%.
The fortune files would get looked up from `/usr/share/games/fortune/`, and by default it'd use the `/usr/share/games/fortune/fortunes` file (or that with `-o` for offensive mode).

With the `str_delims` feature removed, the datafile got a bit of a change in its format.
Firstly, the datafile no longer contained the fortune strings -- the offsets instead point into the plaintext fortune listing, but more relevantly, the [header struct](https://github.com/ralismark/fortune-history/blob/6bf93783e212a153c48e0c5ddfefd1790dd3a364/strfile.h) also got a bit of a change, now consisting of:

- `unsigned long str_version`, which is currently 1.
- `unsigned long str_numstr, str_longlen, str_shortlen, str_flags`, are all still here, same as before.
- `unsigned char str_delim`[^delim-is-stuff] for the delimiter character, usually `%`.
	This was used by the `unstr` program to allow you to recover the plaintext fortune listing from the datafile.
- `unsigned char stuff[3]`, described as "long aligned space", which I'm guessing means padding?

[^delim-is-stuff]: Okay, this is a bit of a lie -- the actual format has `stuff` as an array of 4 characters, and `str_delim` as just a macro expanding to `stuff[0]`.

There were also some new flags:

|Option|Description|
|-
|-e|Weight _files_ equally, instead of distributing probability uniformly among indidivual fortunes.|
|-f|Print files that fortunes could be picked from|
|-m&nbsp;\<pat\>|Print all fortunes that match a regex|
|-i|Ignore case for -m|

<!--TODO rewrite this section to flow better-->

<!-- Loose End: Posfile?? -->

Something else this version introduced was the ability to mark in the datafile that the fortune text is rot13'ed, so that `fortune` would automatically un-rotate them before printing.
The reason for this feature was described as follows:

> Potentially offensive fortune files should NEVER be maintained in
> clear text on the system.  They are rotated (see caesar(6)) 13 positions.
>
> --- [*Notes*](https://github.com/ralismark/fortune-history/blob/6bf93783e212a153c48e0c5ddfefd1790dd3a364/Notes#LL30C1-L31C26)

And accordingly, the offensive fortunes are only distributed in rot-13 form, and additionally don't get installed by default.

It's pretty concerning if the contents are so bad that you explicitly made a feature to obscure them...

## Offensive

Arguably, offensive fortunes are a core part of fortune and its history, but, well... here's a note from a later maintainer:

> In another file in this directory (Notes), the original author(s) of the
> fortune distribution state that "racist, mysogynist [sic] (sexist), or
> homophobic ideas" should never be included in the fortune database.
>
> This was not the case when the database came into my possession
>
> --- [*Offensive*](https://github.com/ralismark/fortune-history/blob/5df75d22bd787ac59d402e199e30c562d295fe71/Offensive#L23C1-L27C64)

Skimming through them, a lot of them are really awful and full of misogyny/sexism/terrible inappropriate jokes.
I suppose you could say that they're a product of their time, but it's incredibly obvious that most of them are written by and for cishet white men.


At least this version doesn't have incredibly vile homophobia, racism, and Hitler quotes that the offensive collection would later gain..?

<div class="flex-centre">
<iframe src="https://tacobelllabs.net/@atomicthumbs/109349923317496233/embed" class="mastodon-embed" style="max-width: 100%; border: 0" width="400" allowfullscreen="allowfullscreen"></iframe><script src="https://tacobelllabs.net/embed.js" async="async"></script>
</div>

<br>

...

<br>

Let's move on.

# A Fork In The Road

After 4.3BSD-Reno came Net/2, from which the [NetBSD](https://en.wikipedia.org/wiki/NetBSD) project began in 1993.
4.4BSD would be released soon after as well and get incorporated (specifically 4.4BSD-Lite) into NetBSD 1.3.
The NetBSD project would stick around all the way to the current day, and maintain fortune with it.
Alas, there's not much to talk about for this part of history: plenty of fortunes would get added, but on the program side, there's basically no feature development, only maintenance and modernisation.

However, this is not the end of the story!
There is another, more interesting fork of history, roughly beginning at NetBSD 1.3, that we will follow.

From here, Florian La Roche[^florian] of Saarland University re-packaged it for Linux in April 1995 -- no functional changes except some compatibility things.
<!--TODO mention the debian version?-->
It would then get picked up by Amy A. Lewis, from the University of North Carolina, who would heavily modify fortune -- ["Too many changes to mention, really"](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/ChangeLog#L2C3-L2C39) -- in September and October 1995.
This involved a ton of bug fixes, some new features, and a lot of cleanup of the fortune collection -- her [changelog](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/ChangeLog) is pretty detailed and provides a bunch of insight into the different revisions during this time, but I only have a snapshot of the code from late October 1995.

[^florian]: He also made [an early Linux distribution known as Jurix](https://en.wikipedia.org/wiki/Jurix).
	This would eventually be used as the basis for SUSE Linux, which he also worked on.

First of all, bug fixes!
It turns out that the sorting and shuffling feature of `strfile` were completely broken, since the routines which reordered the fortunes always thought that there were no fortunes at all, due to the wrong size variable being used.
For this, she had quite some words to say:

> ```c
/*
 * Changes, September 1995, to make the damn thing actually sort instead
 * of just pretending.  Amy A. Lewis
 */
```
> --- [strfile.c](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/util/strfile.c#L39-L41)

> ```c
/*      i = Tbl.str_numstr;
 * Fucking brilliant.  Tbl.str_numstr was initialized to zero, and is still zero
 */
    i = Num_pts - 1;
```
> --- [strfile.c](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/util/strfile.c#L334-L337)

> ```c
/*      cnt = Tbl.str_numstr;
 * See comment above.  Isn't this stuff distributed worldwide?  How embarrassing!
 */
    cnt = Num_pts;
```
> --- [strfile.c](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/util/strfile.c#L386-L390)

> ```c
    Tbl.str_numstr = htonl(Num_pts - 1);
    /* Look, Ma!  After using the variable three times, let's store
     * something in it!
     */
```
> --- [strfile.c](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/util/strfile.c#L521-L524)

(She also fixed another issue with `strfile`'s handling of empty fortunes, but that didn't get nearly as much snark)

On the `fortune` side, there was a lot of change in functionality.
Offensive fortune lookup was changed (again), this time to look inside OFFDIR, allowing her to strip out a bunch of the old offensive fortune handling to filter out `-o` and so on.
There was also improvements to `-f` to make it report probabilities better, and the removal of a bunch of unnecessary file-locking logic that the Reno version had for some reason.

<!-- TODO include the simplified diff? -->

<!-- TODO more on the way in which it was broken: look at this claim by amy in README.Linux?
> I (Amy) hacked on this because it was broken; the BSD source itself is
> broken (I looked at it).  Specifically, if you are using an old version
> of fortune, then it accesses *only* the two files "fortunes" and
> "fortunes-o", even though 'fortune -[ao]f' will tell you differently.
> That was my original reason to start working with the code.
or maybe just relegate this to quirks
-->

Finally, she did the thankless job of going through all the fortunes (including the offensive ones!) and categorising them.

> This is a list of the data files included with this distribution, and
what they contain.
>
> \[...\]
>
> misogyny: Jokes that women encounter as real attitudes daily.  Real attitudes that women have to pretend are jokes daily.
>
> -- [cookie-files](https://github.com/ralismark/fortune-history/blob/11a1aca6e7e035eaf5c66a816488581d5d9eb9ad/cookie-files#L107C1-L108C58)

With these changes, fortune would be released on the UNC's SUNSite, reborn under the new name of `fortune-mod`.
<!-- TODO more on UNC SUNsite? -->

# Dennis

Amy A. Lewis would disappear and two years would pass until the next person decided to take a shot a improving fortune.
This person would be Dennis L. Clark, in UTS across the Pacific here in Sydney, who would _re_port it, fixing Linuxisms and making it work on even more systems, including BSDs again I think.
He would also _add back in_ a kind of `-o` compatibility mode -- when `fortune` encounters an fortune file argument with `-o`, it would remove that suffix and go look in the offensive directory.
This allows both offensive and non-offensive fortunes to share a name, so you could say `fortune 80% politics 20% politics-o` for example.

He would also start a version numbering scheme -- two digit year, two digit month, which is a rather interesting choice given the Y2K problem of the impending millennium.
Under this scheme, his versions are 9705 and 9708, and Amy's final version from October 1995 would be version 9510.

Also, a funny comment given that the first versions of fortune straight up predated ANSI.

> Sorry, pre-ANSI compilers are not supported (c'mon, this
> is the 90's, darn it!)
>
> --- [Changelog](https://github.com/ralismark/fortune-history/blob/b47aca4e4de2ecc614177c9b3101572872846c6f/ChangeLog#L25C17-L26C25)

Happy with the state of things, he would leave it here for the next person to pick up.

# Red Ellipse

In the years after, Debian became the main place where fortune was worked on.
The code would pass through many maintainers' hands during this time: Helmut Geyer, Brian Bassett, Mark Ng, and finally Pascal Hakim.
Pascal would end up reaching out to Dennis in February 2004, and from that Pascal would make a new release of fortune-mod -- version 1.99.1, intended to be a pre-release for a 2.0 (that would never come).

As it turns out, Debian's package of fortune has been around for an incredibly long time, as early as 1995!
Florian's port from NetBSD to Linux would mention a Debian version that's now very much lost to time:

> I have looked at sunsite and tsx and found one very old fortune program
> **and one in the debian Linux distribution**.
>
> --- [README.LINUX](https://github.com/ralismark/fortune-history/blob/5071d9df9791d539e47611b9efd1fe9be574128b/README.LINUX#L1C1-L2C42)

And there was always some cross-pollination between the individual contributors' history I've been describing, and Debian's package.

<!--TODO get quotes-->

.. admonition:: aside

	Within Debian, I only ended up going digging for the history of the fortune-mod package, and not the original fortune.
	The former only goes up to the origin of that name -- Amy's "9510" version.
	The history of the latter likely goes earlier, so I'll fill it in if I get around to it.

In the 7 or so years since Dennis's version, fortune-mod would switch versioning schemes again to be Y2K-compatible, and grow several more features.
Primarily, this was adding support for UTF-8 and some basic internationalisation capability, which were apparently ["one of the most requested features for fortune-mod"](https://web.archive.org/web/20070704161840/http://www.redellipse.net/code/fortune).
Specifically, `fortune` would transcode the fortune text to the native codeset of the system -- UTF-8 was nowhere near as universal yet -- and pick fortunes from locale-specific directory according to `LANG`/`LC_ALL`/`LC_TYPE`.

# Shlomif

And this leads us to Shlomi Fush's fortune-mod, the canonical version in packages repos everywhere today.
I don't think there's much been change except for one (on top of maintenance): making it possible to omit all offensive _functionality_ at compile time, in addition to not installing the offensive fortunes.

# Credits

So, thank you to everyone that's been maintaining Fortune over the years:

- Ken Arnold, who started it all, and possibly other people involved in BSD.
- The NetBSD folk: Chris Demetriou, Charles M. Hannum, J.T. Conklin, and Paul Kranenburg.
- Florian La Roche
- Amy A. Lewis
- Dennis L. Clark
- Pablo Saratxaga
- Pascal Hakim and Joshua Kwan, as well as previous Debian packagers and maintainers: Helmut Geyer, Brian Bassett, Mark Ng, David H. Silber

-------------------------------------------------------------------------------

Loose Ends:

- `Modified Jul 1999, Pablo Saratxaga <srtxg@chanae.alphanet.ch>` in Pascal's version
- reno's posfile
- `*** Fortune datafile 3 ***` in 4bsd's fortune file?
- unstr
