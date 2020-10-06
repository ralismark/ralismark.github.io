FROM jekyll/builder:latest

EXPOSE "4000"

RUN gem install kramdown-math-sskatex

CMD jekyll serve \
	-d /tmp/_site \
	--host 0.0.0.0 --port 4000 \
	--config _config.yml,_config-dev.yml \
	--watch --force_polling
