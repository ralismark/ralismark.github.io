---
layout: post
title: Math Pet Peeves
tags: math
excerpt: Math notation which I don't like
---

I like maths. I do a decent amount of maths, and a lot of my friends do maths. But there are just a few things in maths that are especially annoy me. These aren't actual issues, just my stylistic and notational pet peeves.

<!--more-->

There's probably several more pet peeves, but I couldn't remember them when I wrote this post.

# 1. Parentheses

I really dislike the use of multiple styles of brackets when nesting. Maybe because I do a lot of programming I'm used to nested brackets, but the common practice of using square and round brackets for different nesting levels seems unnecessary.

- This is bad: $$k\left[\left(a+b\right)x + y\right]$$
- This is good: $$k\left(\left(a + b\right)x + y\right)$$

This use of different brackets also causes problems when you have very deeply nested expressions - which brackets do you use then? (I think the most common convention is to use braces next)

# 2. Mixed Fractions

Mixed fractions just should not exist. Yes, it's useful to tell the whole part of a fraction, but it's easily confused with multiplying the fraction with a number. At my level, multiplying a fraction without any operators between is really common. It's also easier to work with. Anyways, if you want the approximate value of a fraction, it's much useful to find the decimal approximation.

-  This is bad: $$3 \frac{2}{3}$$
-  This is good: $$\frac{11}{3}$$

# 3. Multiplication Cross

Also people who write $$x$$ as x.

The multiplication cross is way too easily confused with the letter x, especially if it's formatted in word with sans-serif font for everything (e.g. 2xy - is this 2y?). Honestly, I just use a lot of parentheses around the values being multiplied, but that's just me.

- This is bad: $$2 \times y$$
- This is OK: $$2 \cdot y$$
- This is good: $$(2)(y)$$ or $$2y$$

However, I'm generally okay with the multiplication cross if it's obvious there aren't any letters (e.g. a plain numeric expression, like $$2 \times 3$$).

# 4. Percentages

Don't multiply by 100% (or even worse, 100) to convert a decimal to a percentage! I treat percentages similar to a unit - conversion is implicit. The same thing can be said for ‰ (per mil), ppt (parts per thousand), and ppm (parts per million), though those are less common in maths.

- This is very bad: $$0.2 \times 100 = 20\%$$
- This is somewhat bad: $$0.2 \times 100\% = 20\%$$
- This is good: $$0.2 = 20\%$$

