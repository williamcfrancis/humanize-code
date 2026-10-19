# Go: humanize-code reference

Read this with SKILL.md before you edit Go code beyond comments. Some tells from other languages are plain Go style, and some Go edits that look like tidying change behavior.

## Tells

None of these edits applies to a comment listed under Comments that do things.

- **Comments over idioms** (§5, medium). `// Check for error` above `if err != nil`, `// Return the error`, `// Defer closing the file`. Delete them.
- **Doc comments that restate the signature** (§6, medium). `// GetUser is a function that gets a user`, `// Parameters:` and `// Returns:` sections (not a Go convention), a doc comment on every unexported one-liner. Delete those on unexported helpers. On exported names, shrink instead: https://go.dev/doc/comment asks for a doc comment on each, and revive's `exported` rule wants it to start with the name. Never delete a package comment, a `Deprecated:` paragraph or a `BUG(who):` note.
- **Markdown Go doc does not render** (§7, medium). `**Note:**`, pipe tables, bare "IMPORTANT:". Doc comments do render `#` headings (Go 1.19 and later), lists, indented code blocks and `[Name]` links, so keep those. Run gofmt after editing a doc comment: it reformats them and moves directives to their end (https://go.dev/doc/comment).
- **Interface at the producer** (§13, weak alone). `type UserService interface`, `userServiceImpl` and `NewUserService() UserService` with one implementation. The Go wiki puts interfaces with the consumer. Return the concrete type only when every caller is in the repo, no mock is generated from the interface, nothing type-asserts on it, and no caller compares the result to nil through an interface. Otherwise report it.
- **Java and Python names** (§17, weak alone). Receivers named `this` or `self`, `GetX` getters, `MAX_RETRIES`. Rename a receiver in every method of the type at once, to a name nothing in the bodies uses. Report exported names (`MAX_RETRIES` is exported: it starts with a capital) and struct fields: they break importers and mocks, and encoding/json uses an untagged field's name as the key.
- **Log and return at every layer** (§10, medium). `log.Printf("error getting user: %v", err); return err` all the way up. Remove a log only when the same error is provably logged higher up.
- **Errors turned into zero values** (§12, report only). `if err != nil { return nil }`, `_ = json.Unmarshal(b, &v)`, `panic(err)` in a library.
- **Inflated error strings** (§9, report only). "an error occurred while attempting to load the configuration: %w". Plain "failed to" is common in human Go. Error text is behavior under Rule zero: tests, alerts and callers read `err.Error()`. Leave it and report it.
- **Expression ceremony** (§20, weak alone). `if ok == true` becomes `if ok` for any boolean type; Go has no truthiness. Drop an `else` after `return` only when the `if` branch always returns and the `if` declares no variable the `else` uses (`if v, err := f(); ...`): its scope ends with the `if`, so moved code fails to compile or reads an outer `v` (https://go.dev/ref/spec#Blocks). Drop a declared type only when the constant's default type matches: `var n int = 0` to `n := 0`.
- **Stale idioms** (§21, medium). `ioutil`, `interface{}`, `v := v`. Use the allowlist below.

## What people write instead

- `if err != nil { return err }`, or `return fmt.Errorf("open config: %w", err)` with short lowercase context. The happy path stays unindented. This is the idiom, not noise.
- One- or two-letter receivers, the same in every method; `err`, `n`, `buf`, `ctx` for locals.
- A doc comment on each exported name, starting with the name. One package comment per package, often in `doc.go`. Few comments inside functions.
- Small interfaces where they are used; `func NewStore(db *sql.DB) *Store`; table-driven tests with `t.Run`.

## Comments that do things

Never delete, move, reword or respace these:

- `//go:build` with the blank line after it, and legacy `// +build` (Safe modernizations lists the one exception). File names count too: `_linux.go` and `_arm64.go` suffixes are build constraints and `go build` skips `_test.go` files (https://pkg.go.dev/cmd/go#hdr-Build_constraints), so do not rename files.
- Every `//go:` line (`//go:generate`, `//go:embed`, `//go:debug`, `//go:linkname`, `//go:noinline`, `//go:nosplit`, `//go:wasmexport` and the rest) and `//line`. The toolchain matches the exact text, so with a space after `//` they are ordinary comments (https://pkg.go.dev/cmd/compile, https://pkg.go.dev/cmd/go).
- The whole comment immediately above `import "C"`: it is C source, `#cgo CFLAGS` and `#cgo LDFLAGS` lines included. Also `//export Name`, written exactly so (https://pkg.go.dev/cmd/cgo).
- `// Code generated ... DO NOT EDIT.` Leave the file alone.
- `//nolint:name` (golangci-lint), `//lint:ignore` and `//lint:file-ignore` (staticcheck).
- `// Output:` and `// Unordered output:` in Example functions, and the expected-output comment lines under them. `go test` compares them with stdout; without an output comment, the example compiles but never runs (https://pkg.go.dev/testing).
- `Deprecated:` paragraphs, `BUG(who):` notes and the package comment.
- Every `// +` marker in Kubernetes API types (`// +kubebuilder:validation:Minimum=1`, `// +optional`, `// +groupName=`; https://book.kubebuilder.io/reference/markers/crd), swaggo annotations (`// @Summary`, `// @Param`, `// @Success`, `// @Router`, and `// @title` and `// @BasePath` in main.go), and sqlc `-- name:` lines.
- Doc comments a generator copies. controller-tools turns GoDoc on CRD types and fields into schema descriptions (https://book.kubebuilder.io/cronjob-tutorial/api-design), and swag writes struct field comments, trailing ones included, into the OpenAPI schema (https://github.com/swaggo/swag).

## Looks cosmetic, isn't

- **Swapping `%w` and `%v`.** `%w` adds `Unwrap` and is otherwise identical, so the swap changes what `errors.Is` and `errors.As` match (https://go.dev/blog/go1.13-errors). `fmt.Errorf("load: %v", err)` hides `fs.ErrNotExist` from callers. With a nil `err`, `%w` also prints `%!w(<nil>)` where `%v` printed `<nil>` (https://pkg.go.dev/fmt#Errorf).
- **Returning a typed nil.** An interface holding a nil `*MyError` is not nil, so in a function that returns `error`, collapsing `if p != nil { return p }; return nil` into `return p` returns a non-nil error even when `p` is nil (https://go.dev/doc/faq#nil_error).
- **`=` becoming `:=` in a block.** `:=` redeclares only in the same block, so inside an `if` or loop it makes a new `err` and the outer one stays nil. It compiles, and `go vet` runs the shadow analyzer only when you pass it with `-vettool` (https://pkg.go.dev/cmd/go#hdr-Report_likely_mistakes_in_packages).
  ```go
  var err error
  if retry {
  	_, err := send() // was: _, err = send()
  	log.Print(err)
  }
  return err // now always nil
  ```
- **Defer.** Arguments are evaluated when the `defer` statement executes, not when the call runs, and deferred calls run in reverse order (https://go.dev/ref/spec#Defer_statements). `defer func() { record(time.Since(start)) }()` turned into `defer record(time.Since(start))` records about zero. A deferred closure can change a named result, so `func f() (err error)` turned into `func f() error` plus `var err error` drops that change.
- **Loop variable copies.** Before Go 1.22 a loop shared one variable, so `v := v` before `go func() { use(v) }()` or `&v` is a fix. Delete it only when go.mod says `go 1.22` or later and no `//go:build` line downgrades the file (https://go.dev/blog/loopvar-preview).
- **Changing a receiver kind.** The method set of `T` holds only value-receiver methods (https://go.dev/ref/spec#Method_sets). Moving `String()` to a pointer receiver makes `fmt.Println(t)` print raw fields for a `T` value. A value receiver works on a copy, and a `sync.Mutex` must not be copied after first use (https://pkg.go.dev/sync#Mutex).
- **Dropping a declared type.** Untyped constants take their default type (https://go.dev/ref/spec#Constants). `var f float64 = 1` turned into `f := 1` makes `f` an `int`, and `f / 2` becomes integer division.
- **Lines that look unused.** `import _ "net/http/pprof"` and driver imports run `init` (https://go.dev/doc/effective_go#blank_import). `//go:embed` needs `import _ "embed"` even for `string` and `[]byte` (https://pkg.go.dev/embed), and `//go:linkname` works only in a file that imports `unsafe` (https://pkg.go.dev/cmd/compile). `var _ io.Reader = (*T)(nil)` is a compile-time check (https://go.dev/doc/faq#guarantee_satisfies_interface).
- **Blank lines next to comments.** A doc comment must sit directly above its declaration (https://go.dev/doc/comment), so a blank line under it hides it from godoc. controller-tools and swag take descriptions from that same attached comment, so the CRD or OpenAPI description disappears too. A blank line above `import "C"` detaches the cgo preamble (https://go.dev/wiki/cgo).
- **Moving a lint directive.** `//nolint` at a line's end covers that line, at a line's start the next block, above `package` the file (https://golangci-lint.run/docs/linters/false-positives/). `//lint:ignore` covers only the next line (https://staticcheck.dev/docs/configuration/).

## Safe modernizations

Each holds when go.mod's `go` line is at least the version shown and the file's build constraint names no older `go1.N`, negated or not, since a constraint can make a file target older Go (https://go.dev/blog/loopvar-preview).

- Go 1.16: `ioutil.ReadFile`, `WriteFile`, `ReadAll`, `NopCloser`, `Discard` to `os.ReadFile`, `os.WriteFile`, `io.ReadAll`, `io.NopCloser`, `io.Discard`. The ioutil versions just call these (https://pkg.go.dev/io/ioutil).
- Go 1.17: `ioutil.TempDir` and `ioutil.TempFile` to `os.MkdirTemp` and `os.CreateTemp`.
- Go 1.18: `interface{}` to `any`, if no declaration named `any` is in scope. Delete `// +build` when a matching `//go:build` exists (https://go.dev/doc/go1.18).
- Go 1.20: `if strings.HasPrefix(s, p) { ... strings.TrimPrefix(s, p) ... }` to `if after, ok := strings.CutPrefix(s, p); ok { ... after ... }`, when `s` and `p` have no side effects, nothing changes them in between, and `after` and `ok` are new names.
- Go 1.21: an `==` search loop that does nothing else to `slices.Contains` or `slices.Index`, if the target has no side effects. For integers and strings only: `sort.Slice(s, func(i, j int) bool { return s[i] < s[j] })` to `slices.Sort(s)`, and an if/else min or max of two side-effect-free operands to the built-in, if no declaration named `min` or `max` is in scope.
- Go 1.22: delete `v := v` copies of `range` loop variables. `for i := 0; i < n; i++` to `for i := range n` if nothing in the loop changes `i` or `n`, since `range` reads `n` once.

Since Go 1.26, `go fix -diff ./...` prints the modernize rewrites as a diff (https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/modernize). It also runs fixers that are not on this list, such as the `//go:fix inline` inliner, so apply only the hunks that match an entry above. A loop replaced by a call loses the comments inside it, and a fix can leave unused imports or variables.

Not equivalent:

- `ioutil.ReadDir` to `os.ReadDir`: it returns `[]fs.DirEntry`, not `[]fs.FileInfo`, and partial results on error.
- `err == io.EOF` to `errors.Is`, and `err.(*T)` to `errors.As`: both also match wrapped errors.
- `x/exp/maps.Keys` to standard `maps.Keys`: the standard one returns an `iter.Seq`, not a slice (https://pkg.go.dev/maps#Keys).
- min or max on floats: the built-ins return NaN if any argument is NaN, and `min(-0.0, 0.0)` is `-0.0`; an if/else with `<` can differ on both (https://go.dev/ref/spec#Min_and_max). `slices.Sort` on floats puts NaNs first.
- A custom `sort.Slice` to `slices.SortFunc`: neither promises an order for equal elements, so they can come out in a different order.
- `omitempty` to `omitzero`: the modernize docs call it a behavior change.

## Verify

- Each pass: `gofmt -l .`, `go vet ./...`, `go build ./...`, `go test ./...` (it checks Example output), and `golangci-lint run` or `staticcheck ./...` if configured. Repeat `go vet` for each GOOS and build tag the repo ships (`GOOS=windows go vet ./...`, `go vet -tags=integration ./...`): files a constraint excludes never compile.
- Comment-only pass: `python scripts/check_cosmetic.py` compares Go tokens without comments and flags a changed `//go:`, `// +build`, `//export`, `nolint` or `+kubebuilder:` line, but not a moved one. It misses cgo preamble edits, Example output, swag annotations, `//lint:ignore`, `//line`, other `// +` markers, `Deprecated:` paragraphs and generator-read doc comments. It ignores line breaks, where Go inserts semicolons, so `go build` must pass. Then `git diff -U0 | grep -E '^[-+][[:space:]]*//[[:space:]]*(go:|line |export|nolint|lint:|\+|@|Deprecated:|(Unordered output|Output):)'` should print nothing. Read by hand every hunk that adds or removes a blank line next to a comment, and every hunk in a file that imports `"C"`.
- Generators: run `go generate ./...`, `make manifests` or `swag init` at the baseline and after each pass. The generated files must match the baseline run.
- Rename pass: `gopls rename`, then build, vet and test. The compiler cannot see names used through reflection (encoding/json keys, `{{.UserName}}` in templates), so search for each old name as a string.
- Unless a test compares them, these checks miss moved line numbers. Deleting comment lines changes file:line in `log.Lshortfile` output, panics and golden files.
