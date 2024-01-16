---
layout: post
title: "Capability derivation trees that make sense"
excerpt: TODO fjkdslafjklafjalk
date: 2023-02-07
tags:
reason: wip
---

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

.. admonition:: aside

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
The way seL4 handles these kinds of operations is to require the task yield after $$O(1)$$ of work.
This means we'll need to leave the capability tree in a sensible state, as well as handle other threads making changes to it.

Fortunately, seL4 gives us one trick to make this easier: zombie caps.
They're a way to mark a cap as unusable, without completely deleting it yet.

This is really tricky!
The capability tree needs to be in a consistent state when we yield, and we also can't run for unbounded time.
This means that deconstructing the derivation tree from top-down and reparenting things as necessary won't work, since we might not be able to find a place to graft nodes on in time.
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
