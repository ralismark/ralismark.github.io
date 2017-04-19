---
layout: post
title: School Proxy
tags: school networking
---

In the previous post, I mentioned the school proxy. Today, I'll reveal how
broken and shifty it actually is. It's quite surprising that something made by
the government can be so insecure.

<!--more-->

Let's get right into it:
 1. No encryption of login credentials!!!
 2. Does not work on Linux :(
 3. Just plain doesn't work sometimes

$netsec alerted me to #1, which I did confirm afterwards. The proxy required
your account authentication details, which is needed to provide different levels
of access restrictions (e.g. allowing teachers to access YouTube). In a normal
system, these would be encrypted (no plain text passwords ever!), but not this
one. They are send using basic proxy authentication, which does not encrypt your
passwords. Because of this, $netsec once accidentally got a number of peoples'
passwords when he was packet sniffing. Yes, accidentally.

A while ago, I was dual booting Linux on my old laptop (now deprecated). I tried
setting up the proxy on Linux, which by itself is already a bit harder than
Windows. After some analysis, it turned out that the proxy was a RADIUS proxy.
Even after (hopefully) properly configuring it, Linux was still unable to
connect. This was probably contributed to by the 3rd issue.

Quite commonly, the internet was unavailable due to issues with authentication
somewhere. And being the local tech support guy, this results in me having to
try and fix people's internet connection. Usually, this involves just setting
the proxy locally, but once in a while, things just don't work. Additionally,
there are periods of time (minutes to hours) where the internet just doesn't
work for anyone.

It's quite frustrating, to say the least.
