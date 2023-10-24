---
layout: default-wide
---

{% comment %}
TODO Make all post tiles have the same capitalisation style
{% endcomment %}

<h1
  id="index-banner"
>
  <small>🏵️🌿🌸</small>
  <span>ralismark<span class="paper">.xyz</span></span>
  <small>🌸🌿🏵️</small>
</h1>

<style>
#index-banner {
  font-family: var(--hand-font-family);
  font-size: 300%;

  padding: 4rem 0;
  max-width: 60rem;
  margin: 1rem auto;

  display: flex;
  justify-content: space-around;
  align-items: baseline;

  gap: 2rem 0;
}

@media(max-width: 45rem) {
  #index-banner {
    flex-direction: column;
    align-items: center;
  }
}

#index-banner .paper {
  margin: 0;
  padding: 0;
  background: var(--filled-bg);
  color: var(--filled-fg);

  line-height: 1.2;
}

#index-banner > * {
  flex-grow: 0;
  flex-shrink: 0;
}

#index-banner > small {
  font-size: 80%;
  line-height: 2; /* emoji fonts are tall sometimes */
}
</style>

<main class="content-width" markdown=1>

# Welcome!

<div class="h-card" markdown=1>

I'm **{{ site.me.name }}**{: .p-name } (she/her), but I usually go by **ralismark**{: .p-nickname } on the internet.

This website -- [ralismark.xyz](https://ralismark.xyz){: .u-url.u-uid rel="me" } -- is my canonical corner of the internet, where I [write irregularly]({% link posts.html %}), mostly on technical topics.

I'm [ralismark on GitHub](https://github.com/ralismark), and I toot as [{{ site.me.fedi.str }}]({{ site.me.fedi.url }}).
You can also email me via [tem@ this domain](mailto:{{ site.me.email }}).
<!--cloudflare email obfuscation means I can't u-email that last one-->

</div>

</main>
