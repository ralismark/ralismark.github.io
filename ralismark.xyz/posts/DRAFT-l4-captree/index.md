---
layout: post
title: "Capability derivation trees that make sense"
excerpt: TODO fjkdslafjklafjalk
date: 2023-02-07
tags:
reason: wip
---

assumed knowledge: general computing (not specifically with seL4)

I've been thinking on and off about capability-based microkernels, in particular seL4.
One thing about seL4 that always confused me was how deriving capabilities from other capabilities and revoking them worked.

# A Bit Of Background

seL4 is build on the idea of [Capability-based security] and in particular the [Object-capability model], where instead of the standard ACL model with resources listing who can access them, actors (e.g. processes, users) hold special tokens -- capabilities -- which grant them access to resources.
These tokens contain a reference to the resource (e.g. a chunk of memory), and a set of permissions describing how the token can be used (e.g. forbidding modifications to it), which the kernel enforces.
To work with these capabilities (which I'll shorten to caps), there's a few extra operations you can do with them beyond accessing the resources they encapsulate:

1. Derive: duplicating a capability into a copy that has the same or fewer permissions.
	This is called Mint in seL4.
2. Delegate: transferring a capability to another actor
3. Revoke: invalidate all capabilities derived (including transitively derived) from a particular capability

These operations naturally give rise to a _derivation tree_, describing what capabilities are derived from what, that gets used for revoke.
In many capability-based kernels, this is also called a _mapping database_.

# What seL4 Does

To understand how seL4 handles these operations, we can have a look at [the relevant section of the (literate) Haskell model](https://github.com/seL4/l4v/blob/8f5e6540de315bf424b8a34f0bfc17ba7040d21d/spec/haskell/src/SEL4/Object/CNode.lhs#L617).
In their words,

> The MDB is a double-linked list that is equivalent to a prefix traversal of the derivation tree.

.. admonition:: me/warn

	This is an inaccurate simplification of the actual mechanism that elides some seL4-specific details.

Each entry in this linked list also contains two extra flags:

- `mdbRevocable`, whether the cap can be a parent in the first place
- `mdbFirstBadged`, for distinguishing between sibling caps (for certain types of caps)

They then define that capability A is the ancestor of the next capability B if:

1. `mdbRevocable` is true for A; and
2. The actual resource that B refers to is either A, a subset of A (e.g. if both are memory regions, A contains all of B); and
3. `mdbFirstBadged` is true for A given that `mdbFirstBadged` is relevant for the kind of cap.

Essentially, it looks like this.

.. figure:: {{ recipe.graphviz("./mdb.dot", page.url + "/mdb.svg") }}




This definition limits how deep the tree can be if we don't allow dividing capabilities.
Since the "root" resource must have 


(For type of capabilities that can be divided, such as regions of memory, we can just keep divigi











































I've been thinking on and off about microkernels, particularly seL4.
One thing that bugged me about seL4 was how unclear the capability derivation mechanism is -- there's functionality to derive and revoke caps, but at the same time you're only allowed at most 1 level derivation.
And so, it's not really clear how the two interact.

Modulo verification constraints, I think I've come up with a mechanism supporting unbounded derivation depth that fits the requirements of seL4.

# A Bit Of Background

Let's back up a little: what even are capabilities and capability derivation trees?
These come from the idea of [Capability-based security] and in particular the [Object-capability model], where instead of the standard ACL model with resources listing who can access them, actors (e.g. processes, users) hold special tokens -- capabilities -- which grant them access to resources.
There are also some additional abilities that make this a really powerful security mechanism:

[Capability-based security]: https://en.wikipedia.org/wiki/Capability-based_security
[Object-capability model]: https://en.wikipedia.org/wiki/Object-capability_model

1. *Derivation*: duplicating a capability into a copy that has the same or fewer permissions, including the ability the create further derivation from this copy
2. *Delegation*: transferring a capability to another actor
3. *Revocation*: invalidating all capabilities derived (or transitively derived) from a given one

When implementing these in an operating system kernel, we'll need a way to track caps and their relationships so that we can identify what operations are valid and support the above abilities.
These give rise to the following requirements:

1. Caps need to know the actual resource (e.g. a process, chunk of memory, or device) they refer to, and the specific rights this capability has
2. We must also be able to find all the descendent derived caps of a given cap, in order to support revocation
3. Caps must be easily moved around to support delegation
4. Ideally, caps are a constant size and only require minimal memory allocation

This all happens in a kernel that must mediate between multiple concurrent actors.
The seL4 kernel handles syscalls while holding a big kernel lock and without being able to be preempted, and so requires that long-running kernel operations run in steps of bounded time, yielding between steps.
This means that we only need to consider concurrency at points where we explicitly yield.

# The Tree

Capabilities and their derivation structure can be naturally represented as a n-ary tree, with nodes corresponding to caps, and edges being derivations.
However, implementing this directly would lead to issues trying to represent a possibly unbounded number of children.
The first bit of insight is to instead use a [Left-child right-sibling binary tree], which reduces the problem down to just representing a binary tree.
In particular, we'll have each cap know its first child, next sibling, and (slightly diverging from the standard structure) either its parent or the previous sibling, in addition to the actual resource, permission bits, and any other metadata we need.

[Left-child right-sibling binary tree]: https://en.wikipedia.org/wiki/Left-child_right-sibling_binary_tree

It also turns out that with this representation, we can pretty much implement all the operations!

# Derive

Deriving a cap into another that cannot outlive the first is a reasonably simple operation with our data structure.
It's pretty much a linked list prepend:

1. set the new node's sibling pointer to our first child
2. updating our first child pointer to point to the new node

From this, we know that when our current cap is deleted, this new derived node must also be deleted.

Interestingly enough, there's another way to derive caps -- you can also create a new _sibling_ instead of a new child.
This creates a copy of your cap with a lifetime that is tied to your _parent_, allowing the original cap to be deleted without affecting the new cap, which can be handy sometimes?

.. admonition:: me/say

	I will admit I'm not familiar with capability systems enough to know usecases for these two kind of derive, so please let me know if you know more!

# Delegate/Move

Changing the memory location of a node is relatively easy, since each node is only directly referred to by up to 3 other nodes, and those are exactly the nodes which we might have a pointer to.
We would just need to update:

1. Your first child's parent (if you have children)
2. Your next sibling's previous sibling (if you have a next sibling)
3. Either your parent's first child, or your previous sibling's next sibling, depending on whether you are the first child

# Revoke

Finally, we reach Revoke.
This is the hardest operation to handle, since a cap can have potentially unbounded descendants, and we'll need to process all of them.
This means that Revoke would normally have unbounded runtime, which is _bad_ in a kernel context, particularly with seL4's execution model and realtime guarantees.
The way seL4 handles these kinds of operations is to require the task yield after $O(1)$ of work.
This means we'll need to leave the capability tree in a sensible state, as well as handle other threads making changes to it.

This is really tricky!
The naive method of simply iterating over all descendants and destroying things bottom-up violates the $O(1)$ requirement.
Destroying it top-down and 


These requirements mean that deconstructing the derivation tree from top-down and reparenting things as necessary won't work, since we might not be able to find a place to graft nodes on in time.
<!-- TODO fix wording -->
<!--TODO maybe like an initial idea?-->

Fortunately, seL4 provides a mechanism that will be really helpful: zombie caps.
These are a way to make caps no longer functional, but still exist in memory.
Using this, we can crucially stop other threads from deriving them.

<!--TODO reword-->
Here's how.
We track the cap we were told to revoke, as well another cap that we're currently processing:

1. If the current cap has any children:

	1. Turn the cap into a zombie so it cannot have more children.
	2. Update the current cap to be this cap's first child.
	3. Yield, and start this procedure from the top.

2. Otherwise, if this cap has a next sibling:

	1. Delete the current cap.
	2. Update the current cap to the next sibling.
	3. Yield, and restart the procedure.

3. Otherwise, the cap must have no children and no siblings.
Then:

	1. Delete the current cap.
	2. Update the current cap to its parent.
	3. Yield, and restart the procedure.

It might be necessary to run multiple steps per iteration to stop the tree from growing faster than we can destroy it.

<!--TODO diagram??-->
<!--TODO conclusion-->
