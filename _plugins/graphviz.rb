require "svg_optimizer"

class UseCurrentColor < SvgOptimizer::Plugins::Base
  SELECTOR = %w[circle ellipse line path polygon polyline rect].join(",")

  def process
    xml.css(SELECTOR).each do |node|
      node["stroke"] = "currentColor" if node["stroke"] == "black"
      node["fill"] = "currentColor" if node["fill"] == "black"
    end

    xml.css("text").each do |node|
      node["fill"] = "currentColor" if !node["fill"] || node["fill"] = "black"
    end
  end
end

def svg_optimize(content)
  SvgOptimizer.optimize(content, SvgOptimizer::DEFAULT_PLUGINS + [UseCurrentColor])
end

class GraphBlock < Liquid::Block
  def render(context)
    text = super
    io = IO.popen("dot -Gbgcolor=transparent -Tsvg", "r+")
    io.puts(text)
    io.close_write()
    svg_optimize(io.read())
  end
end

Liquid::Template.register_tag("graph", GraphBlock)
