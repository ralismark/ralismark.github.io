---
layout: post
title: Writing good tests
excerpt: How to write good tests if you're handwriting individual testcases
date: 2020-10-03
tags:
reason: wip
---

Define "bug space" as all possible bugs that could be in your code.

- When writing tests, think about what kind of bugs this test could catch, and roughly how likely those bugs are (e.g. buggy corner cases from independent systems are *very* low likelihood).
	For this, you kind of need an mental model of how likely various bugs are, which comes with programming experience.
- Tests should ideally cover different parts of the "bug space" - what does this testcase check that others don't check?
	- You only need a single failed testcase to pick up a bug, more errors for the same thing doesn't provide any extra benefit.
