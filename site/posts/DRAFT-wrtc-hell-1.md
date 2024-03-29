---
layout: post
title: WebRTC Hell - First Steps
excerpt: "How to connect"
date: 2018-02-20
tags:
reason: wip old
---

Since its release in 2011 (!), WebRTC has changed quite a bit, though with iffy browser support and some poor design decisions.
However, it exists as the only way (right now) to do peer-to-peer browser communication.
And it's a pain to understand if you only want bidirectional data transfer, since most introductions focus on media transmission.
Not this one though.

<!--more-->

As I've explained, the only way right now to do direct peer-to-peer communication is with WebRTC.
Normally, WebRTC is used for AV communication, such as video calls.
But, you can do direct, raw data communication with Data Channels.
But before you can do that, you need to connect to each other.

Say you have 2 browser client, Alice and Bob.
With WebRTC, one client needs to connect to the other.
Here, Alice will initiate the connection and Bob will connect to Alice.

# The API

To start, both Alice and Bob need to create an RTCPeerConnection.

```js
// in their corresponding browsers
let pc = new RTCPeerConnection(servers);
```

> [The argument `servers`][1] describes the ICE servers to use.
> There are plenty of articles on this elsewhere.

[1]: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/RTCPeerConnection

At this point, Bob waits for Alice to create a connection.
Before doing so, Alice needs to [create a data channel][2].
Not sure why this needs to be done before actually connecting, but it is.

[2]: https://developer.mozilla.org/en-US/docs/Web/API/RTCPeerConnection/createDataChannel

```js
// Alice:
let dc = pc.createDataChannel('dc')
```
