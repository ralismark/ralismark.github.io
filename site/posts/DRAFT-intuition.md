---
layout: post
title: Dissecting intuition & Exam technique
excerpt: How I do problem solving
date: 2020-10-30
tags:
reason: lowquality
---

> This post is quite low-polish.
> I had this topic queued up for quite a while, and this is just a dump of my thoughts.
>
> *Note*: For the first half of this post, beware of the [Typical Mind Fallacy](https://www.lesswrong.com/tag/typical-mind-fallacy).
> How my mind works may not be how yours works, or how other people's work.

"Intuition" is a term that gets thrown around quite a bit in competitive programming, at least where I learnt it.
It's generally understood to mean both your innate sense of what parts of the problem are important, and how well you "explore" the solution space to come up with possible approaches.

<!--more-->

I feel intuition is very much *not* a conscious reasoning process -- a bit like muscle memory.
I suspect it's more about pattern recognition, since certain types of problems tend to have certain types of solutions (e.g.
"answer range queries" are segment tree problems).
Of course, getting better at this comes from doing more problems[^1].

[^1]: Sounds like machine learning?

I find the subconscious nature of this reasoning fascinating.
I can often read a question then let it brew in my mind.
Even though my conscious thoughts seem to go in circles, after a bit a potential solution just pops into my mind.

Thinking about it, this is *weird*!

Taking that into consideration, it's really helpful to **read all problems before attempting any of them**.
I've sometimes discovered the solutions to problems over dinner.

On the topic of exam technique, there are certain common failure modes with regard to solution space exploration.
The biggest two are

1. Starting to type up a solution too early, and
2. more subtly, tunnel-visioning on particular techniques or types of solutions

both of which stem from committing to ideas too early.
For instance, in APIO 2019, I spent 3 of the 5 hours progressively improving my solution to problem A, before stumbling across an incredibly simple algorithm.

Another interesting anecdote from my IOI preparation was some people would imagine what their mentor would say about their exam technique, then correct for that.
From this grew the "positive/negative reinforcement" meme -- essentially just saying "positive reinforcement" for behaviour which is desirable, and "negative reinforcement" for undesirable or suboptimal actions.
