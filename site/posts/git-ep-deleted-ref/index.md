---
layout: post
title: "Git Emergency Procedures #1: Recovering Deleted Refs"
tags:
excerpt: Recovering commits from deleted branches
---

Suppose you deleted a branch, or undid a merge with a now deleted branch. How do
you recover the commits? There are several things to go about this.

<!--more-->

# Immediate Action

This is a completely recoverable scenario, since git doesn't immediately delete
unreferenced commits. To find the hash of the commit, you can run `git reflog`
to see the HEAD of previous commands. This allows you to find the tip of the
branch (which you would've been on when working on it). This is probable the
best way to find the commit you need to reference.

Next, to actually restore the reference, you need to make a branch pointing to
the hash: `git branch <name> <hash>`.

# Possible Causes

One way this can happen (as it did to me) was to:
1. Merge branch `feature` into `master`.
2. Delete branch `feature`.
3. Later, delete the merge commit (e.g. during a rebase).

![]({% graph %}
digraph G {
  rankdir="LR";
  graph [ranksep=1];
  node [label="",shape="circle"];

  subgraph cluster_m {
    m0 -> m1 -> m2 -> m3;
    m4 -> m5 [color="grey",style="dotted"];
    m3 -> m5 [constraint=false];
    m4 [color="grey"];
    m3 -> m4 [color="grey"];
    color="none";
  }
  subgraph cluster_b {
    node [color="grey"];
    edge [color="grey"];
    m1 -> b1 -> b2 -> m4;
    color="none";
  }
  { rank=same; master -> m5 [constraint=false]; master [label="master",shape="none"] }
  { rank=same; b2 -> feature [dir=back,constraint=false,color="grey"]; feature [label="feature",shape="none",color="grey",fontcolor="grey"] }
}
{% endgraph %})
Git history after a rebase removed a merge commit.

Normally, deleting the branch in step 2 is fine, since the merge still holds a
reference to the deleted branch. However, after deleting the merge commit (or
all the merged commits), nothing references the branch, and so it disappears
from history! This can be done accidentally, since there's no warnings. However,
if the merged was a fast-forward, you'll have to delete all the commits in the
merged branch (since the commits on `feature` are inlined into `master`).

# Other Notes

If you want to change the commit a branch is pointing to, use
`git reset --hard <hash>`.
