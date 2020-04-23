---
layout: post
title: Algorithmic Proofing - Nearer Optimal Solution
tags: informatics
excerpt: Proving greedy algorithms by making optimal choices more greedy
---

Greedy algorithms are a great solution to problems, but it's usually harder to show they're incorrect than to come up with them. Nearer Optimal Solution is one technique that can be used when the problem involves making a sequence of choices.

<!--more-->

This technique involves initially assuming the greedy is not optimal (i.e. there's a better sequence of choices) and showing that it can always be made more like the greedy without being less optimal. Thus you can convert any "optimal" solution to the greedy, and so the greedy is optimal.

However, you need to be careful to ensure that you can indeed convert any optimal solution into the greedy.

In both of these examples, we'll consider the first difference. While this isn't necessary, it's a common approach. There are also a variety of algorithms which can be proven using this technique, such as Kruskal's MST.

## Example: Interval Maximal Independent Set

> You're given a set of intervals. Pick the largest number of intervals which don't overlap.

The greedy solution for this is to greedily take intervals with the earliest finishing time, ignoring ones which conflict with intervals we've already picked.

Let $$G$$ be the intervals chosen by the greedy, and $$S$$ the chosen intervals in an optimal solution that's different from the greedy i.e. $$S \neq G$$. Since $$S$$ is optimal, it must have as least as many intervals as $$G$$. Consider the first different interval (ordered by finishing time) - $$S_i$$ and $$G_i$$. Since the previous interval is the same, and $$G_i$$ finishes before $$S_i$$, we can replace $$S_i$$ with $$G_i$$ to get a solution that's closer to the greedy.

However, if $$G$$ is a strict prefix of $$S$$, we could've added the missing intervals to $$G$$ and so $$G$$ couldn't have been produced by the greedy.

Since you can always repeat this procedure to get to $$G$$, the greedy algorithm is optimal.

## Example: Sum of Squares[^1]

> You're given a number $$X$$. Pick $$N$$ non-negative integers which sum to $$X$$ so that the sum of squares is minimised.

[^1]: This specific example is used to prove the solution for [IOI 2007 Sails](http://olympiads.win.tue.nl/ioi/ioi2007/contest/day1/sails.pdf).

The optimal solution here is the one which is lexicographically least when sorted in descending order.

Consider two sequences of numbers $$S$$ and $$G$$, where $$G$$ is lexicographically less. Without loss of generality, assume both are sorted in decreasing order. Let $$A = G_i$$ and $$B = S_i$$, where $$i$$ is the first difference. Since $$G$$ is lexicographically less, $$A < B$$. Since the totals must be the same, there must exist $$j > i$$ where $$C = G_j > D = S_i$$.

$$
\begin{aligned}
	G:\;& G_1, G_2, G_3, \dots\ A\dots C \dots \\
	S:\;& \underbrace{S_1,\ S_2,\ S_3, \dots}_\textrm{same}\ B \dots D \dots
\end{aligned}
$$

Since $$A \ge C$$, we have $$B > A \ge C > D$$ and so $$B - D > 2$$ since everything is an integer. As such, we can modify $$S$$ through $$B \mapsto B - 1$$, $$D \mapsto D + 1$$ to make it more efficient and closer to the greedy.

Thus, the lexicographically least solution is optimal.
