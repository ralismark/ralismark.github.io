---
layout: standalone
title: Design System
---

# Code Block

Example:

```bash
#!/usr/bin/env bash

greeting="hello world"
printf '%s\n' "$greeting"
```

# Table

Example:

| |Counter (non-decreasing)|Gauge (up and down)|
|-
|Average slope in time period|rate()|deriv()|
|Difference between last two samples|irate()|idelta()|
|Last sample minus first sample|increase()|delta()|

# Admonition

Example:

.. admonition:: me/say

	Hello I am an admonition!

	This is an example where I am saying something, to demonstrate you can have paragraphs in it!

Example:

.. admonition:: me/say

	Short message!

# Paper

Example:

.. html:: div
	:class: paper

	Paper element!

# Details

Example:

.. details:: This is the summary.

	It expands to show its content.
