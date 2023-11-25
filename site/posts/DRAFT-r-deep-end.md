---
layout: post
title: R confusion
excerpt: R is a weird programming language
date: 2019-01-08
tags: opinion
reason: wip old
---

Over the past year, I've been learning R on-and-off and using it for graphs and statistics.
Now, since I've had experience with many other languages, so I thought that I would be able to learn it relatively quickly.
This, combined with how infrequently I encounter use cases, lead me to try to learn it ad-hoc.

The way I went about this was that I followed a *very* brief tutorial to get to know the language, then figured out how to the things I needed just from searching online (e.g.
stackoverflow).
Despite this approach somewhat working for other languages [^1], I never quite wrapped my mind around R.

[^1]: Lua and Python, and Java to a lesser extent

There are several contributing factors to this that I can think of:

- Odd expression-based syntax
- Emphasis on statistics

Firstly, it is much more flexible with expressions compared to other languages.
Take this example:

```r
plot.1 <- spin %>% ggplot(aes(label = paste(id, t), color = id, x = t, y = ang)) +
	geom_point(shape = 4) + geom_smooth(method = "lm")
```

Normally, `ggplot` takes the data to use as the first parameter, but the `%>%` operator acts as a "pipe", using the previous expression as the first argument instead.
This works with *any* function without modification, which means that the operator is either modifying the expression, or somehow overrides calling.
Either way, this subverts our expectations already.
Secondly, the arguments to `aes` take "variables", but these are in fact columns of the input data, evaluated separately for each row.
This is quite unusual compared to other languages, which can only take arguments by value/reference, and cannot use the actual expression [^2].

[^2]: There are excepctions to this, such as C/C++ macros (inc. `assert`) and possibly introspection, but they are generally considered bad practice or even hacks.
	R much more widely accepts their use.

In comparison, `d3.js`, a javascript library for data visualisation which I am currently learning, uses functions for row-dependent values:

```javascript
d3.select('div').selectAll('p')
    .data(stats)
  .enter()
    .append('p')
    .text((d) => d.name)
```

The last line clearly shows that the value depends on each row.
This syntactic difference is even clearer when the value is computed using other functions.

> Note: despite the issues I describe here, it's still a great language, and definitely my go-to for statistics
