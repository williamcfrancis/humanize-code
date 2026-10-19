# Swift and SwiftUI: humanize-code reference

Read this with SKILL.md before you edit Swift or SwiftUI code beyond comments. First find the deployment targets (the `*_DEPLOYMENT_TARGET` build settings in the project, `platforms:` in Package.swift), because many tells depend on them.

## Tells

- **Doc comments on everything** (§6, medium). `/// The body of the view.` on `var body`, `- Parameter id: The id.` on private helpers. Delete them in internal and private code. On `public` API that DocC publishes, or under SwiftLint's `missing_docs` rule, cut to one line the signature does not say. Keep `- Throws:`, units, and real warnings.
- **Narrating comments in view bodies** (§5, medium). `// Title` above `Text`. Swift comments never reach the rendered view, so deleting them is safe.
- **`// MARK:` every few lines** (§8, weak alone). SKILL.md keeps `// MARK:`: report the density, delete nothing. SwiftFormat's opt-in `markTypes` and `organizeDeclarations` rules write them, so removing them can fail `swiftformat --lint`.
- **Older APIs** (§21, medium). `.foregroundColor`, `.cornerRadius`, and `NavigationView`, which Apple marks deprecated; `ObservableObject` with `@Published` and `@StateObject`, and `Task.sleep(nanoseconds:)`, which are not deprecated but have newer replacements. A tell only when the target has the replacement (`NavigationStack` needs iOS 16, `@Observable` iOS 17); teams on iOS 15 write these on purpose. Apply only the Safe modernizations below and report the rest.
- **Main-thread band-aids** (§11, report only). `DispatchQueue.main.async` inside a `@MainActor` method or a `.task {}`; `await MainActor.run {}` in code already on the main actor; `@MainActor` on every type. Each decides when or where code runs. Report it even in a module that opts into main-actor default isolation (SE-0466).
- **Guards that cannot fail, silent fallbacks** (§11 and §12, report only). `guard let url = URL(string: "https://...") else { print("Invalid URL"); return }` on a literal, `?? ""` on a value that is never nil. Never turn `!` into `?`, `if let`, or `guard ... else { return }`, or back. The [Swift book](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/thebasics/) calls `!` "effectively, a shorter spelling of" `fatalError(_:file:line:)`, so each swap trades a crash for a silent skip, or the reverse.
- **Pre-5.7 unwrapping** (§21, weak alone). `if let user = user` becomes `if let user`. Inside a `[weak self]` closure, `guard let strongSelf = self else { return }` becomes `guard let self else { return }`, and each `strongSelf.` becomes `self.`. Both need a Swift 5.7 compiler.
- **Spelled-out types and `self.`** (§20, weak alone). `let title: String = "Settings"`, `self.` on every member. Drop an annotation only when the literal's default type is the declared type (`Int`, `Double`, `String`, `Bool`). Keep it on stored properties of a type with an attached macro such as `@Model` or `@Observable`: the compiler hands the macro the syntax as written ([Swift book](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/macros/)). Drop `self.` only where no parameter or local shares the name.
- **Names that repeat the type** (§17, medium). `usersArray`, `isLoadingUserDataFlag`. The [API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) say to omit words that repeat type information. Rename only `private` and local names, and never these:
  - `@objc`, `@IBOutlet`, or `@IBAction` members. Selectors, KVO strings, and storyboard XML use the name.
  - Names in a `Codable` type without `CodingKeys`, including enum cases and their associated-value labels.
  - Enum cases with implicit raw values, and `@Model` and `@NSManaged` properties.
  - Names that reach output. Inside a getter, `#function` is the property's name ([docs](https://developer.apple.com/documentation/swift/function())), and code may use it as a `UserDefaults` key or in logs. `print`, `String(describing:)`, and `dump` show property and case names of a type with no custom description ([docs](https://developer.apple.com/documentation/swift/string/init(describing:)-67ncf), [docs](https://developer.apple.com/documentation/swift/mirror)).
  - XCTest methods, which run only if named `test...` ([docs](https://developer.apple.com/documentation/xctest/defining-test-cases-and-test-methods)).
- **Emoji status prints** (§4 and §22, one sighting in a repo with no other emoji). `print("\u{2705} Loaded \(items.count) items")`. Remove the emoji under §4's conditions, or the whole `print` under §22's. Never convert `print` to `Logger`.

## What people write instead

- `if let user` and `guard let self else { return }`.
- A force unwrap where nil is a programmer error: Apple's `.task` example writes `URL(string: "https://example.com")!`.
- One extension per protocol conformance, often under a `// MARK: -`.
- `.task {}`, `@Observable`, and `NavigationStack` once the target allows them.
- `$0`, `map(\.name)`, trailing closures, and `[weak self]` only where a closure could keep an object alive.
- Doc comments on public API only, usually one line.

## Comments that do things

Never delete, move, or reword these:

- SwiftLint: `// swiftlint:disable <rules>`, `// swiftlint:enable <rules>`, `all`, and the positional `:next`, `:this`, and `:previous` forms.
- SwiftFormat: `// swiftformat:disable` and `enable` (also `:next`, `:this`, `:previous`), `// swiftformat:options`, `// swiftformat:sort`, `// swiftformat:sort:begin` and `:end`.
- swift-format: `// swift-format-ignore`, `// swift-format-ignore: RuleName`, `// swift-format-ignore-file`.
- Periphery: `// periphery:ignore`, `:all`, `:parameters`.
- Sourcery: `// sourcery:` annotations, `// sourcery:begin:` and `// sourcery:end`, `// sourcery:file:`, and `// sourcery:inline:` regions, which Sourcery rewrites. Mockolo: `/// @mockable`.
- `// swift-tools-version:` on the first line of Package.swift.
- The shebang in Swift scripts.
- `// MARK:`, `// TODO:`, `// FIXME:`: Xcode's jump bar and minimap show them ([docs](https://developer.apple.com/documentation/xcode/editing-source-files-in-xcode)), and SwiftLint's `mark` and `todo` rules are on by default.
- License headers, and file headers that SwiftLint `file_header` or SwiftFormat `fileHeader` enforce.

Skip generated files entirely (SwiftGen, Sourcery, `*.pb.swift`).

## Looks cosmetic, isn't

- **Removing a main-queue hop.** `dispatch_async` returns immediately and never waits for the block ([docs](https://developer.apple.com/documentation/dispatch/dispatch_async)). Without the hop, the work runs before the lines after it.
  ```swift
  @MainActor func finish() {
      DispatchQueue.main.async { self.isLoading = false }
      analytics.log(isLoading)   // still the old value; without the hop, false
  }
  ```
  `await MainActor.run {}` instead returns the closure's result, so the caller waits for it ([docs](https://developer.apple.com/documentation/swift/mainactor/run(resulttype:body:))).
- **Moving a string into or out of `Text`.** `Text("Save")` with a literal is a localization key ([docs](https://developer.apple.com/documentation/swiftui/text)), and Markdown in the key or its translation renders as styling ([docs](https://developer.apple.com/documentation/swiftui/text/init(_:tablename:bundle:comment:))). `Text(title)` with a `String` variable does neither ([Hacking with Swift](https://www.hackingwithswift.com/quick-start/swiftui/how-to-render-markdown-content-in-text)). Extracting or inlining it changes translations and whether `**bold**` shows asterisks. `Toggle`, `Picker`, and others localize literals the same way ([docs](https://developer.apple.com/documentation/swiftui/localizedstringkey)).
- **Dropping a type annotation.** Number literals take their type from context; alone, integer literals infer `Int` and float literals `Double` ([docs](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/thebasics/)). `let ratio: Double = 1 / 3` is 0.333; `let ratio = 1 / 3` is 0. If `assumedName` is an implicitly unwrapped optional, `let name: String = assumedName` force-unwraps it, and `let name = assumedName` makes `name` an optional.
- **Removing `self.`** When a parameter shares a property's name, "the parameter name takes precedence" ([docs](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/methods/)). In `func show(title: String) { label.text = self.title }`, dropping `self.` compiles and reads the parameter.
- **Renaming names that are data.** An enum case with an implicit `String` raw value uses its name as the value ([docs](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/enumerations/)). Synthesized `Codable` uses property names as keys ([SE-0166](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0166-swift-archival-serialization.md)), and for an enum, case names and associated-value labels ([SE-0295](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0295-codable-synthesis-for-enums-with-associated-values.md)). Renaming `case inProgress` or `var createdAt` changes saved and sent data, and the compiler is silent.
- **`.onAppear { Task { ... } }` to `.task { ... }`.** SwiftUI cancels a `.task` when it removes the view or the view's identity changes, and runs it at `.userInitiated` priority by default ([docs](https://developer.apple.com/documentation/swiftui/view/task(name:priority:file:line:_:))).
- **`@StateObject` to `@State`.** A state object initializes once per view lifetime; `@State` "always instantiates its default value" when SwiftUI creates the view ([docs](https://developer.apple.com/documentation/swiftui/state)), so side effects in the model's `init` repeat each time the parent rebuilds the view. If the class is still an `ObservableObject`, `@State` updates the view only when the reference changes, never when a `@Published` property does (same page). Observation also redraws only views whose `body` reads the changed property ([docs](https://developer.apple.com/documentation/swiftui/migrating-from-the-observable-object-protocol-to-the-observable-macro)).
- **`NavigationView` to `NavigationStack`.** On iPadOS and macOS, `NavigationView` shows the destination in the next column; a stack covers the root ([docs](https://developer.apple.com/documentation/swiftui/navigationview)).
- **`onTapGesture` to `Button`.** A button adapts its look to its container, role, and style, and on tvOS the user activates it by focusing it and pressing select ([docs](https://developer.apple.com/documentation/swiftui/button)).
- **Folding `if`/`else` branches into one view.** Each branch has its own identity, so a condition change transitions between views and resets their state, while one view with a conditional modifier animates in place ([WWDC21](https://developer.apple.com/videos/play/wwdc2021/10022/)).
- **`String(format:)` to `.formatted()`.** `String(format: "%.2f", x)` always prints two decimal places. `x.formatted()` uses `FloatingPointFormatStyle()` ([docs](https://developer.apple.com/documentation/swift/binaryfloatingpoint/formatted())), whose locale defaults to the user's current locale ([docs](https://developer.apple.com/documentation/foundation/floatingpointformatstyle/init(locale:))), so the text changes, starting with the decimal separator.
- **`Task.sleep(nanoseconds:)` to `Task.sleep(for:)`.** `sleep(for:)` defaults to `ContinuousClock` ([docs](https://developer.apple.com/documentation/swift/task/sleep(for:tolerance:clock:))), which keeps counting while the system sleeps ([docs](https://developer.apple.com/documentation/swift/continuousclock)). The Swift 5.9 runtime schedules `sleep(nanoseconds:)` with `dispatch_time(DISPATCH_TIME_NOW, ...)` ([source](https://github.com/swiftlang/swift/blob/release/5.9/stdlib/public/Concurrency/DispatchGlobalExecutor.inc)), whose clock stops while the system sleeps ([docs](https://developer.apple.com/documentation/dispatch/dispatch_time)). After the device sleeps, the two wake at different times.

## Safe modernizations

Equivalent under the stated condition:

- `if let x = x` to `if let x`, also for `guard let`, `if var`, `while let`: Swift 5.7 compiler (SE-0345), plain identifiers only.
- `guard let strongSelf = self` to `guard let self`, renaming each `strongSelf` in that closure: Swift 5.7 compiler.
- `x.count == 0` to `x.isEmpty` on collections that store their elements (`Array`, `Set`, `Dictionary`, `String`, `Data`), as Apple's docs recommend ([docs](https://developer.apple.com/documentation/swift/collection/isempty)). Not on a lazy view: `count` runs its closure on every element, and `isEmpty` can stop at the first.
- `users.map { $0.name }` to `users.map(\.name)`: Swift 5.2 (SE-0249), plain property reads only.

Equivalent only with a passing image snapshot of every affected screen:

- `.foregroundColor(c)` to `.foregroundStyle(c)` with a non-optional `Color`: iOS 15 or macOS 12, or iOS 17 or macOS 14 when the result must stay a `Text` for `+`. Skip views over a material background: the `foregroundStyle` docs say a custom style turns off the vibrancy a material adds, the `foregroundColor` docs are silent, and swift-snapshot-testing renders visual effects only with `drawHierarchyInKeyWindow: true`.
- `.cornerRadius(r)` to `.clipShape(RoundedRectangle(cornerRadius: r))`; `antialiased: false` becomes `style: FillStyle(antialiased: false)`. `RoundedRectangle` defaults to `.continuous` corners, and the docs do not say which style `cornerRadius` draws.

Not equivalent, so report: the API swaps under Looks cosmetic, isn't, removing `@MainActor`, and any swap between `!`, `?`, and `guard`.

## Verify

- Every pass: `xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'`, or `swift build && swift test`. Save `xcodebuild build ... 2>&1 | grep 'warning:' | sort` and allow no new warnings. Run the repo's `swiftlint` and `swiftformat --lint`.
- Comment-only pass: `python scripts/check_cosmetic.py` compares Swift tokens without comments. It tracks `swiftlint:disable` and `enable` lines (a moved `:this` shows as a changed line), `MARK:` lines, the shebang, and the line after `swiftlint:disable:next`. It does not track `swiftformat:`, `swift-format-ignore`, `periphery:`, `sourcery:`, `@mockable`, `swift-tools-version`, TODO, or FIXME lines, so also run `git diff -U0 | grep -E '^[-+].*(swiftlint:|swiftformat:|swift-format-ignore|periphery:|sourcery:|@mockable|swift-tools-version|TODO|FIXME)'` and expect nothing.
- Neither check proves that a positional directive still sits next to its target. The checker follows only `swiftlint:disable:next` and skips blank lines when it does, while SwiftLint applies `:next` and `:previous` to the adjacent line number, blank or not. Check by hand that every `:next` and `:previous` directive, `periphery:ignore`, and `swift-format-ignore` still sits directly beside its target.
- The checker also misses edits after a `//` inside an extended regex literal (`#/https?://(\S+)/#`) or inside a string nested in an interpolation (`"\(s.replacingOccurrences(of: "//", with: "/"))"`), and edits on the lines after a raw string that ends in a backslash (`#"C:\dir\"#`). It flags deleting a nested `/* /* */ */` comment as a code change. Review such lines by hand.
- Do not compare binaries: `fatalError` and `precondition` default to `#file` and `#line`, so deleting a comment above one changes the binary.
- Rename pass: the compiler sees static references only. Grep the old name in `.storyboard`, `.xib`, `.xcdatamodeld`, string catalogs, and string literals. In a package, `swift package diagnose-api-breaking-changes <base-ref>` checks public API.
- UI: run snapshot tests as `TEST_RUNNER_SNAPSHOT_TESTING_RECORD=never xcodebuild test ...` (swift-snapshot-testing 1.17 or later) so a missing reference fails instead of recording; xcodebuild passes `TEST_RUNNER_` variables to the test runner without the prefix ([docs](https://developer.apple.com/documentation/xcode/environment-variable-reference)). Without snapshot tests, compare `xcrun simctl io booted screenshot <file>.png` images of each screen and state, light and dark, plus a second language if a `Text` string moved. `print(app.debugDescription)` in a UI test prints the element tree ([docs](https://developer.apple.com/documentation/xcuiautomation/xcuielement/debugdescription)). None of this shows animations, transitions, or state resets: report those edits.
