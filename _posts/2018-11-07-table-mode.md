---
layout: post
title: Emulating table mode on Casio fx-82AU (and variants)
tags: math
excerpt: Making a table of values by creating a for loop
---

Table mode is a mode available on my old calculator which essentially produced a table of values. This mode is not present on board-approved calculators (like the fx-82AU and similar variants), but I have found a way to essentially produce something similar to it, making obtaining a sequence of numbers much easier.

<!--more-->

Before actually getting to table mode, I'll explain 2 features required for this: variables, and the colon. If you already understand one or both of these, skip to the relevant sections.

# Variables

The fx-82AU has 9 variables: A to F, X, Y, and M. All of these can store a number, which is kept between expressions and even restarts. Typically, these can be either used for numeric constants (often in the sciences e.g. storing the charge of an electron, or the ideal gas constant), or for intermediate steps of a longer calculation. Using a variable is as simple as entering it with <kbd>Alpha</kbd> and the corresponding key. Storing a variable is done using <kbd>STO</kbd> (i.e. <kbd>Shift</kbd> <kbd>RCL</kbd>), followed by the button labelled with the variable (but without Alpha). For example, X is set using <kbd>Shift</kbd> <kbd>RCL</kbd> <kbd>)</kbd>.

The way variable setting seems to work is by adding the → symbol followed by the variable, then evaluating it (pressing <kbd>=</kbd>). Ans is inserted before this if required. This allows the variable to be set again if the expression is re-entered through history and evaluated. The fact that it works through appending symbols is important for table mode, though variables are still very useful in normal use.

# The Colon

The colon (entered through <kbd>Alpha</kbd> <kbd>x³</kbd>) is probably one of the least used symbols. What this does, is it evaluates each sub-expression separated by the colon in sequence, advancing when <kbd>=</kbd> is pressed and starting from the beginning after reaching the end. For example, continually pressing <kbd>=</kbd> after entering Ans+1:Ans+2, when Ans was 0, produces 1, 3, 4, 6, 7, 9, etc. Multiple sub-expressions can be used, such as $$1:2:3:4:5$$. Notably, each expression is re-evaluated each time instead of recalling from history, allowing more interesting things to be done.

# Table mode

Firstly, set X to 0. Then, enter the expression you want in terms of X (say $$X^2+3$$), then the colon, then X+1. After this, the input should be $$X^2+3:X+1$$. Then, enter the button sequence required to save to X. This will produce the value of the expression at X=0. Repeatedly pressing equals alternates between showing the updated value of X, and the value of the expression there.

How this works is a combination of the colon (which has the lowest precedence) and the →X symbols produced when saving a variable. As such, repeatedly pressing <kbd>=</kbd> alternates between evaluating $$X^2+3$$ (producing the value at X) and $$X+1 \rightarrow X$$ (incrementing X). This is effectively a for-loop.

This technique can be expanded to evaluate multiple expressions (e.g. ones with plus or minus). To do this, enter the expressions, separated by colons, instead of the single expression entered above. For example, $$4X+1:4X-1:X+1→X$$. The first and the second expression are evaluated in each iteration of the loop. The initial value can be changed by having a different X prior to starting the loop. Different steps for X can be used by changing the +1 in the final sub-expression (e.g. to $$X-1→X$$).

# Conclusion

Congratulations, you have turned a non-programmable calculator into a programmable calculator!

There are probably other applications of this technique, but I can't think of anything too different right now. Anyways, remember that knowing how to use your calculator will benefit you greatly.
