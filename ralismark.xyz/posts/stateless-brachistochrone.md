---
layout: post
title: Stateless Brachistochrone Trajectories
excerpt: Determining if you need to decelerate without remembering where you started
date: 2017-08-24
tags: math
---

Brachistochrone trajectories are the fastest path an object in space can take from one point to another.
In terms of movement, this involves continuously accelerating until the halfway point, and slowing down for the rest of the journey.
It's trivial to calculate if you need to slow down if you have the starting position; not so much if you don't.

<!--more-->

The basics of how the brachistochrone trajectory works is that you only start slowing down at the latest possible moment.
The time at which you switch turns out to be exactly halfway, since the velocity gained speeding up must equal the velocity lost slowing down.
However, without the initial position, we can still figure this out using the current velocity and position, as well as some algebra.

Let $x$ be our position, $v$ be our velocity (both relative to the target), $t$ be the time until the switchover, and $A$ be our maximum acceleration.

To figure out $t$, we can be a bit sneaky.
We find the point where the velocity is the same on the other side of the switchover ($p$ here), and finding the midpoint of the distance between them.
The section is effectively a mini-brachistochrone trajectory, but with everything moving at speed $v$.

$$
\begin{aligned}
	t_\textrm{stop} &= \frac{v}{A}
	\\
	p &= \frac{1}{2} A t_\textrm{stop}^2 = \frac{v^2}{2A}
	\\
	x_\textrm{switch} &= \frac{x + p}{2} = \frac{x}{2} + \frac{v^2}{4A}
\end{aligned}
$$

You can just use the sign of $x_\textrm{switch}$ to determine if you need to boost forward of backwards[^1].
For most cases, this is sufficient.
As extra, we can solve for $t$ to determine how long until the switchover.

[^1]: The comparison simplifies to $2Ax + v^2 > 0$, which is true if the switchover has not been reached.

$$
\begin{aligned}
	x_\textrm{switch} &= x - vt - \frac{1}{2} At^2
	\\
	0 &= t^2 \left(\frac{A}{2}\right) + t(v) + (x_\textrm{switch} - x)
	\\
	t &= \frac{-v \pm \sqrt{v^2 - 2A(x_\textrm{switch} - x)}}{A}
	\\
	t &= \frac{-v \pm \sqrt{\frac{v^2}{2} + Ax}}{A}
\end{aligned}
$$

Even though there are 2 solutions (either plus or minus), we'll only want one of those.
As both $v$ and $A$ are positive, there'll only be 2 possibilities for the signs of these solutions:

1. One is positive, one is negative.
	This means that you haven't yet reached the switchover point.
	Take the positive one (the negative one is what we get if we reverse time).

2. Both are negative.
	This means that you started slowing down too late.
	Still, for the time you missed the switch, take the higher one.

In both cases, we take the higher solution, leaving us with:

$$
t
= \frac{-v + \sqrt{\frac{v^2}{2} + Ax}}{A}
= t_\textrm{stop} + \sqrt{\frac{1}{2}t_\textrm{stop}^2 + \frac{x}{A}}
$$
