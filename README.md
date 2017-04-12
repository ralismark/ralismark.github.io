# Triple Except

This repo is currently a template for a (somewhat) minimal Jekyll docker
installation for GitHub pages.

## Running docker

This uses `make` for many of the management operations required, such as
rebuilding the docker image and starting/stopping a container. As a result, make
must be installed. Run `make start` to start a new container running Jekyll.

If you're running windows, the setup is still similar. If you have `nmake`
installed (through Visual Studio), that is usable too. Otherwise, install of
`make` (through [GnuWin32][1]) or `nmake` (through Visual Studio, any version
should be fine). Nothing else is needed!

  [1]: http://gnuwin32.sourceforge.net/

This Makefile has several build targets (commands):
- `start` - Create and run a new container
- `stop` - Stop an existing container
- `restart` - Stop a container and then start it again
- `build` - Build the docker image without starting a container
- `flogs` - Show logs and follow (stands for **f**ollow **logs**)
- `sh` - Run a shell in the container (e.g. to inspect files)
- `addr` - Show published ports and their bindings
- `clean` - Remove anything that was build - stopping containers, removing the
    image and clearing tags

For example, run `make start` to create a new container. Look at make/nmake
usage for details.

The name of the docker image and container can be changed through the
DOCKER_NAME environment variable (e.g. `make start DOCKER_NAME=meow` to rename
to "meow").

## Implementation Details

Several workarounds were needed so that the Makefile could be used on both
Windows and Linux without modification. For example, directories were used for
build tags since `mkdir` and `rmdir` were common to both, as well as `|| cd .`
for suppressing return codes silently.
