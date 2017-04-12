FROM alpine:latest

RUN apk add --no-cache \
	ruby \
	libcurl \
	ruby-rdoc \
	ruby-irb

# Build dependencies
RUN apk add --no-cache --virtual build-dependencies \
	ruby-dev \
	build-base \
	libffi-dev \
	zlib-dev

# Install Github Pages
RUN gem install --no-document github-pages

# Delete build dependencies
RUN apk del --no-cache build-dependencies

ENV APPDIR /app
WORKDIR $APPDIR

EXPOSE "4000"
CMD jekyll serve --watch --host 0.0.0.0 --port 4000 --safe -s $APPDIR -d /srv
