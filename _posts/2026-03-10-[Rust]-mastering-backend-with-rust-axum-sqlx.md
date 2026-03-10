---
layout: post
title: "[Rust] Mastering Backend Development: A Deep Dive into Rust, Axum, and SQLx"
date: 2026-03-10
categories: [Rust]
description: "Learn how to build high-performance, type-safe web services using the modern Rust ecosystem."
image: /rust.jpg
---

# Why Rust for the Modern Web?

In the ever-evolving landscape of backend development, performance and safety are no longer optional—they are requirements. Rust has emerged as a powerhouse for building web services that are both blazingly fast and remarkably safe.

By combining **Axum** (a modular web framework) and **SQLx** (compile-time checked SQL), we can build applications that catch bugs before they even run.

## 1. Setting Up Your Rust Environment

First, create a new project:

```bash
cargo new rust-axum-tutorial
cd rust-axum-tutorial
```

Add these dependencies to your `Cargo.toml`:

```toml
[dependencies]
axum = "0.7"
tokio = { version = "1.0", features = ["full"] }
sqlx = { version = "0.7", features = ["runtime-tokio-rustls", "postgres", "macros"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tracing = "0.1"
tracing-subscriber = "0.3"
```

## 2. Your First Axum Server

Axum makes it incredibly easy to define routes. Let's create a basic "Hello World" handler.

```rust
use axum::{routing::get, Router};

#[tokio::main]
async fn main() {
    // Build our application with a single route
    let app = Router::new().route("/", get(|| async { "Hello from Axum!" }));

    // Run it with hyper on localhost:3000
    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();
    println!("Listening on http://localhost:3000");
    axum::serve(listener, app).await.unwrap();
}
```

## 3. Persistent Data with SQLx

SQLx is unique because it checks your SQL queries against your database schema during compilation. 

### Connecting to the Database

```rust
use sqlx::postgres::PgPoolOptions;

let pool = PgPoolOptions::new()
    .max_connections(5)
    .connect("postgres://user:password@localhost/dbname")
    .await
    .expect("Failed to connect to Postgres.");
```

### Performing a Type-Safe Query

```rust
let row: (i64,) = sqlx::query_as("SELECT count(*) FROM users")
    .fetch_one(&pool)
    .await?;
```

## 4. Bringing It All Together: The User API

Here is a simplified example of a handler that fetches a user from the database and returns it as JSON.

```rust
use axum::{extract::State, Json, response::IntoResponse};
use serde::{Serialize, Deserialize};
use sqlx::PgPool;

#[derive(Serialize)]
struct User {
    id: i32,
    username: String,
}

async fn get_user(
    State(pool): State<PgPool>,
) -> impl IntoResponse {
    let user = sqlx::query_as!(User, "SELECT id, username FROM users LIMIT 1")
        .fetch_one(&pool)
        .await
        .unwrap();

    Json(user)
}
```

## Conclusion

This is just the tip of the iceberg. Rust's ecosystem provides unparalleled control over memory and concurrency. In the following parts of this series, we will explore:
- Middleware for Authentication (JWT)
- Complex Database Migrations
- Deploying to the Cloud with Docker

Stay tuned for more!
