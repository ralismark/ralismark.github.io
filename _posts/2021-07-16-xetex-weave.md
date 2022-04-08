---
layout: post
title: XeTeX, weaved
tags:
excerpt: I build the docs for XeTeX (and some other projects) so you don't have to
---

Pretty much as the subtitle says -- I spent most of today figuring out how to generate a nicely typeset pdf from `xetex.web`. Here's it is -- [XeTeX source documentation for v0.999992]({% link assets/xetex.pdf %})!

<!--more-->

I've also taken the opportunity to weave some more related files:

- [tangle v4.6]({% link assets/tangle.pdf %}), from <https://www.ctan.org/pkg/tangle>
- [weave v4.5]({% link assets/weave.pdf %}), from <https://www.ctan.org/pkg/weave>
- The original [TeX v3.14159265]({% link assets/tex.pdf %})
- [ε-TeX v2.6]({% link assets/etex.pdf %}) (using `weave tex.web etexdir/etex.ch`)
- [bibtex v0.99d]({% link assets/bibtex.pdf %}), from <https://ctan.org/pkg/bibtex> (I had to `sed 's/\\ETs/, and~/'` the .tex file to fix a compile error -- I think pdftex was somehow reading it as `\E Ts` due to there being a `\E` macro for exponentials)
- And [XeTeX v0.999992]({% link assets/xetex.pdf %}) from above

The build process for the most of these is just `weave <input.web> && pdftex <input.tex>`.

For some background, the original TeX code, as well as most of XeTeX, is written in Knuth's literate programming system [Web]. Web files are a mix of Pascal code (extracted using `tangle`) and TeX documentation (extracted using `weave`).

[WEB]: https://en.wikipedia.org/wiki/Web_(programming_system)

# Building

Here's how to build the XeTeX weave

- Clone the XeTeX repo with `git clone --depth 1 https://git.code.sf.net/p/xetex/code`[^green-download].
- If you don't already have `weave` -- which is distinct from `cweave`![^cweave] -- either get it from a pre-built TeXLive install, or build this project. There's no need to build if you already have `weave` though.
- Go to `source/texk/web2c/xetexdir`
- If you run `weave xetex.web`, you'll start getting errors. I've made a patch that fixes these errors -- see below.
- Run `weave xetex.web` -- the output should look something like this:

{: .wrap }
```
$ weave xetex.web
This is WEAVE, Version 4.5 (TeX Live 2021/Arch Linux)
*1*17*25*38*54*76*103*114*132*137*155*187*199*225*229*233*237*246*282*298*319*327*330*351*362*396*436*499*522*546*574*619*628*682*683*722*741*762*814*859*908*937*951*971*994*1019*1032*1081*1107*1188*1260*1351*1382*1390*1392*1449*1676*1677
Writing the output file...*1*17*25*38*54*76*103*114*132*137*155*187*199*225*229*233*237*246*282*298*319*327*330*351*362*396*436*499*522*546*574*619*628*682*683*722*741*762*814*859*908*937*951*971*994*1019*1032*1081*1107*1188*1260*1351*1382*1390*1392*1449*1676*1677
Writing the index...Done.
(No errors were found.)
```

- Finally, run `xetex xetex.tex` to generate `xetex.pdf`.

[^green-download]: Don't download using the big green download button on the project summary page -- that gives you v0.9999.3 from 2013! Though that version builds without needing any syntax fixes.
[^cweave]: Thinking that `cweave` == `weave` caused a lot of headache with building, since you'll get a lot of errors if you use `cweave` instead of `weave`.

# Patch

Here's the patch that fixes the syntax errors for commit `bc89c789 Bump version to 0.999992 (targeted for TL'20).`

```diff {% raw %}
diff --git a/source/texk/web2c/xetexdir/xetex.web b/source/texk/web2c/xetexdir/xetex.web
index 81b450c..7fe4b83 100644
--- a/source/texk/web2c/xetexdir/xetex.web
+++ b/source/texk/web2c/xetexdir/xetex.web
@@ -172,7 +172,9 @@
 %       "reflectedabout((.5[l,r],0),(.5[l,r],1));";
 %     input cmbx10
 %+++++++++++++++++++++++++++++++++++++++++++++++++
-\def\TeXeT{\TeX-{\revrm\beginR\TeX\endR}} % for TeX-XeT
+\def\XeT{X\kern-.125em\lower.5ex\hbox{E}\kern-.1667emT}
+\def\TeXeT{\TeX-\hbox{\revrm \XeT}}   % for TeX-XeT
+\def\TeXXeT{\TeX-\hbox{\revrm -\XeT}} % for TeX--XeT
 \def\PASCAL{Pascal}
 \def\ph{\hbox{Pascal-H}}
 \def\pct!{{\char`\%}} % percent sign in ordinary text
@@ -8638,7 +8640,7 @@ else  begin start_cs: k:=loc; cur_chr:=buffer[k]; cat:=cat_code(cur_chr);
     |goto found|@>
   else @<If an expanded code is present, reduce it and |goto start_cs|@>;
   {At this point, we have a single-character cs name in the buffer.
-   But if the character code is > @"FFFF, we treat it like a multiletter name
+   But if the character code is > @@"FFFF, we treat it like a multiletter name
    for string purposes, because we use UTF-16 in the string pool.}
   if buffer[loc]>@"FFFF then begin
     cur_cs:=id_lookup(loc,1); incr(loc); goto found;
@@ -9054,7 +9056,6 @@ else begin
   end;
 goto restart;
 end
-@z

 @ @<Complain about an undefined macro@>=
 begin print_err("Undefined control sequence");
@@ -14745,7 +14746,7 @@ end_node_run: {now |r| points to first |native_word_node| of the run, and |p| to
         link(p):=null;
         { Extract any "invisible" nodes from the old list and insert them after the new node,
           so we don't lose them altogether. Note that the first node cannot be one of these,
-          as we always start merging at a native_word node. }
+          as we always start merging at a |native_word| node. }
         prev_p := r;
         p := link(r);
         while p <> null do begin
@@ -15268,7 +15269,7 @@ while font_ptr>font_base do
   decr(font_ptr);
   end

-@* \[32b] \pdfTeX\ output low-level subroutines (equivalents)
+@* \[32b] \pdfTeX\ output low-level subroutines (equivalents).

 @<Glob...@>=
 @!epochseconds: integer;
@@ -21298,7 +21299,7 @@ terminating node $p_m$. All characters that do not have the same font as
 $c_1$ will be treated as nonletters. The |hyphen_char| for that font
 must be between 0 and 255, otherwise hyphenation will not be attempted.
 \TeX\ looks ahead for as many consecutive letters $c_1\ldots c_n$ as
-possible; however, |n| must be less than max_hyphenatable_length+1, so a character that would
+possible; however, |n| must be less than |max_hyphenatable_length|+1, so a character that would
 otherwise be $c_{max\_hyphenatable\_length+1}$ is effectively not a letter. Furthermore $c_n$ must
 not be in the middle of a ligature.  In this way we obtain a string of
 letters $c_1\ldots c_n$ that are generated by nodes $p_a\ldots p_b$, where
@@ -24427,7 +24428,7 @@ collected:
       measure that space in context and replace it with an adjusted glue value
       if it differs from the font's normal space. }

-    { First we look for the most recent native_word in the list and set |main_pp| to it.
+    { First we look for the most recent |native_word| in the list and set |main_pp| to it.
       This is potentially expensive, in the case of very long paragraphs,
       but in practice it's negligible compared to the cost of shaping and measurement. }
     main_p := head;
@@ -24443,9 +24444,9 @@ collected:
         main_p := link(main_pp);

         { Skip nodes that should be invisible to inter-word spacing,
-          so that e.g. |\nobreak\ | doesn't prevent contextual measurement.
+          so that e.g. `\nobreak` doesn't prevent contextual measurement.
           This loop is guaranteed to end safely because it'll eventually hit
-          |tail|, which is a native_word node, if nothing else intervenes. }
+          |tail|, which is a |native_word| node, if nothing else intervenes. }
         while node_is_invisible_to_interword_space(main_p) do
           main_p := link(main_p);

@@ -24459,7 +24460,7 @@ collected:

           if main_ppp = tail then begin
             { We found a candidate inter-word space! Collect the characters of both words,
-              separated by a single space, into a native_word node and measure its overall width. }
+              separated by a single space, into a |native_word| node and measure its overall width. }
             temp_ptr := new_native_word_node(main_f, native_length(main_pp) + 1 + native_length(tail));
             main_k := 0;
             for t := 0 to native_length(main_pp)-1 do begin
@@ -33335,8 +33336,8 @@ sparse array of the up to 32512 additional registers of each kind,
 one for inter-character token lists at specified class transitions, and
 one for the sparse array of the up to 32767 additional mark classes.
 The root of each such tree, if it exists, is an index node containing 64
-pointers to subtrees for 64^4 consecutive array elements.  Similar index
-nodes are the starting points for all nonempty subtrees for 64^3, 64^2,
+pointers to subtrees for $64^4$ consecutive array elements.  Similar index
+nodes are the starting points for all nonempty subtrees for $64^3$, $64^2$,
 and 64 consecutive array elements.  These four levels of index nodes are
 followed by a fifth level with nodes for the individual array elements.

{% endraw %}```
