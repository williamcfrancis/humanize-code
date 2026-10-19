# Java and Kotlin: humanize-code reference

Read this with SKILL.md before you edit Java or Kotlin code beyond comments. On the JVM, names, field order and annotations often feed reflection, serialization or Spring.

## Tells

- **Javadoc and KDoc on everything** (§6, medium). `@param id the id`, `@return the user`, Javadoc on private helpers, getters and tests. On private and package-private members, delete Javadoc that only restates the signature, unless a tool reads it (see [Comments that do things](#comments-that-do-things); Spring Boot metadata and springdoc read private fields) or a checker covers that scope (Checkstyle `MissingJavadocMethod` with `scope` set to `package` or `private`; https://checkstyle.sourceforge.io/checks/javadoc/missingjavadocmethod.html). On public API it is house style: cut it to what the signature does not say, and leave it alone when the build gates on docs (`javadoc -Werror`, Maven `failOnWarnings`, `javac -Xdoclint` with `-Werror`, Checkstyle `MissingJavadocMethod`). Doclint's `missing` group reports missing comments as warnings, and `-Werror` turns warnings into errors (https://docs.oracle.com/en/java/javase/21/docs/specs/man/javadoc.html). Keep `@throws`, `{@inheritDoc}`, `@apiNote`.
- **Interface, Impl and Factory for one class** (§13, weak alone). `UserService` plus `UserServiceImpl` is Spring house style, not a tell. The tell is a `Factory` whose `static create()` wraps `new`, or a one-implementation interface no container sees. A Spring bean fails §13's conditions, so report it instead of collapsing it. Collapsing changes what Spring reads: default bean names come from class names, which `@Qualifier`, `@Resource(name = …)`, SpEL strings and `getBean` can use (https://docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html); injection points, `@MockBean` and `@MockitoBean` name the interface; and the proxy type can change (see Proxy type below).
- **Catch-all that prints** (§12 and §22, report only). `catch (Exception e) { e.printStackTrace(); return null; }`, `System.out.println` in service code. A logger changes stream, format and level; a narrower catch changes what propagates.
- **Redundant modifiers** (§20, weak alone). `public abstract` on interface methods, `public static final` on interface constants, `static` on nested interfaces, enums and records. They are implicit, so removal is exact (JLS 9.3, 9.4, 9.5 and 8.1.3: https://docs.oracle.com/javase/specs/jls/se21/html/jls-9.html, https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.1.3).
- **Boolean ceremony** (§20, weak alone). `if (valid == true)`, `return ok ? true : false`. Simplify only a primitive `boolean`: a null `Boolean` makes `ok == true` and `ok ? true : false` throw NullPointerException, while a plain `return ok` from a method that returns `Boolean` returns null (https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.21.2).
- **Kotlin with a Java accent** (§11 and §20, weak alone). `!!` after a null check, `: Unit`, `public` everywhere, `for (i in 0 until list.size)`. Remove `!!` only where the compiler reports it unnecessary, and drop `: Unit` and `public` only as Safe modernizations allows. Never turn `!!` into `?.`: a crash becomes a silent skip.
- **Scope-function chains** (§20, weak alone). `?.let { } ?: run { }` as if/else, nested `let`, `also { log(…) }` everywhere. Rewrite as an `if` only when the lambda returns a non-null type and `x` is a local `val`:

```kotlin
val label = x?.let { f(it) } ?: "none"      // before: f returns String
val label = if (x != null) f(x) else "none" // after
```

- **Optional ceremony** (§20, weak alone). `if (opt.isPresent()) return opt.get(); else return load();` becomes `return opt.orElseGet(this::load);`, never `orElse(load())`. Report `Optional` fields and parameters.

## What people write instead

- Constructor injection into `private final` fields with no `@Autowired`; in Kotlin, a primary constructor with `private val`.
- SLF4J placeholders (`log.debug("loaded {} rows", n)`), or `@Slf4j` where the repo already uses Lombok. Never add Lombok.
- Records (Java 16+) or the repo's Lombok style for DTOs; Kotlin `data class` for values.
- `@Valid`, `Objects.requireNonNull` or `require` at entry points, and no re-checks inside.
- Method references and short streams; in Kotlin, expression bodies, `val`, `?.` and `?:`, `when`, `it` in one-line lambdas.

## Comments that do things

Never delete, move or reword:

- IDE and formatter markers: `//noinspection` (covers the next statement), `// @formatter:off` and `// @formatter:on`, `//region` and `//endregion`, `// <editor-fold>`, `// language=SQL`, `// spotless:off` and `// spotless:on`.
- Linter markers: `// CHECKSTYLE:OFF` and `// CHECKSTYLE:ON` plus any format the Checkstyle config defines, `// NOPMD` (must stay on the flagged line), `// NOSONAR`, `// ktlint-disable` and `// ktlint-enable` (ktlint before 0.50; https://github.com/pinterest/ktlint/blob/master/CHANGELOG.md).
- Annotations that act as directives: `@SuppressWarnings` (javac lint names, `"PMD.RuleName"`, Error Prone checks), Kotlin `@Suppress` and `@file:Suppress` (compiler, detekt and ktlint rule IDs), `@SuppressFBWarnings`, `@SuppressLint`, `@Generated`. Removing one can fail the build.
- Javadoc that tools read: a `@deprecated` tag (javac's `dep-ann` lint reads it, and javac treats it as deprecation; https://docs.oracle.com/en/java/javase/21/docs/specs/man/javac.html, https://bugs.openjdk.org/browse/JDK-8072583), Javadoc on `@ConfigurationProperties` fields, private ones included (Spring Boot copies it into configuration metadata; https://docs.spring.io/spring-boot/specification/configuration-metadata/annotation-processor.html), Javadoc on methods and fields that springdoc turns into OpenAPI descriptions through therapi-runtime-javadoc (https://springdoc.org/), `{@link}` and `@see` targets, and `@start`, `@end`, `@highlight`, `@replace` and `@link` markup in `{@snippet}` sources (https://docs.oracle.com/en/java/javase/21/javadoc/snippets.html).
- The shebang of a Java single-file program or a Kotlin script, and license headers that Spotless or license-maven-plugin check.
- In Java, any comment containing `\u`.

## Looks cosmetic, isn't

- **Boxed `==`.** `a.equals(b)` rewritten as `a == b` on two `Integer`s compares identity, guaranteed only from -128 to 127, so `Integer a = 1000, b = 1000; a == b` can be false (https://docs.oracle.com/javase/specs/jls/se21/html/jls-5.html#jls-5.1.7).
- **Unboxing null.** An if/else turned into a ternary can add an unboxing. `Integer n = flag ? map.get(k) : 0;` has type `int`, so a missing key throws NullPointerException where the if/else stored null (https://docs.oracle.com/javase/specs/jls/se21/html/jls-15.html#jls-15.25.2).
- **`orElse` and `orElseGet`.** `opt.orElse(load())` always calls `load()`; `orElseGet(this::load)` calls it only when empty (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Optional.html).
- **`Collectors.toList()` to `.toList()`.** `Stream.toList()` is unmodifiable, so a later `add` throws UnsupportedOperationException (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/Stream.html#toList()).
- **Index loop to for-each.** ArrayList's iterator is fail-fast: if the body adds or removes elements, the for-each can throw ConcurrentModificationException (on a best-effort basis, so not every time) where the index loop did not (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html).
- **Removing `serialVersionUID`.** The computed default is "highly sensitive to class details", so old serialized data fails with InvalidClassException (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/io/Serializable.html).
- **Reordering fields.** Lombok's `@RequiredArgsConstructor` takes fields in declaration order (https://projectlombok.org/features/constructor), a record's canonical constructor follows component order (https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.10.4), and a Kotlin data class numbers `componentN()` in declaration order (https://kotlinlang.org/docs/data-classes.html). Swap two `String` fields and positional calls and destructuring silently swap values. Moving a data class property into the body drops it from `equals`, `hashCode`, `toString` and `copy`. Field initializers and `static` initializers run in textual order, so moving a field past one that reads it can change the value that one sees (https://docs.oracle.com/javase/specs/jls/se21/html/jls-12.html#jls-12.4.2, https://docs.oracle.com/javase/specs/jls/se21/html/jls-12.html#jls-12.5).
- **`?.let … ?: run …` is not if/else.** `let` returns the lambda result and `?:` evaluates its right side whenever the left is null, so a `let` block that returns null runs both branches (https://kotlinlang.org/docs/scope-functions.html, https://kotlinlang.org/docs/null-safety.html). Swapping `let` or `run` for `apply` or `also` changes what the call returns: `let` and `run` return the lambda result, `apply` and `also` return the object. Swapping `apply` for `also`, or `let` for `run`, keeps the return value but switches the object between `this` and `it`, so an unqualified name in the block can bind to the object's member in one and to an outer variable in the other.
- **Self-invocation.** A call on `this` bypasses Spring advice (`@Transactional`, `@Async`, `@Cacheable`) with JDK and CGLIB proxies alike (https://docs.spring.io/spring-framework/reference/core/aop/proxying.html; the transaction docs say so for both kinds of proxy: https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html). Moving another bean's `@Transactional` method into its caller's class drops the transaction.
- **Proxy type.** Plain Spring gives a bean with an interface a JDK proxy; without one it gets a CGLIB subclass, which cannot proxy a final class or advise final or private methods (proxying page above). Since Spring 6.0 a class-based proxy also makes `protected` and package-private `@Transactional` methods transactional, while a JDK proxy covers only public methods of the interface (transaction page above). Spring Boot already defaults to CGLIB (https://docs.spring.io/spring-boot/reference/features/aop.html), so removing the interface keeps the proxy type there, but `final` still breaks it. Kotlin classes and their members are final unless declared `open` or opened by the `kotlin-spring` plugin (https://kotlinlang.org/docs/all-open-plugin.html).
- **Names Spring reads.** With several beans of one type and no qualifier or primary, Spring injects the one named like the field or parameter, so renaming `stripeClient` to `client` injects the bean named `client` if there is one and otherwise loses the match (https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired-qualifiers.html). `@PathVariable Long ownerId` binds by parameter name under `-parameters` (https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-requestmapping.html), which Spring Boot's Gradle plugin turns on (https://docs.spring.io/spring-boot/gradle-plugin/reacting.html).
- **`\u` in comments.** Java decodes Unicode escapes before it finds comments, so a reworded `// see C:\users\app` does not compile, and `\u000a` ends a `//` comment early (https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.3).

## Safe modernizations (§21)

- Implicit modifiers, as under Tells (nested records: Java 16+).
- `String.format(f, args)` to `f.formatted(args)` (Java 15+; documented as equivalent: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/String.html#formatted(java.lang.Object...)). Not the overload that takes a `Locale`.
- `if (o instanceof Foo) { Foo f = (Foo) o; … }` to `if (o instanceof Foo f)` (Java 16+) when `o` is a local variable and the cast is the block's first statement.
- `opt.isPresent() ? opt.get() : load()` to `opt.orElseGet(this::load)` (Java 8+); to `orElse(y)` only when `y` is a constant or a local.
- Drop a plain `@Autowired` from a bean's only constructor (Spring 4.3+; https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html). Not on a JUnit test class: Spring autowires its constructor only with `@Autowired`, or when `@TestConstructor` or `spring.test.constructor.autowire.mode` sets the mode to all (https://docs.spring.io/spring-framework/reference/testing/testcontext-framework/support-classes.html).
- `for (int i = 0; i < list.size(); i++)` to for-each when the body never changes the list or `i` and uses `i` only in `list.get(i)`.
- Kotlin: drop a `!!` the compiler marks unnecessary. Drop `: Unit` from a block body only, never from an expression body such as `fun f(): Unit = g()`, whose return type would become whatever `g()` returns (https://kotlinlang.org/docs/functions.html). Drop `public` outside explicit API mode, but not on an `override`: without a modifier it takes the overridden member's `protected` or `internal` visibility (https://kotlinlang.org/docs/visibility-modifiers.html).

Not equivalent:

- `Collectors.toList()` to `.toList()` or `Collectors.toUnmodifiableList()` (unmodifiable; the second also rejects nulls).
- `Arrays.asList` or a filled `HashMap` to `List.of` or `Map.of`: nulls and duplicate keys throw, every mutator throws (an `Arrays.asList` list allows `set` and is backed by its array), and `Map.of` iteration order is unspecified (https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/List.html, https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Map.html).
- An explicit type to `var`: diamond infers `Object`, an int literal stays `int` where the type was `long`, and the concrete class replaces the interface (https://openjdk.org/projects/amber/guides/lvti-style-guide).
- A class to a record or data class, or hand-written methods to Lombok `@Data`: `equals`, `toString`, accessor names and serialization change.
- Concatenated strings to a text block, which strips indentation and trailing spaces and normalizes line endings (https://docs.oracle.com/javase/specs/jls/se21/html/jls-3.html#jls-3.10.6).
- `final` on a Spring bean class or its methods.

## Verify

- Baseline and after each pass: `./gradlew clean build` or `mvn -B clean verify`, which also run the build's checkers (Checkstyle, PMD, ktlint, detekt). After Javadoc edits, also `./gradlew javadoc` or `mvn javadoc:javadoc`. In Spring code, the checks must include a test that loads the application context; if none does, report bean wiring as unverified.
- Comment-only pass: run `scripts/check_cosmetic.py`. It compares `.java`, `.kt` and `.kts` tokens with comments removed, but it does not decode `\u` escapes and it misses most of the Java markers above (it knows `//noinspection` and `@Suppress`), so also copy the compiled output (`build/classes`, `target/classes`) to `before/` and `after/` and run this in bash:

```bash
dis() { javap -v -p "$1" | grep -vE 'line [0-9]+: [0-9]+|Classfile|Last modified|checksum'; }
for f in $(cd before && find . -name '*.class'); do
  diff -q <(dis "before/$f") <(dis "after/$f") >/dev/null || echo "$f"
done
diff <(cd before && find . -type f | sort) <(cd after && find . -type f | sort)
diff -r -x '*.class' before after
git diff -U0 | grep -E '^[-+]' | grep -E 'noinspection|formatter:|region|editor-fold|language=|spotless:|CHECKSTYLE|NOPMD|NOSONAR|ktlint|Suppress|@deprecated|@link|@see|@start|@end|@highlight|@replace|\\u'
```

  Look at every line it prints. The class comparison catches code that a `\u000a` in a comment turned into real code, class files added or removed, and changed configuration metadata. The `git diff` line catches markers that never reach bytecode. For Kotlin classes, use `javap -c -p` in `dis` instead.
- Rename pass: for Java local variable renames, `javap -c -p` output must not change, since local names live only in debug tables. Parameters are not locals here: `-parameters` stores their names in the class file, and Spring binds by them (see Names Spring reads). For private members, only the names may differ, and a private field can still be data: do not rename a field that JPA, Jackson, Gson or Java serialization reads (§17). For Kotlin, read every difference. Then `git grep -n -w oldName` across resources, templates, `@Query` strings, MyBatis XML and YAML, because Jackson, JPA, SpEL and Thymeleaf find members by name.
- None of this catches data serialized by an older build, a different bean that still starts, or paths only production config reaches.
