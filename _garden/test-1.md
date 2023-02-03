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

&lt;kbd&gt;: <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>Delete</kbd>

<details markdown="1">
<summary>This is collapsed</summary>

```cpp
#include <bits/stdc++.h>

signed main() {
  const char* a = "suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.";
}
```

<details><summary>Open me!</summary>
<details><summary>Open me!</summary>
<details><summary>Open me!</summary>
<details><summary>Open me!</summary>
<details><summary>Open me!</summary>
<details><summary>Open me!</summary>
<p>hello there</p>
</details>
</details>
</details>
</details>
</details>
</details>
</details>


# code escape

using &lt;! and !&gt; with language `escape?lang=cpp`:

```escape?lang=cpp
"hello" <!<a href="/">there</a>!>
```

# long lines in code blocks

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

`raw`:

```raw
this is raw

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

{% include admonition %}
> hello there

This is a long admonition.
I'm having a bunch of text here so I can test the right margins.

{% include admonition %}
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

{% include admonition %}
> short

{% include admonition %}
> Suppose you want to determine whether a star is a giant.
> A giant star has a large extended photosphere.
> Because it is so large, its atoms are spread over a larger volume.

{% include admonition %}
> short

{% include admonition %}
> short
>
> two
