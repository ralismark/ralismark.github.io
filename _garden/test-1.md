---
layout: post
title: Test Post Please Ignore 1
tags:
excerpt: CSS Integration Tests
---

- [Test Post Please Ignore 1]({% link _garden/test-1.md %})
- [Test Post Please Ignore 2]({% link _garden/test-2.md %})

{:toc}
1. toc

# misc

&lt;kbd&gt;: <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd style="font-size: 2em">Delete</kbd>

{: .li-flat }
- foo
- bar
- baz
- suppose you want
- to determine whether
- a star is
- a giant. a
- giant star has
- a large extended

<ul class="li-flat"><li>no space</li><li>before this</li> <li>but there is before this</li></ul>

<details markdown="1">
<summary>This is collapsed</summary>

```cpp
#include <bits/stdc++.h>

signed main() {
  const char* a = "suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.";
}
```

<details markdown="1"><summary>Open me!</summary>
<details markdown="1"><summary>Open me!</summary>
<details markdown="1"><summary>Open me!</summary>
<details markdown="1"><summary>Open me!</summary>
<details markdown="1"><summary>Open me!</summary>
<details markdown="1"><summary>Open me!</summary>

hello there!

|One|Two|Three|Four|Five|Six|Seven|Eight|One|Two|Three|Four|Five|Six|Seven|Eight|
|-
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|

</details>
</details>
</details>
</details>
</details>
</details>
</details>

# overflowing things

```
12345678901234567890123456789012345678901234567890123456789012345678901234567890
         |         |         |         |         |         |         |         |
        10        20        30        40        50        60        70        80
```

```
suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.
```

$$
suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.
$$

```
definition safety :: "'s property ⇒ bool"
  where "safety P ≡ ∀σ. ¬(σ ⊨ P) ⟶
    (∃i. ∀β. ¬(i_take i σ ⌢ β ⊨ P))"
```

# code escape

using &lt;! and !&gt; with language `escape?lang=cpp`:

```escape?lang=cpp
"hello" <!<a href="/">there</a>!>
```

# long lines in code blocks

```raw
foofdjskal
```

```
suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.

suppose you want to determine whether a star is a giant.
a giant star has a large extended photosphere.
because it is so large,
its atoms are spread over a greater volume.

suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.
```

# other syntaxes

```text
here is text filetype

there is another. there are two of them
```

```
this is no format

suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.
```

`plain`:

```plain
this is plain filetype

there is another. there are two of them

suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.
```

`terminal`:

```terminal
$ echo $MSG # do thing
This is a terminal!
$ echo "See $URL for more!"
See https://github.com/rouge-ruby/rouge/blob/358d7a73a3310f5d589bd8693f3329ff3b3f8e9e/lib/rouge/lexers/console.rb for more!
$ sudo true
[sudo] password for user:
user is not in the sudoers file.  This incident will be reported.
```

`terminal?lang=python&prompt=:`:

```terminal?lang=python&prompt=:
In [1]: 1+1 # this lang is terminal?lang=python&prompt=:
Out[1]: 2

In [2]: 3+4
Out[2]: 7

In [3]: print("hello")
hello
```

# tables

narrow table:

|One|Two|Three|
|-|-|-|
|Four|Five|Six|

wide table:

|One|Two|Three|Four|Five|Six|Seven|Eight|One|Two|Three|Four|Five|Six|Seven|Eight|
|-
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|

wide and narrow cells:

|One|Two|Three|
|-
|Four|Five|Six|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|

table without thead:

|-
|Four|Five|Six|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|

multiple tbody:

|-
|Four|Five|Six|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|
|-
|Four|Five|Six|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|
|-
|Four|Five|Six|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|

packed tables:

{% capture content %}
|One|Two|Three|Four|Five|Six|Seven|Eight|One|Two|Three|Four|Five|Six|Seven|Eight|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|
{% endcapture content %}
{% assign content = content | markdownify %}

<div class="flex-centre">
{{ content }}
{{ content }}
{{ content }}
</div>

# input elements

Here's <button>actual button</button>
and <a href="" role="button">anchor with button role</a>
and <a href="" class="btn">anchor with btn class</a>
and <input type="submit" value="submit input" />.

<textarea>
Here's a textarea
</textarea>

<label>URL Textbox: <input placeholder="http://example.com" type="url"></label>

<form>
<label>Checkbox 1 suppose you want to determine whether a start is a giant a giant star has a large extended photosphere because it is so large its atoms are spread over a greater volume <input type="checkbox"></label>
<label>Checkbox 2 <input type="checkbox"></label>
<label>Textbox <input type="text"></label>
</form>

# bleed

regular table

|One|Two|Three|Four|Five|Six|Seven|Eight|One|Two|Three|Four|Five|Six|Seven|Eight|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|

bleed table

{: .bleed }
|One|Two|Three|Four|Five|Six|Seven|Eight|One|Two|Three|Four|Five|Six|Seven|Eight|
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|Suppose you want to determine whether a star is a giant.|A giant star has a large extended photosphere.|Because it is so large,|Its atoms are spread over a greater volume.|

regular blockquote

> Suppose you want to determine whether a star is a giant. A giant star has a large extended photosphere. Because it is so large, its atoms are spread over a larger volume.

bleed blockquote

{: .bleed }
> Suppose you want to determine whether a star is a giant. A giant star has a large extended photosphere. Because it is so large, its atoms are spread over a larger volume.

image

![Photo of my split keyboard]({% link assets/keyboard:own.png %})

bleed image

{: .bleed }
![Photo of my split keyboard]({% link assets/keyboard:own.png %})

captioned image

![Photo of my split keyboard]({% link assets/keyboard:own.png %})
"hello there"

bleed captioned image

{: .bleed }
![Photo of my split keyboard]({% link assets/keyboard:own.png %})
"hello there"

code

```cpp
"Suppose you want to determine whether a star is a giant. A giant star has a large extended photosphere. Because it is so large, its atoms are spread over a larger volume."
```

bleed code

{: .bleed }
```cpp
"Suppose you want to determine whether a star is a giant. A giant star has a large extended photosphere. Because it is so large, its atoms are spread over a larger volume."
```


# admonition

This is a short admonition.

{% include admonition verb="aside" %}
> hello there

This is a long admonition.
I'm having a bunch of text here so I can test the right margins.

{% include admonition verb="aside" %}
> Suppose you want to determine whether a star is a giant.
> A giant star has a large extended photosphere.
> Because it is so large, its atoms are spread over a larger volume.

And this is text afterwards

> and this is a regular blockquote

Here's an big tip

> ![]({% link assets/spiral.svg %}){: width="64" height="64" }
> cool tem's hot tip
>
> I guess you can copy Amos now?

Here's a sequence of messages

{% include admonition verb="say" %}
> short

{% include admonition verb="say" %}
> Suppose you want to determine whether a star is a giant.
> A giant star has a large extended photosphere.
> Because it is so large, its atoms are spread over a larger volume.

{% include admonition verb="say" %}
> short

{% include admonition verb="say" %}
> short
>
> two

Here's a toot I guess

{: admonition="tweet" }
> ![@ralismark@cathode.church](https://deflector.cathode.church/accounts/avatars/110/099/219/993/802/408/original/50065f9fa9cc2e4f.png "@ralismark@cathode.church")
>
> -funsafe-math, for when you want your math to be both fun and safe!
>
> --- temmie ([@ralismark@cathode.church](https://cathode.church/@ralismark))
> [Oct 9, 2023](https://cathode.church/@ralismark/111201602363815163)

# math

This is inline math: $$1+1 \textrm{ is equal to } 2$$, and 1+1 = 2

$$
\textrm{This is block: }
\int_{-\infty}^\infty e^{-x^2}\;dx = \sqrt{\pi}
$$

# foundation styles

<p style="background: var(--box-tint)">box-tint</p>
<p style="background: var(--button-tint)">button-tint</p>
<p style="color: var(--filled-fg); background: var(--filled-bg)">filled</p>

<p style="color: var(--primary)">primary</p>
<p style="color: var(--secondary)">secondary</p>
<p style="color: var(--tertiary)">tertiary</p>
<p style="color: var(--linking)">linking</p>
