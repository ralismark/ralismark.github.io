---
layout: standalone
title: Visual Tests
---

{% set filler = "Suppose you want to determine whether a star is a giant. A giant star has a large extended photosphere. Because it is so large, its atoms are spread over a greater volume." %}

# Code Block

## Test 1: Overflow

The code block should be scrollable and not exceed 50% content width.
The background colour should be present for the entire width.

.. html:: div
	:style: width: calc(var(--content-width) / 2)

	```
	{{ filler }}

	{{ filler }}

	{{ filler }}
	```

## Test 2: Tall Text

Tall text should not make the codeblock vertically scrollable.

TODO

# Table

## Test 1: Overflow

The table should be scrollable within its content width.

.. html:: div
	:style: width: calc(var(--content-width) / 2)

	{% set wide_filler = '<div style="width: calc(var(--content-width) / 3)">' + filler + '</div>' %}

	|Column 1 header|Column 2 header|Column 3 header|
	|-
	|{{ wide_filler }}|{{ wide_filler }}|{{ wide_filler }}|
	|Column 1 content|Column 2 content|Column 3 content|
	|-
	|Column 1 footer|Column 2 footer|Column 3 footer|

# Admonition

Example:

.. admonition:: me/say

	Hello I am an admonition!

	This is an example where I am saying something, to demonstrate you can have paragraphs in it!

## Test 1: Short admonition

TODO acceptance criteria

.. admonition:: me/say

	<div style="width: 4px; height: 4px; background-color: blue"></div>

(content after)

# Paper

## Test 1: Long Paper Element

There should be adequate space between the paper and its surroundings.

**Preceding text.** {{ filler }}

.. html:: div
	:class: paper

	{{ filler }}

**Succeeding text.** {{ filler }}
