---
layout: post
title: A nice subset-sum solution
tags: c-cpp informatics
excerpt: Solving a "standard" problem in a very clean way
---

> This post was rewritten in May 2020

[Subset-sum][subsetsum] is a problem to determine if it's possible to find a subset of a given set of numbers which sum of a certain value. I found a very simple algorithms that can be extended to a few variations of the problem.

[subsetsum]: https://en.wikipedia.org/wiki/Subset_sum_problem

<!--more-->

For the problem, let:

- $$T$$ be our target sum, and
- $$w[0..N]$$ be an array of $$N$$ positive integers.

The standard dynamic programming approach is to have your subproblem be "is it possible to reach $$t$$ using only $$w[0..k]$$" for given $$t$$ and $$k$$. The recurrence is as follows:

$$
sss(t, k) = \begin{cases}
	0 & t < 0 \textrm{ or } k < 0 \\
	1 & t = 0 \\
	sss(t - w[k], k-1) \vee sss(t, k-1) & \textrm{otherwise}
\end{cases}
$$

We can see from this that $$sss(\cdot, k)$$ only depends on values of $$sss(\cdot, k-1)$$. As such, we can "optimise" this algorithm into an iterative one, performing the following transformation at every step:

$$
sss[t] \mapsto sss[t] \vee sss[t - w[k]]
$$

With $$sss[t] = 1$$ if $$t = 0$$ otherwise 0 initially.

Since we're working with boolean values, that looks like a bitshift! Translating this to C++ code:

```cpp
bitset<T+1> sss = {1};
for(int w_i : w) sss |= (sss << w_i);
// answer is sss[T]
```

Solved in only two or three lines.

# Variations of this problem

Since we are able to calculate $$sss(t, N-1)$$ for all $$t$$, we can also answer some optimisation problems:

- What is the largest sum possible under $$T$$? (find the highest bit set)
- How close can we get to T? (Use a bitset of length $$2T$$)

We can also solve similar problems, such as:

- [AIIO2013 - Flatman's Tower][fmt]: Input is a list of pairs. We can pick at most one value from each pair. (`sss |= (sss < a) | (sss < b)`)

[fmt]: https://orac.amt.edu.au/cgi-bin/train/problem.pl?set=aiio13&problemid=649

# Backtracking

In fact, we can even recover the subset used to make the sum by noticing that $$w[i]$$ allows us to "reach" all $$t$$ where $$sss[i+1][t] \wedge \neg sss[i][t]$$ is true:

```cpp
bitset<T+1> sss[N+1] = {{1}};
for(int i = 0; i < N; ++i) sss[i+1] = sss[i] | (sss[i] << w[i]);
// Assuming it's possible to sum to T
vector<int> taken;
for(int i = N-1, t = T; i >= 0; --i) {
	if(!sss[i][t]) {
		// We need w[i]
		taken.push_back(w[i]);
		t -= w[i];
	}
}
```
