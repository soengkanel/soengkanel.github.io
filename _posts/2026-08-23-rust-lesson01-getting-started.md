---
layout: post
title: "[Rust] Lesson 1: Why Rust, and Your First Program"
date: 2026-08-23 09:00:00 +0700
categories: rust
tags: [rust, programming, beginner, lesson-1]
---

Welcome to the first lesson of this practical Rust series. This lesson is for students who already know at least one programming language (Python, JavaScript, C, Java — anything). By the end, you will have Rust installed on your computer, understand *why* Rust exists, and have written and run your first two Rust programs.

I will not waste your time with theory you don't need yet. Everything in this lesson is something you will use in every Rust program you ever write.

---

# 1. Why does Rust exist?

Before you learn *how* to write Rust, you should understand *why* it exists. Otherwise you will fight the language instead of using it.

## The problem Rust solves

Every programming language has to answer one question: **who cleans up memory when you are done with it?**

There are two traditional answers, and both have serious problems.

**Answer 1 — "You clean it up yourself." (C, C++)**

You get maximum speed and full control. But if you forget to clean up, you leak memory. If you clean up too early, your program crashes. If you clean up twice, it crashes. If two parts of your code try to change the same data at the same time, you get bugs that only appear in production at 3 AM.

Roughly **70% of all security vulnerabilities** in Chrome, Windows, and iOS come from this class of bug. This is not an exaggeration — Microsoft and Google have both published this number.

**Answer 2 — "A garbage collector cleans it up for you." (Python, Java, JavaScript, Go)**

Safe and easy. But now a background process pauses your program at random moments to sweep up unused memory. For a web app this is fine. For a video game, a stock trading system, or an operating system kernel, those pauses are unacceptable.

**Rust's answer — "The compiler proves your code is safe *before* it runs."**

There is no garbage collector. There is also no way to accidentally free memory twice or use memory after freeing it. The Rust compiler refuses to compile programs that could do these things.

> **Real-life analogy.** Imagine a busy kitchen.
>
> - **C/C++** is a kitchen where every chef grabs whatever knife they want, whenever they want. Fast, but people get cut.
> - **Python/Java** is a kitchen with a manager who wanders around collecting dirty knives every few minutes. Safer, but everyone freezes when the manager walks through.
> - **Rust** is a kitchen with a strict rule enforced *at the door*: only one chef can hold a specific knife at a time, and when they're done, the knife is automatically returned to the drawer. No manager needed, no accidents.

## Who uses Rust in production?

- **Microsoft** — rewriting parts of Windows in Rust
- **Linux kernel** — accepts Rust code since 2022
- **Discord** — replaced Go with Rust to eliminate latency spikes
- **Cloudflare** — powers a large part of their edge network
- **Firefox** — the CSS engine is written in Rust
- **Amazon** — Firecracker (the tech behind AWS Lambda) is Rust

This is not a toy language. Learning it makes you employable.

---

# 2. Installing Rust

Rust is installed through a tool called **`rustup`**. Never install Rust from your OS package manager (`apt`, `brew`, `winget`) — you will end up with an outdated version and confusion.

**On macOS / Linux:**

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**On Windows:**

Go to [https://rustup.rs](https://rustup.rs) and download `rustup-init.exe`. Run it and accept the defaults.

After installation, **close and reopen your terminal**, then verify:

```bash
rustc --version
cargo --version
```

You should see something like:

```
rustc 1.85.0 (a1b2c3d4e 2026-01-15)
cargo 1.85.0 (f6g7h8i9j 2026-01-10)
```

If both commands work, you are ready.

---

# 3. Meet Cargo — your project manager

`rustc` is the Rust compiler. You will almost never call it directly. Instead, you will use **Cargo**.

Cargo is Rust's build tool and package manager. Think of it as:
- `npm` + `webpack` if you come from JavaScript
- `pip` + `venv` + `setuptools` if you come from Python
- `make` + `apt` if you come from C

But unlike those, Cargo ships *with* Rust. Every Rust developer uses it. Every Rust project uses it. Learn Cargo, and you know how every Rust project works.

Let's create a project.

```bash
cargo new hello_world
cd hello_world
```

Cargo has created a folder for you. Let's look at it:

```
hello_world/
├── Cargo.toml      ← project settings & dependencies
├── .gitignore      ← Cargo initialized a git repo for you
└── src/
    └── main.rs     ← your code goes here
```

Two files matter right now:

**`Cargo.toml`** — the project manifest. Open it:

```toml
[package]
name = "hello_world"
version = "0.1.0"
edition = "2024"

[dependencies]
```

This is like `package.json` (JS) or `pyproject.toml` (Python). When you want to use a library, you add it under `[dependencies]`.

**`src/main.rs`** — your program's entry point. Cargo has already written a "Hello, world!" for you:

```rust
fn main() {
    println!("Hello, world!");
}
```

---

# 4. Running your first program

From inside the `hello_world` folder:

```bash
cargo run
```

You should see:

```
   Compiling hello_world v0.1.0 (/path/to/hello_world)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.42s
     Running `target/debug/hello_world`
Hello, world!
```

Congratulations — you just wrote, compiled, and ran a Rust program.

## The three commands you will use every day

| Command | What it does | When to use |
|---|---|---|
| `cargo check` | Type-checks your code but does *not* produce a binary | While writing — much faster than a full build |
| `cargo build` | Compiles your code into a binary in `target/debug/` | When you want an executable but not run it yet |
| `cargo run` | Builds *and* runs your program | Most of the time, especially while learning |

There is also `cargo build --release` for optimized production builds, but ignore that for now.

## Reading the "Hello, world!" line by line

```rust
fn main() {
    println!("Hello, world!");
}
```

- **`fn`** — declares a function. Short for "function". Same idea as `def` in Python or `function` in JavaScript.
- **`main`** — the special function name Rust looks for when starting your program. Every executable Rust program must have exactly one `main`.
- **`()`** — this function takes no arguments.
- **`{ ... }`** — the function body, wrapped in curly braces.
- **`println!`** — prints a line to the terminal. The **`!`** at the end means this is a **macro**, not a regular function. For now, just remember: `println!` needs a `!`. You will learn what macros really are in a later lesson.
- **`;`** — every statement ends with a semicolon. Rust is strict about this.

---

# 5. Variables — immutable by default

This is where Rust starts to feel different from Python or JavaScript.

Open `src/main.rs` and replace its contents with:

```rust
fn main() {
    let age = 25;
    println!("My age is {age}");
}
```

Run it with `cargo run`. You should see `My age is 25`.

Two things to notice:

**a) `let` declares a variable.** Simple.

**b) `{age}` inside the string** is Rust's way of interpolating a variable — like Python's f-strings (`f"My age is {age}"`) or JavaScript's template literals (`` `My age is ${age}` ``).

Now try to *change* the variable. Modify your code:

```rust
fn main() {
    let age = 25;
    age = 26;                          // try to change it
    println!("My age is {age}");
}
```

Run it. Rust will refuse to compile:

```
error[E0384]: cannot assign twice to immutable variable `age`
```

**In Rust, variables are immutable by default.** Once you set them, they cannot change.

This surprises people coming from Python or JavaScript. But there is a good reason.

> **Real-life analogy.** Think of a Rust variable like your **national ID number**. Once it's assigned to you, it does not change. If you *really* need to change it (a new passport, a legal name change), you must go through an explicit process — you can't just cross it out with a pen.
>
> A `let mut` variable is like your **home address**. It's expected to change over time. You mark it as "will change" from the start.

To make a variable changeable, add the keyword `mut`:

```rust
fn main() {
    let mut age = 25;
    age = 26;                          // now this works
    println!("My age is {age}");
}
```

## Why does Rust do this?

Because most bugs come from data changing when you didn't expect it to. Making immutability the default forces you to *think* every time you want mutation. In practice, you will find that most of your variables can stay immutable — and your code becomes easier to reason about.

## Shadowing — a related trick

Rust also lets you re-declare a variable with the same name using `let` again. This is called **shadowing**:

```rust
fn main() {
    let count = 5;
    let count = count + 1;             // shadowing: new variable named `count`
    let count = count * 2;
    println!("count = {count}");       // prints: count = 12
}
```

Each `let count` creates a *brand new* variable that just happens to reuse the name. This is different from `mut` — with shadowing, you can even change the type:

```rust
let input = "42";                      // input is a string
let input: i32 = input.parse().unwrap(); // input is now a number
```

Try doing that in a statically typed language like Java. You can't.

---

# 6. A practical example — coffee shop order

Let's write something that feels like a real program. Replace `src/main.rs` with this:

```rust
fn main() {
    // Menu prices in dollars
    let coffee_price = 2.50;
    let cake_price = 3.75;

    // Customer's order
    let coffees_ordered = 2;
    let cakes_ordered = 1;

    // Calculate subtotal
    let subtotal = (coffee_price * coffees_ordered as f64)
                 + (cake_price * cakes_ordered as f64);

    // Apply 10% tax
    let tax_rate = 0.10;
    let tax = subtotal * tax_rate;
    let total = subtotal + tax;

    println!("=== Coffee Shop Receipt ===");
    println!("Coffees: {coffees_ordered} x \${coffee_price}");
    println!("Cakes:   {cakes_ordered} x \${cake_price}");
    println!("---------------------------");
    println!("Subtotal: \${subtotal:.2}");
    println!("Tax:      \${tax:.2}");
    println!("Total:    \${total:.2}");
}
```

Run it with `cargo run`. You should see:

```
=== Coffee Shop Receipt ===
Coffees: 2 x $2.5
Cakes:   1 x $3.75
---------------------------
Subtotal: $8.75
Tax:      $0.88
Total:    $9.62
```

There are three new things here worth pointing out:

**`as f64`** — Rust does not automatically convert between number types. `coffees_ordered` is an integer, `coffee_price` is a floating-point number, and Rust refuses to multiply them directly. The `as f64` tells the compiler: "convert this integer to a 64-bit float". This strictness catches bugs where you accidentally lose precision.

**`{subtotal:.2}`** — inside the interpolation braces, `:.2` means "format with 2 decimal places". Same as Python's `f"{x:.2f}"`.

**Nothing is marked `mut`.** Every value in this program is set once and never changes. This is *idiomatic* Rust — you should always try to write your code this way first, and only add `mut` when you truly need it.

---

# 7. Exercises

Try these before moving to Lesson 2. The point is muscle memory — don't just read them.

**Exercise 1 — Warm up.** Change the greeting.

Modify the "Hello, world!" program to print your own name and today's date on two separate lines.

<details markdown="1">
<summary>Show hint</summary>

You can call `println!` twice. Each call prints one line.

</details>

**Exercise 2 — Rectangle area.** Write a program that stores the width and height of a rectangle, then prints its area and perimeter. Use immutable variables.

<details markdown="1">
<summary>Show solution</summary>

```rust
fn main() {
    let width = 8.0;
    let height = 5.0;

    let area = width * height;
    let perimeter = 2.0 * (width + height);

    println!("Width:     {width}");
    println!("Height:    {height}");
    println!("Area:      {area}");
    println!("Perimeter: {perimeter}");
}
```

</details>

**Exercise 3 — The mut check.** Take this broken code and fix it *without* using `mut`. Then fix it again, this time using `mut`. Notice which version reads more clearly.

```rust
fn main() {
    let score = 0;
    score = score + 10;
    score = score + 25;
    println!("Final score: {score}");
}
```

<details markdown="1">
<summary>Show both solutions</summary>

**Without `mut` (using shadowing):**

```rust
fn main() {
    let score = 0;
    let score = score + 10;
    let score = score + 25;
    println!("Final score: {score}");
}
```

**With `mut`:**

```rust
fn main() {
    let mut score = 0;
    score = score + 10;
    score = score + 25;
    println!("Final score: {score}");
}
```

Both compile. For a running total that keeps changing, `mut` is usually clearer. Shadowing is better when you're *transforming* a value into something new (like parsing a string into a number).

</details>

---

# 8. What you learned today

- **Why Rust exists** — memory safety without a garbage collector, proven at compile time
- **How to install Rust** — always through `rustup`, never through your OS package manager
- **Cargo** — the one build tool and package manager every Rust project uses
- **The three daily commands** — `cargo check`, `cargo build`, `cargo run`
- **The structure of `fn main`** and what `println!` does
- **Variables are immutable by default** — use `mut` when you truly need mutation
- **Shadowing** — reusing a name with a new `let`, even changing the type

# 9. What's next

In Lesson 2 we will look at **Rust's type system** — the different number types, booleans, characters, strings, and why Rust distinguishes between `String` and `&str`. You will also meet Rust's most famous feature: **ownership**. That's when Rust really starts to feel different from any other language you've used.

Before then, spend 20 minutes writing small programs. Print things, do arithmetic, use variables. Get comfortable with `cargo run`. The rest of the series will be much easier if you have this basic loop in your fingers.

See you in Lesson 2.
