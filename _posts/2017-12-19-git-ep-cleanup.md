---
layout: post
title: Git Emergency Procedures - Cleaning things up
tags: git
excerpt: Resetting the repo to its inital state & deleting extra files
---

When working on a repo, you may want to reset the repository to the initial
state when you cloned it. This is more involved than you may think.

<!--more-->


While this isn't exactly an emergency, it's still something useful to know. I've
often cloned a large project, made modifications, then had to undo all of them.
Compiled products, generated files and other mess would also need to be removed,
but it's very difficult to find when hidden by `.gitignore`.

For this, I'm assuming you want to reset absolutely everything you've done. If
you want to save things, copy them outside the repo before wiping everything.

## Tracked files

Reverting all tracked files is pretty simple:

```
git reset --hard HEAD
```

This resets the working tree (file system contents) and the index (staged files)
to the current commit, clearing all changes.

However, this misses both files ignore by `.gitignore` and those that are just
plain untracked. These are usually more common than modified files, especially
when you're just building a project. 

## Actually cleaning

Fortunately, there exists a command to do just this - [`git clean`][1]! As its
man page helpfully states:

  [1]: https://git-scm.com/docs/git-clean

> Cleans the working tree by recursively removing files that are not under version
> control, starting from the current directory.

This command allows us to wipe everything else from the repo. However, if you
run `git clean` without any options, you'll see that it misses a lot of stuff.
To truly remove everything, you need this:

```
git clean -x -d -f -f
```

This has three flags, which can be combined into `-xdff`:

- `-x`: Ignore the `.gitignore`, deleting all untracked files
- `-d`: Delete directories as well as files
- `-ff`: (yes, two [^1] f's here) Delete even sub-repositories

 [^1]:
	If the user has `clean.requireForce` set, a single `-f` is always required
	to delete things. However, two are always needed (independent of config
	options) to delete sub-repositories.

Running this command will dutifully, irrevocably delete all untracked files
under the current directory. Make sure you're in the repo root to clean
everything. If you want to see what you're doing, replace the `-f`s with a
single `-n` to show what would've been deleted. For more useful options it's
best to see the [man page][2].

  [2]: https://git-scm.com/docs/git-clean

However, you still need to run `git reset --hard HEAD` to reset modified files,
as `git clean` only works on files not under version control.

## Not everything

The above covers most destructive use cases, but once in a while you'll need to
save a few things from complete destruction.

If there's changes you've made to tracked files, but you want to delete
everything else (e.g. for a clean build), just run the `clean` command. To keep
new files but reset existing ones, `reset` only.

For more fine grained control, it depends on if the file in tracked or not.
`git clean` has the `-e` option which takes a pattern (like those in
`.gitignore`) to skip certain files. This is respected over `-x`. Tracked files
can be reset with `git checkout -- <pathspec>` for files and
`git checkout -p -- <pathspec>` for individual patches of a file.

---

If you want to learn more about any command described here (they all have many
options not described here), check out their corresponding docs/man pages.

