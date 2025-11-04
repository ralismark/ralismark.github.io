---
layout: post
title: Ownership Semantics For C Programmers
excerpt: How to ensure memory safety when the compiler can't help
date: 2021-05-10
tags: c-cpp
---

{% set esc %}<!<span class="code-annotation">{% endset %}
{% set endesc %}</span>!>{% endset %}

*(alt subtitle: How to pretend you're writing rust when in C)*

One of the many unique aspects of C that you won't encounter in other languages is how manual resource management is -- almost all higher level languages have automatic garbage collection, and those that don't typically have other automated methods like destructors.
This memory *un*safety, combined with the lack of any language-level safety rails, make this one thing that's easily mess up.
However, we can borrow ideas that have been developed over time to make it easier to be safe.

<!--more-->

For the purposes of this article, we'll mostly be concerned with memory *management* -- ensuring that we clean up all allocated memory (or other resources) exactly once.
This means no leaking, and no double or invalid frees.
Related issues, like use-after-free, will also be covered to a lesser degree, and we mostly won't bother with the remaining concerns.

# Training Wheels

A basic but rather limiting approach is to never allow multiple pointers to point to a single allocation, instead only allowing a single variable, struct field, or array element to hold each resource.
We'll *disallow* assigning pointers, since that would create a copy of the pointer, as well as passing pointers as arguments, since both the caller and callee would have a variable.

With this restriction, we can easily determine when memory need to be freed:
just before the pointer holding this memory disappears -- a local variable going out of scope, or the parent data structure being freed.
No other references to the held memory exist, so we can't double free or leak.

Let's have a look at how this works:

```escape c
{
  type* val = malloc(sizeof(type));
  val->field = 1; // this is allowed
  do_abc(val->foo); // this is too

  // type* copy = val; {{ esc }}↑ We don't allow this, since we would then have two references{{ endesc }}

  // do_xyz(val); {{ esc }}↑ This is also forbidden - do_xyz's argument would be a second reference. However, we'll allow free() as the only exception to this rule.{{ endesc }}
  free(val);
}
```

Now, we guarantee that nothing else can refer to `*val`, and so we must be the one responsible for freeing it once `val` stops existing.
In a sense, the variable `val` has exclusive ownership of (and responsibility for) the allocated memory.

Even with such strong restriction, we can still do complex data structures ... kinda:

```c
{
  // linked list: 1 -> 2 -> 3 -> NULL
  struct list* head = malloc(sizeof(list))
  head->val = 1
  head->next = malloc(sizeof(list));
  head->next->val = 2;
  head->next->next = malloc(sizeof(list));
  head->next->next->val = 3;
  head->next->next->next = NULL;
```

Unfortunately, we can't use loops, since the loop variable would be an extra reference into the list and that's disallowed.
However, it's pretty easy to figure out how to correctly free the list:

1. `head` will go out of scope, and it contains `head->next`, so we'll need to free that first
2. `head->next` contains `head->next->next` which holds some memory, so that also needs to be freed beforehand
3. `head->next->next` doesn't contain any further references, so we're done

```c
  free(head->next->next);
  free(head->next);
  free(head);
}
```

# No-Cloning Theorem

However, such restrictions are too limiting to do much.
We can't have truly recursive data structures like lists or trees -- no loops means they behave pretty much identical to local variables.
We can't have functions either.

So we're going to extend this with the ability to *transfer ownership*.

We'll still enforce our "one reference per allocation", but instead allow assigning pointers in a restricted way:
when you give a reference to something else, you stop being able to use the old one.
While this atomic get-and-invalidate can't be directly expressed in C, we can approximate this by setting the old pointer to null.

Code-wise, the rules become:

1. All pointers are either null or point to a valid allocation.
2. If we want to pass a pointer to a function or assign it to something, we must null the original variable.
3. You must never leak an allocation -- you must always deallocate before the "holder" gets invalidated

This means that we can now do this

```c
{
  type* val = malloc(sizeof(type));
  val->xyz = 1;
  do_xyz(val); val = NULL; // together as a single action
}
```

Notice that once we've passed off `val` to `do_xyz`, we're no longer responsible for freeing it -- `do_xyz` is, or whoever they pass the reference to.
We can also transfer ownership to the function that calls us:

```c
type* create_type(int n) {
  type* val = malloc(sizeof(type));
  val->xyz = n;
  return val;
}
```

Now, the caller becomes responsible[^ignore-result] for this bit of memory.
`malloc` is a function like this -- it allocates some memory and gives it to the caller.

[^ignore-result]: In standard C, this is a bit risky since the compiler won't stop the caller from simply ignoring the returned pointer.
	But there's compiler-specific ways of turning this into a warning -- `__attribute__((warn_unused_result))` in clang and gcc, and `_Check_return_` in MSVC.

Under this model, we can do much more, though with some difficulty.
For example, this gets the sum of a linked list:

```escape c
// return type
struct pair { struct list* list; int sum; };

struct pair list_sum(struct list* list) {
  // handle the end of the list
  if(!list) { {{ esc }}We actually don't have a reference here, so we don't need to care.{{ endesc }}
    struct pair out = { 0, 0 };
    return out;
  }
{{ esc }}↓ We detach the tail of the list and transfer it to the call of list_sum. This function then gives us back a list (hopefully the one we passed to it) via a struct pair.{{ endesc }}
  struct pair inner = list_sum(list->next);
      list->next = 0;
{{ esc }}↓ Then, we put the list back together.{{ endesc }}
  list->next = inner.list; inner.list = 0;
{{ esc }}↓ We then move the list out of the local variable and into out, which we give back to the caller.{{ endesc }}
  struct pair out;
  out.list = list; list = 0;
  out.sum = inner.sum + list->val;
  return out;
}
```

This is pretty tedious, but at least it's now possible.
If we want a function to be able to simply *read* part of the list -- not even modifying it -- we need to

1. Detach the tail of the list from the head,
2. Pass it to the function,
3. Get it back via the returned value, and
4. Reattach the tail back onto the head

when we would originally just pass a pointer.
The upside is that we can very easily follow how resources moves around our program, and more importantly, we are able to tell if any function handles memory correctly (no leaking or double freeing) *without looking at other functions* -- if we pass a pointer to a function, we can't use it again, and if we get a pointer, we must always do something with it[^linear-logic].

[^linear-logic]: These are sometimes called linear types (or affine types if you have automatic cleanup).
	If you want to read more about this, have a look at [Wikipedia: linear logic](https://en.wikipedia.org/wiki/Linear_logic) and [Wikipedia: linear type system](https://en.wikipedia.org/wiki/Substructural_type_system#Linear_type_systems)

Types that act like this -- not just pointers, but also files handles, mutexes, and other non-copyable resources -- are called *move-only types*.
These give us a massively helpful safety guarantee.
But we can do a bit better.

# Sharing Is Caring

One of the first things we disallowed in this journey was non-owning pointers.
Originally, we banned them to develop our guarantees, but we're now ready to allow them again, as **borrowing pointers**[^rust-borrow].
As such, we'll have two "families" pointers:

[^rust-borrow]: These are close to Rust's concept of borrowing and reference, but are just subtly different enough that they'll trip you up if you're not careful.
	Our version doesn't distinguish between mutable and non-mutable references, and we don't have the "one mutable reference or any number of non-mutable reference" rule.

{# TODO can we please have a code style convention for multiline lists? #}
1. `typedef type* type_ptr_owning;` -- this is the kind we've been using before.
	We can move them, but can't copy them or drop them.
2. `typedef type* type_ptr_borrow;` -- these "borrow" ownership from another pointer -- you can create a new one from either pointer type, but you can't convert this into a `ptr_owning`.
	I'll write this as `&*owning_ptr` -- dereferencing then taking its address -- for reasons that I'll explain shortly.

Now, we can rewrite our linked list sum like this:

```escape c
typedef struct list* list_owned;
typedef struct list* list_borrow; {{ esc }}↑ Here's our two pointer types.{{ endesc }}

struct list { list_owned next; int val; }; {{ esc }}↑ Each node of the linked list actually owns the next node (and indirectly, the rest of the list).{{ endesc }}

int list_sum(list_borrow list) { {{ esc }}↑ We don't need to move or dispose of this list, so we can simple use a borrowing pointer.{{ endesc }}
    if(!list) return 0;
    return list->val + list_sum(&*list->next); {{ esc }}↑ We borrow from list->next, which owns the next node, and pass this new list_borrow as the argument to our list_sum call.{{ endesc }}
}
```

Much nicer!

However, it turns out that just this is unsafe! There's nothing stopping us from keeping a borrowed pointer longer than the target object is alive:

```c
// create a thing
type_ptr_owning thing = malloc(sizeof(type));
// borrow it
type_ptr_borrow borrow = &*thing;
// free the original thing
free(thing); thing = 0;
// use our borrow that we kept around
do_thing(borrow); // boom 💥
```

So we'll just add that as a rule:

1. Borrows must never outlive the value that they point to

In most cases, this reduces to "borrows never outlive the pointer they came from", but for structs and other places where data is accessed from multiple places this can get complicated -- another function could free their memory from under you.
Anyways, you can can see how this rule applies to the last line of `list_sum`:

```c
    return list->val + list_sum(&*list->next);
```

`list` is valid for the duration of the function, so we can look inside it and borrow `list->next`, assuming no-one moves out from it e.g. from another thread.

Our idea of ownership can also be broadened from just owning pointers to functions and structs -- local variables are "cleaned up" when the function returns, and struct members are invalidated when the struct itself is destroyed.
This naturally extends our `&*owning_ptr` syntax to `&local_var` and `&struct->member`, which is quite nice.

```c
// have our head be local instead of in the heap
struct list local_head = /* ... */;
int sum = list_sum(&local_head);
```

In fact, the `&` operator can also be seen to *exclusively* give borrows -- if you take the address of something, then that thing must already exist and hence be owned.

While this model (or similar variants) are used pretty widely, the biggest issue is that correctly reasoning about lifetimes can get tricky when more complex structures e.g. structs containing `borrow_ptr`.
However, in most cases you'll only have temporary borrows that are passed to functions and returned/dropped.
This gives a few heuristics:

- for the caller: the lifetime of the returned borrows is *usually* the same as the lifetime of `borrow_ptr` arguments
- for the callee: `borrow_ptr` arguments are valid for at least the duration of a function, and you can return borrows derived from `borrow_ptr` arguments

As an interesting final note, these `borrow_ptr` and `owning_ptr` types don't actually have to be pointers returned by `malloc`!
For examples of other types:

- `owning_ptr` -- reference counted types[^non-unique], dynamic arrays, and `FILE*`/file descriptors
- `borrow_ptr` -- pointer+length pairs (for slices of arrays)

[^non-unique]: This only works under the "creates must have a corresponding destroy" variant of the rules, not "one owning pointer per resource".

# Closing Words

We've developed a pretty good and practical framework that we can use to eliminate certain classes of memory safety errors.
Now, in real C code much of this is very much implicit and might not even be precisely followed -- pointers that are moved out of might not be nulled, for example.

Much of what I've laid out here is inspired by more modern programming languages, namely C++ and Rust.
These enforce at the language much of what we had to do manually:
C++ has move semantics and move-only types, and Rust has, well, an very comprehensive *compile-time* memory safety features (seriously, take a look if you haven't).

But if you're stuck with C, these concepts will make memory management a little safer.

<style>
.code-annotation {
  display: block;
  white-space: normal;
  font-family: var(--main-font-family);
  color: var(--body-fg);
  // actual styling
  font-style: italic;
  border: 1px solid var(--stroke);
  padding: 0 1ch;
  margin: 0 1em;
  background: var(--body-bg);
}
</style>
