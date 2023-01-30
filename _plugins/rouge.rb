require 'rouge'

module Rouge
  module Formatters
    class Custom < Formatter
      tag 'custom'

      def initialize(opts={})
        Formatter.enable_escape!

        @formatter = opts[:inline_theme] ? HTMLInline.new(opts[:inline_theme])
                   : HTML.new

        @formatter = HTMLLineTable.new(@formatter, opts) if opts[:line_numbers]

        # @formatter = opts[:inline_theme] ? HTMLInline.new(opts[:inline_theme]) : HTML.new
        # @formatter = HTMLLineTable.new(@formatter, opts) if opts[:line_numbers]
      end

      def stream(tokens, &b)
        @formatter.stream(tokens, &b)
      end
    end
  end
end
