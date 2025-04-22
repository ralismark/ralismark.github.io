---
layout: post
title: Thoughts on seL4
excerpt: After a term of getting deep into seL4
date: 2022-06-17
tags:
---

# Limitations/Quirks

A lot of this was just struggling with seL4 until we got a better understanding of things and learned to not swim against the current.

1. Capped derivation depth

	This almost certainly has a good reason (Worst Case Execution Time, verification costs), but has meant it's hard to revoke derived caps you have that you've minted to others.

	One challenge we had was how to handle clients closing services (e.g. files).
	We wanted to revoke the endpoint so that the client couldn't keep using it, but without an capability per client, we couldn't actually revoke.

	Honestly, this could be extended to limits on things:

	- Dimension of notifications
	- Number of caps you can transfer (i.e. at most 1)

2. No select() for Endpoints

	In our project we've had to use badges for this, which is a bit annoying.
	We have a single-threaded OS that acts as if it is the server for a lot of endpoints, and we do this by stuffing both a service id and other metadata in the badge bits.
	However, a client that isn't the originator of the endpoints doesn't have this workaround.

	Notifications has select()-ish, except it's limited in number.

3. Cap transfer is way too hard

	I spend way too long figuring this out.
	For a while we had the workaround of the client passing the CPtr slot they wanted us to mint to, and the OS minting into it.
	But this doesn't scale to multiple clients.

4. No reference counting

	After handing out endpoints to users, there's no easy way to know if you're the only remaining holder (and to clean up resources).
	The solution to this was to have an explicit close.

# Ideas I liked

1. Capability based security

	There's honestly not much to say about it -- capabilities are the best way of handling access management and information flow.

2. Letting the user manage kernel memory

	The seL4 kernel sets aside a fixed amount of memory for itself, then gives the rest to the userland process.
	Then, memory required for userland processes manually handed _back_ to the kernel.
	This means that the kernel doesn't mandate a memory management policy!

4. CSpace tree

5. Policy freedom

6. Time donation (MCS configuration only)

<!--Imported from the cap transfer article-->

# An aside on capabilities

<!--TODO-->

The seL4 Manual is quite in-depth, but while knee-deep in capability things, there were a number of details that weren't that clear:

- How badges actually worked with the capability derivation tree, particularly it being limited depth.
	This includes weird scenarios like trying to modify the badge of a derived and badged capability -- what happens?
- How revoking/deleting a CNode affected the capabilities inside of it.
	We had some crazy ideas about using it as a "lifetime"/"garbage collection" tool, but we never attempted them since we ended up never having a use for them.
