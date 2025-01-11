---
layout: post
title: Gravity Testing
excerpt: A little n-body gravity simulator from 2015
date: 2024-12-06
tags:
series: webgames
---

I'm not that sure where this fits into my "learning to program" timeline but it's also a really early one.

Unlike the others, this uses one external library -- jQuery :)

---

- Clicking moves the spaceship (the red rectangle) while preserving velocity
- Space prompts for new position/velocity values
- 1 stops the simulation
- Z starts simulation, and increases speed for each subsequent press
- C clears the trail
- X does something related to the trail, but I can't tell what
- W/A/S/D boosts in those directions

<p style="text-align: center; font-size: 120%">
	<a href="{{ page.url }}/main.html" role="button">
	Open in new tab
	</a>
</p>

{% for path in recipe.readdir(".") %}
	{% if path.suffix != ".md" %}
		{% do recipe.copy(path, page.url + "/" + path.name) %}
	{% endif %}
{% endfor %}
