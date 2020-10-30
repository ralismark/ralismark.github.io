FROM jekyll/builder:latest

EXPOSE "4000"

RUN gem install kramdown-math-sskatex && \
	wget 'https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js' -O /tmp/katex.min.js
RUN apk --no-cache add graphviz
RUN gem install svg_optimizer

CMD jekyll serve \
	-d /tmp/_site \
	--host 0.0.0.0 --port 4000 \
	--config _config.yml,_config-dev.yml \
	--watch --force_polling
