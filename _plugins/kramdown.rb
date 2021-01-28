# following https://kalifi.org/2015/04/html5-markdown-kramdown.html
# reference docs: https://kramdown.gettalong.org/rdoc/Kramdown/Converter/Html.html
module Kramdown
  class Converter::Html5 < Converter::Html
    # Linkify headings
    def convert_header(el, indent)
      # This is all existing code...
      attr = el.attr.dup
      if @options[:auto_ids] && !attr['id']
        attr['id'] = generate_id(el.options[:raw_text])
      end
      @toc << [el.options[:level], attr['id'], el.children] if attr['id'] && in_toc?(el)
      level = output_header_level(el.options[:level])

      # Create a nested <a> tag
      link = format_as_span_html('a', {"href": "##{attr['id']}"}, inner(el, indent))
      format_as_block_html("h#{level}", attr, link, indent)
    end

    # Generate <figure>s for images
    def convert_p(el, indent)
      if el.options[:transparent]
        inner(el, indent)
      elsif el.children.first.type == :img
        # Removed the extra checks

        # Generate a figure
        img = "#{' ' * (indent + @indent)}<img#{html_attributes(el.children.first.attr)} />\n"

        # manually do inner(el, indent)
        caption = +''
        @stack.push(el)
        el.children.drop(1).each do |inner_el|
          caption << send(@dispatcher[inner_el.type], inner_el, indent + @indent + @indent)
        end
        @stack.pop

        figcap = format_as_block_html("figcaption", {}, caption, indent + @indent)
        format_as_indented_block_html("figure", {}, img + figcap, indent)
      else
        format_as_block_html("p", el.attr, inner(el, indent), indent)
      end
    end

    # I want to use title instead of alt text for caption
    def convert_standalone_image(el, indent)
      attr = el.attr.dup
      figure_attr = {}
      figure_attr['class'] = attr.delete('class') if attr.key?('class')
      figure_attr['id'] = attr.delete('id') if attr.key?('id')
      body = "#{' ' * (indent + @indent)}<img#{html_attributes(attr)} />\n" \
        "#{' ' * (indent + @indent)}<figcaption>#{attr['title']}</figcaption>\n"
      format_as_indented_block_html("figure", figure_attr, body, indent)
    end
  end
end

class Jekyll::Converters::Markdown::Custom < Jekyll::Converters::Markdown::KramdownParser
  def convert(content)
    document = Kramdown::JekyllDocument.new(content, @config)
    html_output = document.to_html5
    if @config["show_warnings"]
      document.warnings.each do |warning|
        Jekyll.logger.warn "Kramdown warning:", warning
      end
    end
    html_output
  end
end
