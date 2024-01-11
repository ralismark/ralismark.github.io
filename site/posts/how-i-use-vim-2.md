---
layout: post
title: "How I Use Vim #2: Plugins"
excerpt: Vim plugins I use
date: 2021-07-24
tags: uses
series: how-i-use-vim
---

In addition to the things listed in part 1, I also use a number of plugins, including some of my own.
All the ones listed here are github repos, so if you're using a plugin manager like `vim-plug`, you can copy these directly.

# ralismark/vim-recover ⬥ [(link)](https://github.com/ralismark/vim-recover)

This is essentially my personal implementation of [chrisbra/Recover.vim](https://github.com/chrisbra/Recover.vim).
I don't particularly remember what's unique about my version -- I wrote it around a year ago and have since forgotten pretty much everything about it.

Whichever plugin you use, this makes dealing with swapfiles much nicer, particularly deleting old files.
It's also helpful in preventing multiple vim instances from editing the same file (my implementation doesn't do this consistently, but I think I know why).

# mbbill/undotree ⬥ [(link)](https://github.com/mbbill/undotree)

Did you know that Vim [stores a *tree* of changes you do](https://vimhelp.org/undo.txt.html#undo-tree), so changes won't be lost even if you undo then?
However, by default it's pretty difficult to use. This plugin graphically represents this tree, making jumping to changes much easier. Highly recommend!

# junegunn/vim-easy-align ⬥ [(link)](https://github.com/junegunn/vim-easy-align)

This allows you to easily align both expressions and tabular data.

I've been using this plugin for a long time, and while the shortcut system is somewhat unique, it's still very easy to use.
I mostly only use this for CSVs and similar tabular data, but it sees regular use with these formats -- yes the `column(1)` command exists, but this also pretty nice.

# tomtom/tcomment_vim ⬥ [(link)](https://github.com/tomtom/tcomment_vim)

I feel a comment/uncomment plugin is pretty handy, even if the alternative is short (it's like `VjjjI// <esc>`).
Though given how simple the no-plugin method is, I'm not actually sure how often I use this plugin. Nonetheless, It's remained a staple of my plugin list since pretty early.

# tpope/vim-eunuch ⬥ [(link)](https://github.com/tpope/vim-eunuch)

Being able to delete and rename files directly is very handy.
Having files with a `#!` line get auto-chmodded also saves time. A small but really useful plugin!

# sgur/vim-textobj-parameter ⬥ [(link)](https://github.com/sgur/vim-textobj-parameter)

Having function arguments as a first-class text object is incredibly useful!
As I'm writing this, I also realised that it'll work for comma-separated expressions between braces and square brackets as well, which honestly makes it better.

*Note that this depends on [kana/vim-textobj-user](https://github.com/kana/vim-textobj-user)*.
There also [many other text object plugins](https://github.com/kana/vim-textobj-user/wiki) that you might find interesting.

# Sort Motion

This isn't a plugin with a repo, but it's pretty self-contained and there are plugins that do this.

```vim
function! SortMotion(motion)
	if a:motion ==# "line"
		'[,']sort
	elseif a:motion ==# "V"
		exec "normal! \<esc>"
		'<,'>sort
	elseif a:motion ==# "block"
		let [left, right] = sort([virtcol("'["), virtcol("']")], "n")
		let regex = '/\%>' . (left - 1) . 'v.*\%<' . (right + 2) . 'v/'
		exec "'[,']sort" regex "r"
	elseif a:motion ==# "\<c-v>"
		exec "normal! \<esc>"
		let [left, right] = sort([virtcol("'<"), virtcol("'>")], "n")
		let regex = '/\%>' . (left - 1) . 'v.*\%<' . (right + 2) . 'v/'
		exec "'<,'>sort" regex "r"
	elseif type(a:motion) == v:t_number
		exec ".,.+" . a:motion . "sort"
	endif
endfunction

nnoremap gs <cmd>set operatorfunc=SortMotion<cr>g@
nnoremap gss <cmd>call SortMotion(v:count1)<cr>
xnoremap gs <cmd>call SortMotion(mode())<cr>
```

This defines `gs` as an operation that sorts the selected lines.
The visual block ones were a bit hard to get right.

> _Addendum 2023-11-19_
>
> I ended up polishing this into a proper plugin, [opsort.vim](https://github.com/ralismark/opsort.vim).

# Autocomplete/LSP/etc

With Neovim v0.5, LSP support now comes with neovim itself, and that is what I'm using.
There's plenty of other resources about how to set it up, so I'll simply list out what I'm using:

- [neovim/nvim-lspconfig](https://github.com/neovim/nvim-lspconfig)
- [nvim-lua/completion-nvim](https://github.com/nvim-lua/completion-nvim)
- [sirver/ultisnips](https://github.com/sirver/ultisnips)

# End

These are the main plugins that I have installed right now.
I've opted to include more unique or lesser-known ones here, since posts about vim setups are aplenty on the internet.

As always, if you have any questions, feel free to ask me!
