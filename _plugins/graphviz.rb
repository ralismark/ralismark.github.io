require "svg_optimizer"

module Jekyll
  class GraphBlock < Liquid::Block

    def render(context)
      text = super
      io = IO.popen("dot -Gbgcolor=transparent -Tsvg", "r+")
      io.puts(text)
      io.close_write()
      SvgOptimizer.optimize(io.read())
    end

  end
end

Liquid::Template.register_tag("graph", Jekyll::GraphBlock)
