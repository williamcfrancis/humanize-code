# Rust: humanize-code reference

Read this with SKILL.md before editing Rust code beyond comments. Claims marked (run) were checked on rustc 1.99.1 through the Rust Playground; the rest come from the official docs or the named crate's docs.

## Tells

- **Clone to quiet the borrow checker** (§20, medium). Watch for `.clone()` on a value never used again, on a `Copy` type, or just before the only use. Remove it only when all of these hold. The build passes without it. Every `Clone` it reaches is derived or from std: a derived `Clone` calls each field's `Clone`, so a hand-written one on a field still ran and printed (run). Nothing observable happens when the value or any field drops (guards, spans, files). Neither the type nor any field holds an `Rc` or `Arc`: cloning a struct with an `Arc` field raised the strong count from 2 to 3 (run).
  ```rust
  // before (Config holds plain data: derived Clone all the way down, no Drop side effects, no Rc or Arc)
  fn save(cfg: Config) {
      let cfg2 = cfg.clone();
      write_config(cfg2);
  }
  // after
  fn save(cfg: Config) {
      write_config(cfg);
  }
  ```
- **to_string and to_owned to make types line up** (§20, weak alone). When the parameter is a concrete `&str`, `log_line(&name.to_string())` becomes `log_line(name)` if `name` is a `&str`, and `log_line(&name)` if it is a `String`; passing the `String` itself does not compile (run).
- **Doc comments on everything** (§6, medium). `# Arguments` lists (`` * `user` - The user. ``) and `# Returns` sections on private helpers. The Rust API guidelines ask for an example on every public item and for Errors, Panics and Safety sections (C-EXAMPLE, C-FAILURE, https://rust-lang.github.io/api-guidelines/documentation.html); they never mention an Arguments section. Delete restating docs on private items unless a derive or attribute macro reads them (see Comments that do things); where clippy's `missing_docs_in_private_items` is on, shrink them to one line instead. On public items, shrink them to one line: `missing_docs` checks those items when it is set to warn or deny (crate attribute, or `[lints.rust]` in Cargo.toml from Cargo 1.74). Keep `# Safety`, `# Errors`, `# Panics` and every code block.
- **Narrated SAFETY comments** (§7, report only). SKILL.md §7 keeps `// SAFETY:` comments on `unsafe`. Do not delete, shorten, reword or move one; report the narration instead.
- **Shapes clippy already flags** (§20, weak alone). `return x;` as the last statement, `if done == true`, `match opt { Some(v) => Some(f(v)), None => None }`, `v.len() == 0`, `fn f<'a>(s: &'a str) -> &'a str`, `&Vec<T>` and `&String` parameters; clippy flagged each (run). Apply clippy's machine-applicable fixes after the checks in Safe modernizations. Change `&Vec<T>` to `&[T]` only on private functions whose body uses it only as a slice (`size_of_val` gave 24 for a `&Vec<i32>` of five items and 20 for the same items as `&[i32]`, run); report it on `pub` items.
- **Silent defaults, unwrap and expect** (§12, report only). `.unwrap_or_default()` on a parse result, `.unwrap()` in library code, `.expect("Failed to read file")`. Each decides whether a failure panics, returns or vanishes.
- **Box<dyn Error> or String errors everywhere** (§19, report only). `Result<T, Box<dyn Error>>` in a library, `Result<T, String>` with `map_err(|e| e.to_string())?`. Changing it changes the API and printed output.
- **Machinery for one thread or one call** (§13, weak alone, report only). `Arc<Mutex<T>>` that never crosses a thread, `async fn` with no `.await`.
- **dbg!, println! progress, emoji** (§22 medium, §4 one sighting). `dbg!` prints to stderr in release builds too, and `dbg!(expr)` moves and returns `expr` (`dbg!(a, b)` returns a tuple), so replace it with the expression, not with nothing (https://doc.rust-lang.org/std/macro.dbg.html).
- **#[allow(dead_code)] over unused code** (§15, medium). Delete an item only if it is private and dead under every feature set, target and test build, since code behind a `cfg` is checked only when compiled. Report dead fields instead of deleting them: the lint ignores derived `Debug` and `Clone`, so a field it called never read still printed in `{:?}` output (run), and removing one changes the struct's size.

## What people write instead

- `?` with a typed error enum (often `thiserror`) in libraries; `anyhow::Result` with `.context(...)` in binaries.
- Borrowed parameters where the callee only reads: `&str`, `&[T]`, `&Path`, `impl AsRef<Path>`.
- Iterator chains for transforms, `for` loops for side effects, `.cloned()` and `.copied()`.
- `if let`, `let ... else` (1.65+), `matches!`, `Option::map`, `and_then`, `is_some_and` (1.70+).
- Docs on public items: a summary line and a runnable example. Few comments inside bodies.

## Comments that do things

- Doc comments: `///`, `//!`, `/** */`, `/*! */`. They are `#[doc]` attributes. Rustdoc renders them, `missing_docs` and clippy's `missing_safety_doc` read them, and derive macros turn them into behavior: clap uses them as `--help` text (run), schemars as schema descriptions, displaydoc as the `Display` output, and cbindgen reads `/// cbindgen:` annotations. Check an item's derives and attribute macros first.
- Code blocks in doc comments are doctests, including the fence info (`ignore`, `no_run`, `should_panic`, `compile_fail`, `edition2021`) and hidden `# ` lines. A README included with `#[doc = include_str!("../README.md")]` is tested too.
- `// SAFETY:` above `unsafe` blocks and impls. Clippy's `undocumented_unsafe_blocks` looks for `SAFETY:` (any case, colon required) in the comment lines above the block: it skipped blank lines, accepted `// safety:`, and failed on `// SAFETY -` or with a line of code in between (run). `unnecessary_safety_comment` flags one on safe code. Both are restriction lints; check whether the repo enables them.
- Doc headings that lints read: `# Safety`, `# Errors`, `# Panics`.
- Script headers: the shebang, rust-script's `//! ```cargo` manifest block, and a cargo script's `---` frontmatter.
- UI test annotations: `//@ compile-flags: ...`, `//@ check-pass`, `//~ ERROR ...` (rustc, clippy, and crates using `ui_test`).
- `@generated` near the top of a file (rustfmt skips it when `format_generated_files = false`), license and `SPDX-License-Identifier` headers, and any marker CI passes to grcov's `--excl-line`, `--excl-start` or `--excl-stop`.

## Looks cosmetic, isn't

- **Removing a clone moves the value**, so Drop runs elsewhere: with `consume(a.clone())`, `a` dropped at the end of the caller's scope; with `consume(b)`, inside the callee (run). Removing an `Rc` or `Arc` clone changes the strong count, which decides what `get_mut`, `try_unwrap` and `make_mut` do (https://doc.rust-lang.org/std/rc/struct.Rc.html).
- **Renaming `let _guard = lock()` to `let _ = lock()`** drops the value at once, because `_` does not bind (run; https://doc.rust-lang.org/reference/patterns.html).
- **Moving `m.lock().unwrap().len()` into the tail,** out of `let n = ...; n` or `return ...;`. In edition 2021, tail temporaries drop after the block's locals, so another local's Drop saw the mutex still locked; with `let` or `return`, or in 2024, it did not (run; https://doc.rust-lang.org/edition-guide/rust-2024/temporary-tail-expr-scope.html). Clippy's `let_and_return` and `needless_return` skipped both shapes while flagging plain ones, so make these edits only where clippy suggests them (run).
- **`if let ... else` rewritten as `match`, or back.** Edition 2024 drops `if let` scrutinee temporaries before `else`; `match` keeps them to the end of the statement. Under 2024, with `*lock.read().unwrap()`, `try_write()` succeeded in the `else` and failed in the `match`'s `None` arm (run; https://doc.rust-lang.org/edition-guide/rust-2024/temporary-if-let-scope.html).
- **`unwrap_or(f())` versus `unwrap_or_else(f)`.** The argument runs even for `Some` (run). The same holds for `map_or`, `ok_or` and `or` (https://doc.rust-lang.org/std/option/enum.Option.html).
- **A `for` loop turned into `.for_each`.** `return` in the closure ends only that element: the loop that stopped at 0 collected `[1]`, the `for_each` collected `[1, 2]` (run). An unconsumed `.map` runs nothing (https://doc.rust-lang.org/std/iter/index.html#laziness).
- **`.unwrap()` to `?`** turns a panic into an early `Err` return (https://doc.rust-lang.org/reference/expressions/operator-expr.html). Editing an `expect` or `panic!` message can break `#[should_panic(expected = "...")]`, which matches a substring (https://doc.rust-lang.org/reference/attributes/testing.html).
- **`Box<dyn Error>` to `anyhow::Error` in `main`.** `main` prints `Error: {err:?}`: `Error: Os { code: 2, kind: NotFound, ... }` became `Error: No such file or directory (os error 2)` (run).
- **`panic!("x is {}", x)` to `panic!("x is {x}")`** prints the literal `{x}` in editions 2015 and 2018 (https://doc.rust-lang.org/edition-guide/rust-2021/panic-macro-consistency.html). In 2018 the same happened with a message-only `assert!`, `debug_assert!` and `unreachable!` (run).
- **Dropping a `.to_string()` where the parameter is generic.** A `T: Debug` printer showed `"42"`, then `42`; `serde_json::to_string` did the same (run).
- **Doc comments and field names in derives.** Deleting a clap field's `///` emptied its `--help` line, and the field `max_width` is the `--max-width` flag (run). Field names also appear in `{:?}` output and serde keys (run), and `#[instrument]` records arguments under their parameter names (https://docs.rs/tracing/latest/tracing/attr.instrument.html).
- **Reordering fields or variants.** Derived `PartialOrd` and `Ord` compare fields top to bottom; swapping `major` and `minor` flipped a comparison (run; https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html). Derived enum ordering follows the discriminants, and implicit discriminants count from the first variant (same page; https://doc.rust-lang.org/reference/items/enumerations.html). Swapping two fields also swapped them in `{:?}` and `serde_json` output (run).
- **Deleting comment lines** shifts the line numbers in `line!()`, panic locations and `dbg!` output (https://doc.rust-lang.org/std/macro.line.html).

## Safe modernizations

Exactly equivalent:
- `try!(x)` to `x?` in a function returning `Result`: both return `Err(From::from(e))` (run). Editions 2018 and later spell the macro `r#try!`.
- `mem::replace(&mut x, Default::default())` to `mem::take(&mut x)`, 1.40+.
- `.map(|x| x.clone())` to `.cloned()`; `.map(|&x| x)` to `.copied()`, 1.36+.
- `std::u32::MAX` to `u32::MAX`, 1.43+.
- `format!("{}", name)` to `format!("{name}")` for plain identifiers, 1.58+, but before edition 2021 not in a message-only `panic!`, `assert!`, `debug_assert!` or `unreachable!` (see above).
- `v.len() == 0` to `v.is_empty()` on std collections, slices and `str`.

Equivalent after a check:
- Fixes from `cargo clippy --fix` (lifetime elision, `needless_return`, `bool_comparison`, `manual_map`, `map_clone`, `clone_on_copy`). It applies only machine-applicable suggestions unless `__CARGO_FIX_YOLO` is set; never set it. Machine-applicable does not mean side-effect free: cargo counted as fixable a `clone_on_copy` suggestion that removed `.clone()` on a `Copy` type whose hand-written `Clone` printed (run). Keep a `clone_on_copy` hunk only when the type's `Clone` is derived or from std; clippy's `non_canonical_clone_impl`, on by default, warned on that impl (run).

Not equivalent:
- `unwrap()` to `?`, `unwrap_or` to `unwrap_or_else` around a call, `if let` to `match`: see above.
- `&Vec<T>` to `&[T]` on `pub` items: callers that hold it as `fn(&Vec<T>)` or pass `&iter.collect()` stop compiling (run), in other crates too (clippy `ptr_arg`, which also flags `pub` items).
- `Box<dyn Error>` to `anyhow`: changes printed errors and requires `Send + Sync + 'static`.
- Removing `async` from a function with no `.await`: callers get a value instead of a future.
- `Arc<Mutex<T>>` to `Rc<RefCell<T>>`: the type stops being `Send`.
- Bumping `edition` in Cargo.toml: changes the drop timing and `panic!` formatting above.

## Verify

Run before and after each pass, with the feature sets and targets CI uses:

```sh
cargo build --workspace --all-targets --all-features
cargo clippy --workspace --all-targets --all-features    # compare warnings with the baseline
cargo test --workspace --all-features                    # unit, integration and doctests
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps --all-features   # broken intra-doc links
cargo fmt --all --check
```

- **Comment-only pass:** run `scripts/check_cosmetic.py`. Its Rust check strips every comment, doc comments, `SAFETY:` and UI-test annotations included, so list those edits and review each one against the list above: `git diff -U0 -- '*.rs' | grep -iE '^[-+][[:space:]]*(//[/!@~]|/\*[*!])|safety:|@generated|spdx-license'`. Add any grcov markers your CI uses. The pattern misses inner lines of a `/** */` block, so read those blocks in the diff. `cargo +nightly rustc -- -Zunpretty=expanded` is no substitute: it keeps comments and bakes in `line!()` values (run). Binaries change when lines move, so do not compare them.
- **Clippy fixes:** run them on a clean tree (cargo fix refuses uncommitted changes unless given `--allow-dirty`), then keep only hunks from lints you meant to apply. Code behind features or targets you did not enable is neither fixed nor checked.
- **Rename pass:** the compiler catches every static reference but not names that become data: `{:?}` output, serde keys, clap flags, `#[instrument]` fields, `stringify!`, `#[no_mangle]` symbols, test names used as CI filters, and module paths, which are the default `log` target (https://docs.rs/log/latest/log/macro.log.html) that `RUST_LOG` filters match. Grep each old name in tests, `.snap` files and docs.
- **Limits:** doctests run only for the library target (https://doc.rust-lang.org/cargo/commands/cargo-test.html). Nothing above proves drop timing or evaluation order unchanged; only tests that observe them do.
