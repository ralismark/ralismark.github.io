---
layout: post
title: Inline sidenotes
tags:
excerpt: A neat css-only inline note
---

I found a nice way to make inline sidenotes from [Sidenotes in Web Design (Gwern)](https://www.gwern.net/Sidenotes). And sorry to RSS feed users who have little to no idea what's going on.

<!--more-->

Here is a demonstration of these: <sup class="note"><span>Hello from note!</span></sup>. As you can see, they don't break the paragraph *at* the note position, but allow text to continue until the end of the line<sup class="note"><span>As you can see, these <em>just work</em></span></sup><sup class="note"><span>And they number themselves automatically!</span></sup>. This required no Javascript -- only CSS! The HTML code for a single note is

```html
<sup class="note">
  <span>And they number themselves automatically!</span>
</sup>
```

and the CSS is just this:

{% capture css %}
article {
	counter-reset: note_nr;
}
sup.note::before {
	counter-increment: note_nr;
	content: counter(note_nr);
}
sup.note > span {
	display: block;
	float: left;
	clear: both;
	width: 100%;
	padding: 0 2rem;
}
sup.note > span::before {
	content: counter(note_nr) " ";
	vertical-align: super;
}
{% endcapture %}

```css {{ css }} ```

Unfortunately, I haven't figured out how to make Jekyll & Kramdown generate footnotes in this style<sup class="note"><span>You could do it with custom Liquid tags/filters, but those aren't as nice as kramdown's footnote syntax</span></sup>, so bottom-of-page footnotes will be staying until I do.

<style>{{ css }}</style>
