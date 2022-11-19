---
layout: post
title: Debugging Capability Transfer on seL4
tags:
excerpt: "Finding why a central part of capabilities wasn't working"
---

# A bit of context

We were working on the project for the [Advanced Operating Systems course at UNSW][comp9242], which essentially involves building a bunch of OS facilities on top of seL4.
We were figuring out how to handle IO, in particular how to implement file handles.
Now, the boring way is to associate each process with a file descriptor table, with indices of it being passed around in syscalls to perform IO.
However, seL4 is an ✨object-capability kernel✨, at the core of which are Endpoints -- kernel objects for doing remote procedure calls, allowing the transfer of data, and more interestingly, *other capabilities*.
So, our thought was to represent open files as Endpoints, so instead of the `write()` syscall taking in the file descriptor as the argument, it'd be a direct write call through the file you want to write to.
Sounds amazing and really in line with the principles of object capability!

[comp9242]: http://www.cse.unsw.edu.au/~cs9242/20/project/index.shtml

However, this crucially relies on being able to give Endpoints to the process.
One way is for the OS (i.e. what we're implementing, not seL4) to directly put the file endpoint in the process's CSpace -- the "address space" of the process's capabilities.
However, seL4 also supports sending capabilities over Endpoints, which seemed more appropriate.
This was actually quite hard to figure out, which is where our story starts.

# The state of the docs

It turned out that seL4 tutorial has more useful information than the manual.
Pertinent to this is the [Cap Transfer section of the IPC tutorial], which directly gives you example code for a transfer.

[Cap Transfer section of the IPC tutorial]: https://docs.sel4.systems/Tutorials/ipc.html#cap-transfer

The first hurdle was getting a capability your own CSpace root.
It turned out that there's no way to find it if it wasn't explicitly given to you, which is a bit unfortunate.
So, off we go adding code to mint a copy of the user process's own CSpace capability into itself.

```c
seL4_CNode_Mint(
  /*_service*/   proc->root_cnode,
  /*dest_index*/ 2,
  /*dest_depth*/ seL4_WordBits,
  /*src_root*/   cspace, /* OS task's own cspace */
  /*src_index*/  proc->root_cnode,
  /*src_depth*/  seL4_WordBits,
  /*rights*/     seL4_AllRights,
  /*badge*/      0
);
```

After that, we added a `seL4_SetCapReceivePath` call to the receiver like in that tutorial:

```c
// sender:
seL4_SetCap(0, ep);

// receiver:
seL4_SetCapReceivePath(
  2, /* the task's own cspace */
  slot, /* some unused slot */
  seL4_WordBits /* depth??? */
);
```

... and it doesn't work.
The client process would see that no caps were sent at all, not even capsUnwrapped.
We tried doing a transfer the other way -- the client sending the server some caps, and they (correctly, though a bit unexpectedly) got passed via capsUnwrapped since we were transferring references to the same endpoint.
Furthermore, it wasn't raising any debug warnings like you'll see with other malformed endpoint calls, like calling a null cap.

Unfortunately, we were really out of our depth here.
We had only seen seL4 for the first time a few weeks prior and still trying to get our heads around how parts of its API worked.
The relevant part of the manual is [&sect;4.2.2 Capability Transfer], but looking over that multiple times I couldn't see what we were doing wrong.

[&sect;4.2.2 Capability Transfer]: https://sel4.systems/Info/Docs/seL4-manual-latest.pdf#subsection.4.2.2

# Finding out why

So, having not really any other leads, I reached out to a [helpful friend][niccba], who suggested adding debug statements to seL4 itself.
He pointed me to the [transferCaps function] as a good starting point, and told me that that `printf` should already work for printing things.
Luckily, the project's build system also bundled and built seL4, so it was really easy to just modify seL4 and run this modified kernel.
Following various function calls[^what-fns] and sprinkling various `printf`s around led me to find the root error to be `seL4_FailedLookup` holding a `seL4_DepthMismatch` that indicated there were 57 unused bits in the address.

[niccba]: https://nickba.dev
[transferCaps function]: https://github.com/seL4/seL4/blob/3978092885e4f3e6524fb3e40b04c02b35804c50/src/kernel/thread.c#L241
[^what-fns]: Unfortunately, I'm writing this blog post quite a bit after I figured out the issue -- several months later in fact! -- so I don't remember more specifics about the code flow in the kernel.

Digging into seL4 also revealed why we weren't getting any warnings.
It seems to be because the kernel doesn't directly print the warning, but instead just returns them to the caller via its message registers, and the `libsel4` syscall wrapper library is usually configured to issue `seL4_DebugPutchar`s if it noticed it got an error.
However, in the case of a bad CapReceivePath, the endpoint call will still succeed and produce data, so this channel for alerting the program of issues isn't available anymore.

Anyways, updating the SetCapReceivePath call to pass the correct depth fixed things!

```diff
 seL4_SetCapReceivePath(
   2, /* the task's own cspace */
   slot, /* some unused slot */
-  seL4_WordBits /* depth??? */
+  7 /* depth??? */
 );
```

But why does that work?
And why do we need 7 here when `seL4_WordBits` worked before when we were doing the `seL4_CNode_Mint`?
To answer that, we need to talk about ~~[parallel universes]~~ CSpace addressing.

[parallel universes]: https://youtu.be/kpk2tdsPh0A?t=632

# A primer on CSpace addressing work

In seL4, capability slots in CNodes are addressed via CSpaces, analogous to how memory in pages/page tables are addressed via a VSpace.
However, unlike VSpaces, which have a very rigid architecture-dependent structure, CSpaces are an seL4 construct and are much more flexible.
This also means they're much more complicated, and the seL4 manual spends quite a number of words and diagrams explaining it.
Firstly, you need to grasp two things:

- CNodes (equivalent to both pages and page tables) can be any power-of-two size
- CNodes can contain other CNodes, and you can do an indirect lookup through both, like with a multi-level page tree

These two means that whenever you address something in a CSpace (which is just a particular CNode to start your search), you also need to specify how many bits wide your address it.
This is so that seL4 can distinguish between you referring to a particular CNode capability, or something inside it, which is "deeper" in the CSpace and requires more bits to lookup.

<!--TODO diagram-->

Another feature of CNodes is that they can be sparse through the use of a *guard*, which is modified through the same was as Endpoint badges.
This allows a CNode to pretend it's larger and requires more bits of addressing when doing CSpace lookups.
For example, a CNode with 128 slots (7 bits) can pretend it is actually a full 64 bits by setting a guard on the CNode capability.

In fact, this is what was happening here!
When we were Minting the process's root CNode into itself, we were accidentally resetting the guard to 0 and making it 7 bits deep instead of a full 64 bits.
So, what we should've been doing was using `seL4_CNode_Copy`, which does the same thing but preserves the guard, making it appear the full `seL4_WordBits` deep:

```diff
-seL4_CNode_Mint(
+seL4_CNode_Copy(
   /*_service*/   proc->root_cnode,
   /*dest_index*/ 2,
   /*dest_depth*/ seL4_WordBits,
   /*src_root*/   cspace, /* OS task's own cspace */
   /*src_index*/  proc->root_cnode,
   /*src_depth*/  seL4_WordBits,
   /*rights*/     seL4_AllRights
   /*rights*/     seL4_AllRights,
-  /*badge*/      0
 );
```


# How to actually do a cap transfer

Firstly copy the task's CSpace root CNode into itself so that it can be referenced by the task itself.
You can also Mint the capability, but be aware that this changes the CNode capability's guard and can cause the transfer to fail.

Then, before the IPC call, call `seL4_SetCapReceivePath` with the following arguments:

1. The CNode you want received caps to be sent to
This is usually the process's own CSpace, but you need to be given this explicitly, as explained earlier.
2. An unoccupied CPtr addressed in that CNode that you want the received cap to go.
3. The depth of the target CSpace, usually `seL4_WordBits`.
Often `seL4_WordBits`, but having this incorrect will cause the operation to silently fail (which is what happened to us)!

If you've done everything correctly (and permissions are also right), you'll be able to send capabilities over endpoints!
