---
layout: plain-wide
title: Test Post Please Ignore 2
tags:
excerpt: CSS Integration Tests
---

# Test Post 2: Electric Boogaloo

- [Test Post Please Ignore 1]({% link _garden/test-1.md %})
- [Test Post Please Ignore 2]({% link _garden/test-2.md %})

# long lines in code blocks

No line numbers

{::options syntax_highlighter_opts="{ line_numbers: false \}" /}

```
suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.

suppose you want to determine whether a star is a giant.
a giant star has a large extended photosphere.
because it is so large,
its atoms are spread over a greater volume.

suppose you want to determine whether a star is a giant. a giant star has a large extended photosphere. because it is so large, its atoms are spread over a greater volume.
```

# packed tables

{% capture content %}
{: .mx-0 .card }
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
