---
layout: article
title: Ownership Semantics for C programmers
tags:
excerpt: How to ensure memory safety when the compiler can't help
---

{% capture content %}
@import "defns";
div.highlight {
  background: rgba(153, 4, 97, .1);
  padding: 0 1ch;
}
div.highlight .cp {
  // hide the header
  // reset stuff
  display: block;
  white-space: normal;
  font: $font;
  color: var(--body-fg);
  // actual styling
  font-style: italic;
  border: 1px solid $accent-bg;
  padding: 0 1ch;
  margin: 0 1em;
  background: var(--body-bg);
}
{% endcapture %}<style>{{ content | scssify }}</style>

{% capture content %}
{::options syntax_highlighter_opts="{ line_numbers: false \}" /}

*(alt subtitle: How to pretend you're writing rust when in C)*

TODO we need an intro

<!--more-->

For the purposes of this article, we'll mostly be concerned with memory *management* -- ensuring that we clean up all allocated memory (or other resources) exactly once. This means no leaking, and no double or invalid frees. While we're at it, we'll also want to prevent other memory safety issues like use-after-free if we can.

# Sharing is caring, but it's also kinda unsafe

A basic but rather limiting approach is to never allow multiple pointers to point to a single allocation. Instead, you're only allowed a single variable, struct field, or array element. For now, we'll also forbid changing the value of pointers. Let's have a look at how this works:

```c
{
  type* val = malloc(sizeof(type));
  val->field = 1; // this is allowed
  do_abc(val->foo); // this is too

  // type* copy = val;
### ↑ We don't allow this, since we would then have two references

  // do_xyz(val);
### ↑ This is also forbidden - do_xyz's argument would be a second reference. However, we'll allow free() as the only exception to this rule.
  free(val);
}
```

Now, we guarantee that nothing else can refer to `*val`, and so we must be the one responsible for freeing it once `val` stops existing. In a sense, the variable `val` has exclusive ownership of (and responsibility for) the allocated memory.

Even with such strong restriction, we can still do complex data structures...kinda:

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

We can't use loops since we'd create another reference, but we pretty easily figure out how to correctly free it:

1. The variable `head` would vanish, so we need to free the first node...
2. That would invalidate `head->next`, and so we'd have to free the second one...
3. Which in turn would cause `head->next->next` to disappear, forcing us to free the last node

```c
  free(head->next->next);
  free(head->next);
  free(head);
}
```

In this way, fields of structs can own memory, not just variables. We also observe that allocations need to be freed before their owners can be freed.

# No-cloning theorem

However, such strong restrictions are quite limiting. While we can have linked lists and such, they're still essentially glorified local variables since we can't loop over them. Also, I haven't even mentioned how that interacts with returning pointers (e.g. `malloc`), and we're having `free` be an exception.

So we're going to extend this with the ability to *transfer ownership*.

Now, this is very different to simply creating a new reference. Instead, when we give our reference to someone else, we stop being able to use our old one[^set-null]. This ensures that there's still exactly one reference throughout the whole program. Formally:

[^set-null]: We don't have Rust-style destructive moves, so we have to make do with setting pointers to null. Strictly speaking, this is not safe -- between assigning the pointer and setting it to null, there's two copies of the pointer. This is more obvious if we're moving the reference to a function, since we only clear the pointer *after* the function terminates.

1. All pointers are either null or point to a valid allocation.
2. If we want to pass a pointer to a function or assign it to something, we must null the original variable.
3. You must never "leak" a allocation -- you must always deallocate before the pointer becomes TODO reword invalid

In C, this translates to

```c
{
  type* val = malloc(sizeof(type));
  val->xyz = 1;
  do_xyz(val); val = NULL; // together as a single action
}
```

Notice that once we've passed off `val` to `do_xyz`, we're no longer responsible for freeing it -- `do_xyz` is, or whoever they pass the reference to. We can also transfer ownership to the function that calls us:

```c
type* create_type(int n) {
  type* val = malloc(sizeof(type));
  val->xyz = n;
  return val;
}
```

Now, the caller becomes responsible[^ignore-result] for this bit of memory.

[^ignore-result]: In standard C, this is a bit risky since the compiler won't stop you from simply ignoring this. But there's compiler-specific ways of turning this into a warning -- `__attribute__((warn_unused_result))` in clang and gcc, and `_Check_return_` in MSVC.

We can also incorporate `malloc` and `free` into this framework -- `malloc` transfers ownership of memory from the allocator to us, and `free` transfers ownership back. Initially, all memory is owned by the system, and by the end, all memory must be returned.

Under this model, we can do pretty much everything we want, albeit with difficulty. For example, this gets the sum of a linked list:

```c
// return type
struct pair { struct list* list; int sum; };

struct pair list_sum(struct list* list) {
  // handle the end of the list
  if(!list) {
### We actually don't have a reference here, so we don't need to care.
    struct pair out = { 0, 0 };
    return out;
  }

### ↓ We detach the tail of the list and transfer it to the call of list_sum. This function then gives us back a list (hopefully the one we passed to it) vai a struct pair.
  struct pair inner = list_sum(list->next);
      list->next = 0;

### ↓ Then, we put the list back together.
  list->next = inner.list; inner.list = 0;

### ↓ We then move the list out of the local variable and into out, which we give back to the caller.
  struct pair out;
  out.list = list; list = 0;
  out.sum = inner.sum + list->val;
  return out;
}
```

This is pretty tedious. If we want a function to be able to simply *read* part of the list -- not even modifying it -- we need to

1. Detach the tail of the list from the head,
2. Pass it to the function,
3. Get it back via the returned value, and
4. Reattach the tail back onto the head

when we would originally just pass a pointer. The upside is that we can very easily follow how ownership of memory moves around our program, and more importantly, we are able to tell if any function handles memory correctly (no leaking or double freeing) *without looking at other functions* -- if we pass a pointer to a function, we can't use it again, and if we get a pointer, we must always do something with it[^linear-logic].

[^linear-logic]: If you want to read more about this, have a look at [Wikipedia: linear logic](https://en.wikipedia.org/wiki/Linear_logic) and [Wikipedia: linear type system](https://en.wikipedia.org/wiki/Substructural_type_system#Linear_type_systems)

This gives us a massively helpful safety guarantee. But we can do a bit better.

# The pointer that keeps on giving

One of the first things we disallowed in this journey was non-owning pointers. Originally, we banned them to develop our guarantees, but we're now ready to allow them again, as **borrowing pointers**[^rust-borrow]. As such, we'll have two "families" pointers:

[^rust-borrow]: These are close to Rust's concept of borrowing and reference, but are just subtly different enough that they'll trip you up if you're not careful. Our version doesn't distinguish between mutable and non-mutable references, and we don't have the "one mutable reference or any number of non-mutable reference" rule.

1. `typedef type* type_ptr_owning;`{:.language-c} -- this is the kind we've been using before. We can move them, but can't copy them or drop them.
2. `typedef type* type_ptr_borrow;`{:.language-c} -- these "borrow" ownership from another pointer -- you can create a new one from either pointer type, but you can't convert this into a `ptr_owning`. I'll write this as `&*owning_ptr`{:.language-c} -- dereferencing then taking its address -- for reasons that I'll explain shortly.

Now, we can rewrite our linked list sum like this:

```c
typedef struct list* list_owned;
typedef struct list* list_borrow;
### ↑ Here's our two pointer types.

struct list { list_owned next; int val; };
### ↑ Each node of the linked list actually owns the next node (and indirectly, the rest of the list).

int list_sum(list_borrow list) {
### ↑ We don't need to move or dispose of this list, so we can simple use a borrowing pointer.
    if(!list) return 0;
    return list->val + list_sum(&*list->next);
### ↑ We borrow from list->next, which owns the next node, and pass this new list_borrow as the argument to our list_sum call.
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

In most cases, this reduces to "borrows never outlive the pointer they came from", but for structs and other places where data is accessed from multiple places this can get complicated -- another function could free their memory from under you. Anyways, you can can see how this rule applies to the last line of `list_sum`:

```c
    return list->val + list_sum(&*list->next);
```

`list` is valid for the duration of the function, so we can look inside it and borrow `list->next`, assuming no-one moves out from it e.g. from another thread.

Our idea of ownership can also be broadened from just owning pointers to functions and structs -- local variables are "cleaned up" when the function returns, and struct members are invalidated when the struct itself is destroyed. This naturally extends our `&*owning_ptr` syntax to `&local_var` and `&struct->member`, which is quite nice.

```c
// have our head be local instead of in the heap
struct list local_head = /* ... */;
int sum = list_sum(&local_head);
```

In fact, the `&` operator can also be seen to *exclusively* give borrows -- if you take the address of something, then that thing must already exist and hence be owned.

While this model (or similar variants) are used pretty widely, the biggest issue is that correctly reasoning about lifetimes can get tricky when more complex structures e.g. structs containing `borrow_ptr`. However, in most cases you'll only have temporary `borrow_ptr`s that are passed to functions and possibly returned. This gives a few heuristics:

- for the caller: the lifetime of the returned borrows is *usually* the same as the lifetime of `borrow_ptr` arguments
- for the callee: `borrow_ptr` arguments are valid for at least the duration of a function, and you can return borrows derived from `borrow_ptr` arguments

As an interesting final note, these `borrow_ptr` and `owning_ptr` types don't actually have to be pointers returned by `malloc`! For examples of other things:

- `owning_ptr` -- reference counted types[^non-unique], dynamic arrays, and `FILE*`/file descriptors
- `borrow_ptr` -- pointer+length pairs (for slices of arrays)

[^non-unique]: This might relax the "one owning pointer per resource" rule into just "each create must have a corresponding destroy". However, our move-only rules from our second model still applies.

# TODO section title

We've developed a pretty good and practical framework that we can use to eliminate certain classes of memory safety errors. Now, in real C code much of this is very much implicit -- there probably wont' be comments pointing this stuff out, let alone typedefs.

Much of what I've laid out here is inspired by more modern programming languages, namely C++ and Rust. These enforce at the language much of what we had to do manually: C++ has move semantics and move-only types -- essentially our second model -- and Rust has, well, very comprehensive *compile-time* memory safety features (seriously, take a look if you haven't).

TODO a better conclusion

{% endcapture %}{{ content | markdownify | replace: "###", "" }}
