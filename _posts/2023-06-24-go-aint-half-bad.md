---
layout: post
title: "Go Ain't Half Bad"
tags:
excerpt: "Reflections after a year of using Go"
---

I learnt Go in early 2022 from [blog posts about Go's issues](https://fasterthanli.me/tags/golang).

And now I've been reading and writing Go for a year, and honestly, they were pretty overblown.

Sure, Go's got its fair share of issues.
`nil`s have bitten me multiple times, in the form of maps, lists, and struct members that I forget to initialise.
I curse the [channel axioms](https://dave.cheney.net/2014/03/19/channel-axioms) every time I want to get the writer to a channel to stop.
And the uppercase-lowercase for access control still feels like a very unusual choice.

But as someone that's writing service code that would run on internal Linux boxes, a lot of the sharp edges I heard of haven't really been an issue.
And there's plenty of really great things about Go!

# Simplicity

One thing that I've come to really appreciate is the simplicity of all of Go -- it gets out of the way of what you want to do as much as it can.
This is probably the biggest difference with Rust, and it's this aspect that I think is one of the biggest weaknesses of Rust.

Take, for example, Go's way of doing modules.
Everywhere, modules are identified by a URL, which indicate what Git repo they're from, and which directory inside that repo holds the source files.
This includes when you're doing what would be relative imports!
And it's honestly pretty genius with how easy it is to reason about -- no more issues with relative imports that plague e.g. Python, and no need to manage a global package registry.
It's also so easy to replace a dependency with another repo or a local directory, or lookup the actual implementation of a module.

Having a garbage collector, and a really simple and predictable syntax, also makes it really easy to avoid getting bogged down when doing complex things.
At work, I had a component which involved passing multiple functions to a method.
In turn, that method involved spawning and orchestrating several goroutines, some invoking the functions that got pass with channel, other waiting on even more channels, before waiting for everything to finish.
I don't think I'd come up with this in any other language, but in Go it was really reasonable after a bit of planning.

# Concurrency

One of Go's most strongest areas is how it does concurrency.
Having channels as _the_ basic concurrency primitive instead of shared memory & synchronisation, along with its mantra "do not communicate by sharing memory; instead, share memory by communicating", have fundamentally changed how I think about concurrency.
Message-passing is seriously so much nicer to think about than juggling mutexes[^mutex], and combined with `select` it leads you towards doing things the [actor model](https://en.wikipedia.org/wiki/Actor_model) way -- controlling resources using processes that allow (synchronised) access via message-passing.

[^mutex]: Or mutices :)

(Plus, message-passing is also more way compatible with distributed system over a network (or funky cache-incoherent supercomputers), where shared memory isn't even possible!)

This way of thinking also helps a bunch outside of Go!

When I was working on [an async Rust project](https://github.com/elkowar/eww/pull/743), needing to think about how lifetimes & ownership interacted with how async worked in Rust was quite a challenge.
I struggled a lot with figuring out how to have an object with async methods, and have tasks using this object to be cancelled when the object got cancelled -- a bit like [scoped threads](https://rust-lang.github.io/rfcs/3151-scoped-threads.html).
So much so that I would take quite a break from this project[^burnout].
When I came back to it, it was actually thinking about how I would do this in Go, that led me to a really clean solution -- using the actor model i.e. a single task with a big select.

[^burnout]: Mostly because I didn't have time to, but this framing is more dramatic :)

# Other Things

Another really strong area of Go is its tooling -- I'm legitimately spoiled by how well `gprof` and `gopls` work.
But I'm not going to go much into those.

There's still a lot of areas of Go I didn't touch much.
Generics is the main one that stands out in my mind -- I never really encountered a usecase that I couldn't achieve without reflection or existing language facilities, and managed completely avoided interacting with them.
I also had only limited exposure to unit tests, my experience of which was slightly frustrating due to how bare-bones the testing library was.

But yeah, despite all the press about Go's issues, it's honestly not that bad.
