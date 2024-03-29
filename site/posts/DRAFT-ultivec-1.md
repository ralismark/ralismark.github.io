---
layout: post
title: Hunt for the Ultimate Vector (part 0) - Prelude
excerpt: "Building a nice vector type in C++"
date: 2018-01-06
tags: c-cpp
reason: wip old
---

There exist many, many linear algebra libraries for c++, with a wide range of features - ranging from effectively [structs with operators][sfml-vec] to [fancier ones with swizzle support][cxxswizzle].
I attempt to make another one, not focused on speed, but on usability.

[sfml-vec]: https://www.sfml-dev.org/documentation/2.4.2/classsf_1_1Vector2.php
[cxxswizzle]: https://github.com/gwiazdorrr/CxxSwizzle

<!--more-->

## Features

Before beginning work, it's helpful to list the features that we're focused on.
This way, we'll know what to aim for and what to avoid.
Additionally, this can help reduce complexity and template madness somewhat.

These are the features that we're going to try and achieve:

1. **Unrestricted size and type.**
	We want to be able to use any type as the elements, as well as have vectors of arbitrary size.
	To make implementation easier, we'll have both of these as templates.

2. **Named elements.**
	We want to be able to refer to dimensions by name.
	This is most useful for vectors of up to 3 dimensions, as they can clear up syntax quite a bit - using `vec.y` instead of `vec[1]`.
	However, we still want access to all elements for larger vectors, so we'll have subscript as well.

3. **Not break auto.**
	Some potential extensions, most notably [swizzling][3], are much easily implemented using proxy types.
	However, this leads to several issues[^1], especially type deduction.

[3]: https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)

[^1]: Interestingly, [a similar issue][vector-bool] arose in the STL with `std::vector<bool>`, which uses a proxy type instead of `bool&` for its `reference` type

[vector-bool]: https://stackoverflow.com/q/17794569

4. **Good type support.**
	Due to sheer number of linear algebra libraries, it's useful to have our vector interop at least somewhat well with them.
	This can be done several ways, as we'll later discuss.
	Additionally, it's helpful to properly support element type conversions as well as returning the correct types from operators.

## Overall Design

With these features in mind, we can begin the overall design of this class.

To achieve goals 2 and 3, we'll want to use a union with an unnamed struct[^2].
A naive way is to use a union as the type, like this:

[^2]: This is technically an extension to the standard.
	However, it's supported by the major compilers (gcc, clang and msvc), albeit with warnings, so we'll use it.
	Besides, there's no other way (that I know) of doing this without messing up the element names (to be `vec.v.x` instead of just `vec.x`).

```cpp
template <typename T, size_t N>
union vec {
	T data[N];
	struct {
		T x, y, z, w;
	};
};

// specialisations for smaller vectors
```

However, as unions cannot be inherited, we would have to declare the same constructors as well as some operators again and again for each specialisation (there's 3-4).
Following the DRY principle, this is pretty bad.
A naive way to fix this is with macros to repeat them, but that's messy.

However, there's a better way of doing things - putting the union (unnamed) in a struct:

```cpp
template <typename T, size_t N>
struct vec {
	union {
		T data[N];
		struct {
			T x, y, z, w;
		};
	};
};
```

This pretty much works!
It allows inheritance, so you can make a generic derived class which doesn't have to specialise for the smaller dimensions.

From my past attempts, I've found that it's best to have two separate classes, one for the actual storage (which has specialisation for smaller sizes) and another for the interface (without any specialisation).
This allows for the interface to be easily modified.
