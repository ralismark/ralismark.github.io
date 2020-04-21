---
layout: post
title: Small Merge
tags: informatics
excerpt: A generalisation of DSU's merge by size to be more useful.
---

Small merge is a technique derived from DSU which allows merging of groups (and data about groups) by moving elements between groups at most O(n log n) times.

<!--more-->

tl;dr: When merging collections of objects, only move from smaller group to larger group. This is O(n log n).

This was originally explained to me as a variation of union find: what if we directly update the parent pointer when we merge two sets? To do this, we'll need to be able to iterate over all nodes in a set, and we can store this in a vector. Then, when we merge, we only change the parent pointers of elements in the smaller set. In code, it's something like this:

```cpp
int root[N]; // initially, root[i] = i
vector<int> contents[N]; // initially, contents[i] = {i}

void merge(int a, int b)
{
	a = root[a]; b = root[b];
	if(contents[a].size() < contents[b].size()) swap(a, b); // ensure a's group is larger
	for(int i : contents[b]) {
		parent[i] = a;
		contents[a].emplace_back(i);
	}
	contents[b].clear();
}
```

By observing how a single value moves between sets, we can see that the number of moves is log of the size of set its in -- when a number moves, the set must at least double in size. Thus, the overall complexity in terms of total number of moves is in fact $$O(n \log n)$$.

# Generalising this idea

We can take the idea of only merging smaller into larger, and generalise it, such as by storing more useful information. Suppose we have the following problem:

> There are N integers, initially in separate groups. We want to support the following operations:
>
> - Merge two groups into one.
> - Answer query: How many elements in a certain group have a certain value?

To answer the second operation, we keep a map of the number of each value instead of just the contents, and use normal DSU. When merging, we merge from the group whose map is smaller into the one whose map is larger, thus being able solve the problem in $$O(n \log^2 n)$$ with each query being $$O(\log n)$$.

In particular, this technique is much more useful on trees, where we can entire remove the DSU required to find the root. [HackerRank - Coloring Tree][coloring-tree] is a good problem to demonstrate this:

[coloring-tree]: https://www.hackerrank.com/contests/101feb14/challenges/coloring-tree

> There is a rooted tree of size N, where each node has a value associated. We want to answer Q queries offline, each asking for the number of distinct values in a given subtree.

To do this, we keep a set for each node containing all values in the subtree. Then, we answer queries starting from the leaves, merging children subtrees into parents as needed. However, this lends itself more to a recursive algorithm. In pseudocode:

```
// solve queries at node
// returns the set of all value in its subtree
solve(node):
	values = set()
	for v in node's children:
		s = solve(v)
		values = merge(values, s) // small merge here
	add node's value to values
	answer queries at node
	return values
```

And that's the general shape of Small Merge algorithms! If you can keep data that's at most the size of the group, you can small merge.

If you want to read more, there's [a section on cp-algorithms][cp-algo].

[cp-algo]: https://cp-algorithms.com/data_structures/disjoint_set_union.html#toc-tgt-15

# Practice Problems

I couldn't find many problems which use this technique. If you know of any, please let me know in the comments below!

- [HackerRank - Coloring Tree][coloring-tree]
- [USACO Gold - Ying and Yang](http://usaco.org/index.php?page=viewproblem2&cpid=286)
- [Codeforces - Magic Tree](https://codeforces.com/contest/1193/problem/B)
