---
layout: post
title: Where have I been?
excerpt: "The answer, as it always is, is burnout"
date: 2023-12-29
tags: meta static-site-generator
---

I currently have about 4 unfinished posts for this blog from this year.
I've pretty much completed the first draft for all of them, and only need to edit and clean them up.
So where are they?

The technically true answer is that I've been writing my own static site generator that I've named Heron, and using that instead of Jekyll.

# Heron

Now, this is something I've been wanting to do for a while -- I kept running into the limits of what is easy with Jekyll, and I never learnt enough Ruby to make plugin writing easy.
Especially when I started deviating more and more from the standard "individually rendered pages" scheme with [Somewhere](/somewhere).
Its replacement, Heron, is in Python and is way more flexible in the ways that I care about, particularly about the layout of the input files, to the point where I'm affectionately calling it a static site _build system_.

But that only took a handful of weekends, and all the content was migrated over by the end of November.

The actual answer is that completing Heron severely burnt me out from working on this website, and also coding in general.
Because even though Heron reached 90% feature parity within about two weeks, that last 10% took so much longer than expected:

- The `escape` filetype, which allowed insertion of arbitrary HTML into a code block.
I've only used this 5 times _ever_, across 2 blog posts ([Ownership](ownership) and [Alpern & Schneider](lets-prove-1)).
- Support for rendering GraphViz graphs (for 3 blog posts).
- Beating the hell out of the markdown engine[^mistune] until I was happy with its dialect.
- Tweaking all 80+ posts, drafts, and other pages to fix all the formatting differences between mine and Jekyll's dialect.
- Figuring out how to link blog posts together when Heron uses an _acyclic_ build graph.
- Coming up with a sensible way of doing wordcount.
- Figuring out a nice way to deploy the damn thing on GitHub Pages.

[^mistune]: Sorry, that's a bit harsh.
	[Mistune](https://github.com/lepture/mistune), which is what I'm using, is pretty good out-of-the-box and more importantly is extremely customisable.
	It's only because of that that I'm even able to make it do exactly what I want.

Each thing on its own isn't that major of an issue, but when you have 5 to 10 then it gets quite out of hand, and ended up taking several days of work more than I anticipated.
Plus I worked on this way more intensely during those last days than I should have because I was eager to have everything done and be able to get back to focusing on the actual content of the blog.

Days of what's basically crunch time on something that is meant to be a passion project, with the end that was always just barely out of reach, is a perfect recipe for burnout.

# Aftermath

I finished the rewrite 25th of November.
I then stopped doing basically any coding, I didn't even look at my blog, for a month.

To be honest, killing off all desire to code and enjoyment from it hasn't entirely been a bad thing.
It's taken up too much of my life in the past, and wanting to just relax is pretty nice, if a little boring.
And I guess lesson learned to stop myself from doing so much at a time.

I do want to get those drafts out the door soon -- one of them has been in the works since like January.
Probably early next year.
Though with that one I crunched a bit too hard as well and killed all the enthusiasm I had for it.

This post is just something I'm throwing together in an afternoon to waste some time and to ease myself back into website things.

Nothing about how Heron works here.
Maybe a future blog post.
[Or not](https://rakhim.org/honestly-undefined/19/).
