---
layout: post
title: Fortune
excerpt: print a random, hopefully interesting, adage
date: 2023-04-18
tags:
---

<form onsubmit="return false">
	<label>URL of fortune file: <input id="fortfile"></label>
	<button type="submit" onclick="fortune()">I'm Feeling Lucky</button>
</form>

<br>

.. admonition::
	:image: {{ recipe.copy("./fortune.png", "/assets/fortune.png") }}
	:alt: fortune cookie

	Ask again later...

<br>

<script>
// load ?fortfile=
(() => {
	const fortfile = (new URLSearchParams(window.location.search)).get("fortfile");
	if (fortfile !== null) {
		document.getElementById("fortfile").value = fortfile;
	}
})();

// TODO error handling if fetching the fortfile fails
const cache = { url: null, forts: null };
function fortfile(url) {
	if (cache.url !== url) {
		cache.url = url;
		cache.forts = new Promise((resolve, reject) => {
			const xhr = new XMLHttpRequest();
			xhr.open("GET", url, true);
			xhr.addEventListener("load", () => {
				if (xhr.status === 200) {
					let items = xhr.responseText.split("\n%\n").filter(x => x.trim() != "");
					if (items.length == 0) items = ["(no fortunes)"];
					resolve(items);
				} else reject(new Error("Request returned status code " + xhr.status));
			});
			xhr.addEventListener("error", e => reject(e));
			xhr.send();
		});
	}
	return cache.forts;
}

async function fortune() {
	const url = document.getElementById("fortfile").value;
	if (url === "") return;

	const newLoc = new URL(window.location.href);
	newLoc.searchParams.set("fortfile", url);
	window.history.replaceState({}, "", newLoc);

	const forts = await fortfile(url);
	const text = forts[Math.floor(Math.random() * forts.length)];
	document.querySelector("[admonition=fortune] p").innerText = text;
}

async function setfortfile(url) {
	document.getElementById("fortfile").value = url;
	await fortune();
	document.querySelector("[admonition=fortune]").scrollIntoView({
		behavior: "smooth",
		block: "center",
	});
}

fortune();
</script>

<hr>

This is an adaptation of [fortune(6)], adapted for a webpage.
To use this, enter the URL of a plaintext fortune file, consisting of individual messages separated by a line consisting of a single `%`.
For example:

[fortune(6)]: https://en.wikipedia.org/wiki/Fortune_(Unix)

```
Nobody will buy or use your compilers.
%
No. What is the point of doing that?
%
Good question!

The answer is no.
```

You can also use some existing public fortune collections:

.. details:: my own ones

	<button onclick="setfortfile('https://raw.githubusercontent.com/ralismark/nixfiles/main/assets/fortunes')">My personal collection</button>
	<button onclick="setfortfile('{{ recipe.copy("./jingling.txt", "/assets/fortune:jingling") }}')">Compilers</button>

.. details:: fortune-mod

	These are fortunes from [`fortune-mod`](https://github.com/shlomif/fortune-mod/tree/master/fortune-mod/datfiles).

	Many of these are offensive.
	I do not endorse their content, and only provide them as a demonstration.

	{% for fortune in [
		"art", "ascii-art", "computers", "cookie", "debian", "definitions",
		"disclaimer", "drugs", "education", "ethnic", "food", "fortunes",
		"goedel", "humorists", "kids", "knghtbrd", "law", "linux", "literature",
		"love", "magic", "medicine", "men-women", "miscellaneous", "news",
		"paradoxum", "people", "perl", "pets", "platitudes", "politics",
		"pratchett", "riddles", "rules-of-acquisition", "science",
		"shlomif-fav", "songs-poems", "sports", "startrek", "tao",
		"translate-me", "wisdom", "work", "zippy",
	] -%}
	<button onclick="setfortfile('https://raw.githubusercontent.com/shlomif/fortune-mod/master/fortune-mod/datfiles/{{ fortune }}')">{{ fortune }}</button>
	{% endfor %}

(Fortune cookie photo licensed under CC0 Public Domain from <https://www.publicdomainpictures.net/en/view-image.php?image=207643>)
