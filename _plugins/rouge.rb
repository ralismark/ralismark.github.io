require 'rouge'

module Rouge
  module Formatters
    Formatter.enable_escape!

    class CustomBlock < Formatter
      def initialize(opts={})
        @formatter = HTMLPygments.new(HTML.new())
      end

      def stream(tokens, &b)
        @formatter.stream(tokens, &b)
      end
    end

    class CustomSpan < Formatter
      def initialize(opts={})
        @formatter = HTML.new()
      end

      def stream(tokens, &b)
        @formatter.stream(tokens, &b)
      end
    end
  end
end
