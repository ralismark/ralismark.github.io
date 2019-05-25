---
layout: post
title: Fenwick Trees
tags: informatics interactive
---

Fenwick trees are a lesser-known data structure capable of O(log n) update and prefix query. However, they are often forgotten in favour of the more useful segment tree. Still, they're much easier to implement and make a cool structure when drawn.

<!--more-->

If you draw out a Fenwick tree to sufficient depth, you'll see that they're fractal in nature - a tree of depth N is defined as 2 trees of depth N-1, with root of the second tree as a child of the root of the first. This definition makes it really easy to render.

<center>
	<div style="display: inline-block">
		<label for="maxdepth">Depth</label>
		<div>
			<input id="maxdepth" type="number" min="0" value="7" oninput="update()">
		</div>
	</div>
	<div style="display: inline-block">
		<label for="step">Step size</label>
		<div>
			<input id="step" type="range" min="10" max="200" value="70" step="10" oninput="update()">
		</div>
	</div>
	<div style="display: inline-block">
		<label for="scale">Step decay</label>
		<div>
			<input id="scale" type="range" min="0.5" max="1.2" value="0.9" step="0.01" oninput="update()">
		</div>
	</div>

	<hr>

	<canvas id="canvas" width="800" height="600" style="max-width: 80%; max-height: 600px"></canvas>
</center>

<script>

let canvas = document.querySelector("canvas");
let ctx = canvas.getContext("2d");

let maxdepth, step, scale;

function fenwick(x, y, width, depth) {
	if(depth >= maxdepth) return;
	fenwick(x, y, width/2, depth + 1);
	fenwick(x + width/2, y + step * scale ** depth, width/2, depth + 1);
	ctx.beginPath();
	ctx.moveTo(x, y);
	ctx.lineTo(x + width/2, y + step * scale ** depth);
	ctx.stroke();
}

function update() {
	function load(sel) {
		return parseFloat(document.querySelector('input#' + sel).value);
	}
	maxdepth = load('maxdepth')|0;
	step = load('step');
	scale = load('scale');

	if(scale == 1) {
		canvas.height = step * maxdepth;
	} else {
		canvas.height = step * (scale ** maxdepth - 1) / (scale - 1);
	}

	ctx.clearRect(0, 0, canvas.width, canvas.height);
	fenwick(0, 0, canvas.width, 0);
}

update();
</script>
