---
layout: post
title: An SSH Workflow
tags:
excerpt: How to have a nice time developing remotely
---

For both uni and my day job, I regularly do development over ssh, where your entire development environment -- that is source code, compilers, and other tooling -- are all situation on a remote machine.
As with most people, my local environment is set up just the way I like it, so working remotely using out-of-the-box vim or nano is a bit painful.

Now, if you use [VSCode], this is pretty easy to do with extensions such as [SSH FS] (there is also Remote SSH but it's surprisingly intensive on the remote server so please avoid it if you can).
These allow you to essentially work as if everything was local, still using your local VSCode setup, directly editing the remote files.
My friend has [a pretty good guide on this], though it's tailored to students at UNSW.

[a pretty good guide on this]: https://abiram.me/cse-setup
[VSCode]: https://code.visualstudio.com/
[SSH FS]: https://marketplace.visualstudio.com/items?itemName=Kelvin.vscode-sshfs

However, if VSCode is not your thing and you prefer doing things via another editor and the command line, things can get a bit more involved.
I'll be assuming a Linux local environment from here on out -- they might apply to WSL and MacOS with tweaking, but I haven't checked compatibility with either.

# SSHFS

The first stop on our journey is [sshfs](https://github.com/libfuse/sshfs)[^archived], a service that mounts a remote system's filesystem directly to your local machine, allowing you to access remote files as if they were local, kinda like how you would a USB drive.
It's pretty popular and likely can be directly installed from your system's package manager.

[^archived]: The repo itself was recently archived due to the maintainer not being able to work on it as much, but despite that it's still a very solid production-ready piece of software.

Using it is pretty simple -- just `sshfs <host>: <localdir>` (note the trailing colon) where `<host>` is what you'd use with the `ssh` command, and `<localdir>` is the local directory that files would be accessible through.
Unmounting is then `fusermount -u <localdir>`.

Honestly though, there's already plenty of introductory sshfs tutorials online, such as [my friend's][cse-sshfs], so to avoid adding to that pile I'm going to defer to them.
Instead, I'll outline some additional options that really make sshfs nicer that often aren't covered in those tutorials.
As always, you can look at [the sshfs man page] for specifics.

[cse-sshfs]: https://abiram.me/cse-sshfs
[the sshfs man page]: https://man.archlinux.org/man/sshfs.1

# Options

Firstly, you almost certainly want `-o idmap=user`, which avoids files owned by the remote user being reported as owned by someone else.
The reason is a bit technical.
By default, when accessing things over sshfs, remote user/group IDs are not translated to what they should be locally.
This means that on using sshfs with a system where I have a different user ID (i.e. basically all ssh servers), I'll see this:
```
$ sshfs cse: ~/mnt

$ ls -l ~/mnt
total 252
drwxr-x--- 1 51148 51148   4096 Aug 13 01:21 aos
drwxr-x--- 1 51148 51148   4096 Jun  3 13:51 cs9242
-rw-r--r-- 1 51148 51148 226852 Jul 14 18:57 duck.jpg
drwxr-x--- 1 51148 51148   4096 Jul  8 18:10 testing
-rw-r--r-- 1 51148 51148   4704 Jul 11 14:56 odroid
drwxr-xr-x 1 51148 51148   4096 Aug 17 18:33 public_html
drwxr-xr-x 1 51148 51148   4096 Jul  8 00:26 remote-bin
-rw-r--r-- 1 51148 51148      0 Jul 13 12:01 results.tsv
-rw-r--r-- 1 51148 51148      0 Jul 19 14:53 sosh
```
showing that, to my local system, none of the files actually appear owned by me!
To be honest though, I'm not really sure what the implications of this are -- I thought it'd mess with permissions or something but that doesn't seem to be the case?

Still, you can fix it with the option `-o idmap=user`.
You'll see this instead:
```
$ sshfs cse: ~/mnt -oidmap=user

$ ls -l ~/mnt
total 252
drwxr-x--- 1 temmie temmie   4096 Aug 13 01:21 aos
drwxr-x--- 1 temmie temmie   4096 Jun  3 13:51 cs9242
-rw-r--r-- 1 temmie temmie 226852 Jul 14 18:57 duck.jpg
drwxr-x--- 1 temmie temmie   4096 Jul  8 18:10 testing
-rw-r--r-- 1 temmie temmie   4704 Jul 11 14:56 odroid
drwxr-xr-x 1 temmie temmie   4096 Aug 17 18:33 public_html
drwxr-xr-x 1 temmie temmie   4096 Jul  8 00:26 remote-bin
-rw-r--r-- 1 temmie temmie      0 Jul 13 12:01 results.tsv
-rw-r--r-- 1 temmie temmie      0 Jul 19 14:53 sosh
```

Out-of-the-box, sshfs will also unmount and exit when it disconnects.
That's pretty disruptive if you have a spotty internet connection, or if you're suspending your laptop and moving around (causing the internet connection to temporarily drop), which is what I often do.
Fortunately, sshfs has the `-o reconnect` option, which makes it reconnect when it gets disconnected.
You probably also want to pair this with `-o ServerAliveInterval=5` to make it detect that faster, since by default it takes around 45 seconds for sshfs to realise it got disconnected, and during this time anything trying to access the remote files will freeze.

There's a few more interesting options like `-o transform_symlinks`, but I haven't used them much so I don't know if there's any sharp edges with them.
But that's pretty much it for making sshfs itself nicer.

Still, there's so much more you can do!

# Remote execution

With sshfs acting just like your local filesystem, you can in fact run (local) commands there!
However, anything filesystem-intensive takes *forever*:

```
$ time git status -sb # remote command, remote filesystem
## master...origin/master
 M projects/aos/apps/countdown/src/main.c
?? duck.jpg
git status -sb  0.03s user 0.09s system 68% cpu 0.174 total

$ time git status -sb # local command, remote filesystem
Refresh index: 100% (4732/4732), done.
## master...origin/master
 M projects/aos/apps/countdown/src/main.c
?? duck.jpg
git status -sb  1.18s user 1.58s system 1% cpu 4:22.04 total
```

Under a seconds compared to over 4 minutes -- that's a *1505x* slowdown!
Pretty awful for something as common as `git statsus`.
Furthermore, if you're working over ssh you almost certainly have some commands that must be run remotely, such as `make` or other tools that only exist on the remote system.
Running them via `ssh <host> <command>` would work, except that they always run in the home directory and not where you're actually doing work.

What would be nice is something that automatically figures out where the current directory corresponds to on the remote machine, and runs the command there.
You can accomplish this by writing a simple shell script.
Or, take the one I made -- [tunnel-run] -- and stick it in your \$PATH!
It's used as command wrapper, just like with `ssh`.

[tunnel-run]: https://github.com/ralismark/micro/blob/main/tunnel-run

```shellsession
$ hostname
delta
$ tunnel-run hostname
weaver
$ time tunnel-run git status -sb
## master...origin/master
 M projects/aos/apps/countdown/src/main.c
?? .cache/
?? .editorconfig
?? duck.jpg
?? projects/aos/apps/sosh/results.png
tunnel-run git status -sb  0.07s user 0.07s system 12% cpu 1.148 total
```

Now it's just a bit over a second (I'm guessing from ssh connecting) instead of several minutes -- much better!

It turns out a pretty useful extension to this was to also detect if you're *not* in sshfs and just run the command locally.
Then you could alias `git` to `tunnel-run git` and it'll just figure out the right thing to do.
And, inspired by [distcc's "masquerading" feature], I also added support for directly creating a symlink named `git` to `tunnel-run` in your PATH to do the same thing.
This primarily means that it'll do the right thing even in scripts or other shells that don't have your alias.
And as a bit of a hack, if you truly wanted to run it locally then you can do `tunnel-run locally git`.

[distcc's "masquerading" feature]: https://man.archlinux.org/man/distcc.1#MASQUERADING

Anyways, if you have any questions about that script feel free to send them over to me!

# SSH options

In addition to SSHFS options, there are a couple of options for ssh that are really helpful.
These go in your ~/.ssh/config file below a `Host *` (or other) line.
See [man ssh_config] for more info!

[man ssh_config]: https://man.archlinux.org/man/ssh_config.5

First are ones to keep ssh connections around and reuse them:

- `ControlMaster auto` will enable this feature -- if there is an existing connection, reuse it, otherwise start a new one and allow other to reuse it
- `ControlPath /run/user/%i/sshmux-%r@%h:%p-%l` sets the path that ssh uses to lookup this connection.
What specifically this is isn't that important but there are some constraints[^controlpath].
- `ControlPersist 60` determines how many seconds a connection is kept around for reuse (in this case 1 minute), so that the process doesn't hang around forever taking up resources, but you still get the benefits if you run commands on the same server a bunch.

[^controlpath]: it should contain either all of `%l`, `%h`, `%p`, and `%r`, or `%C`, so that it doesn't reuse connections that should be distinct.

# System mount

If you use sshfs ever day, it's convenient to have the directories automatically mounted when you start up your system.
I'm quite a fan of systemd, so here's my way of integrating these mounts into it.

Systemd has mount units, which are a special kind of unit that corresponds to mounting something at a specific place in your filesystem.
To use sshfs for it, put a file that looks like this
```ini
[Unit]
Description=sshfs mount cse: to /home/temmie/.local/mount/cse

[Mount]
What=cse:
Where=/home/temmie/.local/mount/cse
Type=fuse.sshfs
Options=idmap=user,x-systemd.automount,_netdev,reconnect,ControlPath=none,ServerAliveInterval=5
LazyUnmount=true

[Install]
WantedBy=default.target
```
in `~/.config/systemd/user/`.
The name for the file is a bit funny, since systemd needs special escaping for the path, but you can find this with `systemd-escape -p $PWD`.

Then, `systemctl enable --now $PWD` to mount and have it remount on startup!

# Bookmarks

If you're using sshfs a lot, you probably have fixed locations for them.
And if you're using them a lot, having them be anywhere deeper than you home directory can be a hassle.
However, if you're not a fan of polluting the home directory, and you use [zsh], then there is something you can do.

[zsh]: https://wiki.archlinux.org/title/Zsh

{% include admonition verb="aside" %}
> As you might be able to tell, it's going to get more and more tailored to me as we go.

I currently have all my mounts as subdirectories of `~/.local/mount/`.
To avoid the pain of having to type out `~/.local/mount/remote/...` each time, I've set up zsh so that `~remote` points there, so you can just do `cd ~remote` to go to the mount for that server.
The way this is done is with *directory hashes*.
Let me demonstrate -- all of this is running in zsh.

```
$ cd ~remote
cd: no such file or directory: ~remote
$ hash -d remote=$HOME/.local/mount/remote
$ cd ~remote
$ pwd
/home/temmie/.local/mount/remote
```

And you can put this in your zshrc!

# Summary

That about wraps it up for this grab-bag of ssh/sshfs tricks I've discovered over the years.
Let me know if you have any other cool things in your workflow!

One thing I've wanted to make is a VPN of sorts, where the hostname `remote.ssh` gets translated to an IP that automatically forwards ports to the remote server.
At work, I need to work with a lot of servers that have services that only accessible from localhost, so this means that instead of needing to do `ssh -L 9900:localhost:9900 remote` I can just connect to `remote.ssh:9900`.
Alas, seems like a lot of work to hook into all the layers of the network stack to make this work, but if/when it exists it would be really cool!

<!--
# Addendum: Remote SSH Overload

At UNSW, our computer science faculty (CSE) provides shared Linux servers for all students.
These are heavily used as *the* standard development environment for all students for assignments/exams, in order to reduce issues that would otherwise arise from everyone having slightly different local environments.
However, having some sort of local environment was still nicer, since the alternative was to use VNC or just a text-only ssh connection.

A year or two ago, a friend of mine discovered Microsoft's Remote SSH plugin and released [a guide to setting up VSCode and using it][abiram-legacy].
This easy-to-follow guide meant that students quickly began moving to using this.
However, as we would discover during the exam period, the Remote SSH plugin runs its own server on the remote machine, and more if you have language servers configured.
With hundreds of people connected simultaneously working on exams, this accumulated to *many gigabytes* of memory usage, slowing the servers and anything on them to a crawl.

[abiram-legacy]: https://abiram.me/cse-setup-legacy

For this and some other reason, this plugin became deprecated
-->
