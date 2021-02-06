---
layout: post
title: Extending Kramdown
tags: blog
excerpt: Changing Kramdown at the ruby level
---

Back in my [Inline Sidenotes]({% link _posts/2020-11-20-inline-notes.md %}) post I discovered an interesting alternative to footnotes, but unfortunately couldn't make Kramdown emit them instead of the regular footnotes. Recently, I stumbled across [Making Markdown more HTML5 with Kramdown](https://kalifi.org/2015/04/html5-markdown-kramdown.html), which listed out the steps for changing how markdown gets rendered. However, it lacked some detail and was a bit outdated, and this process is pretty obscure, so here's another explanation.

<!--more-->

> All of this assumes that you have a Jekyll setup that allows custom plugins and code execution. Github Pages' Jekyll support does not! If you're using github pages, see my [Site Infrastructure] post for *one* way of getting around this.

[Site Infrastructure]: {% link _posts/2021-01-08-blog-infra.md %}

As an example, we'll change Kramdown to make headings into links. This'll allow readers to easily link to specific sections of articles -- try clicking the link of any header on my articles! Of course, there are other ways of doing this -- see this [stackoverflow question](https://stackoverflow.com/q/40469259) -- but directly extending Kramdown is the cleanest.

Fortunately, we can change Kramdown's behaviour pretty easily by subclassing [`Kramdown::Converter::Html`](https://kramdown.gettalong.org/rdoc/Kramdown/Converter/Html.html) which converts Kramdown's internal document representation to HTML. The `convert_*` method of this class produce the HTML for different Markdown parts. For our change, we'll want to change `#convert_header` -- other changes will require editing other methods.

Put this in `_plugins/kramdown.rb`:

```ruby
module Kramdown
  # Subclass the existing converter
  class Converter::Html5 < Converter::Html
    # Override the function
    def convert_header(el, indent)
      # super doesn't work since we can't just patch stuff
      # at the end, so I'm copying and editing the original
      # code from here:
      # https://kramdown.gettalong.org/rdoc/Kramdown/Converter/Html.html#method-i-convert_header
      attr = el.attr.dup
      if @options[:auto_ids] && !attr['id']
        attr['id'] = generate_id(el.options[:raw_text])
      end
      @toc << [el.options[:level], attr['id'], el.children] if attr['id'] && in_toc?(el)
      level = output_header_level(el.options[:level])

      # New code. inner() recursively generates the content
      # inside the tag, and format_as_span_html() wraps that
      # in a <a> tag with the right id. The #{...} bits are
      # string interpolation, like {...} in python f-strings.
      link = format_as_span_html('a', {"href": "##{attr['id']}"}, inner(el, indent))
      format_as_block_html("h#{level}", attr, link, indent)
    end
end
```

*Note: This class must be in the `Kramdown::Converter` module, and the actual name of the class is used in a method name -- I'll point this out when it turns up.*

However, we can't change the converter that's used by Kramdown using config options. Instead, to get Jekyll to recognise our new Kramdown converter, we need to make (well, subclass) our own Markdown variant:

```ruby
class Jekyll::Converters::Markdown::Custom < Jekyll::Converters::Markdown::KramdownParser
  def convert(content)
    # Again, we're just slightly modifying existing code.
    # Original at
    # https://github.com/jekyll/jekyll/blob/master/lib/jekyll/converters/markdown/kramdown_parser.rb
    document = Kramdown::JekyllDocument.new(content, @config)
    # NOTE the name of the #to_html5 method is derived from the class name above
    html_output = document.to_html5
    if @config["show_warnings"]
      document.warnings.each do |warning|
        Jekyll.logger.warn "Kramdown warning:", warning
      end
    end
    html_output
  end
end
```

Finally, to make Jekyll use this Markdown variant, we need to set the `markdown` config option in `_config.yml` to `Custom` (or whatever you've named the last converter).

```yaml
markdown: Custom
```

Now, if you've done everything right, your headings should be links now! Congrats on your first Kramdown modification! If you have problems, feel free to reply below or contact me.
