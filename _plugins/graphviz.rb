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
