---
layout: post
title: A Healthy Diet of Monoids
tags:
excerpt: Doing a bunch of stuff with monoids
reason: wip
---

# Syntactic monoids & balancing parentheses

You have your monoid (S, e, +), but include a mapping `metric :: C -> S` and a set of accepting states A.

- Each token maps to a value in your monoid
- A string is in L iff `foldMap metric` of that string gives a value in A

For balanced parentheses you have

- S = (Z+, Z+)
- e = (0, 0)
- metric(`(`) = (0, 1) and metric(`)`) = (1, 0)
- (a, b) + (c, d) = (a + min(0, c - b), d + min(0, b - c))
- A = { e }

The pair is the *bicyclic semigroup* and represents the amount of unpaired closing and opening parentheses.

# Length

Mapping `metric = const 1` over the Plus monoid. Gives you number of tokens in your string. Not really useful on its own, but helpful when combined with other stuff.

# First and Last

Two basic monoids using S = `Option<T>` and e = None. First gives you the first non-None value, and Last gives you the last non-None value. (l + r) is defined that if either argument is None, return the other, but if both are not None, return `l` (for First) or `r` (for Last).

If we have `T = (value, offset)` and a `metric`, we can get the location of "first/last occurrence of something".

# Outer semidirect product - Fancy composition

Given two monoids `M` and `N` as well as a homomorphism `act :: M -> (N -> N)` (like the notion of group action, but, you know, monoids), the semidirect product `M * N` satisfies

- S = M x N (normal cartesian product)
- e = e x e (identity is the same)
- (a, x) + (b, y) = (a + (act y) b, x + y)

Useful example is the semidirect product of `Last (T, offset)` and `Length`, with `act l (v, o) = (v, o + l?)`, which gives offset without you needing to pass it in.
