---
layout: post
title: "Tatham's Device - Hacking Coroutines Into C++"
date: 2099-01-01
excerpt: Abusing switch statements and lambdas for fun and profit
tags:
reason: wip
---

- intro
  - what are coroutines
  - how coroutines usually work
  - c++ has coroutines, but we can't use that yet
- switch statement abuse
  - duff's device
  - tatham's coroutines in c (both simple and advanced version) <https://www.chiark.greenend.org.uk/~sgtatham/coroutines.html>
- doing it in c++
  - limitation of tatham's device
  - using lambdas
- call/cc
  - callbacks (inc. non-allocating func)
  - supporting "co_await" and "co_return"
