---
layout: post
title: You don't know binary search
tags: blog
excerpt: How to never write a binary search wrong again
---

Binary search is a very fundamental algorithm, but it's also quite a finicky one. It's easy to introduce bugs, especially when dealing with more complex criteria. One of the first things that students learn at the AIOC December camp is how to think about binary search in a way such that you'll never write it wrong ever again. This post is more or less a written version of that.

<!--more-->

> "*Although the basic idea of binary search is comparatively straightforward, the details can be surprisingly tricky*"
>
> ---Donald Knuth

But before we actually get into binary search, you have to learn about loop invariants first.

# Invariants

Broadly, invariants are guarantees about your code. For example, that one variable is always less than another.

**Loop invariants** are a common kind: these are conditions that are always true between every iteration of a loop. These define what assumptions you can make, but also what conditions you need to satisfy. Here's an example:

```c
// Determine the greatest value in an array
int max(int n, int* vals) {
	int most = vals[0];
	for(int i = 1; i < n; ++i) {
		if(vals[i] > most) most = vals[i];
	}
	return most;
}
```

The invariant here is that $$most$$ is the greatest value in $$vals[0 .. i-1]$$. 

Firstly, the invariant is before the loop is run -- the maximum of $$vals[0..0]$$ is simply the only element it contains, $$vals[0]$$.

Inside the loop, we want to maintain the invariant for the next iteration of the loop -- that $$most = \max(vals[0..i])$$. We're guaranteed by our invariant that $$most = \max(vals[0..i-1])$$, which we use in the body of the loop

$$
\begin{aligned}
most \gets& \max(vals[0..i])
\\ &= \max(vals[0..i-1], vals[i])
\\ &= \max(most, vals[i]).
\end{aligned}
$$

In this example, we used the loop invariant to determine the body of the loop.

# Binary Search

For our binary search, we'll find the first element in $$A[N]$$ that's not larger than $$X$$[^1], returning one past the end if it's not found[^2]. For this, we'll have two variables:

[^1]: The "standard" binary search of finding an element in a sorted array has [many edge cases that you need to consider & specify][so-binary-search]: How do we handle duplicate elements? What if the value is missing? What if the array is empty? and so on. The "lower bound" binary search is much simpler to reason about and avoids all of these edge cases.

[so-binary-search]: https://stackoverflow.com/q/504335/6936976

[^2]: i.e. the [lower_bound](https://en.cppreference.com/w/cpp/algorithm/lower_bound) function from the C++ standard library

```c
int lo = -1, hi = N;
```

Let $$P(i)$$ be a predicate which is true if $$A[i] \ge x$$. We'll have 3 invariants:

1. None of $$[0..lo]$$ satisfy $$P$$.
2. All of $$[hi..N-1]$$ satisfy P.
3. The loop only runs while there are indices between $$lo$$ and $$hi$$.

In our loop, we update either $$lo$$ or $$hi$$ depending on if the midpoint $$mid$$ satisfies $$P$$:

1. If $$P(mid)$$ then $$hi \gets mid$$
2. Otherwise, $$mid$$ does not satisfy $$P$$ and so $$lo \gets mid$$.

In both of these cases, we look at our invariants to avoid off-by-one errors.

<!-- TODO binary search diagram:
     0               N-1
    >-------------------<
..._.                   ._..
..._|_______||          |_...
...__________|   ||     |_...
^ blue      green ^       ^ red
              pivot

    (and so on, until red meets blue)
-->

From this, we can write the loop:

```cpp
while(lo + 1 < hi) {
	int mid = lo + (hi - lo) / 2;
	if(A[mid] >= X) {
		hi = mid;
	} else {
		lo = mid;
	}
}
```

Since $$mid$$ is always between $$lo$$ and $$hi$$[^3], the loop must eventually terminate. After this loop ends, we're guaranteed that:

[^3]: For an explanation of why `lo + (hi - lo) / 2` instead of the simpler `(lo + hi) / 2`, see [Nearly All Binary Searches and Mergesorts are Broken][broken-bs].

[broken-bs]: https://ai.googleblog.com/2006/06/extra-extra-read-all-about-it-nearly.html

1. There are no elements between $$A[lo]$$ and $$A[hi]$$, which means that
2. $$lo$$ is the greatest index that doesn't satisfy $$P$$, and
3. $$hi$$ is the smallest index that does.

And so we return $$hi$$.

# Generalising P(i)

In the entirety of our binary search, we haven't relied on any properties about $$P$$ other than the fact that it's monotonic:

$$
\begin{aligned}
P(i) &\implies P(i+1) & \textrm{and} \\
\neg P(i) &\implies \neg P(i-1)
\end{aligned}
$$

<!-- TODO monotonicity graph -->

In competitive programming, there are often situations where we have a monotonic predicate and we want to find the lowest integer where it is true. For example:

- [AIO2015 - Wet Chairs](https://orac.amt.edu.au/cgi-bin/train/problem.pl?set=aio15int&problemid=853)
- [IOI2010 - Quality of Living](https://ioi2010.org/Tasks/Day1/Quality_of_Living.shtml)
- [Widest path problem](https://en.wikipedia.org/wiki/Widest_path_problem)

In fact, whenever you want to "minimise the maximum" (or "maximise the minimum") of some quantity, binary search is almost always the answer.

# Extra: Early Exit

Binary search implementations commonly "early exit", returning the index if the midpoint matches the element you want to find. However, this rarely is useful:

- It has no effect on time complexity, and doesn't even get run most of the time.
- If you actually want the first/last element that's equal, the algorithm won't work.
- It's still another source of bugs, particularly if you're using "the loop terminated" to mean that the element wasn't found.

# Extra: Preconditions & Postcondition

There are another kind of invariant: preconditions and postconditions on functions. Instead of describing features of a loop, they are correspondingly guarantees before and after the function. Preconditions sometimes are requirement about the arguments (e.g. a pointer is not null), while postconditions can be guarantees about the return value (e.g. the function returns the maximum value in the array).
