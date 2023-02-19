require "svg_optimizer"

class UseCurrentColor < SvgOptimizer::Plugins::Base
  def process
    xml.root.add_child(
      <<-EOF
        <style>
          svg {
            color: #e7e6e5;
          }
          @media (prefers-color-scheme: light) {
            svg {
              color: initial;
            }
          }
          @media print {
            svg {
              color: initial;
            }
          }
        </style>
      EOF
    )

    xml.css("circle,ellipse,line,path,polygon,polyline,rect").each do |node|
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
    site = context.registers[:site]
    #
    # p context
    #
    input = super
    io = IO.popen("dot -Gbgcolor=transparent -Tsvg", "r+")
    io.puts(input)
    io.close_write()
    svg = svg_optimize(io.read())

    file = ConstFile.new(site, site.dest, "/assets", "graphviz-#{Digest::SHA1.hexdigest(input)}.svg")
    file.set_content(svg)
    site.static_files << file

    file.relative_path
  end
end

class ConstFile < Jekyll::StaticFile
  def modified?
    return false
  end

  def set_content(content)
    @content = content
  end

  def write(dest)
    dest_path = destination(dest)
    FileUtils.mkdir_p(File.dirname(dest_path))
    File.open(destination(dest), "w") do |file|
      file.write(@content)
    end
    true
  end
end

Liquid::Template.register_tag("graph", GraphBlock)
