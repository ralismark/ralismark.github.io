FROM starefossen/github-pages:latest

ENV APPDIR /app
ENV OUTDIR /srv
WORKDIR $APPDIR

ENV JEKYLL_ENV=development
EXPOSE "4000"
ENTRYPOINT jekyll serve \
	--host 0.0.0.0 --port 4000 -s $APPDIR -d $OUTDIR \
	--config _config.yml,_config-dev.yml \
	--watch --force_polling --safe
