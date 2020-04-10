# Triple Except

This repo is the code for [the blog][1]. Additionally, it supports running
through docker (via the use of a makefile).

  [1]: https://ralismark.github.io

## Experiments

These are changes I make to the blog that may be temporary e.g. testing
features, services etc.

Currently:

- [GoatCounter][2] for analytics

  [2]: https://www.goatcounter.com/

## Running docker

This uses `make` for many of the management operations required, such as
rebuilding the docker image and starting/stopping a container. As a result, make
must be installed. Run `make start` to start a new container running Jekyll.

This Makefile has several build targets (commands):
- `start` - Create and run a new container
- `stop` - Stop an existing container
- `restart` - Stop a container and then start it again
- `image` - Build the docker image without starting a container
- `flogs` - Show logs and follow (stands for **f**ollow **logs**)
- `sh` - Run a shell in the container (e.g. to inspect files)
- `clean` - Remove anything that was build - stopping containers, removing the
    image and clearing tags

For example, run `make start` to create a new container.

The name of the docker image and container can be changed through the
DOCKER_NAME environment variable (e.g. `make start DOCKER_NAME=meow` to rename
to "meow").
