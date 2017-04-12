#
# Project Make File
#

# This makefile is meant to be compatible with both make (on linux) and nmake
# (on windows, with msvc). As a result, there are a few workarounds for
# differences between these (e.g. CWD)

DOCKER_NAME = app-serve

# A bit of a hack to make it work with both make and nmake
# Since (hopefully) only one is defined, this allows CWD to be a simple concat
CWD = $(MAKEDIR)$(CURDIR)


# Start a container
start: tag/running addr .phony

# Stop a running container
stop: .phony
	docker stop -t 2 $(DOCKER_NAME) || cd .
	cd tag && rmdir running || cd .

# Restart (stop then start) a container
restart: stop tag/running .phony

# Build container image (don't run)
build: tag/app-image .phony

# Display and follow stdout/err logs
flogs: tag/running .phony
	docker logs -f $(DOCKER_NAME)

# Run sh in the container
sh: tag/running .phony
	docker exec -it $(DOCKER_NAME) /bin/sh

# Show address of exposed ports
addr: tag/running .phony
	echo Published ports:
	docker inspect $(DOCKER_NAME) --format="{{$$r := .NetworkSettings}}{{range $$p, $$conf := .NetworkSettings.Ports}} {{$$p}} -> {{$$r.IPAddress}}:{{(index $$conf 0).HostPort}}{{end}}"

clean: stop
	docker rmi gh-pages $(DOCKER_NAME) || cd .
	cd tag && rmdir running app-image dir || cd .
	rmdir tag

tag/running: tag/app-image
	docker run --rm -v $(CWD):/app -it --detach -p 127.0.0.1:4000:4000 --name $(DOCKER_NAME) $(DOCKER_NAME)
	cd tag && mkdir running || cd .

tag/app-image: Dockerfile tag/dir
	docker build -t $(DOCKER_NAME) -f Dockerfile .
	cd tag && mkdir app-image

tag/dir:
	mkdir tag
	cd tag && mkdir dir || cd .

.phony:
