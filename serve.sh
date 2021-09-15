#!/bin/sh

IMAGE_NAME=site

# For caching
mkdir -p .jekyll-cache
touch .jekyll-metadata

docker build -t "$IMAGE_NAME" . &&
docker run --rm -it -p 4000:4000 --name "$IMAGE_NAME" \
  -v "$PWD:/srv/jekyll:ro" \
  -v "$PWD/.jekyll-cache:/srv/jekyll/.jekyll-cache:rw" \
  -v "$PWD/.jekyll-metadata:/srv/jekyll/.jekyll-metadata:rw" \
  -e JEKYLL_ENV=development \
  "$IMAGE_NAME" "$@"
