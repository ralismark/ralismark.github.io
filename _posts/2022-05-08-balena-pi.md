---
layout: post
title: "Raspberry-Pi-As-Code"
tags:
excerpt: Embedded device infrastructure entirely in docker with balenaOS
---

{% include admonition verb="warn" %}
> By late 2022, I no longer had anything that needed to be run on a raspberry pi, and I've now decommissioned my raspberry pi.
> While I still have the infra configurations (including GitHub Actions deploy workflows), alas I cannot vouch for whether this is post is still up to date.

For a while now I've been running [balenaOS] on my raspberry pi.
This is an operating system that's tailored towards hosting docker containers on embedded devices, allowing you to avoid basically all stateful or manual configuration on the device itself.

[balenaOS]: https://www.balena.io/os/

You can either run a single docker container by deploying a Dockerfile & context, or a group using [docker-compose].
One thing to be mindful of is that raspberry pi's are ARM architecture and not x86-64, meaning that it's harder to test the containers on your own system, and you'll also need containers that support ARM in the first place.
Fortunately, balena have available [a massive set of docker images] across a matrix of linux distro and software stack combinations that you can directly use in the `FROM` line in a Dockerfile.
There are a few more balena-specific limitations due to it running their own container engine ([balenaEngine]), but [it's all listed in their docs][balena-docker-compose].

[docker-compose]: https://docs.docker.com/compose/
[a massive set of docker images]: https://www.balena.io/docs/reference/base-images/base-images/
[balena-docker-compose]: https://www.balena.io/docs/reference/supervisor/docker-compose/

Before we go on, I just want to clarify that [balenaOS] is just the raw operating system and [balenaEngine] the container engine, both of which have limited documentation on their own page.
The entire infrastructure stack, which typically includes the balena cloud platform, is just called balena, with [its docs] being the main source of information.

[balenaEngine]: https://www.balena.io/engine/
[its docs]: https://www.balena.io/docs/learn/welcome/introduction/

{% include admonition verb="say" %}
> balenaOS being another [free] component of a fully functioning balena platform?
> [Where have I heard that before](https://wiki.installgentoo.com/index.php/Interjection)?

[free]: https://www.balena.io/os/docs/custom-build/

I also want to highlight the [massive list of example project] (and [even more community ones]) as well as the docs being split up into "Learn", "FAQ", and "Reference" -- I didn't notice those until I was writing this post, but that's really cool.

[even more community ones]: https://hub.balena.io/projects
[massive list of example project]: https://www.balena.io/docs/learn/more/examples/seed-projects/

{% include admonition verb="ask" %}
> By the way, can you use balenaOS without balena cloud?

Yep! Despite most of the stack assuming you're using balenaCloud -- which is free if you're managing less than 10 devices -- you can in fact just run unmanaged balenaOS, avoiding any cloud bits.
For this, follow the [balenaOS guide] instead of the main docs.

[balenaOS guide]: https://www.balena.io/os/docs/raspberrypi3/getting-started/

Even if you're not using the cloud platform, you still get all the benefits of their OS and container engine.
One of the many nice things about having everything declared via Dockerfiles/docker-compose.yml is that the system can be made really resilient to networking/power issues, which by specialising for embedded systems they have done really well -- everything just automatically gets restarted if things go down.

Another is the entire Infrastructure-as-Code thing you can do.
I have my entire system setup stored in a github repo, and the [balena cli] makes deploying changes (and a lot of other management utilities) just a single command.
And with balenaCloud, you can even deploy via the cloud instead of directly to the device, which allowed me to have everything automatically deploy when I push.

[balena cli]: https://www.balena.io/docs/reference/balena-cli/

# Afterword

This idea of treating even your own systems like [cattle instead of pets] resonates with me a lot.
I'm definitely aware of [NixOS] which has similar ideas (as well as [this person that erases their system every reboot]), and I'm gradually trying to learn that ecosystem (albeit with difficulty, which is why I'm somewhat reluctant to go beyond having it installed atop Manjaro).

[cattle instead of pets]: http://cloudscaling.com/blog/cloud-computing/the-history-of-pets-vs-cattle/
[NixOS]: https://nixos.org/
[this person that erases their system every reboot]: https://grahamc.com/blog/erase-your-darlings

On another note, I'm trying to avoid this article turning into a "this is how you use it" one like some of my others, and it's turning more into me just saying how nice and under-appreciated balena is.
So, if any of this seems like an interesting way to run a raspberry pi (or other embedded-like system), head on over to [their website] for a managed install or the [balenaOS guide] for an unmanaged one.
And feel free to ask me if you have an questions!

[their website]: https://www.balena.io/
