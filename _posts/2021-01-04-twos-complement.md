---
layout: post
title: Against "Flip Bits, Plus One"
tags:
excerpt: Teaching two's complement in a more intuitive way
---

A very common way of teaching the [two's complement](https://en.wikipedia.org/wiki/Two's_complement) representation of signed numbers is via "flip bits, plus one": to negate a number, flip all the bits then add one to it. However, this obscures the mathematical foundation underlying it that makes it works so nicely.[^1]

[^1]: *This is adapted from [one of my older tweets](https://twitter.com/ralismark/status/1272017613267189760?s=20)*

<!--more-->

> For this post, I'll be assuming that we're working with 8-bit numbers, but the idea can be easily extended for numbers of any size.

A better way to derive two's complement is to assume addition and subtraction "just work" for negative numbers. For example, here's -1, which we find by calculating 0 - 1:

| | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| &minus; | | | | | | | | 1 |
| - | - | - | - | - | - | - | - | - |
| -1? | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

We're also left with an extra borrow at the end. What if we just forget about it? This essentially means that numbers "wrap around" from 0 to 256[^2]. Following this rule, we can deduce that, for example, -10 gets represented as $$1111\;0110$$ (246 in decimal).

[^2]: In modular arithmetic terms, we're working with integers modulo 256, or $$\mathbb{Z}_{256}$$.

However, we encounter the problem that numbers which are any multiple of 256 apart are represented the same, and we can't distinguish between -10 and 246. Two's complement resolves this by defining $$1000\;0000$$ as the smallest number (-128) and $$0111\;1111$$ as the largest number (127). Placing the cutoff here means that there are roughly the same amount of positive and negative numbers. But more usefully, you can tell if a number is negative by looking at the highest bit.

You can similarly extend this to larger integers, defining $$1000\;0000\;0000\;0000$$ (-32768) as the smallest 16-bit number and $$0111\;1111\;1111\;1111$$ (32767) as the largest.

This representation has its foundation in [modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) ($$-1 \equiv 255 \mod 256$$), which also gives us the fact that addition, subtraction and multiplication all work the same as what we would do for regular unsigned numbers. In contrast, [ones' complement](https://en.wikipedia.org/wiki/Ones%27_complement) and [sign-magnitude](https://en.wikipedia.org/wiki/Signed_number_representations#Signed_magnitude_representation) are both plagued with several issues that two's complement automatically avoids, such as

- multiple zero representations i.e. both positive and negative zero
- more complex arithmetic operations

Finally, we can re-derive the "flip bits, plus one" explanation. Firstly, negating a number is the same as subtracting it from zero. Because numbers which are 256 apart are identical, negation is also equivalent to subtracting from 256. We can deduce that

$$
\begin{aligned}
-n &\equiv 0 - n
\\ &\equiv 256 - n
\\ &\equiv (255 - n) + 1
\\ &\equiv (0b1111\;1111 - n) + 1
\\ &\equiv (\text{\textasciitilde}n) + 1
\end{aligned}
$$

to recover the alternate "flip bits, plus one" explanation.
