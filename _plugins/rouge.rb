require 'rouge'

module Rouge
  module Formatters
    Formatter.enable_escape!

    class CustomBlock < Formatter
      def initialize(opts={})
        @formatter = HTML.new()
      end

      def stream(tokens, &b)
        yield "<pre><code>"
        @formatter.stream(tokens, &b)
        yield "</code></pre>"
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
