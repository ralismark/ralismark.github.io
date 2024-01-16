---
layout: post
title: The Surprising Complexity Of Paths
excerpt: When filesystems are directed graphs and not trees
date: 2021-07-11
tags:
---

When you're working with paths, especially comparisons between two paths, there are a *lot* of edge cases that can pop up.
And a lot of it is due to symlinks making the filesystem actually not strictly a tree.

<!--more-->

There's two main ways of working with paths, and symlinks are the cause of differences between them:

- *lexically*, only looking at the path string itself and not consulting the OS/filesystem
- *canonically*, where you ask the filesystem to give you the true path of something.

For an example of this, did you know that the path `a/b/..` might point to something different to `a`?
This happens if `b` is a symlink somewhere else, causing it parent directory to not actually be `a`:

```console
$ tree
.
├── a
│   └── b -> ../c/actual-b
└── c
    └── actual-b
$ realpath --relative-to . a/b/..
c
```

However, if you try to process this by removing the previous component when you see a `..`, you'll get a different answer -- `a`.

# Hiding a path

Here's the motivating problem:
Suppose you're writing the `open-file` function for some application, and [you want to support hiding a given path][tectonic-769].
The only guarantee about the path you'll be asked to open and the hidden path is that they'll be well-formed paths -- no syntax error or whatever, but you don't know if:

[tectonic-769]: https://github.com/tectonic-typesetting/tectonic/issues/769

- They're absolute or relative
- Whether there's symlinks or other kinds of links
- If they even exist

There's a couple approaches you can take.

## Direct comparison

You're not that bothered about correctness, so you just do a direct (lexical) comparison of the paths using your path type's `==` operator.

Yes, this works for the common use cases.
But not if:

- one is absolute and the other is relative
- your path has `..` and `.` in places
- if there are symlinks involved *anywhere*
- you're trying to access a file *inside* a hidden folder

That's a lot of things that we don't handle.
Not good.
Let's do this correctly.

## Canonicalisation

Fortunately, there's a handy function that asks the operating system to give you the *canonical path* -- a path that's always the same for each file system object, no matter what path you use to access it, as long as the target exists.
So you just canonicalise everything, and since you'll be opening the path anyways, you just skip missing hidden paths, and fail the call if the requested path is missing.
Then, direct comparison with `==`.

Now, this works wonderfully for hidden *files*!
If you're trying to open a hidden file, both the hidden path and the requested path will canonicalise to the same thing.

But less so for directories.

## More canonicalisation

Now, what we're trying to do here make a bit more sense if we completely drop the idea of the filesystem being like a tree.
With symlinks and hardlinks and the oddities those bring, it's much more helpful to consider it as a directed graph, with `..` just being a regular edge.

Now, under this, paths are just instructions on how to traverse it from either the node corresponding to the (or *a*, on windows[^win-root]) root or current directory.
Which points us at how to hide a directory:
Check every prefix of the requested path

[^win-root]: On unix-like systems, fortunately there's a unique `/`, but on windows, you've got multiple drives (and multiple working directories -- it turns out that each drive has it's own!) as well as UNC paths. Have a look at <https://docs.microsoft.com/en-us/dotnet/standard/io/file-path-formats> for more complexities.

- Get the canonical path of the hidden path
- For every prefix of the requested path, canonicalise it and equality-compare against the hidden path

This means that if we fail the call if ever need to access the hidden path.
However, this has an interesting implication if we try to hide an *ancestor* of a path we use.
Take this tree:

```
.
├── a
│   └── b -> ../c/actual-b
└── c
    └── actual-b
        └── inside
```

If we hide `c`, the path `a/b/inside` is still valid!
We never actually visit it so it's all fine, but this may be a bit unexpected.
Additionally, hiding `c/actual-b` still fails the lookup of `a/b/inside`.

This process pretty much gets us what we want.

## Hiding an edge

What about a different semantic?
What if, instead of hiding the node, we hide the edge to that node?
This is equivalent to deleting the *directory entry*, rather than the inode itself.

Well, now we need to find the directory containing the hidden path, which is different from the *actual* parent directory of the hidden path.
Fortunately, this is pretty easy -- just remove the last component of the hidden path (with special handling for `/` and `.`).
Then, we can do some slightly more advanced checks against the prefixes of the requested path to get us what we want.

# Summary

In short, handle path-based stuff correctly is hard and can involve making weird decisions.

For more, see [this extensive discussion of `..` on Plan9](https://9p.io/sys/doc/lexnames.html), which has to deal with an abundance of mounts, but not symlinks.
Path handling of different languages is also discussed in this [rustlang rfc proposal](https://github.com/gdzx/rfcs/blob/3c69f787b5b32fb9c9960c1e785e5cabcc794238/text/0000-normalized-paths.md).
