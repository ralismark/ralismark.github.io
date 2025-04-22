---
layout: post
title: "5 Years Of This Website"
excerpt: A tour of the history of this place
date: 2022-05-10
tags: meta
---

Last month was the 5 year anniversary of the [first ever post] on this blog 🎉!
Both the website and I have changed a lot since then.
Still, many things have remained the same -- this has been hosted on Github Pages and made with Jekyll since the start, and I'm surprisingly still using the same laptop.
So here's a tour through its history.

[first ever post]: initial-post

# A Start

Here's what my first ever iteration of this website looked like.
It's only because of using git from the very start that this is even possible -- I only had to checkout the appropriate commit, copy over the latest Dockerfile and test script, and run it.

.. admonition:: me/say

	Fun fact: Originally there was a janky Makefile that was used to manage the docker container for local testing.
	It did some awkward stuff to try to be compatible with both Linux make and Windows nmake, including using temp files to track docker state.
	Nowadays, everything is handled by a 15-line shell script.

.. figure:: {{ recipe.copy("./1.png", "/assets/five-years:1.png") }}
	:alt: The main post listing page in an early version of this website.
		There is a big banner image of a white cherry blossom tree spanning the whole width, and an equally wide black bar just below with links to "Blog" and "Tags".
		Above this heading, on the left is the name of the blog "Triple Except" and on the right is the description "Discussion from all depths of computer science".
		The rest of the page consists of two blog post listings.
		The top one, titled "A Tale of Indices", was published on 13 April 2017, and the second, titled "e4ecd8b Initial Post" was published 11 April 2017.
		Below each of these is an excerpt from the post.

	29 April 2017.
	The first version.

If it looks vaguely familiar: yep, it's the [Wordpress _Twenty Ten_ theme] (well, an imitation of it).
I was most likely inspired by [Andrezej's blog] -- and at the time of writing this post, he _still_ has that 2010 theme (including the same header photo!), so hop on archive.org if you want to compare.

[Wordpress _Twenty Ten_ theme]: https://wordpress.org/themes/twentyten/
[Andrezej's blog]: https://akrzemi1.wordpress.com/

The "Triple Except" name has since been removed in favour of just calling this `ralismark.xyz`, rather unceremoniously in a April 2020 commit simply titled "Rebranding".
The line "Discussions from all depths of computer science" has also been mostly removed, but still lives on in link previews and search engine results as the default description metadata.

In the first month I also made two further posts that I've since hidden for privacy reasons, for a total of 4 -- not a bad start for someone still in high school -- and I would round out the year with total of 8.

# A Journey Through Time

The next step on the website's evolution was a complete overhaul into Bootstrap v4.0 in August of that year.

.. figure:: {{ recipe.copy("./2.png", "/assets/five-years:2.png") }}
	:alt: The post list page in a later version of this website.
		At the top is a grey navbar, with only the title 'Triple Except' on the left and a hamburger menu button on the right.
		Below is a big heading "Posts", followed by three blog posts entries:
		"Even More Concepts in C++14 (part 1)", published 7 May 2017;
		"A Tale of Indices", published 13 April 2017;
		"e4ecd8b Initial Post", published 11 April 2017.
		There is a small sidebar on the right, which just has a single area titled "Tags", listing out all tags for posts: "blog", "exploit", "c", "story", "school", "networking", "cpp", "template-mp".

	24 August 2017.
	Quite a significant change in scenery.
	This too was inspired by another person's blog, but unfortunately whose exactly has been lost to time.

And that general look would last all the way to the end of 2020, through several design updates, Jekyll tweaks, and overall refactors.
It'd get a separate landing page, a proper footer, and many more posts, but you can still trace the lineage back to the 2017 one.

.. figure:: {{ recipe.copy("./3.png", "/assets/five-years:3.png") }}
	:alt: Two screenshots of the website, in a similar style to before.
		The one on the left is of the Index page, which reads
		"Hi, I'm [redacted]. Welcome to my website.
		I'm a 1st year computer science student at UNSW.
		Right now, the most complete part is my blog, where I post stuff related to
		competitive and non-competitive programming, maths, as well as the occasional interactive post."
		Then there's a project listing, in the form of a garden with a simplistic tree for each one.
		The screenshot on the right is similar to the previous one, just with posts up to "You don't know binary search", and without the sidebar.

	22 July 2020[^details].
	It had gotten an index page and a bit of a rebranding, and recently a cute project listing, inspired by [an old version of a friend's blog] (maybe I should bring it back?).

[^details]: The redacted bits are my old name.
	~~Also, the website used to be public on github; see [this post](going-private) for why that's no longer the case.~~
	*\[update 2023-01-15: it's public again\]*

[an old version of a friend's blog]: http://htmlpreview.github.io/?https://github.com/acenturyandabit/acenturyandabit.github.io/blob/68a24395b008dde778b6576c805a4346a35f06b7/index.html

In those four years, I'd get way too involved in competitive programming, graduate high school, and get hit with a good amount of pandemic time.
C++17 came and went, and eventually so did C++20 (honestly C++17 still feels like the latest version to me even though it's already 2022).

And while I'd go start and eventually finish/abandon a lot of projects, this site always remained as something I'd occasionally come back to.
It wouldn't get much activity from me or traffic from the internet, but it would never get truly abandoned either.
And it stayed using the basic non-ES6, non-React web practices that I had gotten so familiar with over the years.

# A Ship of Theseus

A bit of a tangent: a good number of the changes I've done to the site were inspired by other people's blogs.
Both the original Wordpress look and the subsequent Bootstrap one were both reimplementations of other people's themes.
The cute garden from 2020, the webmention comments, even some of my posts -- such as [this][uses] and [this][sidenotes] -- were things I've added because I saw others with those features.

[uses]: uses
[sidenotes]: inline-notes

.. admonition:: me/say

	And more recently, I'd make myself home on these blog posts too, inspired by [Amos's Cool Bear] and [Xe's Mara (and co)].

[Xe's Mara (and co)]: https://christine.website/blog/how-mara-works-2020-09-30
[Amos's Cool Bear]: https://fasterthanli.me/articles/peeking-inside-a-rust-enum

So shoutout to the countless blogs and personal websites I've seen over the years that have shaped what this website became!

And with that, we reach January 2021, where I redid the design one "final" time -- this time more of an original theme -- to bring us to what we have today.

.. figure:: {{ recipe.copy("./4.png", "/assets/five-years:4.png") }}
	:alt: A screenshot of the index page in the style of this website.
		In the centre at the top is the website logo, a spiral of colour, atop a square of purple.
		Together with the links on its left and right, 'tools' and 'posts' respectively, they form the navbar.
		Below is a big heading 'Hi!'.
		Then there are two paragraphs reading
		"I'm [redacted] (or [redacted]), but I go by ralismark on the internet.
		I'm a second year computer science/maths student at UNSW";
		"On my blog, I (irregularly) post about competitive programming which sometimes goes into the more theoretical parts of computer science, other computing things and the occasional mathy post".
		Another header, "Things I've done" follows, then a list:
		"I've contributed to Tectonic Typesetting, a LaTeX engine written in Rust and C, submitting PRs to upgrade diagnostic reporting, add an unstable flag system, and integrate cbindgen";
		"I created a game using HTML Canvas and Javascript -- You can play it here".
		Significant portions of the text are shown as links.
		At the bottom is the page footer, which includes links to Twitter, Mastodon, Github, and email, links named "blog", "cat /posts/asterisk", "reading list", and "rss".
		There is also some text reading "All work licensed under CC BY-SA 4.0 unless otherwise stated. This site is open source!"

	29 January 2021[^details].
	It's honestly mostly the navbar and the dark theme.

You can somewhat see the resemblance to the contents of the previous index page, but alongside the initial Bootstrap version from 2017 or the earlier Wordpress imitation it's unrecognisably different.

In these intervening years, almost none of the lines of code have gone untouched.
[Is it still the same website](https://en.wikipedia.org/wiki/Ship_of_Theseus)?
Of course it is.

And since that day that I brought in this new design, I've started an actual job, gotten into and out of burnout, and had my world completely turned upside down by me turning out to be trans.
Looking back on my high school years it's hard to believe that that radically different person was me but, well, it is.

# A Look Forward

I don't this website going anywhere for the foreseeable future.
Posts are still coming, even if there's long gaps between them.
Heck, I'll probably end up redoing the design again at some point when I'm not satisfied by it.
And my life will keep on ticking through whatever new things come up.

So here's to another 5 years of me, my website, and my writing 🥂!
Who knows what things will be like then?

See you in 2027.
