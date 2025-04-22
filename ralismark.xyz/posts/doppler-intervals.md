---
layout: post
title: Estimating speed with musical intervals
excerpt: "At the intersection of physics and music theory"
date: 2025-02-08
tags: math
---

As a vehicle speeds past you, you'll hear a drop in frequency due to the [Doppler effect](https://en.wikipedia.org/wiki/Doppler_effect).
Since the frequency you hear is the original frequency multiplied by some value related to the speed, for the same speed the drop will always be the same _musical interval_.
Which means that, if you're good at identifying musical intervals, you can estimate the speed of the vehicle!

.. admonition:: me/say

	I remember seeing the table for this at some point -- it's the direct inspiration for this post -- but alas I forgot where I found it and I cannot find it again.

|Musical Interval|Speed (km/h)|Speed (mph)|
|-
{% for interval in [
	"Semitone",
	"Tone",
	"Minor Third",
	"Major Third",
	"Perfect Fourth",
	"Tritone",
	"Perfect Fifth",
	"Minor Sixth",
	"Major Sixth",
	"Minor Seventh",
	"Major Seventh",
	"Octave",
] %}
{%- set I = 2 ** (loop.index / 12) -%}
{%- set v = (I - 1) / (I + 1) -%}
|{{ interval }} | {{ "{:.0f}".format(v * 1225.044) }} | {{ "{:.0f}".format(v * 761.207) }}|
{% endfor %}

I'm using 12-tone equal temperament for this.
I'm also assuming the source of the sound is heading directly towards then directly away from you, which is only true if the vehicle hits you.
So in reality, the vehicle's speed will be a little bit higher, since the speed relative to you is a bit less than its actual speed.

# The Math

Assuming you're stationary, the resulting frequency from the Doppler effect is
$$
f = \left( \frac{c}{c - v} \right) f_0
$$
where $c$ is the speed of sound and $v$ is the speed of the source of the sound relative to you (i.e. negative as the vehicle approaches, then positive as it goes away).

So, the ratio between frequency of sound as the vehicle approaches and the frequency as it leaves is
$$
\frac{\frac{c}{c - v}f}{\frac{c}{c + v}f} = \frac{c + v}{c - v} = I.
$$
Rearranging for $v$,
$$
\begin{aligned}
c + v &= Ic - Iv \\
(I + 1)v &= (I - 1)c \\
v &= \frac{I - 1}{I + 1}c
\end{aligned}
$$
which we can use to generate the table above!
