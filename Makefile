#
# Project Make File
#

DOCKER_NAME = app-serve

# Start a container
start: image
	docker run --rm -v $(CURDIR):/app -it --detach -p 127.0.0.1:4000:4000 --name $(DOCKER_NAME) $(DOCKER_NAME)

foreground: image
	docker run --rm -v $(CURDIR):/app -it -p 127.0.0.1:4000:4000 --name $(DOCKER_NAME) $(DOCKER_NAME)

# Stop a running container
stop:
	docker stop -t 2 $(DOCKER_NAME)

# Build container image (don't run)
image: Dockerfile
	docker build -t $(DOCKER_NAME) -f Dockerfile .

# Restart (stop then start) a container
restart: stop start

# Display and follow stdout/err logs
flogs:
	docker logs -f $(DOCKER_NAME)

# Run sh in the container
sh:
	docker exec -it $(DOCKER_NAME) /bin/sh

clean: stop
	docker rmi $(DOCKER_NAME)

.PHONY: start foreground stop image restart flogs sh clean
