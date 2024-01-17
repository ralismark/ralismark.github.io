---
layout: post
title: A Simple "Derivation" Of The Speed Of Light
excerpt: Deriving an expression for c without advanced vector calculus
date: 2019-04-05
tags: math
---

By assuming the nature of the propagation of EM waves, we can derive the speed of light from Maxwell's equations in a much simpler way and without advanced vector calculus.
However, I'm not sure how valid this is, so if there's any issues, please let me know!

<!--more-->

I'm currently studying EM waves as part of HSC physics, and I looked at this for interest (though this is definitely beyond the syllabus).
I shared this with my friend who might also post this derivation on [his blog][sabicool].
The reason I use quotes around "derivation" is that this seems too simple to be true - it doesn't really require anything beyond the curl equation (and no need for a conceptual understanding either) and simple calculus.

[sabicool]: https://sabicool.github.io/

# Assumptions

We assume that B and E are perpendicular and only exist along one line, the $\vec{x}$ axis.
This axis is also the direction of propagation, so $\vec{E} \times \vec{B} \parallel \vec{x}$, i.e.:

$$
\begin{aligned}
	\vec{E} &= E(x) \vec{y}
	\\
	\vec{B} &= B(x) \vec{z}
\end{aligned}
$$

{#
To build the below diagram, run

$ pdflatex -output-format=dvi -interaction=batchmode em-wave.tex
$ dvisvgm em-wave.dvi -p1 -n -o em-wave.svg

--- em-wave.tex ---

\documentclass{standalone}

\usepackage{tikz}
\usepackage{tikz-3dplot}

\newcommand{\wave}[1] { cos(deg(pi*#1-1)) }

\begin{document}

\begin{tikzpicture}[x={(-10:1cm)}, y={(90:1cm)},z={(210:1cm)}]

	% Axes
	\draw[-latex] (-.5, 0, 0) node[above] {$x$} -- (5, 0, 0);
	\draw[-latex] (0, -.2, 0) -- (0, 2, 0) node[above] {$y$};
	\draw[-latex] (0, 0, -.2) -- (0, 0, 2) node[left] {$z$};

	% Waves
	\draw[latex-latex,thick,red]  plot[domain=-.15:4.6, samples=20 0] (\x, {\wave\x}, 0);
	\draw[latex-latex,thick,blue] plot[domain=-.15:4.6, samples=20 0] (\x, 0, {\wave\x});

	% Arrows
	\foreach \x in {0.1,0.3,...,4.3} {
		\draw[-latex',help lines,red]  (\x, 0, 0) -- (\x, {\wave\x}, 0);
		\draw[-latex',help lines,blue] (\x, 0, 0) -- (\x, 0, {\wave\x});
	}

	\node[above right,red] at (0,1,0) {$\vec{E}$};
	\node[below right,blue] at (0,0,1) {$\vec{B}$};

\end{tikzpicture}

\end{document}

#}

.. figure:: {{ recipe.copy("./em-wave.svg", "/assets/speed-of-light:em-wave.svg") }}
	:alt: A diagram of EM wave, with a red sine wave, labelled E, along the X-Y plane and a blue sine wave, labelled B, along the X-Z plane

	Electromagnetic wave.
	Credits to [sabicool].

# Maxwell's Equations

These are the relevant equations, after some simplification by assuming there are no charges:

$$
\begin{aligned}
	\nabla \times \vec{E} &= -\frac{\partial \vec{B}}{\partial t}
	\\
	\nabla \times \vec{B} &= \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}
\end{aligned}
$$

We can apply the formula for curl[^2] to simplify these down to two differential equations.

[^2]: Taken from [Wikipedia](https://en.wikipedia.org/wiki/Curl_(mathematics\)).

$$
\begin{aligned}
	\nabla \times \vec{E} &= 0\vec{x} + 0\vec{y} + \frac{\partial E}{\partial x}\vec{z} = -\frac{\partial B}{\partial t}\vec{z}
	&&\Longrightarrow&& - \frac{\partial E}{\partial B} = \frac{\partial x}{\partial t}
	\\
	\nabla \times \vec{B} &= 0\vec{x} - \frac{\partial B}{\partial x}\vec{y} + 0\vec{z} = \mu_0 \epsilon_0 \frac{\partial E}{\partial t}\vec{y}
	&&\Longrightarrow&& \left( - \frac{\partial E}{\partial B} \right) \cdot \frac{\partial x}{\partial t} = \frac{1}{\mu_0 \epsilon_0}
\end{aligned}
$$

Then, after some rearranging and then equating $\frac{\partial B}{\partial E}$, we can get the partial derivative of position with respect to time.
This represents the effective propagation of the wave as you 'follow' its movement[^3], so the velocity is essentially the speed of light.

[^3]: In reality, the fields themselves aren't moving. It's like a wave in water - the particles are moving up and down, creating motion, but they aren't actually moving longitudinally.

$$
\frac{\partial x}{\partial t} = \frac{1}{\sqrt{\mu_0 \epsilon_0}} = c = 299792458\ \mathrm{m \, s^{-1}}
$$
