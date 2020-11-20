---
layout: post
title: Which blockquote looks better
tags: blog
excerpt: A sample of a few possible blockquote styles
---

Somewhat recently, I changed the style of blockquotes here from just "text with grey bar" to "boxed text with grey bar". Still, I've seen various style floating around, so here's a comparison of them.

<!--more-->

{% assign lipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.<br>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat." %}

# Current style

Preceeding text about some things

> {{lipsum}}

And this is the text that follows

# Grey bar

Preceeding text about some things

<p style="margin-left: 1rem; margin-right: 2rem; border-left: 0.4rem solid lightgrey; padding: 0.6rem 0 0.6rem 0.6rem">{{ lipsum }}</p>

And this is the text that follows

# Blue bar

Preceeding text about some things

<p style="margin-left: 1rem; margin-right: 2rem; border-left: 0.4rem solid rgba(20,150,200,0.1); padding: 0.6rem 0 0.6rem 0.6rem">{{ lipsum }}</p>

And this is the text that follows

# Background

Preceeding text about some things

<p style="box-sizing: content-box; margin-left: -2rem; margin-right: -2rem; padding: 1rem 2rem; background: rgba(127, 127, 127, 0.1)">{{ lipsum }}</p>

And this is the text that follows

# Blue Background

Preceeding text about some things

<p style="box-sizing: content-box; margin-left: -2rem; margin-right: -2rem; padding: 1rem 2rem; background: rgba(20, 150, 200, 0.1)">{{ lipsum }}</p>

And this is the text that follows

# Fullwidth background

Preceeding text about some things (don't mind the scroll)

<p style="box-sizing: content-box; margin-left: -50vw; margin-right: -50vw; padding: 1rem 50vw; background: rgba(127, 127, 127, 0.1)">{{ lipsum }}</p>

And this is the text that follows

# Fullwidth blue background

Preceeding text about some things (don't mind the scroll)

<p style="box-sizing: content-box; margin-left: -50vw; margin-right: -50vw; padding: 1rem 50vw; background: rgba(20, 150, 200, 0.1)">{{ lipsum }}</p>

And this is the text that follows

# Plain Card

Preceeding text about some things

<p class="card" style="padding: 0.5rem 1rem">{{ lipsum }}</p>

And this is the text that follows
