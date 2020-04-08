---
layout: post
title: A nice 0-1 knapsack variation solution
tags: c-cpp informatics
excerpt: Solving a "standard" problem in a very clean way
---

The [knapsack problem][ksp] is a informatics problem to find the set of items whose total weight is under a given limit and whose total value is as high as possible. The 0-1 knapsack problem is a variation where there is only 1 of each item. A subcategory of this problem (I call it the allocation problem) is when the value is the weight i.e. the problem is to find the highest weight possible under a limit. It turns out that there's very simple way to solve this problem.

[ksp]: https://en.wikipedia.org/wiki/Knapsack_problem

<!--more-->

Inputs:

- N, the total number of items
- W, the weight limit
- w<sub>i</sub>, the weight of the ith element (non-negative)

Output:

- W<sub>max</sub>, the maximum attainable weight under W

In this variation, we only need to store if each weight sum is possible, and that this sum will not be greater than W. As such, we can represent it an array of bools. Normally, for each item, you would iterate through the possible weights in reverse and update the possible weight. This is what you'd do for general 0-1 knapsack, but since we only care about if its possible, we can use `std::bitset` and bit shifting to get a very clean solution:

```cpp
bitset<W+1> possible = {1};

for(int w_i : weights) {
	possible |= (possible << w_i);
}

for(int i = W; i >= 0; --i) {
	if(possible[i]) {
		cout << i;
		break;
	}
}
```

Note that this requires W to not be too large, but most problems don't have an extremely large W. This also works for similar problems where the weight and the value is the same.

