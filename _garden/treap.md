---
layout: article
title: Deterministic Treap
noindex: true
---

Dump of my treapy research. A bunch of sources from <https://en.wikipedia.org/wiki/Join-based_tree_algorithms>.

> Note: [Finger Trees](https://en.wikipedia.org/wiki/Finger_tree) exist and mostly supersede the work here

# Weight-Balanced Trees

I'll be using *weight* to refer to the number of nodes in a tree. We'll then use the alternate balance criteria of

$$
|T.left| \le \beta |T.right| \ \wedge\ |T.right| \le \beta |T.left|
$$

*TODO*: figure out what values of $$\beta$$ make the resulting tree balanced.

We can immediately determine the weight of a join operation's output, so analysis is a bit easier. Plus, we're already storing the weight in each node.

*TODO*: figure out how these trees actually work, since wikipedia doesn't actually provide a balancing algo. [^hirai2011] has some good info. Main way seem to be to do either a single or double rotation.



# Parallel Ordered Sets Using Join

Ref: [^blelloch2016] and [^yihan2019]. The first is a shorter version of the latter.

This paper goes through a lot of balancing schemes and gives proofs for the algorithms.

# Implementing Sets Efficiently in a Functional Language

Ref: [^adams1992]

This describes how to have join3 and split on a weight-balanced tree (which they call a bounded balanced tree).

Instead of the usual $$\alpha$$-based balancing criterion of

$$
|T.left|, |T.right| \ge \alpha |T|
$$

they instead use $$w$$ and require that, if either subtree has size greater than 1,

$$
|T.left| \le w |T.right| \ \wedge\ |T.right| \le w |T.left|
$$

As an additional note, we can kinda convert the $$\alpha$$-based criterion back to $$1+y \le x \cdot (1-\alpha)/\alpha$$.

$$\alpha$$ (used in the same way as the original criteria) is used as a parameter into the algorithm to determine when to rotate.

For tree manipulation, they define `T'(v, l, r)` as a "join back up after a single-node insert or delete". It gets used a lot. Seems like it's derived from regular weight-balanced trees

Their join2 does the classic thing of basing itself off of join3, which I'm not that much a fan of. But the use of $$w$$ is a cool way of making analysis easier.

<!-- bibiography -->

[^adams1992]: Adams, Stephens (1992), *Implementing Sets Efficiently in a Functional Language*, [CiteSeerX:10.1.1.501.8427](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.501.8427)
[^blelloch2016]: Blelloch, Guy; Ferizovic, Daniel; Sun, Yihan (2016), *Parallel Ordered Sets Using Join*, [arXiv:1602.02120](https://arxiv.org/abs/1602.02120)
[^hirai2011]: Hirai, Yoichi; Yamamoto, Kazuhiko (2011), *Balancing weight-banaced trees*, [doi:10.1017/S0956796811000104](doi.org/10.1017/S0956796811000104), <https://yoichihirai.com/bst.pdf>
[^yihan2019]: Sun, Yihan (2019), *Join-based Parallel Balanced Binary Trees*, <https://www.cs.cmu.edu/~yihans/papers/thesis.pdf>
