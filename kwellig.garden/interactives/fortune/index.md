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

.. admonition:: fortune
	:image: {{ recipe.copy("/assets/fortune.png", "./fortune.png") }}
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
	document.querySelector("blockquote[admonition=fortune] p").innerText = text;
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

	<button onclick="setfortfile('https://gist.githubusercontent.com/ralismark/3f3733e661358a2dc45e3ca10588b9d5/raw/fortune')">My personal collection</button>
	<button onclick="setfortfile('{{ recipe.copy("/assets/fortune:jingling", "./jingling.txt") }}')">Compilers</button>

.. details:: fortune

	These are fortunes available in [`fortune-kind`](https://github.com/cafkafk/fortune-kind)[^not-shlomif].

	[^not-shlomif]: I've intentionally not referenced the most popular [`fortune-mod`](https://github.com/shlomif/fortune-mod/tree/master/fortune-mod/datfiles).
		The maintainer has been generally against moderating the existing fortune collection to remove bigoted and vile quotes.

	{% for fortune in [
		"ascii-art",
		"computers",
		"debian",
		"disclaimer",
		"fedi",
		"food",
		"fortunes",
		"goedel",
		"humorists",
		"kids",
		"linux",
		"magic",
		"medicine",
		"miscellaneous",
		"nethack",
		"news",
		"nixos-offtopic",
		"paradoxum",
		"people",
		"pets",
		"pratchett",
		"riddles",
		"tao",
		"testtunes",
		"translate-me",
	] -%}
	<button onclick="setfortfile('https://raw.githubusercontent.com/cafkafk/fortune-kind/refs/heads/main/fortunes/{{ fortune }}')">{{ fortune }}</button>
	{% endfor %}

(Fortune cookie photo licensed under CC0 Public Domain from <https://www.publicdomainpictures.net/en/view-image.php?image=207643>)
