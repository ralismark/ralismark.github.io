FROM starefossen/github-pages:latest

ENV APPDIR /app
WORKDIR $APPDIR

EXPOSE "4000"
CMD jekyll serve --watch --force_polling --host 0.0.0.0 --port 4000 --safe -s $APPDIR -d /srv --drafts
