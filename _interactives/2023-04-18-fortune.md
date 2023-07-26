---
layout: post
title: Fortune
tags:
excerpt: print a random, hopefully interesting, adage
---

<form onsubmit="return false">
  <label>URL of fortune file: <input id="fortfile" type="url"></label>
  <button type="submit" onclick="fortune()">I'm Feeling Lucky</button>
</form>

{: .my-4 id="output" }
{% include admonition verb="fortune" %}
> *Ask again later...*

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
  document.querySelector("#output p").innerText = text;
}

async function setfortfile(url) {
  document.getElementById("fortfile").value = url;
  await fortune();
  document.getElementById("output").scrollIntoView({
    behavior: "smooth",
    block: "center",
  });
}

fortune();
</script>

<details markdown="1">
<summary>What is this?</summary>

This is an adaptation of [fortune(6)](https://en.wikipedia.org/wiki/Fortune_(Unix)), adapted for a webpage.
To use this, enter the URL of a plaintext fortune file, consisting of individual messages separated by a line consisting of a single `%`.
For example:

```
Nobody will buy or use your compilers.
%
No. What is the point of doing that?
%
Good question!

The answer is no.
```

(Fortune cookie photo licensed under CC0 Public Domain from <https://www.publicdomainpictures.net/en/view-image.php?image=207643>)
</details>

<details markdown="1">
<summary>Public fortune lists</summary>

# fortune-mod

These are fortunes from [`fortune-mod`](https://github.com/shlomif/fortune-mod/tree/master/fortune-mod/datfiles).

Some of these are rather insensitive and offensive.
I have not reviewed them, and I do not endorse their content.

{% capture fortunes %}
art ascii-art computers cookie debian definitions disclaimer drugs education
ethnic food fortunes goedel humorists kids knghtbrd law linux literature love
magic medicine men-women miscellaneous news paradoxum people perl pets
platitudes politics pratchett riddles rules-of-acquisition science shlomif-fav
songs-poems sports startrek tao translate-me wisdom work zippy
{% endcapture %}{% assign fortunes = fortunes | replace: "\n", " " | split: " " %}
{% for fortune in fortunes %}
<button onclick="setfortfile('https://raw.githubusercontent.com/shlomif/fortune-mod/master/fortune-mod/datfiles/{{ fortune }}')">{{ fortune }}</button>
{%- endfor %}

</details>
