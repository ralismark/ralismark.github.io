---
layout: post
title: "Flashy Protocols and Empty Promises"
excerpt: "An observation about fancy technologies"
date: 2023-07-25
tags:
reason: wip
---

- there's this trope
- it happens in crypto
- it kinda makes sense in context
- bluesky kinda has this as well which is why is feels sus
- it might not be a bit deal
- conclusion: yeah, there was this trope, maybe it means something maybe it doesn't



There's this thing I see a lot of in cryptocurrency & blockchain spaces.
Projects that have overly complex technology/algorithms, promising things like "decentralisation" or "protection from sybil attacks" or "fraud proofs", among other guarantees.
However, looking into them, they feel more and more like just a facade meant to give the appearance of soundness and security, rather than actually, demonstrably, providing some useful functionality.
Often times, they're just not used, or even not implemented, instead deferred to the future.

.. admonition:: me/say

	I just wanna make a point that I don't support cryptocurrency and blockchain community.
	It's pretty much all fraud, scams, insecurity, and other things to make you lose your money, and that's not even getting into the environmental problems and the gross misapplication of tech to non-technical issues.

# What This Looks Like

As an introductory example, we'll have a look at [the Arbitrum blockchain](https://docs.arbitrum.io/intro/).
It was launched in mid 2021, and now has reportedly several billion USD worth of assets on it (citation needed), which makes it a notable player in the crypto ecosystem, though nowhere as big as bitcoin/ethereum (citation needed).

One idea that's very foundational to the crypto space is that of _decentralisation_ -- that no individual or small group of actors should ever possess enough power to disrupt normal financial operation.
You can see this via the proof-of-work consensus mechanisms present in Bitcoin and (pre-[Paris-hardfork](https://ethereum.org/en/roadmap/merge/)) Ethereum, where security is provided by the difficulty and cost of getting enough computing power to become a majority.
Importantly, even the creators should not have absolute power over any part of the system.
(Nowadays, proof-of-stake is more common, where security is assured by having many actors lock up some money (usually the blockchain's own token) that gets taken away if they do anything naughty.
However, when distributing tokens, blockchains developers usually set aside a large amount of token for themselves, essentially reserving themselves a good chunk of the voting power...)

# The Devil's In The Details

One important component of Arbitrum is the Sequencer, which is responsible for collecting and ordering the transactions.
If this is compromised, users must instead apply transactions via a much more complex and slow (and likely not well tested) route involving Ethereum.
The ability to reorder transactions is also actually really powerful -- with it you can insert your own transaction before and after users' ones and manipulate prices to earn risk-free money at the expense of the user, and cause other disruptions.
As such, you probably want this to be somewhat decentralised to mitigate risk.
However:

> **Current status: Centralized.**
>
> The Sequencers for both Arbitrum One and Arbitrum Nova are currently maintained by the Arbitrum Foundation.
> Governance currently has the power to select new Sequencers.
>
> -- [The state of Arbitrum's progressive decentralisation](https://docs.arbitrum.foundation/state-of-progressive-decentralization#3-sequencer-ownership)

Not great.

If we trust the Arbitrum Foundation to be somewhat trustworthy this is not too big of a deal, but it is still a central point of failure that would require big shifts in the Arbitrum ecosystem to work around if compromised.

This is one way in which the system may not be as trustworthy as it appears -- subtle details where the creators still retain a lot of control.

TODO include this link & quote somewhere https://docs.arbitrum.io/inside-arbitrum-nitro/#if-the-sequencer-is-malicious

# Decoy Technology

Another way is when features the ecosystem advertises depends on mechanisms that are given barely any care and consideration.
In Arbitrum's case, this is those fallback mechanisms -- .
They're extremely over-engineered (I'll talk about this separately in a bit), spanning a great number of components and many, many pages of documentation that honestly go over my head.


Another blockchain, Harmony, advertises better throughput through having multiple shards -- essentially parallel blockchains that can interact with each other.
In theory, this distributes the load of the ecosystem, but in practice all chains but the main one are essentially never user, basically limiting the throughput to just a fraction of what it could be.

# Not-Invented-Here

Ano














In particular:

1. Decentralisation
2. Dispute resolution and fraud proofs.

The actua




# Why This Makes Sense

It's crypto.
Half the point of crypto is to gain your trust, then your money, then running away.
(The other half is getting hacked and losing your money irretrievably.)
And so, you gotta convince people, "please trust us, we pinky promise your money won't run away (this time)".




























There's a thing I see a lot of in the cryptocurrency/blockchain space.
It's when projects have overly complex technology that promise things like "decentralisation" or "protection from sybil attacks" or other security guarantees.
However, there's the sense that these are all built _for the appearance_ of these guarantees, which _in practice_ aren't actually taken advantage of or even properly implemented.

# Arbitrum

To see what I mean, let's have a look at [Arbitrum](https://developer.arbitrum.io/intro/).
It's a blockchain (basically, the foundational infrastructure that you can build more capable cryptocurrency systems on top of) that launched mid 2021, and now has reportedly several billion US dollars worth of value on it.
Its design is pretty standard for a more recent blockchain -- basically the same execution environment as the Ethereum Virtual Machine, a validator-based way of accepting transactions rather than proof-of-work, and some complicated fraud proof mechanism to theoretically stop malicious actors.
One idea that should be very foundational to the cryptocurrency space is that you should never need to trust a small group of actors.
In fact, this is the key idea behind Bitcoin and later blockchain, and is arguably their only use case[^why-decentralised] -- no individual or group of actors should ever be able to possess enough power to violate protocol guarantees.
It's been a few years, so Arbitrum would definitely have this, right?

[^why-decentralised]: There's a lot of words that can be said on the history of blockchain and why this guarantee is even enticing. From vague memories of other blog posts, I think it's rooted in distrust of government control after like the 2008 financial crisis.


[Nope](https://docs.arbitrum.foundation/state-of-progressive-decentralization#3-sequencer-ownership).

> **Current status: Centralized.**
> The Sequencers \[services that accept and process transactions\] for both Arbitrum One and Arbitrum Nova are currently maintained by the Arbitrum Foundation.

Literally a single point of failure.

And has any of the other availability or fraud proof mechanisms ever been used?

Not even once (citation needed).

Similarly is true for other blockchains (citation needed).

So what's the point of all that then?

It's all marketing.

(Add something about all the crypto hacks somewhere as empirically demonstrating that security is shit)

# Genre Conventions

Just like anything else (TODO), the crypto space has many norms and expectations.
One of these is the expectation for protocols to have a _white paper_ -- a document formatted like an academic paper that outlines the theory behind it and justifies various guarantees and design decisions.
Uniswap V2, arguably the biggest system for exchanging between cryptocurrencies, has [a white paper](https://uniswap.org/whitepaper.pdf).
[Bitcoin](https://bitcoin.org/bitcoin.pdf) and [Ethereum](https://ethereum.github.io/yellowpaper/paper.pdf) too, though the latter's is tinted yellow for some reason.
And for comparison, here's [an example of an actual academic paper](https://arxiv.org/pdf/2106.05123.pdf).
Exactly the same format, even down to the LaTeX theme.

So among all the flashy marketing with big numbers they're a bit out of place.
But they're a well-established trope of the space used to provide authenticity to the project (REWORD it's like people believing it's legit and secure).
And it's not just these artifacts, but also the way the technology is talked about (EXPAND).

Similarly is the case for all the fancy decentralisation mechanisms.
It makes a layperson think that it's well thought out and complicated for a reason, and at the same time burying the fact that there's not actually that much decentralisation.
That is, all that technology is only there for marketing.

Bluesky smelled the same.

# Bluesky's AT Protocol

I'm sure you've heard of the no-so-latest twitter clone, Bluesky.
It claims to be decentralised and support federation, just like Mastodon, Pixelfed, Lemmy, and numerous other services that form the Fediverse.
And they've laid out their bespoke protocol quite nicely in their [big documentation website](https://atproto.com/docs).
They use [DIDs](https://www.w3.org/TR/did-core/) as stable distributed identifiers, have [a whole federation architecture planned out](https://blueskyweb.xyz/blog/5-5-2023-federation-architecture), and [a data storage layer that looks surprisingly like a series of signed blocks](https://atproto.com/specs/repository).

So, with this impressive amount of protocol design, what do they actually have to show for it?

Two DID methods -- [did:web](https://w3c-ccg.github.io/did-method-web/) and did:plc.
The first no one uses, and the latter they invented[^s3].
And exactly one instance of all services.

[^s3]: And which, someone used to become [all of s3](https://chaos.social/@jonty/110307532009155432).

# Conclusion

(I have no idea how to conclude rip)
