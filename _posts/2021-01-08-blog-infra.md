---
layout: post
title: Site Infrastructure
tags:
excerpt: The tech stack of this site
---

I've gotten a decent number of questions asking about how my blog is set up. Last year, I wrote [Blog CI], which covered the continuous deployment that I recently introduced. This post will be an extension of that, detailing everything else about how this site works.

[Blog CI]: {% link _posts/2020-10-28-blog-ci.md %}

<!--more-->

# Hosting

This site is entirely hosted for free on [Github Pages]. Repos named *username*.github.io, like [the one for this site][repo], are automatically hosted at *username*.github.io.

[Github Pages]: https://pages.github.com/
[repo]: https://github.com/ralismark/ralismark.github.io/

> _**A note to those starting**_
> 
> My github pages setup is quite a bit more complex than what's needed for a beginner. Any markdown files you put under your *username*.github.io repo will get rendered to github pages without further configuration -- that's the bare minimum to get started. Afterwards, you can customise the theme under the repo settings.

# Site Generation

Github Pages can only serve static sites -- ones that don't require any moving parts serverside besides simply serving files. While you can directly write and serve raw HTML, as some people do, using a static site generator is much more convenient.

I use [Jekyll] for this. [Github Pages has built-in support for Jekyll][github-pages-jekyll], but this is somewhat limited. Some features are disabled, and you're restricted to a small set of plugins. I've gotten around this by using [Github Actions & Docker][Blog CI].

[Jekyll]: https://jekyllrb.com/
[github-pages-jekyll]: https://docs.github.com/en/free-pro-team@latest/github/working-with-github-pages/about-github-pages-and-jekyll

While not essential, it provides many features, such as includes and Liquid templating, that make working on the site much nicer. However, the biggest benefit is that it allows you to write posts in markdown.

Without Github Pages's restrictions on Jekyll, I have plugins to

- [Render graphviz], such as on my [Kruskal Tree post]
- [Turn headings into links]
- [Create redirects] after I changed the URL scheme

[Render graphviz]: https://github.com/ralismark/ralismark.github.io/blob/d0a7ce4823f2f5a88295c031f470d102eaa8f792/_plugins/graphviz.rb
[Kruskal Tree post]: {% link _posts/2019-05-28-edge-trees.md %}
[Turn headings into links]: https://github.com/ralismark/ralismark.github.io/blob/d0a7ce4823f2f5a88295c031f470d102eaa8f792/_plugins/markdown-header.rb
[Create redirects]: https://github.com/ralismark/ralismark.github.io/blob/d0a7ce4823f2f5a88295c031f470d102eaa8f792/_plugins/redirect.rb

# Local Testing

I generate my website using a Docker container, both for local testing and when deploying. A lot of guides suggest having a local ruby install, but I find using Docker much nicer. This is something I would suggest to everyone.

Here's a `Dockerfile` for it:

```docker
FROM jekyll/builder:latest
EXPOSE "4000"
CMD jekyll serve -d /tmp/_site \
	--host 0.0.0.0 --port 4000 \
	--config _config.yml \
	--watch --force_polling
```

and a script for running it:

```sh
#!/bin/sh
IMAGE_NAME=site
docker build -t "$IMAGE_NAME" . &&
docker run --rm -it -p 4000:4000 \
	-v "$PWD:/srv/jekyll:ro" \
	--name "$IMAGE_NAME" "$IMAGE_NAME" "$@"
```

You'll be able to see the site at `localhost:4000`.

# Deployment

I've gone through my deployment setup before in [Blog CI]. The gist of it is that I have Github Actions spin up a docker container to render the site and push it to the `gh-pages` branch whenever I commit.

# Custom Domain

I've also set this up site to be reachable from a custom domain -- [here are the instructions for that][custom-domain].

[custom-domain]: https://docs.github.com/en/free-pro-team@latest/github/working-with-github-pages/managing-a-custom-domain-for-your-github-pages-site

I originally bought the `ralismark.xyz` domain from Namecheap, but I've since switched to [Cloudflare Registrar]. Namecheap significantly discounts the first year of registration, but Cloudflare seems cheaper in the long term. I also use Cloudflare's other (free) features, so switching meant one less service I had to manage.

[Cloudflare Registrar]: https://www.cloudflare.com/en/products/registrar/

# Summary

I think I've covered everything about my setup. It's interesting to note that only thing here costing money was the domain name. If you have any further questions, feel free to ask!
