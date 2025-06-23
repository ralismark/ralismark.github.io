---
layout: post
title: They Did Surgery On An (Ephemeral) NixOS
excerpt: "\"Copy over your home directory\" the hard way"
date: 2025-06-14
tags:
---

One of the first things I had to do when I got my new laptop is migrate my stuff over from my old one.
Now, I use NixOS and in a pretty quirky way -- my root partition gets wiped every boot and everything repopulated (using bind mounts and NixOS) from an separate persistent partition -- essentially the [Erase your darlings] setup.
This persistent partition has:

[Erase your darlings]: https://grahamc.com/blog/erase-your-darlings/

- My home directory
- Some other persistent state for system services
- All of `/nix`

.. admonition:: me/say

	Well, not actually a disk partition, but a ZFS dataset.
	They are the same for most purposes, but the only difference is that it's _really easy_[^zfs-send] to send a whole dataset from one ZFS filesystem to another, which was what I did to get all my data across.

	For convenience I'll call both regular partitions and ZFS datasets partitions.

[^zfs-send]: Well, it was a bit complicated, but only from trying to transfer 50GB in a reasonable time.
	Doing it over the network wasn't feasible -- my WiFi was too bad, and neither of my laptops have an ethernet port.
	What I ended up doing was writing `zfs send` into a file, copying it onto a harddrive (after splitting it up using [split(1)](https://man.archlinux.org/man/split.1) to get around FAT32's filesize limits), then piecing everything together with `cat`, before finally feeding it into `zfs recv`.

However, that doesn't actually provide a working OS on the new system.

# The Journey Ahead

It's not as easy as just copying the boot entries over and just booting them -- differences in partition UUIDs for one, but also hardware differences and probably a myriad of other little things that I didn't particularly feel like finding out.

To get there, we'll need to step from NixOS install to NixOS install:

1. Firstly, partitioning the disk, setting up ZFS, and just getting a independent NixOS installation on the new laptop.
2. From there, pivot to booting something simple using the `/nix/store` copied from the old laptop.
3. Then, we can gradually update our NixOS configuration until we've got all the features from the old laptop enabled.

Getting to stage 1 is nothing novel: just following the [NixOS Root on ZFS](https://openzfs.github.io/openzfs-docs/Getting%20Started/NixOS/Root%20on%20ZFS.html) instructions.
Neither is going from 2 to 3.
The hard part is getting to stage 2.

# Getting Ready

Because we don't have the root partition from the old laptop, only the persistent one, stage 1 necessarily has to support that as well.
For my system configuration, this means using [nix-community/impermanence].
And for reasons that we'll see in a bit, I also want the system configured via my [nixfiles repo] on GitHub.

[nix-community/impermanence]: https://github.com/nix-community/impermanence
[nixfiles repo]: https://github.com/ralismark/nixfiles

I'll omit the details of that, but once we've got that set up our system will have 4 partitions:

- EFI boot partition
- root partition (that gets wiped on boot)
- new (temporary) persistent data -- called `bootstrap_persist`
- old (copied over) persistent data -- called `persist`

Stage 1 boots with `bootstrap_persist`, and we want to get to something that boots with `persist`.

# The Switcheroo

Now, how to get to stage 2?

The answer: we have it already built and ready in the `persist`'s `/nix/store` that we copied over from the old laptop.
This is why I wanted stage 1 in configured via my nixfiles repo on GitHub -- I could just:

- Change the references to `bootstrap_persist` to `persist` in the stage 1 configuration
- `nixos-rebuild boot` to install the boot entries
- Also build that configuration on the old laptop, into the `/nix/store` of its copy of `persist`
- Sync `persist` over

Now with the files required to boot stage 2 in the `/nix/store` of both `bootstrap_persist` and `persist`, we can reboot directly into it!
And if that doesn't work, we still have stage 1 in our boot entries to fall back to.

And from here, it's smooth sailing to getting a fully set up system :)

.. admonition:: me/say

	This post was sitting in my drafts for a long time.
	I did all of this originally in July 2024, so it's been almost a whole year...
