---
---

The compass can lead you to:

{% for place in site.somewhere -%}
{% assign name = place.url | split: "/" | last -%}
- [{{ name }}](#{{ name }})
{% endfor %}
