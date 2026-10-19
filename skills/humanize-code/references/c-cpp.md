# C and C++: humanize-code reference

Read this with SKILL.md before you edit C or C++ code beyond comments. The preprocessor, object lifetimes and overload resolution turn many tidy edits into behavior changes that compile cleanly.

## Tells

- **`// Function to ...` comments** (§5, medium): `// Function to calculate the sum`, `// Driver code` above `main`, `// Constructor`, `} // end for`. Delete them. Keep units, ownership ("caller frees"), locking ("called with mu_ held"), reasons, and the `// for std::vector` notes after includes, which IWYU suggests and `fix_includes.py --comments` writes.
- **Doxygen boilerplate** (§6, medium): `@brief Constructor.`, `@param v The vector.`, `@return The result.` on `static` and private functions; `@author Your Name` and `@date` headers. Delete in internal code when no Doxygen or kernel-doc runs. If one does, read the Doxyfile first: deleting a `/** @file */` block drops the file's global functions, typedefs, enums and macros from the docs ([Doxygen](https://www.doxygen.nl/manual/docblocks.html)), and with `WARN_AS_ERROR` set, the warnings for undocumented members (`WARN_IF_UNDOCUMENTED`) or partly documented parameters (`WARN_IF_INCOMPLETE_DOC`) fail the docs build ([config](https://www.doxygen.nl/manual/config.html)). Report placeholder authors and dates (§2); never fill them in.
- **Banner boxes** (§8, weak alone): `// ===== Helper Functions =====`, `/***** UTILITIES *****/`. Old C code is full of them, so delete them only where the repo's human-written files have none.
- **Closing comments** (§5, medium): keep `}  // namespace foo` (Google style requires it, clang-tidy `google-readability-namespace-comments` checks it, clang-format `FixNamespaceComments` re-adds it) and `#endif  // FOO_H_` (cpplint `build/header_guard`). Keep `#endif /* HAVE_FOO */` after long conditional blocks.
- **Tutorial residue** (§20, §21, weak alone): `std::endl` everywhere, `#include <bits/stdc++.h>`, `using namespace std;`, index loops that only read `v[i]`. People write these too. Convert the loop as below; report the rest.
- **Catch and rethrow** (§10, medium): remove a handler only when its whole body is `throw;` and every call path reaches an outer handler with no `noexcept` function in between. If no handler catches the exception, whether the stack unwinds before `std::terminate` is implementation-defined ([cppreference](https://en.cppreference.com/w/cpp/language/throw)), and an exception leaving a `noexcept` function may or may not unwind ([cppreference](https://en.cppreference.com/w/cpp/language/noexcept_spec)). Either way, destructors that ran before the rethrow may no longer run. `throw e;` is not a rethrow (below).
- **Long names** (§17, medium): rename only locals, file-scope `static` functions and anonymous-namespace names (a `static` member function is not file-local). Never rename external-linkage or `extern "C"` functions, names reached through `dlsym` or `GetProcAddress`, names built by `##` pasting (grep misses them), names inside `assert` and other stringizing macros, or a local that a macro body uses without taking it as a parameter: the body binds to whatever that name means where the macro expands ([GCC](https://gcc.gnu.org/onlinedocs/cpp/Object-like-Macros.html)).

## What people write instead

- C: `static` file-local functions, one `goto out;` cleanup label, `p = malloc(sizeof(*p))` with no cast, names like `n`, `p`, `buf`, `len`, `ret`.
- C++: `'\n'`, range-for over `const auto&`, `std::unique_ptr` for ownership, `= default`, `override`, an anonymous namespace for helpers, a small `{ }` block to release a lock early.
- Layout from `.clang-format`, error handling in the file's existing style, and no new try/catch.

## Comments that do things

Never delete, move, or reword:

- clang-tidy and cpplint: `// NOLINT`, `// NOLINT(check)`, `// NOLINTNEXTLINE`, `// NOLINTBEGIN` / `// NOLINTEND`.
- cppcheck: `// cppcheck-suppress id`, `cppcheck-suppress-begin` / `-end` / `-file` / `-macro`.
- `// clang-format off` / `on`, and the `/* */` forms.
- `// IWYU pragma:` with `keep`, `export`, `begin_exports`, `end_exports`, `private`, `friend`, `no_include`, `no_forward_declare`, `always_keep`, `associated`, `begin_keep`, `end_keep` (clangd honors `keep`, `export` and `private`).
- Fallthrough markers that GCC's `-Wimplicit-fallthrough` reads (`// falls through`, `/* FALLTHRU */`). Only whitespace and other comments may separate one from the next `case`, `default`, or a label in front of one ([GCC](https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html)).
- Coverage: `LCOV_EXCL_LINE`, `LCOV_EXCL_START` / `STOP` and other `LCOV_EXCL_*` markers, `GCOVR_EXCL_*` (gcovr reads both).
- Doc input where docs are published: `/** */`, `/*! */`, `///`, `//!`, `///<`, `@file`, kernel-doc blocks.
- `}  // namespace foo` and `#endif  // FOO_H_`.
- `SPDX-License-Identifier` lines (the kernel wants them on the first line that can hold a comment), license blocks, Emacs `-*- mode -*-` lines, Vim modelines.
- Rcpp `// [[Rcpp::export]]`, Qt `//:` translator comments and `//~` extras, gettext `/* TRANSLATORS: */`, lit `// RUN:` and FileCheck `// CHECK:` lines.
- Pragmas: `#pragma once`, `pack`, `GCC diagnostic`, `warning`, `comment`, `omp`, `hdrstop`, `region`, `mark`.

## Looks cosmetic, isn't

- `std::endl` to `'\n'` drops a flush ([cppreference](https://en.cppreference.com/w/cpp/io/manip/endl)). When stdout is a file or pipe, a crash loses buffered lines, and output can land after later writes to stderr through `fprintf`, `std::clog` or a child process. Writes through `std::cerr` keep their order, because it flushes `std::cout` first ([cppreference](https://en.cppreference.com/w/cpp/io/cerr)). Terminals are usually line-buffered, so local runs hide it.
- `NULL` or `0` to `nullptr` can switch overloads. `NULL` may be `0` ([cppreference](https://en.cppreference.com/w/cpp/types/NULL)) and `f(0)` picks `f(int)` over `f(char*)` ([N2431](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2007/n2431.pdf)); `f(nullptr)` picks `f(char*)`. Under MSVC, `std::make_pair(NULL, 3.14)` is a `pair<int, double>` ([Microsoft](https://learn.microsoft.com/en-us/cpp/cpp/nullptr)).
- `using std::swap; swap(a, b);` to `std::swap(a, b)` skips the type's own `swap` found by argument-dependent lookup ([cppreference](https://en.cppreference.com/w/cpp/named_req/Swappable)). Removing `using namespace std` and qualifying calls risks the same.
- Moving a declaration across a block, deleting a bare `{ }`, or removing an `else` after `return` (its locals move up a scope) changes when destructors run. A `std::lock_guard` unlocks when control leaves its scope ([cppreference](https://en.cppreference.com/w/cpp/thread/lock_guard)):
  ```cpp
  {
      std::lock_guard<std::mutex> lk(mu_);
      queue_.push(job);
  }
  cv_.notify_one();  // without the braces, mu_ is still held here
  ```
- Reordering class members reorders their initialization, which follows declaration order whatever the initializer list says ([cppreference](https://en.cppreference.com/w/cpp/language/initializer_list)). It also reorders their destruction ([cppreference](https://en.cppreference.com/w/cpp/language/destructor)) and their layout in memory ([cppreference](https://en.cppreference.com/w/cpp/language/data_members)), and changes which member each value in an aggregate's `T{1, 2}` initializes ([cppreference](https://en.cppreference.com/w/cpp/language/aggregate_initialization)).
- Argument evaluation order is unspecified ([cppreference](https://en.cppreference.com/w/cpp/language/eval_order)), so `auto h = readHeader(in); auto b = readBody(in); return Msg(h, b);` is not `return Msg(readHeader(in), readBody(in));`. Temporaries die at the end of the full-expression ([cppreference](https://en.cppreference.com/w/cpp/language/lifetime)), so extracting `const char* p = name().c_str();` dangles.
- `catch (const std::exception& e) { throw e; }` throws a sliced copy; only `throw;` rethrows the original ([cppreference](https://en.cppreference.com/w/cpp/language/throw)). Removing or "fixing" it can change which outer `catch` matches.
- A `//` comment ending in a backslash swallows the next line, since line splicing comes before comment removal ([cppreference](https://en.cppreference.com/w/cpp/language/translation_phases)). Deleting `// copy to C:\temp\` revives the line below. Each comment also counts as one space (same page), so deleting the comment from `-/* twice */-x` without leaving a space gives `--x`, a decrement.
- Deleting lines shifts `__LINE__` for every line below; renaming changes `__func__` and expression text. `assert` prints all three ([cppreference](https://en.cppreference.com/w/cpp/error/assert)), as can logging macros, `std::source_location` ([cppreference](https://en.cppreference.com/w/cpp/utility/source_location/current)) and `#x`.
- `_GNU_SOURCE` and other feature-test macros must precede every system header ([glibc](https://sourceware.org/glibc/manual/latest/html_node/Feature-Test-Macros.html)), `config.h` goes first ([Autoconf](https://www.gnu.org/software/autoconf/manual/autoconf-2.72/html_node/Configuration-Headers.html)), and MSVC `/Yu` skips everything above the precompiled-header include ([Microsoft](https://learn.microsoft.com/en-us/cpp/build/reference/yu-use-precompiled-header-file)). clang-format sorts each include block alone, and a comment line ends a block, as does a blank line under `IncludeBlocks: Preserve` ([source](https://github.com/llvm/llvm-project/blob/main/clang/lib/Format/Format.cpp)). Delete a comment between include groups and the next format run may merge and reorder them.
- Guards to `#pragma once` deletes the guard macro, so `#ifdef FOO_H_` elsewhere flips, and some preprocessors ignore the pragma ([GCC](https://gcc.gnu.org/onlinedocs/cpp/Alternatives-to-Wrapper-_0023ifndef.html)). A renamed guard can collide with another header's and silently empty it.
- A function or `constexpr` evaluates an argument once where the macro may have evaluated it twice ([GCC](https://gcc.gnu.org/onlinedocs/cpp/Duplication-of-Side-Effects.html)), and `#if` cannot see a `constexpr`. Dropping `do { } while (0)` breaks `if (x) MACRO(); else` ([GCC](https://gcc.gnu.org/onlinedocs/cpp/Swallowing-the-Semicolon.html)). Adding parentheses around a macro parameter or body changes the result for arguments like `b & c` ([GCC](https://gcc.gnu.org/onlinedocs/cpp/Operator-Precedence-Problems.html)): report the missing parentheses as a bug and leave the macro alone.
- `// NOLINT` covers its own line, `// NOLINTNEXTLINE` the next one ([clang-tidy](https://clang.llvm.org/extra/clang-tidy/)). Joining or splitting that line, or adding a comment line between directive and target, moves the suppression.
- In C before C23, `int f(void)` to `int f()` drops the prototype: `f(2)` then compiles and is undefined behavior ([cppreference](https://en.cppreference.com/w/c/language/function_declaration)).

## Safe modernizations

- `typedef A B;` to `using B = A;` (C++11) in a file no C compiler reads: identical ([cppreference](https://en.cppreference.com/w/cpp/language/type_alias)).
- `c.size() == 0` to `c.empty()`: standard containers, any version.
- Index loop to range-for (C++11): `i` runs from 0 to `v.size()` by one, the body only reads `v[i]` and uses `i` nowhere else, nothing adds or removes elements during the loop (range-for reads `end()` once), `v` is a standard container, and the loop variable is `const auto&`, or the element type when copying it has no side effects.
- Adding `override` (C++11): it either compiles with no change or fails to compile ([cppreference](https://en.cppreference.com/w/cpp/language/override)).
- `NULL` or `0` to `nullptr` (C++11, C23): only when assigned to or compared with a pointer, returned from a function declared to return one, or passed as a pointer argument to a plain function (no overloads, templates, `...` or `_Generic` macro).
- `std::endl` to `'\n'` on `std::cerr` or `std::wcerr`, whose `unitbuf` flushes anyway ([cppreference](https://en.cppreference.com/w/cpp/io/cerr)), unless the code clears it.
- C only: `p = (int *)malloc(n)` to `p = malloc(n)` when `p` is an `int *`, `<stdlib.h>` is included, and nothing compiles the file as C++. Keep the cast where the result feeds arithmetic or indexing, such as `(int *)malloc(n) + 4`. `malloc(n * sizeof(char))` to `malloc(n)`, since `sizeof(char)` is 1 ([cppreference](https://en.cppreference.com/w/c/language/sizeof)).

Not equivalent:

- `std::endl` to `'\n'` on `std::cout` or file streams: no flush.
- `std::unique_ptr<T>(new T)` to `std::make_unique<T>()`: value-initializes, zeroing a trivial `T`. The match is `std::make_unique_for_overwrite` (C++20) ([cppreference](https://en.cppreference.com/w/cpp/memory/unique_ptr/make_unique)).
- A loop to `std::accumulate(v.begin(), v.end(), 0)` over doubles: every partial sum becomes `int` ([cppreference](https://en.cppreference.com/w/cpp/algorithm/accumulate)).
- Types to `auto`: `auto s = "id";` is `const char*`, and `auto n = v.size();` is unsigned where `int n` was signed.
- `bits/stdc++.h` to explicit headers, or dropping `using namespace std`: lookup can change. A passing build is not proof; compare object code.
- Guards and `#pragma once` either way; macros to functions or `constexpr`.

## Verify

Take flags from `compile_commands.json` and build every shipped configuration: code under an unbuilt `#ifdef` is unchecked.

Comment-only pass:

```sh
gcc -fpreprocessed -dD -E -P before.c > a.i   # g++ for C++
gcc -fpreprocessed -dD -E -P after.c  > b.i
diff a.i b.i                                   # explain every hunk
```

`-fpreprocessed` strips comments without expanding macros or includes ([GCC](https://gcc.gnu.org/onlinedocs/gcc/Preprocessor-Options.html)). `#include` and `#if` lines pass through as text, and `-dD` prints the `#define` lines this mode still processes ([libcpp source](https://github.com/gcc-mirror/gcc/blob/master/libcpp/directives.cc)). GCC keeps each line's first token in its column ([source](https://github.com/gcc-mirror/gcc/blob/master/gcc/c-family/c-ppoutput.cc)), so deleting a `/* */` at the start of a line leaves a harmless hunk. Do not add `-w`: it hides whitespace changes inside string literals and between tokens, such as `- -x` becoming `--x`. The check cannot see directive comments (it strips them all) or backslash-continued `//` comments (this mode skips line splicing). So also:

- Do not rely on `check_cosmetic.py` alone for C and C++. It compares tokens with comments removed, splits `--` into two `-` tokens, ends a `//` comment at the newline even after a backslash, and does not recognize `FALLTHRU`, `cppcheck-suppress`, `clang-format off`, `IWYU pragma`, `LCOV_EXCL`, `GCOVR_EXCL`, `SPDX`, `[[Rcpp::export]]` or `RUN:` comments, so it passes when they are deleted.
- Rebuild with `-Wall -Wextra -Wimplicit-fallthrough -Wcomment` on top of the project's flags and compare the warnings with the baseline build.
- Run `clang-tidy -p build`, `cpplint`, `cppcheck --inline-suppr` and `clang-format --dry-run --Werror` on the changed files and on the originals, and compare. They catch lost NOLINT, namespace and guard comments, and include blocks that would re-sort.
- Diff Doxygen output before and after if the project publishes docs.
- Deleting any line shifts `__LINE__` below it. Grep the file for `assert`, `__LINE__`, `source_location` and logging macros, and check that no test, golden file or alert matches on those line numbers.

Rename pass:

- Build with `-Wall -Wextra -Wshadow` and compare the warnings with the baseline; `-Wshadow` flags a short name that hides another.
- `nm -C --defined-only --extern-only` must list the same symbols before and after.
- Build both with `-g0` and identical flags and diff `objdump -d --no-show-raw-insn`. Expect only renamed labels to differ; trace anything else. `objdump -d` reads only code sections ([binutils](https://sourceware.org/binutils/docs/binutils/objdump.html)), so also diff `strings -a` of both objects. Apart from the renamed names, look there for changed `#x`, `__func__` and assert text.
- After moving declarations, run tests with `-fsanitize=address,undefined` (in GCC this turns on ASan's use-after-scope check ([GCC](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html))). If a lock scope changed, also run them in a separate build with `-fsanitize=thread`, which GCC cannot combine with ASan.

None of this catches string lookups (`dlsym`, config files), outside code linking your symbols, longer lock hold times, or paths the tests never run.
