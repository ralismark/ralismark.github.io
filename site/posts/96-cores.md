---
layout: post
title: Contention On 96 Cores
excerpt: An interesting issue with std::locale and massive parallelism
date: 2021-11-14
tags: c-cpp
---

I recently investigated an interesting issue at work:

> Running one build variant of a program takes approx 5 seconds on a 96 core machine.
> Running this other build variant takes 30 seconds.
> CPU usage is 100% for 96 core, so it is definitely running stuff efficiently - seems there is a huge amount of overhead here.

The program is architectured in a way such that it should scale up to more threads very well -- essentially generating a large number of independent tasks, then running them in parallel and gathering the results.
So a 6x slowdown is not something that's expected.

After some investigation with [`perf`][perf] and [`hotspot`][hotspot], it turns out that most of that time is within the [`std::basic_ostringstream` constructor][basic_oss], and within that almost entire in the [`std::locale` constructor][locale].

Turns out we had a very hot loop that was constructing a `std::stringstream` every iteration, and this was being run by every single core.
Moreover, this code was compiled out in the first build variant which meant it didn't have that performance issue.
Editing this loop to not use `std::stringstream` fixed the issue, and that's more or less where the original story ended.

But, what's the actual cause behind this slowness?

[perf]: https://www.brendangregg.com/perf.html
[hotspot]: https://github.com/KDAB/hotspot
[basic_oss]: https://en.cppreference.com/w/cpp/io/basic_ostringstream/basic_ostringstream
[locale]: https://en.cppreference.com/w/cpp/locale/locale/locale

Looking on cppreference leads us to a couple of pointers as to the cause:

> Each stream object of the C++ input/output library is associated with an std::locale object and uses its facets for parsing and formatting of all data.
>
> [...]
>
> Internally, a locale object is implemented as-if it is a reference-counted pointer to an array (indexed by `std::locale::id`) of reference-counted pointers to facets: copying a locale only copies one pointer and increments several reference counts.
> To maintain the standard C++ library thread safety guarantees (operations on different objects are always thread-safe), both the locale reference count and each facet reference count are updated in thread-safe manner, similar to `std::shared_ptr`.
>
> --- <https://en.cppreference.com/w/cpp/locale/locale>

This would explain it: the frantic construction and destruction of the `std::locale` for the hot loop's `std::stringstream` was causing all the threads to compete to update a global reference count, and with 96 threads across 96 cores, trying to modify this shared global state was causing massive amounts of contention.

Revisiting the off-cpu (i.e. blocking) flame graph from the `perf` trace supports this, showing a massive *27 seconds* of blocking within `std::locale`.

But, there's a slight wrinkle in this story.
Note the wording of the above passage: _**as-if** it is a reference-counted pointer_.
So, it's not actually guaranteed to be the case.
In fact, the standard says

> Whether there is one global locale object for the entire program or one global locale object per thread is implementation-defined.
> Implementations should provide one global locale object per thread.
> If there is a single global locale object for the entire program, implementations are not required to avoid data races on it (\[res.on.data.races\]).
>
> --- [\[locale.general\]/9](http://eel.is/c++draft/locale#general-9)

So, time to dig into libstdc++ and see what's actually happening.

We find that the implementation of `std::locale`'s default constructor in in [libstdc++-v3/src/c++98/locale_init.cc](https://github.com/gcc-mirror/gcc/blob/a8029add3065e4abb5dbaa92ce3f1b307f3e16ef/libstdc%2B%2B-v3/src/c%2B%2B98/locale_init.cc#L268-L288).

```cpp
  locale::locale() throw() : _M_impl(0)
  {
    _S_initialize();

    // Checked locking to optimize the common case where _S_global
    // still points to _S_classic (locale::_S_initialize_once()):
    // - If they are the same, just increment the reference count and
    //   we are done.  This effectively constructs a C locale object
    //   identical to the static c_locale.
    // - Otherwise, _S_global can and may be destroyed due to
    //   locale::global() call on another thread, in which case we
    //   fall back to lock protected access to both _S_global and
    //   its reference count.
    _M_impl = _S_global;
    if (_M_impl != _S_classic)
      {
        __gnu_cxx::__scoped_lock sentry(get_locale_mutex());
        _S_global->_M_add_reference();
        _M_impl = _S_global;
      }
  }
```

The [`_S_initialize`][_S_initialize] call just runs [`_S_initialize_once`][_S_initialize_once] if it hasn't been run, which in turn initialises a `_S_global` and `_S_classic`.

[_S_initialize]: https://github.com/gcc-mirror/gcc/blob/a8029add3065e4abb5dbaa92ce3f1b307f3e16ef/libstdc%2B%2B-v3/src/c%2B%2B98/locale_init.cc#L331-L340
[_S_initialize_once]: https://github.com/gcc-mirror/gcc/blob/a8029add3065e4abb5dbaa92ce3f1b307f3e16ef/libstdc%2B%2B-v3/src/c%2B%2B98/locale_init.cc#L321-L329

```cpp
  void
  locale::_S_initialize_once() throw()
  {
    // 2 references.
    // One reference for _S_classic, one for _S_global
    _S_classic = new (&c_locale_impl) _Impl(2);
    _S_global = _S_classic;
    new (&c_locale) locale(_S_classic);
  }

  void
  locale::_S_initialize()
  {
#ifdef __GTHREADS
    if (__gthread_active_p())
      __gthread_once(&_S_once, _S_initialize_once);
#endif
    if (!_S_classic)
      _S_initialize_once();
  }
```

After that, we load a `_S_global`, then if it's not the default of `_S_classic`, we lock and increment a reference count.
Now, given what we've seen this seems to imply that our program had a non-default locale.
Doing a simple grep seems to imply that this isn't the case though, so it's not clear what's up.

However, `_S_global` and `_S_classic` are both defined as plain `_Impl*` so maybe memory contention there, despite them not being atomics?
At this point, I don't have a good enough grasp of how CPUs handle this so unfortunately I don't have a clean resolution to this mystery.
