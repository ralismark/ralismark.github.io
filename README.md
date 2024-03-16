# ralismark.xyz

This repo houses the code & documents for [my blog][index].

[index]: https://ralismark.xyz

To render this website locally, run `./serve.sh`.

## Syntax Style Rules

- Use tabs for indentation.
	Tabs are 4 spaces wide, but that shouldn't matter.

- Each sentence is on its own line.
	Lines are not broken at a certain column (use your editor's word wrapping feature for that).
	This isn't that strict when using colons -- both of these are permissible

	```
	There are some situations where colons make sense: This is one of them.

	There are some situations where colons make sense:
	This is one of them.
	```

	However, it is preferred that the part after the colon starts with an uppercase letter.
	So this is discouraged, but is not a strong requirement of the style guide:

	```
	There are some situations where colons make sense:
	this is one of them.
	```

- For multi-line footnotes and list items, subsequent lines (from multiple sentences) are indented one level.
	For example:

	```
	- This is a list item.
		It goes on and on and on.
	```

- For RST directives, leave a blank line before and after, and also have a blank line between the directive and the body (which is indented).

	```
	This is what an RST directive looks like:

	.. sparkle::

		Wow!

		This is a RST directive!

	That was quite the sparkle!
	```

There are a few things which I haven't decided on yet:

- Casing for titles and section headings.
- When to use tight/loose lists.
- Punctuation for list items and footnotes.

I am also yet to make a linter for this.
