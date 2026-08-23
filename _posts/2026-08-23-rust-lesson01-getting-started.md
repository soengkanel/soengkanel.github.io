---
layout: post
title: "[Rust] Lesson 1: Why Rust, and Your First Program"
date: 2026-08-23 09:00:00 +0700
categories: rust
tags: [rust, programming, beginner, lesson-1]
---

# Why Rust

Every language answers one question: **who cleans up memory?**

- **C** — you do. Miss it, you get crashes.
- **Python, Java** — a collector does. Safe, but it pauses your program.
- **Rust** — the compiler proves your code is safe *before* it runs. No collector, no pauses, no crashes.

That's the whole reason.

---

# Install

Go to [rustup.rs](https://rustup.rs). Run the installer.

```bash
cargo --version
```

If that works, you're ready.

---

# Your first program

```bash
cargo new hello
cd hello
cargo run
```

You just wrote, compiled, and ran Rust. Open `src/main.rs`:

```rust
fn main() {
    println!("Hello, world!");
}
```

- `fn main` — where the program starts.
- `println!` — prints a line. The `!` means macro. Ignore for now.

---

# Variables don't change

```rust
let age = 25;
age = 26;   // ERROR
```

Once set, it stays. To allow change, say so:

```rust
let mut age = 25;
age = 26;   // OK
```

> `let` is your birth date. `let mut` is your phone number.

Use plain `let` by default. Add `mut` only when you must.

---

# A real program

```rust
fn main() {
    let price = 2.50;
    let cups = 3;
    let total = price * cups as f64;
    println!("Total: \${total:.2}");
}
```

- `cups as f64` — Rust won't mix integers and floats silently. Convert explicitly.
- `{total:.2}` — two decimal places.

---

# Try it

1. Print your name and today's date on two lines.
2. Compute a rectangle's area. No `mut`.
3. Fix without `mut`:

```rust
let score = 0;
score = score + 10;
```

<details markdown="1">
<summary>Answer</summary>

```rust
let score = 0;
let score = score + 10;
```

Re-declaring with `let` is called **shadowing**.

</details>

---

# Next

Types, strings, and **ownership** — the feature that makes Rust Rust.
