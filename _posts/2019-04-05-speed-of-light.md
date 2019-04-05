---
layout: post
title: A simple "derivation" of the speed of light
tags: math
---

By assuming the nature of the propagation of EM waves, we can derive the speed of light from Maxwell's equations in a much simpler way and without advanced vector calculus. However, I'm not sure how valid this is, so if there's any issues, please raise them on [the repo for my blog][repo].

[repo]: https://github.com/ralismark/ralismark.github.io

<!--more-->

I'm currently studying EM waves as part of HSC physics, and I looked at this for interest (though this is definitely beyond the syllabus). I shared this with my friend who might also post this derivation on [his blog][sabicool].

[sabicool]: https://sabicool.github.io/

# Assumptions

We assume that B and E are perpendicular and only exist along one line[^1]. i.e.:

[^1]: If I figure out how to make 3D LaTeX diagrams I'll update this to make it clearer.

$$
\begin{align*}
	\vec{E} &= E(x) \vec{y}
\\	\vec{B} &= B(x) \vec{z}
\end{align*}
$$

$$\vec{x}$$ is the direction of propagation, so $$\vec{y} \times \vec{z} = \vec{x}$$.

# Maxwell's Equations

These are the relevant equations, after some simplification by assuming there are no charges:

$$
\begin{align*}
	\nabla \times \vec{E} &= -\frac{\partial \vec{B}}{\partial t}
\\	\nabla \times \vec{B} &= \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}
\end{align*}
$$

We can apply the formula for curl[^2] to simplify these down to two differential equations.

[^2]: Taken from [Wikipedia][curl].

[curl]: https://en.wikipedia.org/wiki/Curl_(mathematics)

$$
\begin{align*}
	\nabla \times \vec{E} &= 0\vec{x} + 0\vec{y} + \frac{\partial E}{\partial x}\vec{z} = -\frac{\partial B}{\partial t}\vec{z} 
	&\Longrightarrow& - \frac{\partial E}{\partial B} = \frac{\partial x}{\partial t}
\\	\nabla \times \vec{B} &= 0\vec{x} - \frac{\partial B}{\partial x}\vec{y} + 0\vec{z} = \mu_0 \epsilon_0 \frac{\partial E}{\partial t}\vec{y}
	&\Longrightarrow& \left( - \frac{\partial E}{\partial B} \right) \cdot \frac{\partial x}{\partial t} = \frac{1}{\mu_0 \epsilon_0}
\end{align*}
$$

Then, after some rearranging and then equating $$\frac{\partial B}{\partial E}$$, we can get the derivative of position with respect to time i.e. the speed of light.

$$
\frac{\partial x}{\partial t} = \frac{1}{\sqrt{\mu_0 \epsilon_0}} = c
$$
