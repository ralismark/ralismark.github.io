---
layout: article
title: Behind The Scenes
---

{% capture content %}
- "_plugins/graphviz.rb"
- "_plugins/kramdown.rb"
- "_plugins/redirect.rb"
- "_plugins/webp.rb"
- "_plugins/yaml.rb"
- "_config.yml"
- "Dockerfile"
- "serve.sh"
- ".github/workflows/deploy.yml"
{% endcapture %}{% assign exposed = content | yaml_parse %}

Site built at `{{ site.time }}` and deployed to `{{ site.url }}`. Here are **{{ exposed | size }}** exposed files:

{% for file in exposed %}
<details markdown="1"><summary>{{ file }}</summary>
```{{ file | split: "." | last }}
{% include_relative {{ file }} %}```
</details>
{% endfor %}
