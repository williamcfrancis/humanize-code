# C# and .NET: humanize-code reference

Read this with SKILL.md before you edit C# beyond comments. Much of what looks like AI ceremony in C# is house style.

## Tells

- **Skeleton XML doc comments** (§6; medium on non-public members, weak alone on public API, since Visual Studio inserts the skeleton when you type `///`). Delete them on members that are not publicly visible, unless StyleCop runs: its SA1600 requires docs on internal members by default ([settings](https://github.com/DotNetAnalyzers/StyleCopAnalyzers/blob/master/documentation/Configuration.md)). For public and protected members of public types, check the .csproj and Directory.Build.props: with `GenerateDocumentationFile` set, a missing comment raises CS1591, which `TreatWarningsAsErrors` makes fatal, so shrink instead. When you shrink, keep every `<param>` tag or none: documenting some parameters and not others raises CS1573. Keep `<inheritdoc/>`, `<include>`, `<exception>`, `<remarks>`, `<response>`, `<example>`, and every comment on endpoints and DTOs when an OpenAPI generator reads them.
  ```csharp
  /// <summary>
  /// Gets the user by identifier.
  /// </summary>
  /// <param name="id">The identifier.</param>
  /// <returns>The user.</returns>
  private User GetUser(int id) => _users[id];
  ```
  ```csharp
  private User GetUser(int id) => _users[id];
  ```
- **IFoo with one Foo** (§13, weak alone). An interface per service, registered with `AddScoped<IFoo, Foo>()` and mocked in tests, is house style. Leave it. Report one-caller factories and static helpers.
- **Catch that only rethrows** (§10, medium). Remove `catch (Exception) { throw; }` only when it does nothing else and no caller uses an exception filter (`catch ... when`), because the catch decides whether `finally` and `Dispose` code under it runs before or after those filters. `throw ex;` is a bug (CA2200): report it, and do not switch it to `throw;`, which changes logged stack traces.
- **Null checks** (§11, medium). Keep `ArgumentNullException` checks on public parameters even with nullable reference types on, since nothing enforces them at run time. Remove only what §11 allows. Chains like `user!.Profile!.Name` are report only.
- **Expression ceremony** (§20, weak alone). `if (isActive == true)` becomes `if (isActive)` for a `bool` (for `bool?` the compiler rejects the short form). `.Count() > 0` on a `List<T>` becomes `.Count > 0` only when the list cannot be null: on null, `Count()` throws `ArgumentNullException` and `.Count` throws `NullReferenceException`. An explicit type becomes `var` only when it equals the initializer's type. In a `foreach`, it must equal the element type, because an explicit type there is a cast: `foreach (string s in arrayList)` throws `InvalidCastException` on a non-string item, and `var` does not.
- **Async ceremony** (§20, report only). Single-await methods and `ConfigureAwait(false)` in library code are normal; do not elide or strip them. Report `async void` outside event handlers, `.Result`, and `.Wait()`.
- **Step logs** (§22, medium). Remove `_logger.LogInformation($"Starting ProcessOrder...")` under §22's conditions. Never convert between interpolation and message templates.
- **Names** (§17, medium). Rename locals only, and skip a local that appears in `nameof(...)` or is passed to `ArgumentNullException.ThrowIfNull`, since both turn its name into a string. Named arguments, `nameof`, model binding, serializers, EF Core, and Unity read parameter, field, and property names. Unity calls `Awake` and `Update` methods that look unused, and its own examples declare them private ([Unity](https://docs.unity3d.com/ScriptReference/MonoBehaviour.Update.html)).
- **`?.`, `??`, or `is null` on Unity objects** (§11, report only). `_target?.TakeDamage(1)` on a cached `_target` does not skip a destroyed object. Report it as a likely bug: Unity says these operators are safe only on objects that are never destroyed ([Unity](https://docs.unity3d.com/ScriptReference/Object.html)).
- **Test scaffolding** (§26, weak alone). `// Arrange`, `// Act`, `// Assert` and `Method_Scenario_Expected` names come from Microsoft's unit testing guidance ([docs](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)). Act only when the repo's human tests lack them.

## What people write instead

- `var` where the .editorconfig `csharp_style_var_*` settings allow it.
- Expression-bodied one-liners, switch expressions, and `is not null` (except on types that define or inherit `==`).
- Guard clauses at public entry points (`ArgumentNullException.ThrowIfNull` on .NET 6 and later), trust inside.
- Records for DTOs, classes for entities.
- Log templates: `_logger.LogInformation("Loaded {Count} users", users.Count)`.
- In Unity: `[SerializeField] private` fields, cached component references, `TryGetComponent`, and `obj != null` checks.

## Comments that do things

- `#pragma warning disable` and `restore`, `#pragma checksum`, and `#nullable enable`, `disable`, and `restore` in all forms.
- `#if`, `#elif`, `#else`, `#endif`, `#define`, `#undef`, `#error`, `#warning`, `#line`, `#region`, `#endregion`.
- .NET 10 file-based app directives (`#:package`, `#:sdk`, `#:property`, `#:project`, and `#:include` from SDK 10.0.300), which belong at the top of the file, and a `#!` first line ([docs](https://learn.microsoft.com/en-us/dotnet/core/sdk/file-based-apps)).
- Every `// ReSharper` comment, such as `// ReSharper disable once <Id>`, `// ReSharper disable <Id>`, and `// ReSharper disable All` with `// ReSharper restore All`, plus `// @formatter:off` and `// @formatter:on`.
- `<auto-generated>` or `<auto-generated/>` in a file's first comment, which turns off nullable analysis and most analyzers for the file ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/update-applications/nullable-migration-strategies)).
- Language-injection comments: `// lang=regex` and `// lang=json` (Visual Studio), `//language=regexp` and `/*language=json*/` (Rider and ReSharper).
- File headers checked by IDE0073 or StyleCop (`// <copyright file="..." company="...">`), and license blocks.
- `<inheritdoc/>`, `<include file="..." path="..."/>`, and `///` text that an OpenAPI generator, DocFX, or a shipped IntelliSense XML file carries.
- Attributes doing the same job: `[SuppressMessage]`, `[ExcludeFromCodeCoverage]`, `[FormerlySerializedAs]`.

## Looks cosmetic, isn't

"Verified" means compiled with the C# 5 compiler from .NET Framework 4.8 and run on .NET Framework 4.8 and on .NET 8. Nothing from C# 6 or later was compiled.

- **Eliding `async`/`await`.** Verified: a `using` disposes before the task finishes, argument checks throw at the call instead of faulting the task, `AsyncLocal` writes leak to the caller, and a surrounding `try/catch` misses the failure.
  ```csharp
  async Task<string> Read() { using (var r = new Res()) { return await r.ReadAsync(); } } // ok
  Task<string> Read() { using (var r = new Res()) { return r.ReadAsync(); } }             // reads after Dispose
  ```
- **`throw ex;` versus `throw;`.** Verified: `throw ex` drops the frames below the catch ([CA2200](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2200)).
- **Removing `catch { throw; }`.** A `when` filter runs before the stack unwinds ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/exception-handling-statements)), and a catch below it ends that search early. Verified with a `using` inside the `try` and a caller's VB `When` filter, the same CLR filter C# `when` compiles to: with the catch, `Dispose` ran before the filter; without it, after. In C#, the same held for an `AppDomain.UnhandledException` handler.
- **LINQ runs on each enumeration.** Verified: `var q = orders.Select(o => Charge(o)); q.Count(); foreach (var r in q) {}` charged 3 orders 6 times, and 3 times with `.ToList()`. A query saw an item added to its source later; a `ToList()` snapshot did not. A `foreach` that adds to its list threw `InvalidOperationException`, so `list.ToList()` in a `foreach` is often needed.
- **`.Count() > 0` to `.Any()`.** `Any()` stops at the first item, so later items are never produced. Verified: a logging iterator logged 3 items under `Count()` and 1 under `Any()`, and on a sequence that throws at its second item, `Count()` threw while `Any()` returned `true`.
- **`?.`, `??`, and `is null` skip a custom `==`.** Unity's `==` reports destroyed objects as null, and `?.` and `??` bypass it ([Unity](https://docs.unity3d.com/ScriptReference/Object.html)); `x is null` never calls a user-defined `==` ([patterns](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns)). A base class's `==` counts: Unity scripts inherit it from `UnityEngine.Object`. Verified with `==` overloaded only on a base class: for a derived `target`, `target != null` was false, yet `target ?? fallback` returned `target`.
- **`IShape s = new Square()` to `var s`.** The static type changes, so explicit interface members and overloads resolve differently, and a struct is no longer boxed. Verified: `s.Name()` switched from the interface method to the class method, and for a struct, a copy of the variable stopped sharing state with it.
- **Nullable annotations.** The language ignores them at run time ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/nullable-reference-types)), but a `?` added to or removed from an entity property flips EF Core between a nullable and a required column ([EF Core](https://learn.microsoft.com/en-us/ef/core/modeling/entity-properties)), MVC validates non-nullable model properties as `[Required]` ([validation](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation)), and minimal API handlers treat a parameter with no `?` and no default value as required ([parameter binding](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/parameter-binding)).
- **Deleting public doc comments.** Verified: `csc -warnaserror` passed with an undocumented public method; adding `-doc:Docs.xml` failed with CS1591. Swashbuckle publishes `<summary>` as the OpenAPI operation summary ([Swashbuckle](https://learn.microsoft.com/en-us/aspnet/core/tutorials/getting-started-with-swashbuckle)), and the built-in OpenAPI support in .NET 10 reads `<summary>`, `<remarks>`, `<param>`, and `<response>` ([docs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/openapi-comments)).
- **Deleting comment lines above a `[CallerLineNumber]` call.** The value is compiled into IL ([caller info](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/attributes/caller-information)). Verified: deleting one line above the call lowered the logged value by one. `[CallerArgumentExpression]` captures source text, so renaming a local passed to `ArgumentNullException.ThrowIfNull` changes the exception's parameter name.
- **Renaming parameters or serialized fields.** Verified: parameter names are in the assembly, plain local names are not. ASP.NET Core binds request values to parameters by name ([model binding](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/model-binding)). A renamed Unity serialized field loses its saved values without `[FormerlySerializedAs]` ([Unity](https://docs.unity3d.com/ScriptReference/Serialization.FormerlySerializedAsAttribute.html)).
- **Interpolating a log template.** `LogWarning($"Person {name}")` loses the `{FirstName}` property that `LogWarning("Person {FirstName}", name)` records ([CA2254](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2254)).
- **Class to record, or back.** Records add value equality, a synthesized `==`, and a `ToString` that prints public members ([records](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record)), which changes dictionary keys and log output.

## Safe modernizations

Each rewrite needs the C# version shown. The target framework sets the default (C# 7.3 on .NET Framework and .NET Standard 2.0, C# 12 on .NET 8, C# 14 on .NET 10) unless `LangVersion` overrides it ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning)).

- `"id"` to `nameof(id)` when the string equals the identifier (C# 6).
- `int F() { return x; }` to `int F() => x;` (C# 6; constructors and setters C# 7).
- `string.Format("{0} of {1}", a, b)` to `$"{a} of {b}"` when the result goes to a `string`, not to a log template or to a method with an interpolated string handler overload, such as `Debug.Assert` on .NET 6 and later, which may skip evaluating the holes ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/tokens/interpolated)). Both use the current culture (C# 6; verified for `string.Format`). Not when the only argument is an array: verified, `string.Format("{0}", names)` formats `names[0]`.
- `List<int> xs = new List<int>();` to `new()` (C# 9) or `var` (C# 3) when the declared type is the constructed type.
- `x == null` to `x is null`, `x != null` to `x is not null` (C# 7, C# 9), when neither the type nor a base class defines `==`.
- `if (x != null) x.Run();` to `x?.Run();` (C# 6) and `a != null ? a : b` to `a ?? b`, for reference-type locals and readonly fields when neither the type nor a base class defines `==`.
- `x = x ?? y;` to `x ??= y;` for locals (C# 8). On a property, `??=` skips the setter when the value is not null; verified, `x = x ?? y` calls it.
- `int n; int.TryParse(s, out n)` to `out var n` when the declaration sits directly above the call and the call is its own statement or an `if` condition, not a loop condition (C# 7).
- `new int[] { 1, 2 }` to `[1, 2]` when the target is an array type and the array is not empty (C# 12).
- `.Count() > 0` to `.Any()` on a materialized collection, or to `.Count > 0` or `.Length > 0` when it also cannot be null.
- File-scoped namespace (C# 10) in a one-namespace file, keeping inner `using` directives below `namespace X;`, where the repo already uses it. Do not re-indent multi-line `@"..."` strings: verified, their leading spaces are part of the value.

Not equivalent:

- `.Result` to `await`: verified, `.Result` wraps the failure in `AggregateException`.
- `async void` to `async Task`: verified, an `async void` exception went to the `SynchronizationContext`, or crashed the process when there was none, while an `async Task` exception stayed in the task. Event handler signatures also break.
- `public List<T> Items { get; } = new();` to `=> new();`, which creates a new list on every read.
- Primary constructors (C# 12) for a constructor plus `readonly` fields: the parameters can be assigned, and members that use them read hidden fields ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/tutorials/primary-constructors)).
- Collection expressions for interface targets: the compiler picks the type, and `[]` can be `Array.Empty<T>()` ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/collection-expressions)).
- `using (var r = Open()) { ... }` to `using var r = Open();` (C# 8): `Dispose` moves to the end of the enclosing scope ([docs](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using)).
- A `switch` statement to a switch expression (C# 8): a value no arm matches throws instead of doing nothing ([patterns](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns)).
- Every edit under Looks cosmetic, isn't.

## Verify

Run before the first edit and after each pass, from the same commit, then diff the outputs:

```sh
dotnet build -c Release --no-incremental -p:Deterministic=true -p:DebugType=none \
  -p:IncludeSourceRevisionInInformationalVersion=false 2>&1 \
  | grep -oE '(warning|error) [A-Z]+[0-9]+: .*' | sort | uniq -c > build.txt
find . -path '*/bin/Release/*' \( -name '*.dll' -o -name '*.xml' \) -print0 | sort -z | xargs -0 sha256sum > bin.sha
dotnet test -c Release --no-build
dotnet format --verify-no-changes   # only if the repo already runs it
```

The .NET 8 SDK and later put the commit hash in `InformationalVersion`, which the extra property turns off ([docs](https://learn.microsoft.com/en-us/dotnet/core/compatibility/sdk/8.0/source-link)).

- **Comment-only pass.** The warning list must not change; a new entry usually means a removed directive or doc comment. DLL hashes should match, though this was not verified here, since no .NET SDK was available. If one differs, look for `[CallerLineNumber]` calls below an edit, or a source generator that emits interceptors, which name the source location of each call they replace ([C# 12](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-12#interceptors)). Any `///` edit changes the XML doc file, so diff it and the served OpenAPI JSON. With the XML comment support in .NET 10 OpenAPI, a source generator also compiles `///` text into the DLL ([docs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/openapi-comments)).
- **Rename pass.** Renaming a plain local should leave the DLL unchanged, since local names live in the PDB. Verified with the C# 5 compiler: plain local names stayed out of the DLL, while parameters, lambda parameters, captured locals, and locals in async methods and iterators were metadata, so renaming them changes the DLL.
- **Unity.** Run `Unity -runTests -batchmode -projectPath "$PWD" -testPlatform EditMode -testResults "$PWD/editmode.xml"`, then the same with `PlayMode` ([Unity Test Framework](https://docs.unity3d.com/Packages/com.unity.test-framework@1.1/manual/reference-command-line.html)).
- **Not caught:** paths no test reaches, structured log properties, destroyed-object behavior that only play mode shows, and EF Core schema changes unless you run `dotnet ef migrations has-pending-model-changes` (EF Core 8 and later; [docs](https://learn.microsoft.com/en-us/ef/core/cli/dotnet)).
