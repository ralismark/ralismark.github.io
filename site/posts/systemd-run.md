---
layout: post
title: "Systemd-matising Nohup"
excerpt: Leveraging the system manager for ad-hoc tasks
date: 2022-04-28
tags:
---

[systemd] is a massive bundle of system components and management utilities, but at its core, it is a service manager.
It has found its way into a significant amount of distros, which means we can often rely on it being available, allowing us to leverage it as a nicer replacement for some older staples of Linux.
While service management is usually done at a system-wide level and require root, systemd notably offers a _per-user_ service manager we can use as a regular unprivileged user.

[systemd]: https://systemd.io/

.. admonition:: aside

	I've used systemd a bunch on my laptop (including running my graphical environment) under it, so I might write more on it.

# nohup

One aspect where systemd can outright replace and older utility is with [`nohup`](https://en.wikipedia.org/wiki/Nohup), a utility that runs a command detached from your shell, so it'll remain after you disconnect.
The main use for this I see is running services or batch tasks in an ad-hoc manner, but there are a few issues with doing this outside of a service manager:

The biggest is that tracking this detached process is hard, with:

1. Little indication of if/when they exit or get killed
2. No real way of identifying them beyond process name/args or PID
3. As such, it's easy to forget about them and have them linger around forever.
	I've seen this happen many times, sometimes eating up a whole CPU core or several gigabytes of RAM doing who knows what.
4. stdout gets dumped to `~/nohup.out` by default, contributing to the above "no identification" problems, and causing issues if you have multiple detached processes.

(There's also `screen` and `tmux`, which solve some of these by having a persistent shell session.
And they do fill this niche pretty well!
But we're here to talk about systemd, so I'll skim over those)

# Replacing nohup

Now, how can systemd do background processes better?

Introducing [systemd-run](https://man.archlinux.org/man/systemd-run.1.en)!
Here's what running the `distccd` looks like:

```console
$ systemd-run --user -u distcc-123 distccd --no-detach
Running as unit: distcc-123.service
```

Now, what we did here is start a unit, which is just a single "thing" that systemd manages.
As the `.service` suffix indicates, it's a service, which is a process and any children it creates.

Just like with ssh and other command wrappers, options before the first non-option argument are to systemd-run and the ones after are for the spawned process.

- Firstly, the `--user` flag tells systemd-run to use the user service manager (systemd utilities interact with the system-wide service manager by default, which will usually prompt you for a password).
- The subsequent `-u distcc-123` option sets the name that will be used to identify the service.
	This can basically be anything, but will be something unfriendly like `run-r1051a71b69934d1fb3414578fab92172.service` by default.

After starting, we can interact with it via `systemctl`, and read logs with `journalctl`.
As a quick reference:

- `systemctl --user status <service>` to get a quick overview of the state of the process, including information like PID, child processes, memory/cpu usage (if that's enabled), and the last few log lines.
- `systemctl --user stop <service>` to, well, stop it.
- `systemctl --user restart <service>` to stop and start again.
- `journalctl --user -x -a -u <service>` to see logs.
	The `-x` means to explain when systemd notices something (e.g. the service starting/stopping/etc), `-a` makes all lines be printed, even if they're long or have unprintable characters, and `-u <service>` specifies the unit.
	You can also pass `-e` to jump to the end, and `-f` to `tail -f` the log.

The service will automatically unload itself if it exits cleanly, making `systemctl` but not `journalctl` not work with it.
If it crashed or exited with non-zero return code, then it'll remain, allowing you to restart it for example.
If you do want it gone, then you can do `systemctl --user reset-failed <service>`[^reset-failed]

Another caveat is that you might need `loginctl enable-linger` to ensure the process stays around after you log out.
I've used systems where that wasn't necessary, as well as systems where it was (with the process gets killed some time after you log out if you had linger disabled).

[^reset-failed]: I'm actually not sure how necessary this is. I think if you use the same service name you'll get something about it already exists, and I don't actually know if it ever gets automatically unloaded, other than when systemd restarts.

Finally, a comparison with nohup:

1. You can always look in the journal to see how a process exited.
2. Always identifiable by the name you gave it!
3. `systemctl --user status` shows you all your user processes, so you can see if you need to kill any.
4. stdout _and_ stderr are dumped to the journal for you to read at any point!

# Summary

Bringing background processes into a service manager by using systemd-run, instead of leaving it to float around in your system, has several benefits in terms of ease of management.
I also prefer systemd-run due to how it integrates into the wider systemd ecosystem, allowing you to manage both transient tasks like these as well as your standard system services with the same set of tools.

What I've described here is just the surface of using systemd-run (go read the man page!) -- for one, there's way to place limits on memory/cpu.
And systemd itself is quite the featureful service manager as well.
