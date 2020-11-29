---
layout: post
title: Rope-Making With Treaps
tags: informatics
excerpt: Building treap ropes from first principles
---

Treaps are a very neat data structure that I've grown fond of. Though they are a [self-balancing binary search tree][sbbst], they differ from most other variants in that they can do much more than just store key-value pairs -- they can become *[ropes]*.

<!--more-->

[sbbst]: https://en.wikipedia.org/wiki/Self-balancing_binary_search_tree

Like dictionaries, [ropes] fall under the category of [abstract data types], but that's where the similarities end. They extend arrays with the two new abilities

[ropes]: https://en.wikipedia.org/wiki/Rope_(data_structure)
[abstract data types]: https://en.wikipedia.org/wiki/Abstract_data_type

1. Join (i.e. concatenate) two ropes into a single one
2. Split a rope at a point into two halves

in addition to access to elements by index.

Of course, this can be implemented using either linked lists or dynamic arrays, but both have time complexity trade-offs.

| | Access | Join | Split |
|--|--|--|--|
| Linked List | $$O(n)$$ | $$O(1)$$ | $$O(1)$$ |
| Dynamic Array | $$O(1)$$ | $$O(n)$$ | $$O(n)$$ |
| Treap | $$O(\log n)$$\* | $$O(\log n)$$\* | $$O(\log n)$$\* |

Treaps are a nice middle ground, with *expected* $$O(\log n)$$ (because of their probabilistic nature) for all operations.

# Cartesian Trees

Almost all the machinery for treaps are built on top of [Cartesian trees], so we'll look at them first. Formally, they are binary trees derived from a sequence of numbers, and satisfy two properties:

[Cartesian tree]: https://en.wikipedia.org/wiki/Cartesian_tree

<!-- that last sentence is kinda bad -->

1. An [in-order] traversal gives the original sequence (like other binary search trees)
2. Each node's value is not larger than its children's -- this is also known as the [heap] property

[in-order]: https://en.wikipedia.org/wiki/Tree_traversal#In-order_(LNR)
[heap]: https://en.wikipedia.org/wiki/Heap_(data_structure)

Though you *can* convert a list of numbers into a Cartesian tree, we won't need to -- you can join a bunch of single-element trees to do the same thing.

!["Cartesian tree"](https://upload.wikimedia.org/wikipedia/commons/d/d5/Cartesian_tree.svg)

*Cartesian Tree. Source: [wikipedia](https://en.wikipedia.org/wiki/Cartesian_tree#/media/File:Cartesian_tree.svg)*

# Join

The first operation we'll tackle is joining. The final tree will need to satisfy the heap property, so the root node must be the smallest element. Fortunately, due to that property, we know it must be one of the two root nodes.

We'll assume the left root is smaller. We can just mirror our final algorithm if the right root was actually greater. Here's an example:

{% graph %}
digraph {
	node [shape=circle, color="#ff9999"];

	1 [color="#99ee99"];

	1 -> {3, 8};
	3 -> {9, 7};

	node [color="#9999ff"];

	5 -> 10 -> {12, 15};
	15 -> {20, 18};
	5 -> r5 [style=invis]; r5 [style=invis];
}
{% endgraph %}

Since the in-order traversal of the output must go through the entire left tree before going through the right, we know that 1's left subtree remains there. The right side is different though -- if 8 remains the right child, we'll break the heap rule.

{% graph %}
digraph {
	node [shape=circle];

	node [color="#99ee99"];

	1 -> 3 [weight=3];
	1 -> r1 [style=invis]; r1 [style=invis];
	3 -> {9, 7};

	node [color="#ff9999"];

	8;

	node [color="#9999ff"];

	5 -> 10 -> {12, 15};
	15 -> {20, 18};
	5 -> r5 [style=invis]; r5 [style=invis];

	1 -> {8, 5} [style=invis];
}
{% endgraph %}

The correct child would be the smaller one, but we'd need to merge *their* subtrees ... wait, this is the same as our first step!

The problem we have now is analogous to our initial one, so recursion is the way to go to give us the complete join algorithm, which

1. Firstly, finds the smaller root node and sets it as the root of the output.
2. Then, recursively merges the other tree with the subtree on the same side -- that's blue with red in the example.

And that's it!

# Split

The other operation we need to support is splitting. Let's bring back the wikipedia example:

!["Cartesian tree"](https://upload.wikimedia.org/wikipedia/commons/d/d5/Cartesian_tree.svg)

*Cartesian Tree. Source: [wikipedia](https://en.wikipedia.org/wiki/Cartesian_tree#/media/File:Cartesian_tree.svg)*

Suppose we want to split this tree between 10 and 20. The first problem is that there are 3 edges between the two sides of the split: 1-5, 5-8, and 10-15. No worries -- we'll just erase them. But this leaves us with *too* many components.

Now, we could use the join algorithm we just made. But let's take a step back. Suppose we could efficiently determine, for any node, which side the split was on. With this, we could determine whether the split is in the *left or right subtree*. We'll tell that subtree, if it exists, to split itself (recursively), and replace it with the half that was on our side of the split[^1].

[^1]: I intended to including a visual for this. Unfortunately, making these trees with GraphViz is a real pain. Forcing the nodes to stay in the right place requires tangling up the graph with a lot of invisible edges and nodes.

This gives us the full splitting algorithm:

1. Determine which side of the root the split is on
2. Split the subtree on that side, if it exists
3. Reattach the closer half to the root

However, we've assumed that we can easily determine which side the split is on. I'll admit this is bit of a cop-out, since it isn't even possible with a bare Cartesian tree, but it'll be easy to support in a treap.

# Complexity

Both of our algorithms run in $$O(depth)$$. This looks great until you realise it's valid for a Cartesian tree to be a *linked list*. Which makes the worst case complexity $$O(n)$$.

Now, the obvious solution would be to require the tree be balanced. *How* to achieve this without tacking on a full-blown [self-balancing binary search tree][sbbst] is less obvious.

Treaps solve this is by exploiting two theorems[^2]:

[^2]: I don't know how either of these are proven. Sorry.

1. Random binary trees are, With High Probability[^3], balanced.
2. Cartesian trees generated from arrays of random numbers are uniformly random.

[^3]: To mathematicians, this means that the probability tends towards 1 as the size of the tree goes to infinity.

By using random numbers for the Cartesian tree, we ensure our operations are almost always $$O(\log n)$$ i.e. fast. However, we've lost the ability to store anything useful. To remedy this, we attach an *additional* value to each node (and call the random numbers the nodes' *priority*, to avoid confusion). Since the value can change independently to the priority, we can allow updating it in-place.

Or, we can forbid it, instead updating via split-split-clone-merge-merge, and gain persistence, since each node only know about its subtree.

This last point is important -- we can store *any* aggregate statistic, *as long as it doesn't depend on things outside its subtree*. This permits summaries like

- total length -- each node's length is one plus the sum of its children's lengths
- line count -- store the number of newlines
- *other* treaps computed from this treap
- well, *any* monoid or semigroup

to be calculated efficiently -- expected $$O(\log n)$$, as well.

# Actually Split

Still, we haven't solved our assumption for splitting: that we can determine which side of each node the split is on.

For now, we'll restrict our split function to only take the split-point as an index. Now, notice that this index will be on the left of the root *if and only if* it's not larger than the size of the left subtree. By tracking the size of each subtree, we'll satisfy our promise of an efficient response. This'll also allow us to *index* our nodes, which is really important.

In fact, you can use stranger split-point conditions, such as "before the first element which satisfies this predicate", by storing special summary information in each node. What information to store is left as an exercise to the reader.

# Summary

And with that, we have a fully functional *rope*. You can store sequences of any type, join them, split them, index them, even summarise them. You *can* adapt this into a dictionary by bolting on a binary search to a split function, but why would you -- there's way better ways of doing it.

The fast *summaries* -- `foldMap`, if you're familiar with Haskell -- are a lesser-known superpower of treaps (and ropes in general). With the right setup, you can achieve advanced behaviour including [word wrap](https://xi-editor.io/docs/rope_science_05.html) and [parenthesis matching](https://xi-editor.io/docs/rope_science_04.html) -- if you're interested (like me), have a read of the [Rope Science series in the Xi editor docs](https://xi-editor.io/docs/rope_science_00.html).

As an additional note, some other binary search trees also support join & split. [Wikipedia has a page on it](https://en.wikipedia.org/wiki/Join-based_tree_algorithms) which goes through a few other operations, but treaps are by still far the simplest.
