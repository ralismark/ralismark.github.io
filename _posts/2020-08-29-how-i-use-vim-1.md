---
layout: post
title: How I Use Vim (part 1)
tags:
excerpt: Interesting aspects of my vim usage
---

I've been using Vim (well, Neovim) for several years now and I've developed some idiosyncrasies along the way. [My vimrc][vimrc] is quite large, so here's a few points.

[vimrc]: https://github.com/ralismark/vimfiles

<!--more-->

> Note: This not intended as a guide on how to learn or use Vim -- it's how *I* use Vim, not how you should use Vim. This is a sample of the things I do and use.
>
> Nor is this written with absolute beginners in mind. If you're just starting, take time to learn Vim fundamentals before diving into extensive customisation.

# Core Vim

Like all Vim users, I use `hjkl` to navigate. However, one thing you might see in Vim tutorials that I *don't* use are numbers with these keys -- `5j` to go down 5 lines, for example. I had [`'relativenumber'`] set for several years, but it never felt intuitive. This extends to operator-pending mode too -- I heavily rely on [visual line]/[block] mode to do multiline operations. For example, to delete multiple lines, I would do `Vjjjjd` instead of `d4j`.

[`'relativenumber'`]: https://vimhelp.org/options.txt.html#%27relativenumber%27
[visual line]: https://vimhelp.org/visual.txt.html#linewise-visual
[block]: https://vimhelp.org/visual.txt.html#blockwise-visual

Furthermore, for plain navigation I often use uppercase [`W`] and [`B`] to move left and right. I also use `0w` instead of `^`, which is harder to type, to move to the start of line. I haven't figured out a good way of navigating vertically yet, so I'm still on h/j plus fast keyrepeat.

[`W`]: https://vimhelp.org/motion.txt.html#W
[`B`]: https://vimhelp.org/motion.txt.html#B

# Leader Mapping

I have [`<leader>`][leader] mapped to `<space>`. Here's some of my bindings for inspiration:

[leader]: https://vimhelp.org/map.txt.html#%3CLeader%3E

- `<leader>w` to save ([`:update`]), which I use *very* often
- `<leader>q` to close buffer with `:q`
- `<leader>o<key>` to toggle various options, such as [(w)rap]['wrap'], [(d)iff]['diff'], [(s)pellchecking]['spell']
- `<leader>m` to make using [tpope/vim-dispatch]
- `<leader>x` to "run" the current file (`ExecCurrent()` in my vimrc).

[`:update`]: https://vimhelp.org/editing.txt.html#:update
['wrap']: https://vimhelp.org/options.txt.html#%27wrap%27
['diff']: https://vimhelp.org/options.txt.html#%27diff%27
['spell']: https://vimhelp.org/options.txt.html#%27spell%27
[tpope/vim-dispatch]: https://github.com/tpope/vim-dispatch

# Splits & Tabs

I have a lot of bindings set up to make splits and tabs easier to use. This includes:

- `<leader>s<key>` to open empty splits in different directions with [`:new`] and [`:aboveleft`]/[`:belowright`]/[`:vertical`].
- `<c-hjkl>` to move between splits
- `<leader>t` to open a new tab
- `[t` and `]t` to move between tabs

[`:new`]: https://vimhelp.org/windows.txt.html#:new
[`:aboveleft`]: https://vimhelp.org/windows.txt.html#:aboveleft
[`:belowright`]: https://vimhelp.org/windows.txt.html#:belowright
[`:vertical`]: https://vimhelp.org/windows.txt.html#:vertical

When I started using Vim, I often encountered articles about how "people are using tabs wrong" and how buffers are the way you're meant to use Vim e.g. [this][tab-buffer-1]. However, having hidden buffers ([`'hidden'`]) didn't feel right and I kept forgetting which I had open, so this was the setup I eventually settled into.

[`'hidden'`]: https://vimhelp.org/options.txt.html#%27hidden%27
[tab-buffer-1]: https://stackoverflow.com/a/103590/6936976

# Less surprising behaviour

I've got quite a few mappings that make movement and operations behave "as you would expect", or just generally more useful. Firstly, for wrapping:

```vim
noremap <expr> G &wrap ? "G$g0" : "G"
noremap <expr> 0 &wrap ? 'g0' : '0'
noremap <expr> $ &wrap ? "g$" : "$"
noremap <expr> j (v:count == 0 ? 'gj' : 'j')
noremap <expr> k (v:count == 0 ? 'gk' : 'k')
```

And a few for visual mode:

```vim
" Fixed I/A for visual
xnoremap <expr> I mode() ==# 'v' ? "\<c-v>I" : mode() ==# 'V' ? "\<c-v>^o^I" : "I"
xnoremap <expr> A mode() ==# 'v' ? "\<c-v>A" : mode() ==# 'V' ? "\<c-v>Oo$A" : "A"
" Keep selection
xnoremap < <gv
xnoremap > >gv
" Paste without overwriting default register (doesn't work with other registers)
xnoremap p pgvy
```

And a bunch that don't really fit the above two groups:

```vim
" Yank to end of line
nnoremap Y y$
" Escape as normal
tnoremap <esc> <c-\><c-n>
" go to correct column
noremap ' `
" Don't copy single letter deletes
nnoremap x "_x
```

# A grab bag of mappings

Finally, here's a collection of miscellaneous mappings that I use often

```vim
noremap ; :
" Folding
nnoremap <tab> za
" Clear search highlight
nnoremap <silent> <esc> <cmd>nohl<cr>
" for f/F/t/T
noremap , ;
" <cr> mutlitool: follow link in man/help/quickfix, otherwise run recorded macro
map <expr> <return> (or(&buftype == 'help', expand("%:p") =~ '^man://')) ? "\<c-]>" : (&buftype == 'quickfix' ? "\<CR>" : "@q")
" non-saving delete
noremap X "_d
```

# Conclusion

This is the more "core" part of my Vim usage. I plan on going into my many plugins in part 2 (whenever I get around to it).
