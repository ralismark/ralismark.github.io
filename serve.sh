#!/bin/sh

IMAGE_NAME=site

# For caching
mkdir -p .jekyll-cache
touch .jekyll-metadata

docker build -t "$IMAGE_NAME" . &&
docker run --rm -it --name "$IMAGE_NAME" \
  -p 0.0.0.0:17003:17003 \
  -v "$PWD:/srv/jekyll:ro" \
  -v "$PWD/.jekyll-cache:/srv/jekyll/.jekyll-cache:rw" \
  -v "$PWD/.jekyll-metadata:/srv/jekyll/.jekyll-metadata:rw" \
  -e JEKYLL_ENV=development \
  "$IMAGE_NAME" "$@"
