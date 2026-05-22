---
layout: post
title: "Understanding Ownership in Rust"
date: 2026-05-22 21:25:00 +0700
categories: rust
---

Imagine you have **one toy car** 🚗.

Your mom says:

> “Kanel, this toy car belongs to YOU. You are the owner.”

That means:

* You can play with it
* You can give it away
* You can throw it away
* Only ONE person owns it at a time

That is the idea of **ownership** in Rust programming language.

---

# Ownership in Rust = “Who owns the toy?”

Rust wants to always know:

> “Who is responsible for this data?”

Because computers have memory, and Rust wants memory to stay clean and safe.

---

# Example with String

```rust
let name = String::from("Kanel");
```

Rust creates a real string in memory.

Now:

* variable `name`
* OWNS the string `"Kanel"`

Like:

```text
name ---> "Kanel"
```

`name` is the owner.

---

# What happens when ownership moves?

```rust
let name1 = String::from("Kanel");
let name2 = name1;
```

Now ownership moves to `name2`.

Like giving your toy car to your friend.

```text
Before:
name1 ---> "Kanel"

After:
name2 ---> "Kanel"
name1 ❌ no longer owns it
```

So this will ERROR:

```rust
println!("{}", name1);
```

Because `name1` no longer owns the data.

Rust says:

> “You already gave the toy away!”

---

# Why does Rust do this?

To prevent dangerous problems like:

* two people deleting same memory
* memory leaks
* crashes
* bugs

Rust is very strict so your program becomes super safe.

---

# Now what is `&str`?

`&str` is DIFFERENT.

It does NOT own the string.

It only BORROWS it.

Like this:

---

# Real Life Example of Borrowing

Imagine your friend owns a book 📖.

You ask:

> “Can I read it for a moment?”

You are borrowing.

You can read it,
but it is NOT yours.

That is `&str`.

---

# Example

```rust
let name = String::from("Kanel");

let borrowed = &name;
```

Now:

```text
name owns the string
borrowed only looks at it
```

Like:

```text
Owner:
name ---> "Kanel"

Borrower:
borrowed ---> looks at "Kanel"
```

Both can use it safely because:

* only `name` owns it
* `borrowed` only reads it

---

# Super Simple Difference

| Type     | Owns Data? | Like         |
| -------- | ---------- | ------------ |
| `String` | ✅ Yes      | Your toy     |
| `&str`   | ❌ No       | Borrowed toy |

---

# Another Realistic Example

## `String`

```rust
let food = String::from("Pizza");
```

You BOUGHT the pizza 🍕

You own it.

---

## `&str`

```rust
let food = "Pizza";
```

Rust gives you a reference to some text already stored somewhere.

You can read it,
but you are not the real owner.

Like reading a restaurant menu.

You can SEE `"Pizza"` but you do not own the menu.

---

# Important Memory Idea

## `String`

* flexible
* grow/shrink
* stored in heap memory
* owned

```rust
let mut s = String::from("Hi");
s.push_str(" Kanel");
```

Now:

```text
"Hi Kanel"
```

You changed it because you own it.

---

## `&str`

Usually fixed and read-only.

```rust
let s = "Hi";
```

Cannot easily grow.

Because you do not own it.

---

# Easy Rule to Remember

## String

> “I OWN the text.”

## &str

> “I only BORROW the text.”

---

# Visual Diagram

```text
String
======

owner
  |
  v
"Kanel"


&str
====

owner ------> "Kanel"
borrow -----> "Kanel"
```

Only one owner.
Many borrowers allowed.

---

# Why This Matters

Rust uses ownership to make programs:

* fast ⚡
* safe 🛡️
* no garbage collector needed
* fewer crashes

This is why Rust is famous.

---

# Tiny Practice

Can you guess?

```rust
let a = String::from("Apple");
let b = a;
```

Who owns `"Apple"` now?

Answer:

```text
b owns it
a lost ownership
```

---

# Golden Rule

> Ownership = who is responsible for the data.
>
> `String` owns.
>
> `&str` borrows.
