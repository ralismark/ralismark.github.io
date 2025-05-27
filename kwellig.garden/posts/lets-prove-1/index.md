---
layout: post
title: "Let's Prove #1: Safety, Liveness, Alpern and Schneider"
excerpt: "theorem \"Every property is the intersection of a safety and a liveness property\""
date: 2023-06-07
tags: isabelle
---

A couple of years ago I took [COMP4161 "Advanced Topics in Software Verification" at UNSW](https://www.handbook.unsw.edu.au/undergraduate/courses/2023/comp4161), which taught how to use the [Isabelle proof assistant] to prove theorems and eventually formally verify C programs.
I had so much fun in that course, but unfortunately formally proving theorems isn't something that is widely applicable these days, so I haven't had much chance to do more.

[Isabelle proof assistant]: https://en.wikipedia.org/wiki/Isabelle_(proof_assistant)

However, I'm currently doing [COMP3151 "Foundations of Concurrency" at UNSW](https://www.handbook.unsw.edu.au/undergraduate/courses/2023/comp3151).
While the main portion of the course is for formally reasoning about concurrent programs, it began with reasoning about single-threaded program via the different states they go through, and the properties these sequences of states can satisfy.
A major theorem in this area is Alpern and Schneider’s Theorem:

.. sparkle::

	Every property is the intersection of a safety and a liveness property.

I've seen this theorem alluded to in a bunch of other computing courses, but this is the first time I've been properly introduced to it.
And so, I'm gonna have some fun and take you on a journey to formally proving that!

.. admonition:: me/warn

	I'll be assuming a basic understanding of (first order) logic and set theory.
	We'll also be diving right into Isabelle, so if you're looking for an introduction, this isn't the place unfortunately.

# Foundations

First of all, let me explain what that even means:

- A **behaviour**, also called a program trace, is an infinite sequence of all the states that a program goes through during execution[^halt].
	This includes, for example, the value of variables, though what states actually are doesn't really matter -- they just are abstract equality-comparable mathematical objects.
- A **property** is a predicate on behaviours, i.e. a function from behaviours to bool.
- A [**safety** property](https://en.wikipedia.org/wiki/Safety_and_liveness_properties#Safety) is, colloquially, is one that requires that "nothing bad happens", e.g. "the program uses more than 100MB of memory", "when the program exits, it has printed `hello world`", "the program never halts".
- A [**liveness** property](https://en.wikipedia.org/wiki/Safety_and_liveness_properties#Liveness) is, colloquially, one that requires that "something good eventually happens", e.g. "the program halts", "all requests are eventually responded to", "the state $s$ occurs at least once".

[^halt]: A halting program would have a finite trace, but we usually represent that by having the last state repeat forever.

Thus, Alpern and Schneider's Theorem states that, for all properties $P$, you can find two properties, a safety one $P_S$ and a liveness one $P_L$, such that $P$ is satisfied by a behaviour if and only if it satisfies both $P_S$ and $P_L$.
This was proven in their 1984 paper ["Defining Liveness"][alpern1984], and we'll follow a similar approach to what's described there.

[alpern1984]: https://www.cs.cornell.edu/fbs/publications/DefLiveness.pdf

Now that the basics are out of the way, let's boot up Isabelle!

.. admonition:: me/say

	Unfortunately, there's no syntax highlighting for Isabelle right now :(.
	[It's been implemented upstream](https://github.com/rouge-ruby/rouge/pull/1682), but I'm still on an old version of Jekyll and haven't figured out how to update that dependency.

# Working with Infinite Lists

While Isabelle comes with a theory for finite lists, it doesn't have one for infinite lists, so we'll need to make our own!
We'll represent infinite lists as functions from naturals to the elements -- the first state is $\sigma\ 0$, the second is $\sigma\ 1$, and so on.

```isabelle
type_synonym 's behaviour = "nat ⇒ 's"
```

For functions manipulation these, we'll mirror the names in [an existing theory I found](https://www.isa-afp.org/browser_info/Isabelle2011/HOL/List-Infinite/index.html), and copy their cute `a ⌢ b` notation for `i_append`.

```isabelle
(* get the behaviour from the nth state onwards *)
definition i_drop :: "nat ⇒ 's behaviour ⇒ 's behaviour"
  where i_drop_def[simp]: "i_drop n σ ≡ λk. σ (n + k)"

(* get the first n states of the behaviour *)
definition i_take :: "nat ⇒ 's behaviour ⇒ 's list"
  where i_take_def[simp]: "i_take n σ ≡ [σ i. i ← [0..<n]]"

(* prefix a behaviour with a (finite) list of states *)
definition i_append :: "'s list ⇒ 's behaviour ⇒ 's behaviour" (infixr "⌢" 65)
  where i_append_def: "xs ⌢ σ ≡
    λn. if n < length xs
      then xs ! n
      else σ (n - length xs)"
```

We'll add supplementary theorems about them later, but this is enough for now.

For properties, I defined those as predicates.
A decent amount of literate defines them as sets (which are equivalent), and that gets reflected in wording as well -- that's why Alpern & Schneider's statement of their theorem uses _intersection_.

```isabelle
type_synonym 's property = "'s behaviour ⇒ bool"
```

# Syntax Sugar

I took a bit of a detour at this point to try and get some nice syntax for the things we're working with.
This wasn't done much in COMP4161 so I was initially a bit lost, and so headed to my local search engine.
Looking online, I was led to [§8.2 of The Isabelle/Isar Reference Manual (IIRM)](https://isabelle.in.tum.de/doc/isar-ref.pdf#section.8.2), plus all the `syntax`, `notation`, `abbreviation`, and so on in the subsequent sections that went entirely over my head.
But after a bunch of trial and error I managed to make turnstile notation (i.e. "does a behaviour satisfy this property") with

```isabelle
abbreviation(input) models :: "'s behaviour ⇒ ('s behaviour ⇒ bool) ⇒ bool" (infix "⊨" 15)
  where "models σ p ≡ p σ"
```

Here, `abbreviation` ([IIRM §5.4](https://isabelle.in.tum.de/doc/isar-ref.pdf#command.abbreviation)) creates new syntax without defining any new terms, unlike `definition` -- a bit like C's preprocessor macros.
This allows us to write `σ ⊨ P`, and will make Isabelle show all function application involving `behaviour` using `⊨`.
Unfortunately, the latter isn't desirable as it is too eager and will happily change forall into `P ⊨ All`.
This is why I specified `(input)`, which only does the desugaring without modifying the rendering of statements while we're proving things.

Additionally, I discovered you can directly overload syntax, so we can just use the standard logic operators between properties (with full sugar)!

```isabelle
abbreviation pNot :: "'s property ⇒ 's property" ("¬_" [40] 40)
  where "pNot p ≡ λσ. ¬(p σ)"

abbreviation pConj :: "'s property ⇒ 's property ⇒ 's property" (infix "∧" 35)
  where "pConj p q ≡ λσ. (p σ) ∧ (q σ)"

abbreviation pDisj :: "'s property ⇒ 's property ⇒ 's property" (infix "∨" 30)
  where "pDisj p q ≡ λσ. (p σ) ∨ (q σ)"

abbreviation pImp :: "'s property ⇒ 's property ⇒ 's property" (infixr "⟶" 25)
  where "pImp p q ≡ λσ. (p σ) ⟶ (q σ)"
```

Though unfortunately you regularly get syntax ambiguity warnings:

> Ambiguous input⌂ produces 2 parse trees:
>
> - ```escape
> 	("<!<b><i>const</i></b>!>Pure.eq"
> 	  ("_applC" ("_position" pNot) ("_position" p))
> 	  ("_lambda" ("_position" b)
> 	    ("<!<b><i>fixed</i></b>!>pNot"
> 	      ("_applC" ("_position" p) ("_position" b)))))
> 	```
>
> - ```escape
> 	("<!<b><i>const</i></b>!>Pure.eq"
> 	  ("_applC" ("_position" pNot) ("_position" p))
> 	  ("_lambda" ("_position" b)
> 	    ("<!<b><i>const</i></b>!>HOL.Not"
> 	      ("_applC" ("_position" p) ("_position" b)))))
> 	```
>
> Fortunately, only one parse tree is well-formed and type-correct,
> but you may still want to disambiguate your grammar or your input.

We know that our new syntax isn't ambiguous with default HOL operators once you consider the types, so we can whisk these warnings away with this, from [IIRM §8.4.5](https://isabelle.in.tum.de/doc/isar-ref.pdf#attribute.syntax-ambiguity-warning):

```isabelle
(* since we're overloading a bunch of logic operators *)
declare [[syntax_ambiguity_warning = false]]
```

And finally, True and False.

```isabelle
abbreviation pTrue :: "'s property"
  where "pTrue ≡ λ_. True"

abbreviation pFalse :: "'s property"
  where "pFalse ≡ λ_. False"
```

Okay, we're now ready to define safety and liveness!

# Safety and Liveness

In ["Defining Liveness"][alpern1984], Alpern and Schneider proposes the mathematical definitions for safety and liveness that are commonly used today.
Their definitions are that a property $P$ is a safety one if and only if

$$
(\forall\sigma: \sigma \in S^\omega : \sigma \not\models P \implies (\exists i: 0 \le i : (\forall \beta: \beta \in S^\omega : \sigma_i \beta \not\models P))).
$$

The notation there is a bit quirky, so let's convert the definition to Isabelle.

```isabelle
definition safety :: "'s property ⇒ bool"
  where "safety P ≡ ∀σ. ¬(σ ⊨ P) ⟶
    (∃i. ∀β. ¬(i_take i σ ⌢ β ⊨ P))"
```

The intuition behind this definition is that, if a behaviour violates a safety property, there must be an identifiable point (index $i$) where the violation happens, and nothing you do after that (behaviour $\beta$) can then un-violate that property.

Alpern and Schneider then define liveness as properties $P$ where

$$
(\forall \alpha : \alpha \in S^* : (\exists \beta : \beta \in S^\omega : \alpha \beta \models P)).
$$

This is a bit less of a mouthful than safety.
In Isabelle it's

```isabelle
definition liveness :: "'s property ⇒ bool"
  where "liveness P ≡ ∀α. ∃β. α ⌢ β ⊨ P"
```

and says that for all finite program traces, there can always be some future behaviour satisfy the liveness property become satisfied.
In essence, it's impossible to show that a behaviour has violated a liveness property just from a finite number of states.

# Mugs and Donuts

The way that both ["Defining Liveness"][alpern1984] and COMP3151 approach proving Alpern and Schneider's Theorem is via the topological concepts of [limit points](https://en.wikipedia.org/wiki/Accumulation_point), and [closed](https://en.wikipedia.org/wiki/Closed_set)/[dense](https://en.wikipedia.org/wiki/Dense_set) sets.
Now, this isn't really coffee-mug-and-donut topology, and this route invokes a bunch of additional maths involving metric theory[^topo].
We'll follow COMP3151 and sidestep this using an alternate but equivalent formulation:

[^topo]: If you want the metric-theoretic topology way: Define the distance metric $d(x, y)$ as $2^{-k}$, where $k$ is the length of the longest common prefix of $x$ and $y$.
	Then, take the regular (topological) definitions of limit points, closed sets, and so on.

.. sparkle::

	The _limit closure_ of a property $P$ is another property $\bar{P}$ that accepts all behaviours whose finite prefixes are all a prefix of some behaviour accepted by $P$.

Or, in math notation,

$$
\sigma \models \bar{P} \iff \forall n \in \mathbb{N}.\; \exists \sigma' \models P.\; \left(\forall i < n.\; \sigma_i = \sigma'_i\right),
$$

which I entered as

```isabelle
definition limit_closure :: "'s property ⇒ 's property"
  where "limit_closure P ≡
    λσ. ∀n. ∃σ'. (σ' ⊨ P) ∧ (i_take n σ = i_take n σ')"
```

With this, there's two basic theorems for limit closure:

1. $P$ is a subset of its limit closure.

	```isabelle
	lemma limit_closure_subset[intro]: "σ ⊨ P ⟹ σ ⊨ limit_closure P"
	  unfolding limit_closure_def i_drop_def
	  by auto
	```

	I labelled it as an `[intro]` rule ([IIRM §9.4.2](https://isabelle.in.tum.de/doc/isar-ref.pdf#attribute.intro)) to make automated methods (e.g. `auto`) try it.

2. The limit closure operation is idempotent -- repeating it does nothing and should be removed, hence `[simp]`.
	```isabelle
	lemma limit_closure_idem[simp]: "limit_closure (limit_closure P) = limit_closure P"
	  unfolding limit_closure_def i_take_def
	  by fastforce
	```

Next up we define what it means for a property to be [limit closed](https://en.wikipedia.org/wiki/Closed_set) and [dense](https://en.wikipedia.org/wiki/Dense_set):

1. **Limit-closed** properties are equal to their limit closure.
	Equivalently but more usefully, limit-closed properties have all behaviours satisfying the limit closure also satisfy P.

	```isabelle
	definition limit_closed :: "'s property ⇒ bool"
	  where "limit_closed P ≡ (limit_closure P) = P"
	
	lemma limit_closed_forall[simp]:
	    "limit_closed P = (∀σ. (σ ⊨ limit_closure P) ⟶ (σ ⊨ P))"
	  unfolding limit_closed_def
	  by auto
	```

	`limit_closed_forall` here is basically the reverse direction of `limit_closure_subset`.

2. **Dense** properties have their limit closure satisfied by all properties.

	```isabelle
	definition dense :: "'s property ⇒ bool"
	  where "dense P ≡ (limit_closure P) = pTrue"
	
	lemma dense_forall[simp]: "dense P = (∀σ. σ ⊨ limit_closure P)"
	  using dense_def by auto
	```

# Four Big Lemmas

There's only two theorems we need to show before we can attack Alpern and Schneider’s Theorem, and they are that

.. sparkle::

	Safety properties are exactly the limit-closed ones

and

.. sparkle::

	Liveness properties are exactly the dense ones

However, it turns out that proving these directly _seriously_ involved, so we'll split up the two implication directions for each, giving us four lemmas.

```isabelle
lemma safety_is_closed: "safety P ⟹ limit_closed P"
  sorry

lemma closed_is_safety: "limit_closed P ⟹ safety P"
  sorry

theorem safety_closed[simp]: "safety P = limit_closed P"
  using closed_is_safety safety_is_closed by blast

lemma liveness_is_dense: "liveness P ⟹ dense P"
  sorry

lemma dense_is_liveness: "dense P ⟹ liveness P"
  sorry

theorem liveness_dense[simp]: "liveness P = dense P"
  using dense_is_liveness liveness_is_dense by blast
```

.. admonition:: me/say

	Strictly, we don't actually need the "safety implies limit-closed" and "liveness implies dense" directions, but we'll still prove those for fun.

	Also, while looking at the IIRM I discovered that in addition to `[simp]`, `[intro]`, `[elim]`, and so on, there's also `[iff]` which, uh, "declares logical equivalences to the Simplifier and the Classical reasoner at the same time".
	I'm not really sure what that means though...

# Liveness Is Dense

The definition of liveness and denseness is a bit simpler, so we'll tackle the lemmas with those first.
First step, unfold the definitions and do some basic tidying

```isabelle
lemma liveness_is_dense: "liveness P ⟹ dense P"
  unfolding liveness_def dense_forall limit_closure_def
  apply (intro allI)
```

I didn't realise it, but you can actually unfold with any theorem of the right shape -- here I'm doing it with `dense_forall` -- and not just the original definitions!
This leaves us with

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀σ n. ∀α. ∃β. P (α ⌢ β) ⟹
>            ∃σ'. P σ' ∧ i_take n σ = i_take n σ'
> ```

Alrighty, our goal here is to show that there's some $\sigma' \models P$ whose first $n$ states are the same as $\sigma$.
Our only assumption is the expanded liveness property, which, after a bit of interpretation, is saying that for any finite sequences of states $\alpha$, there's some subsequent behaviour $\beta$ that makes $\alpha \frown \beta$ satisfy $P$.
So let's instantiate that assumption with $\alpha = i\_take\ n\ \sigma$

```isabelle
  apply (erule_tac x="i_take n σ" in allE)
  apply (erule exE)
```

and fulfil the existential with $\sigma' = (i\_take\ n\ \sigma) \frown \beta$

```isabelle
  apply (rule_tac x="(i_take n σ) ⌢ β" in exI)
```

leaving us with

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀σ n β.
>        P (i_take n σ ⌢ β) ⟹
>        P (i_take n σ ⌢ β) ∧
>        i_take n σ = i_take n (i_take n σ ⌢ β)
> ```

The first part of that conjunction is simply our assumption, while the latter looks like it should be a basic list identity.
So let's chuck sledgehammer at it.

> Sledgehammer
> ```
> cvc4 found a proof...
> cvc4: Try this: by (simp add: i_append_def) (16 ms)
> z3 found a proof...
> z3: Try this: by (simp add: i_append_def) (12 ms)
> QED
> ```

allowing us to finish off the proof with

```isabelle
  by (simp add: i_append_def)
```

That wasn't so bad!

.. details:: Full proof of liveness_is_dense

	```isabelle
	lemma liveness_is_dense: "liveness P ⟹ dense P"
	  unfolding liveness_def dense_forall limit_closure_def
	  apply (intro allI)
	  apply (erule_tac x="i_take n σ" in allE)
	  apply (erule exE)
	  apply (rule_tac x="(i_take n σ) ⌢ β" in exI)
	  by (simp add: i_append_def)
	```

# Dense Is Liveness

Now for the other direction of this.

.. admonition:: me/say

	If you wanna see an outtake where I messed up a definition and went finding it, see [Let's Prove #2](lets-prove-2)!

```isabelle
lemma dense_is_liveness: "dense P ⟹ liveness P"
  unfolding liveness_def dense_forall limit_closure_def
  apply (rule allI)
```

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀α. ∀σ n. ∃σ'. P σ' ∧ i_take n σ = i_take n σ' ⟹
>          ∃β. P (α ⌢ β)
> ```

This time we want a behaviour accepted by $P$ that starts with $\alpha$.
Our assumption is that $P$ is dense, which we can use to generate a behaviour that starts with $\alpha$:

```isabelle
  apply (erule_tac x="α ⌢ _" in allE)
  apply (erule_tac x="length α" in allE)
  apply (erule exE)
```

and fulfill $\beta$ with the correct suffix of $\sigma'$:

```isabelle
  apply (rule_tac x="i_drop (length α) σ'" in exI)
```

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀α σ'.
>        P σ' ∧
>        i_take (length α) (α ⌢ ?uu6 α) = i_take (length α) σ' ⟹
>        P (α ⌢ i_drop (length α) σ')
> ```

It's only basic infinite list manipulation left, but unfortunately it's too much for sledgehammer --

> Sledgehammer
> ```
> No proof found
> ```

-- so we'll need to introduce some extra identities for our behaviour functions.

The first one I notice is that we have `i_take (length α) (α ⌢ ?uu6 α)` -- appending something to $\alpha$, then cutting it off again -- which should just be equal to $\alpha$.
So I'll make a theorem that's easily proven with the help of sledgehammer.

```isabelle
lemma append_inv[simp]: "i_take (length a) (a ⌢ b) = a"
  by (simp add: i_append_def map_upt_eqI)
```

We'll also get the expression `i_take (length α) σ' ⌢ i_drop (length α) σ'` -- splitting a behaviour at a point then joining the two parts together -- which should also just be $\sigma'$.

```isabelle
lemma take_append_drop[simp]: "i_take n xs ⌢ i_drop n xs = xs"
  unfolding i_take_def i_drop_def i_append_def
  by force
```

Now, back to the `dense_is_liveness`.
Sledgehammering again has all the provers yelling `metis` at us,

> Sledgehammer
> ```
> cvc4 found a proof...
> vampire found a proof...
> cvc4: Try this: by (metis append_inv take_append_drop) (15 ms)
> verit found a proof...
> vampire: Try this: by (metis append_inv take_append_drop) (24 ms)
> verit: Try this: by (metis append_inv take_append_drop) (24 ms)
> zipperposition found a proof...
> zipperposition: Try this: by (metis append_inv take_append_drop) (17 ms)
> QED
> ```

which we'll gladly take to complete our proof.

.. details:: Full proof of dense_is_liveness

	```isabelle
	lemma dense_is_liveness: "dense P ⟹ liveness P"
	  unfolding liveness_def dense_forall limit_closure_def
	  apply (rule allI)
	  apply (erule_tac x="α ⌢ _" in allE)
	  apply (erule_tac x="length α" in allE)
	  apply (erule exE)
	  apply (rule_tac x="i_drop (length α) σ'" in exI)
	  by (metis append_inv take_append_drop)
	```

And with this, we can prove that liveness properties are exactly the dense ones!

```isabelle
theorem liveness_dense[simp]: "liveness P = dense P"
  using dense_is_liveness liveness_is_dense by blast
```

# Safety Is Closed

Here's our starting point:

```isabelle
lemma safety_is_closed: "safety P ⟹ limit_closed P"
  unfolding safety_def limit_closed_forall limit_closure_def
```

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ∀σ. (¬P) σ ⟶ (∃i. ∀β. (¬P) (i_take i σ ⌢ β)) ⟹
>     ∀σ. (∀n. ∃σ'. P σ' ∧ i_take n σ = i_take n σ') ⟶ P σ
> ```

Now that's quite a mess, and the negations scare me a little.
The obvious thing is to get rid of the foralls in the goal with `allI`, and-

.. admonition:: me/say

	*psst*

Hm?

.. admonition:: me/say

	Use sledgehammer!

No way that's gonna w-

> Sledgehammer
> ```
> vampire found a proof...
> ```

You what?

> Sledgehammer
> ```
> vampire: Try this: by (metis take_append_drop) (748 ms)
> ```

Oh.

Wow.

That was so much easier than expected, but I'll take that.

.. details:: Full proof of safety_is_closed

	```isabelle
	lemma safety_is_closed: "safety P ⟹ limit_closed P"
	  unfolding safety_def limit_closed_forall limit_closure_def
	  by (metis take_append_drop)
	```

I guess the lesson from this is to always try sledgehammering.

(As it turns out, the previous lemma is also trivially discharged with a bit of sledgehammer:

```isabelle
lemma dense_is_liveness: "dense P ⟹ liveness P"
  unfolding liveness_def dense_forall limit_closure_def
  by (metis append_inv take_append_drop)
```

though with the additional lemmas we made.)

# Closed Is Safety

The final one.
Limit-closed properties are safety properties.

```isabelle
lemma closed_is_safety: "limit_closed P ⟹ safety P"
  unfolding safety_def limit_closed_forall
  apply (intro allI impI)
```

Unfortunately, sledgehammer won't be able to help-

> Sledgehammer
> ```
> e found a proof...
> e: Try this: by (metis append_inv diff_zero i_take_def length_map length_upt limit_closure_def) (97 ms)
> ```

...seriously?
Way to ruin the fun.

For the sake of content I'll make the executive decision to ignore that proof by `metis`, and instead do things more manually.
Here's what we need to do.

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀σ. ∀σ. (limit_closure P ⟶ P) σ ⟹
>          (¬P) σ ⟹ ∃i. ∀β. (¬P) (i_take i σ ⌢ β)
> ```

Notably, our assumption includes $\sigma \not\models P$, which is a bit tricky since we need to now think about what's true for behaviours _not_ satisfying a property.

When I was originally going through and proving these 4 lemmas, the extra `[simp]` rules I had at the time caused a `clarsimp` to expand it out into some monster with a bunch of negations, and I got so intimidated I `sorry`ed it and moved on to prove the big theorem at the end.

It was only at night, as I was going to bed, that I remembered with a start that I didn't actually prove this lemma!
And so, away from any pen, paper, or machine with Isabelle, I juggled mathematical objects in my mind and thought about how to remedy that.
By midnight, I had formulated a vague idea for a plan of attack.
I hurredly scribbled it into Discord before proceeding to falling asleep.

In the morning, I booted up Isabelle again.
My idea was that, because $\sigma$ _doesn't_ satisfy $P$ and hence also doesn't satisfy its limit closure, it must have some prefix that differs from all behaviours satisfying $P$.
We can then use this prefix in the definition of safety, as nothing you do after that prefix can make a behaviour satisfying $P$.

First step of this is to show that $\sigma \not\models limit\_closure\ P$, which took more steps than I expected.
Instantiating the forall with $\sigma$,

```isabelle
  apply (erule_tac x="σ" in allE)
```

we're left with

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀σ. (¬ P) σ ⟹
>          (limit_closure P ⟶ P) σ ⟹
>          ∃i. ∀β. (¬ P) (i_take i σ ⌢ β)
> ```

That second assumption is just `(σ ⊨ limit_closure P) ⟶ (σ ⊨ P)` but rewritten, and for the life of me I could not figure out how to directly combine it with `¬(P σ)` to get `¬(σ ⊨ limit_closure P)`.
And so I resorted to `case_tac`[^subgoal_tac].

[^subgoal_tac]: An alternative to `case_tac` is `subgoal_tac`.
	While `case_tac` splits the goal into two, one where a fact is true one and one where it's false, `subgoal_tac` directly creates an assumption and a subgoal for it.
	Very handy for stepping stones in longer proofs without invoking Isar!

```isabelle
  apply (case_tac "limit_closure P σ")
```

Here's what that does by the way:

> Output
> ```
> proof (prove)
> goal (2 subgoals):
>  1. ⋀σ. (¬P) σ ⟹
>          (limit_closure P ⟶ P) σ ⟹
>          limit_closure P σ ⟹
>          ∃i. ∀β. (¬P) (i_take i σ ⌢ β)
>  2. ⋀σ. (¬P) σ ⟹
>          (limit_closure P ⟶ P) σ ⟹
>          (¬limit_closure P) σ ⟹
>          ∃i. ∀β. (¬P) (i_take i σ ⌢ β)
> ```

The first subgoal is simply a contradiction that gets resolved with the simplifier[^subgoal_by], and for the second, our original assumptions aren't necessary anymore and can be removed with `thin_tac`,

[^subgoal_by]: I like doing `subgoal by` with `simp` and `auto` so that if something changes and the method stops proving the subgoal, it produces an error instead of mangling the proof state.

```isabelle
   subgoal by simp
  apply (thin_tac "σ ⊨ ¬P")
  apply (thin_tac "σ ⊨ limit_closure P ⟶ P")
```

leaving us with a very clean goal.

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀σ. (¬ limit_closure P) σ ⟹
>          ∃i. ∀β. (¬ P) (i_take i σ ⌢ β)
> ```

The next step of my midnight plan is to show that $\sigma$ has a prefix that isn't a prefix of anything satisfying $P$.
We'll do that in a separate lemma, though using the size of the prefix instead of the contents of the prefix.

.. admonition:: me/say

	It turns out that it's an full-blown iff and not just an implication, since it's pretty much just a consequence of quantifier De Morgan's.

```isabelle
lemma not_limit_closure: "(σ ⊨ ¬(limit_closure P)) =
    (∃n. ∀σ'. (σ' ⊨ P) ⟶ (i_take n σ ≠ i_take n σ'))"
  unfolding limit_closure_def
  by blast
```

Back to the lemma.
There's a couple of ways of applying this:

1. Directly substituting with `subst (asm) not_limit_closure` ([IIRM §9.2.2](https://isabelle.in.tum.de/doc/isar-ref.pdf#method.subst)).
2. Forming an meta-implication using `iffD1` then doing a forward proof step with `drule not_limit_closure[THEN iffD1]` ([IIRM §9.2.1](https://isabelle.in.tum.de/doc/isar-ref.pdf#method.drule)).
3. You can also do the same with `frule` instead ([IIRM §9.2.1](https://isabelle.in.tum.de/doc/isar-ref.pdf#method.frule)), or combine those two theorem with `iffD1[OF not_limit_closure]` ([IIRM §6.4.3](https://isabelle.in.tum.de/doc/isar-ref.pdf#attribute.OF)), for `frule iffD1[OF not_limit_closure]`!

.. admonition:: me/say

	To be honest, I just wanted to show off a bit :)

We'll take the first one, then play around with existentials to pass the prefix to the safety definition.

```isabelle
  apply (subst (asm) not_limit_closure)
  apply (erule exE)
  apply (rule_tac x="n" in exI)
```

> Output
> ```
> proof (prove)
> goal (1 subgoal):
>  1. ⋀σ n. ∀σ'. P σ' ⟶ i_take n σ ≠ i_take n σ' ⟹
>            ∀β. (¬P) (i_take n σ ⌢ β)
> ```

This leaves us with just a bunch of behaviour manipulation to show that you can never satisfy the safety property.
Doing it manually would lead us to showing a neat identity that `i_take n (i_take n σ ⌢ b) = i_take n σ` (which previously showed up in the end of [Liveness is Dense](#liveness-is-dense)!) but at this point I got bored and simply threw a sledgehammer at it to get

```isabelle
  by (metis append_inv i_take_def length_map take_append_drop)
```

That's the final one of the big 4 lemmas, giving us that `safety = limit_closed`!

```isabelle
theorem safety_closed[simp]: "safety P = limit_closed P"
  using closed_is_safety safety_is_closed by blast
```

.. details:: Full proof of closed_is_safety

	```isabelle
	lemma closed_is_safety: "limit_closed P ⟹ safety P"
	  unfolding safety_def limit_closed_forall
	  apply (intro allI impI)
	  apply (erule_tac x="σ" in allE)
	  apply (case_tac "limit_closure P σ")
	   subgoal by simp
	  apply (thin_tac "σ ⊨ ¬P")
	  apply (thin_tac "σ ⊨ limit_closure P ⟶ P")
	  apply (subst (asm) not_limit_closure)
	  apply (erule exE)
	  apply (rule_tac x="n" in exI)
	  by (metis append_inv i_take_def length_map take_append_drop)
	```

And now, the big boss battle: Alpern and Schneider’s Theorem.

# Alpern and Schneider

Here's the goal:

```isabelle
theorem alpern_schneider: "∃S L. safety S ∧ liveness L ∧ (P = (S ∧ L))"
```

It seems pretty daunting to find $S$ and $L$, but fortunately ["Defining Liveness"][alpern1984] provides us exactly what they should be -- in their notation, $S = \bar{P}$ and $L = \lnot(\bar{P} - P)$ -- that we can plug directly into the existential.

```isabelle
  apply (rule_tac x="limit_closure P" in exI)
  apply (rule_tac x="¬((limit_closure P) ∧ ¬P)" in exI)
  apply (intro conjI)
```

> Output
> ```
> proof (prove)
> goal (3 subgoals):
>  1. safety (limit_closure P)
>  2. liveness (¬(limit_closure P ∧ ¬P))
>  3. P = (limit_closure P ∧ ¬(limit_closure P ∧ ¬P))
> ```

The first simplifies away, the second can be sledgehammered with the help of `vampire` again, and the third is dismissed with `auto`.

```isabelle
    subgoal by simp
   subgoal by (metis (mono_tags, lifting) dense_def dense_is_liveness not_limit_closure)
  subgoal by auto
```

And now, we are greeted with best thing a proof engineer can see:

> Output
> ```
> proof (prove)
> goal:
> No subgoals!
> ```

```isabelle
  done
```

.. details:: Full proof of alpern_schneider

	```isabelle
	theorem alpern_schneider: "∃S L. safety S ∧ liveness L ∧ (P = (S ∧ L))"
	  apply (rule_tac x="limit_closure P" in exI)
	  apply (rule_tac x="¬((limit_closure P) ∧ ¬P)" in exI)
	  apply (intro conjI)
	    subgoal by simp
	   subgoal by (metis (mono_tags, lifting) dense_def dense_is_liveness not_limit_closure)
	  subgoal by auto
	  done
	```


And thus, just so I get to reuse this cute theorem styling[^css], we have proven that

[^css]: Sorry people without CSS, for whom it just looks like a plain paragraph.

.. sparkle::

	Every property is the intersection of a safety and a liveness property.

For completeness, here's the [full theory]({{ recipe.copy("/assets/lets-prove-1:Full.thy", "./Full.thy") }}) with with everything we've done.

# Reflections

This has been quite the journey.
Both in proving theorem theorem, as well as writing this monster of a blog post.

This has been one of the rare opportunities where I get to exercise my theorem prover muscles, and honestly, it's still nearly addictive as it was back when I learned Isabelle.
Though I think some of the proofs I tackled in COMP4161 are harder, if only by step count.
Plus, I completely managed to avoid Isar, which, while probably more powerful, is also a more cumbersome to use in my experience.

In this process, I also made an interesting mistake that I'll be turning into a followup blog post, ~~so stay tuned for that~~ which you can see in [Part 2](lets-prove-2) :)

On the blog writing side, this has become my longest article so far by quite the margin[^big].
But despite that, it's is still nowhere near the hour-long reads by the likes of [JeanHeyd](https://thephd.dev/), [Amos](https://fasterthanli.me), and other, who I genuinely look up to for technical writing.
With so much content, I've also a couple opportunities to get a better feel for writing style, such as with that vampire sledgehammer interjection.
This been quite fun to write, so much so that I've genuinely been neglecting my university coursework (and sleep to some extent) this week.
Though I don't know how many people would even have the background to read this, but hey, I'm mostly writing for myself here.

[^big]: At over 4.5k words, this is over 2 times the word count of the next longest, [Ownership Semantics For C Programmers](ownership).
	That count is probably a bit inflated from all the spaces in my maths and Isabelle code, but I write with a new line per sentence and it's actually around 3 times as long by that metric.
	The next longest are [Edge-based Tree Data Structures](edge-trees) and [An SSH Workflow](ssh-workflow), with their order depending on which metric you use.

And finally, if you got all the way here, thanks so much for reading! 💜
