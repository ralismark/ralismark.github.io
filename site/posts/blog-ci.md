---
layout: post
title: Blog CI
excerpt: Using github CI to deploy to github pages
date: 2020-10-28
tags: static-site-gen meta
---

{# TODO admonition #}
> This setup was accurate at the time of writing, but may not reflect the infrastructure I am using today.
> You can see the latest setup from [the source code](https://github.com/ralismark/ralismark.github.io) or by asking me!

While I've tried to keep this blog as static as possible, I've struggled with the limitations of github-pages for many features that I wanted to use.

<!--more-->

- Biggest of all, you can't render $\LaTeX$ in jekyll and must include KaTeX or MathJax to render it client-side.
- Turning sections headings into links requires either doing it client-side or [parsing html with the Liquid templating system][jekyll-anchor-headings].
- Including GraphViz graphs (or other rendered diagrams) requires either generating them by hand, or automating it using a Makefile.
	Either way, you need to re-render the graphics by hand when you make changes.

[jekyll-anchor-headings]: https://github.com/allejo/jekyll-anchor-headings

Switching to github actions to build significantly relaxes these constraints.
My current setup (shown below) involves spinning up a docker container and building the site there -- so I can test locally -- then automatically pushing to the `gh-pages` branch.
It still uses Jekyll as the static site generator, so migration was quite painless.

.. details:: deploy.yml

	```yaml {% raw %}
	name: Deploy to Github Pages
	
	on:
	  workflow_dispatch:
	  push:
	    branches:
	      - master
	
	jobs:
	  build:
	
	    runs-on: ubuntu-latest
	
	    steps:
	    - name: Checkout
	      uses: actions/checkout@v2
	
	    - name: Jekyll build
	      run: |
	        docker build . --tag=image
	        docker run \
	          -v ${{ github.workspace }}:/srv/jekyll -v ${{ github.workspace }}/_site:/srv/jekyll/_site \
	          image jekyll build
	    - name: Push to gh-pages
	      uses: JamesIves/github-pages-deploy-action@3.6.2
	      with:
	        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
	        # This is the branch you wish to deploy to, for example gh-pages or
	        # docs.
	        BRANCH: gh-pages
	        # The folder in your repository that you want to deploy. If your build
	        # script compiles into a directory named build you would put it here.
	        # Folder paths cannot have a leading / or ./. If you wish to deploy the
	        # root directory you can place a . here.
	        FOLDER: _site
	        # This option can be used if you'd prefer to have a single commit on
	        # the deployment branch instead of maintaining the full history.
	        SINGLE_COMMIT: true
	``` {% endraw %}

With the full power of Jekyll, you can render $\LaTeX$ server-side by switching kramdown's math engine to [sskatex](https://github.com/kramdown/math-sskatex).
You can also write plugins in the `_plugins` folder e.g.
to run graphviz or add anchor tags to headers -- I've included both of these plugins below; check out Jekyll's docs for more info.

.. details:: graphviz.rb

	```ruby
	module Jekyll
	  class GraphBlock < Liquid::Block
	
	    def render(context)
	      text = super
	      io = IO.popen("dot -Gbgcolor=transparent -Tsvg", "r+")
	      io.puts(text)
	      io.close_write()
	      io.gets() # skip <?xml>
	      io.gets() # skip <!doctype>
	      io.gets() # skip end of doctype
	      io.gets() # skip comment
	      io.gets() # skip comment
	      io.read()
	    end
	
	  end
	end
	
	Liquid::Template.register_tag("graph", Jekyll::GraphBlock)
	```

.. details:: markdown-header.rb

	```ruby
	module Jekyll
	  class MarkdownHeader < Converters::Markdown
	    def convert(content)
	      super.gsub(/<h(\d) id="(.*?)">(.*)<\/h(\d)>/, '<h\1 id="\2"><a href="#\2">\3</a></h\1>')
	    end
	  end
	end
	```
