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

        img = ' ' * (indent + @indent) + self.convert_img(el.children.first, indent)
        return img if el.children.length == 1

        # Generate a figure

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
      # note: in ruby the last expression gets returned (like in rust)
    end

    # Do picture tag & WEBP generation
    def convert_img(el, indent)
      src = el.attr['src']
      if src && src.start_with?("/")
        if src.end_with?(".png") || src.end_with?(".jpg")
          webp = Pathname.new(src).sub_ext(".webp").to_s

          spc = ' ' * (indent + @indent)
          body = "#{spc}<source type=\"image/webp\" srcset=\"#{webp}\" />\n" \
            "#{spc}<img#{html_attributes(el.attr)} />\n"
          return format_as_block_html("picture", {}, body, indent)
        end
      end
      super(el, indent)
    end

    # This was originally called from convert_p, but i'm not sure if it's still used
    def convert_standalone_image(el, indent)
      self.convert_img(el, indent)
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
