---
layout: post
title: Spaces v. Tabs
tags:
excerpt: My opinion on tabs or spaces
---

The war between using spaces and tabs has existed pretty much since code ever written, with all programmers having their own opinions on the matter -- from the 8-wide tabs of linux to the 4 spaces of PEP8, there is no conclusive standard on what to use. Here, I'll provide a third, albeit rather unusual, approach.

<!--more-->

> Despite the wide range of standards, there is one universal rule regarding indentation: if you're contributing to a project **always use the style that's there** - never ever mix styles.

From occasionally witnessing this debate, there seems to be one main argument in support of spaces:

> _A tab could be a different number of columns depending on your environment, **but a space is always one column.**_
> -- StackOverflow, [Tabs versus spaces—what is the proper indentation character for everything, in every situation, ever?][1]

[1]: https://softwareengineering.stackexchange.com/a/66

However, this argument mainly stems from the need to _align_, rather than _indent_. Indeed, if you're only using tabs to align (and maybe a few spaces for more precision), this is the case - viewing with a tab width different to the one used to write will mess up the alignment. And in most cases, it's necessary to use spaces to align:

```python
do_thing(arg1,
         arg2,
         arg3)
```

Projects rarely have tabs be 3 or 9 characters, meaning spaces must be used for either the entire indent, or to fill in the remaining space after using some tabs.

It's this lack of distinction between indenting and alignment which makes space indenting much more commonly used. However, by distinguishing between these two uses, we can freely exploit the main benefit of tabs, their user-configurable width. Hence the rule becomes **tabs to indent, spaces to align**, also known as Smart Tabs. Aligned code looks aligned for everyone, and people are free to use whatever tab size they want.

I'm not completely sure about how easily editors can be configured to support this. I pretty much only use (Neo)Vim, and this behaviour cannot be achieved with just in-built settings. Plugins exist to support this, [including my own][2], which I use daily.

[2]: https://github.com/ralismark/itab

# Addendum: On tabs xor spaces

In the absence of any existing convention (e.g. C and C++), My preference is still towards using tab characters. I don't have a strong reason for this, though the customisability of tabs is one positive aspect.

Also, there's an accessibility argument to be made in favour of tabs -- see [this reddit post](https://www.reddit.com/r/javascript/comments/c8drjo/nobody_talks_about_the_real_reason_to_use_tabs/). The gist of it is this:

> i get approached by not one, but TWO coworkers who unfortunately are highly visually impaired, and each has a different visual impairment
>
> - one of them uses tab-width 1 because he uses such a gigantic font-size
> - the other uses tab-width 8 and a really wide monitor
> - these guys have serious problems using codebases with spaces, they have to convert, do their work, and then unconvert before committing
>
> --- /u/ChaseMoskal, Jul 2019
