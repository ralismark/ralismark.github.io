---
layout: post
title: A Glossy Menagerie
excerpt: Inline character dialogue across blogs
date: 2023-05-14
tags:
---

An interesting trend I've seen with blogging is people introducing characters to their blog in order to have a dialog with them, a bit like the [Socratic method].
I think this is a nicer alternative to rhetorical questions, plus they make the posts more interesting!

[Socratic method]: https://en.wikipedia.org/wiki/Socratic_method

I added support for them a bit under a year ago, but I'm still getting the hang of using them.
They're also pending some better art, though credits to [spdskatr] for the current placeholder one!

[spdskatr]: https://violetteahouse.com/

.. admonition:: say

	You should really get onto that!

I will!

# Other Examples

From a brief search I actually found quite a few occurrences:

- Amos (fasterthanlime) has [Cool Bear](https://fasterthanli.me/articles/the-bottom-emoji-breaks-rust-analyzer#exploring-utf-8-and-utf-16-with-rust)
- Xe Iaso has [Mara, Cadey, Numa, Aoi, Mimi, etc](https://xeiaso.net/characters)
- Cendyne has a lot of stickers, [such as ones here](https://cendyne.dev/topics/canonicalization.html)
- Manish Goregaokar has [pions](https://manishearth.github.io/blog/2022/08/03/colophon-waiter-there-are-pions-in-my-blog-post/)
- Matus Benko has [a cute little octopus](https://primamateria.github.io/blog/neovim-nix/)
- Not quite characters, but Alexander Payne (myrrlyn) uses [ISO 7010 signs](https://myrrlyn.net/blog)

# What I Want

So far, there's a few archetypes for how I use blockquotes and these characters:

1. Quotations, e.g. "`std::locale` is implementation defined --- \[locale.general\]"
2. Meta-information about the post, e.g. "This is part 1 of this series"
3. Warning callouts, e.g. "This won't work if you enable `use_foobar`"
4. Author's notes, e.g. "I might write a followup on this particular point"
5. Asides, e.g. "A fun fact is that this was broken until 2004"
6. Dialog, e.g. "I thought you explained it wouldn't work, so why does it?"

It doesn't really make sense for quotations to use custom portraits.
Warnings should definitely stand out and be very visually distinct.
There isn't really a clear line between meta-information, author's notes, and asides, but they're all pretty much "me saying things while I write".
Dialog is the only really distinct one.
This brings the minimal set of portraits to roughly:

1. Warning, or indicating caution
2. Asking a question
3. Talking while writing the article
4. (Neutral) talking

As an aside, a friend mentioned that a lot of games also have character portraits accompanying their dialog (e.g. Undertale, OneShot, Omori).

# Afterword: What's With The Title

The other day, I was wondering what it's called when you have a bit of text in a different style between paragraphs of regular text.
HTML has the `<aside>` tag, but I've also seen ones for warnings/etc be called *callouts* and *admonition*.
So I asked around:

<iframe src="https://fosstodon.org/@ralismark/110092770799442633/embed" class="mastodon-embed" style="max-width: 100%; border: 0" width="400" allowfullscreen="allowfullscreen"></iframe><script src="https://fosstodon.org/embed.js" async="async"></script>

Among the responses (mostly answering "aside"), a friend made me aware of the word *gloss*, meaning "A brief explanatory note or translation of a foreign, archaic, technical, difficult, complex, or uncommon expression, inserted after the original, in the margin of a document, or between lines of a text" (from [wiktionary]).
That's a pretty fun word!

[wiktionary]: https://en.wiktionary.org/wiki/gloss#English

Now, this is a pretty distinct thing from the character dialogues above, but honestly once I thought of the title it was too good to pass up.
And to be honest, I do also use the dialogue-style for these asides when it's me (the author) talking about the post.
