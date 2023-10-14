---
layout: post
title: "Logical Day"
tags:
excerpt: 'An alternate meaning of "today" and "tomorrow"'
---

Conventionally, "today" and "tomorrow" are relative to a date that switches over to a new day at midnight.
However, this can be a bit awkward when it's around midnight, which can be a frequent occurrence for people with less-than-ideal sleep schedules.
In these cases, "tomorrow" can become "today" halfway through a conversation, for example.
It also causes a mismatch with each day being a big period of awakeness delineated by sleep.

As such, I'm going to propose an alternate system: _Logical Day_.

# Logical Day

What if a period of awakeness _is_ the same day?
If you're out on a Friday night and it gets to 1 or 2am, "today" is _still_ Friday for you, and if you're planning something for "tomorrow", then that means it's scheduled for Saturday.
There might be other names for this (let me know if there are!), but I've been calling it _logical_ day, and the starts-at-midnight day _physical_ day.

I originally stumbled across this idea from [NativLang's video on timekeeping around the world](https://youtu.be/eelVqfm8vVc?t=384).
To summarise a part of that video, in Japan, times past midnight are sometimes considered part of the previous day and counted as such, with 1am being the 25th hour, 2am being the 26th, all the way to the 30th hour at 6am.
The [Wikipedia page](https://en.wikipedia.org/wiki/Date_and_time_notation_in_Japan#Time) also elaborates on this, giving examples of usages in late-night bars and television scheduling.
And from a quick search online, it seems that many societies in history have had day start at sunset, with night being part of the next day, or sunrise, with night being part of the previous day.

{% include admonition verb="aside" %}
> Similarly, for many cultures and much of history, [a year didn't start on January 1](https://en.wikipedia.org/wiki/New_Year#Adoptions_of_January_1)!
> 25 of March was used in several countries during the Middle Ages, for example.

I guess along these lines you could just have a fixed start-of-day time at some time when everyone should be asleep, like 4am.
I've found this kind of logical day in some pieces of software.
The main one that comes to mind right now is Anki, which has a "next day starts at" settings.
I also do this in my [Ibis Wiki](https://ralismark.xyz/ibis-wiki/) for determining which day's journal entry to show, though I hardcode the day to start at 5am.
If you know any other software that does this please let me know!

Of course, things are ambiguous while both conventions are around.
And in this aspect, physical day is unfortunately way more established.
Plus, logical day breaks down with more extreme sleep patterns, such as if you pull an all nighter (when does day switch over if you don't sleep?), or if you go to bed after others have woken up.

Anyways, that's an overview of logical day!

# Tangent: "Next Monday" Problem

While most people use physical day for "today" and "tomorrow" making them not unclear, the same isn't the case for terms for days relative to today.
There's a lot of variety in this area, meaning different things to different people:

- next monday
- this monday
- the coming monday
- next week monday
- next monday week

and similar for other weekdays.
I think people are able to figure out what is meant most of the time but at the same time people don't actually agree on the rules on what term to use, or what each phrasing mean.

(There probably has been surveys done about what people actually use but I haven't looked for any qualitative data on this topic. It's just a thing that comes up in conversation every so often)

And this doesn't even get to which day weeks start on -- is it Sunday[^weekends]? Monday? Or even Saturday? -- making the phrase "this week" ambiguous for a couple days each week.
I'm personally in favour of having the week start on Sunday, partly because on Sunday you're thinking about the upcoming week, and partly for the humorous reason that that makes the weekends be the two _ends_ of the _week_.

[^weekends]:
    I like sunday as the first day of the week for two reasons.
    Firstly, on Sunday you'll often be planning for the week ahead, and in that context "next week" feels somewhat unnatural.
    Secondly, this makes Saturday and Sunday the two ends of the week ;)

# Tangent: Absolute Time, Relative Day

While writing this, I was reminded of a notation that was used at Autumn Compass for time during a trading day.
Since all of our software operated in UTC, a trading day for many exchanges would cross over midnight UTC and physically be part of two days, and given that UTC midnight is a bit before noon here in Australia, this was a very common occurrence.
We also often needed to have a way to specify a time within each trading day, e.g. to set when we should start trading.
Since each trading day has an associated date (usually the day it fell into in the local timezone), we used times relative to midnight UTC of that date -- e.g. `22:00:00` -- but with an extension.
You could append `+1` or `-2` or similar to the end to specify "tomorrow", or "two days ago", or any other day offset.
For example, 11pm here in Sydney (UTC+10) is at `9:00:00+1`, and 7am in Pacific Standard Time (UTC-8) is `23:00:00-1`.
