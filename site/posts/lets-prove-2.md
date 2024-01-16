---
layout: post
title: "Let's Prove #2: An Existential Crisis"
excerpt: Finding a mishap in translating an Exists into Isabelle
date: 2023-06-23
tags: isabelle
---

Last time, we dove right into the process of proving Alpern and Schneider's Theorem.
However, the process there was quite trimmed down from the actual proof wrangling journey I went through.
One thing I omitted was a mistake I made in my definition of `limit_closure`.
I was considering including it in previous post, but it disrupted the flow too much so I've relegated it to this followup.
So, let's rewind back, just before I went into the topology bits.

# Alternate History

Instead of the correct definition of

```isabelle
definition limit_closure :: "'s property ⇒ 's property"
  where "limit_closure P ≡
    λσ. ∀n. ∃σ'. (σ' ⊨ P) ∧ (i_take n σ = i_take n σ')"
```

I had this, with an implies instead of and after `σ' ⊨ P`.

```isabelle
definition limit_closure :: "'s property ⇒ 's property"
  where "limit_closure P ≡
    λσ. ∀n. ∃σ'. (σ' ⊨ P) ⟶ (i_take n σ = i_take n σ')"
```

The issue is that, while $\forall x \in A.\; P$ is equivalent to $\forall x.\; (x \in A) \longrightarrow P$, this translation isn't correct for $\exists$!
Specifically, $\exists \sigma' \models P.\; Q$ is not equivalent to $\exists \sigma'.\; (\sigma' \models P) \longrightarrow Q$, but instead $\exists \sigma'.\; (\sigma' \models P) \land Q$.

However, let's rewind time back to my initial theorem proving attempt, and I'll take you through the journey of finding this issue!

# Action!

I had already proven that liveness implies dense, and was just starting with `lemma dense_is_liveness: "dense P ⟹ liveness P"` when

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. dense P ⟹ liveness P
> Auto Nitpick found a counterexample for card 'a = 1:
>   Free variable:
>     P = (λx. _)((λx. _)(0 := a₁) := False)
>   Skolem constant:
>     ??.liveness.α = []
> ```

Huh?

Clearly, Nitpick isn't happy with _something_, and I hadn't fully convinced myself of this lemma either.
Assuming the formal methods literature is sound, it's either that Nitpick found a counterexample that isn't real[^nitpick-wrong], or more likely, I messed up something in my definitions.
Let's follow that second theory.

[^nitpick-wrong]: I vaguely remember this being possible?
	I have really low confidence in this claim though.
	Let me know if you have stronger evidence either way.

Nitpick's counterexample notation using function updates is a bit hard to read, but what it's saying is that the theorem is false for the property "the first state is not $a_1$".
This didn't seem like a liveness property nor dense, until I noticed the `card 'a = 1`, which I'm guessing stands for cadinality.
That is, $a_1$ is the only value of its type, meaning the counterexample is actually just the False property.

(I'm not sure what Skolem constants are, so let me know if you do!)

However, False, being impossible to satisfy, should be neither liveness nor dense!
So let's try something.

```isabelle
lemma "dense pFalse"
  sledgehammer
```

> Sledgehammer
> ```
> spass found a proof...
> vampire found a proof...
> spass: Try this: by (simp add: limit_closure_def) (4 ms)
> vampire: Try this: by (simp add: limit_closure_def) (7 ms)
> zipperposition found a proof...
> e found a proof...
> e: Try this: by (simp add: limit_closure_def) (6 ms)
> zipperposition: Try this: by (simp add: limit_closure_def) (16 ms)
> QED
> ```

Yeah, that clearly shouldn't be happening.
I initially thought my definition of dense was wrong, but after some more double-checking I noticed the existential implication issue in my limit closure definition.
Fixing that satisfied Nitpick, and surpringly didn't break my proof for `liveness_is_dense: "liveness P ⟹ dense P"`!

# Exeunt

Well, lesson learned!

If you came here from the previous post, it resumes from [this section](lets-prove-1#dense-is-liveness).
