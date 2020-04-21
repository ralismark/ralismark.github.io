---
layout: post
title: Short and simple LIS
tags: informatics
excerpt: O(n log n) Longest Increasing Subsequence in just 7 lines
---

The [Longest Increasing Subsequence problem](https://en.wikipedia.org/wiki/Longest_increasing_subsequence) is a "standard" problem in informatics, and it is sometimes used as an introduction to more advanced DPs. While the naive DP algorithm runs in $$O(n^2)$$, this can be optimised to $$O(n\log n)$$ using a variety of data structures and algorithms.

<!--more-->

Here's the algorithm:

```cpp
size_t lis(vector<int> const& nums) {
	set<int> s;
	for(int i : nums) {
		auto at = s.lower_bound(i);
		if(at != s.end()) s.erase(at);
		s.emplace(i);
	}
	return s.size();
}
```

# Deriving this algorithm

Despite not looking like a DP, it is in fact based on one: Let $$dp(n, h)$$ equal the length of the LIS using numbers no greater than $$h$$ from $$A[1..n]$$. Thus, we derive the recurrence

$$
dp(n,h) = \begin{cases}
dp(n-1,h) & h < A[n] \\
\max(dp(n-1,h), dp(n-1, A[n]-1)+1) & h \ge A[n]
\end{cases}
$$

From this we can see to calculate $$dp(n, \cdot)$$, we only need the values of $$dp(n-1, \cdot)$$. As such, we can memory optimise the DP to performing the mapping

$$
lis(h) \mapsto \begin{cases}
lis(A[n] - 1) + 1 & h \ge A[n] \wedge lis(h) = lis(A[n] - 1) \\
lis(h) & \text{otherwise}
\end{cases}.
$$

for each element of $$A$$. Additionally, we can observe that $$lis$$ is strictly increasing (that is, if we increase $$h$$, the LIS can only stay the same or increase), meaning that the range of $$h$$ which satisfy the first condition is continuous, and so we simplify the recurrence to

$$
lis(h) \mapsto \begin{cases}
lis(h) + 1 & A[n] \le h < m \\
lis(h) & \text{otherwise}
\end{cases}
$$

where $$m \in \mathbb{Z} \cup \{\infty\}$$ is the lowest number such that $$lis(m) > lis(A[n])$$.

> I'll see if I can make a diagram demonstrating this

Now, you can get an $$O(n \log n)$$ solution from here using a segment tree, but with a few more observations, we can further simplify things:

1. $$lis(h) - lis(h-1)$$ is either 1 or 0 for all $$h$$.
2. $$lis(h) \neq lis(h-1)$$ only when $$h \in A[1..n]$$.

Intuitively, (1) means that $$lis$$ can only step up one at a time (removing the last element from a increasing sequence will produce another increasing sequence) and (2) means that these steps only occur at values of $$A$$ (which is intuitively obvious once you think about it).

The key idea to creating the `std::set` solution is to *only* track these steps. Thus, finding $$m$$ becomes a `lower_bound` (line 4) and the range increment is equivalent to decreasing a value in the set (lines 5 and 6).

Getting the value of $$lis(h)$$ is then the same as counting how many "steps" are below $$h$$ i.e. the number of elements in the set not greater than $$h$$. Finding $$lis(\infty)$$, which is done to get the final answer, simply means taking the size of the set, and querying any other value can be supported by using an [order-statistic tree](https://en.wikipedia.org/wiki/Order_statistic_tree).

# Extensions of this algorithm

You can use the basic ideas of this LIS algorithm to support:

- Longest decreasing sequence, by sorting the set in reverse order with `std::set<int, greater<int>>`
- Longest non-increasing/non-decreasing sequence, by using a multiset
- Run-length encoding as input, using a `std::map`.

# Practice Problems

In order of difficulty:

- [LeetCode - Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence)
- [AIO2008 - Russian Dolls](https://orac.amt.edu.au/cgi-bin/train/problem.pl?set=aio08sen&problemid=360)
- [BOI2010 - PCB](http://kodu.ut.ee/~ahto/boi/2010/?item=boi.tasks.1)
- [Codeforces - Magic Tree](https://codeforces.com/contest/1193/problem/B)
