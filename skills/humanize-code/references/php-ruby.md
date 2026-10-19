# PHP and Ruby: humanize-code reference

Read this with SKILL.md before you edit PHP or Ruby code beyond comments. In both languages, behavior hides in things that look like style: loose comparison, magic comments, and docblocks that frameworks read at runtime.

## Tells

- **Docs that restate the signature** (§6, medium). PHP: `@param int $id The ID.` above `find(int $id)`. Remove a tag only when its type equals the native type and its text only repeats the name; `php-cs-fixer fix --rules=no_superfluous_phpdoc_tags --dry-run --diff` lists candidates. Keep types more precise than the native one (`list<User>`, `array{id: int}`), `@template`, `@throws`, `@deprecated`, and any docblock with an annotation or tool tag. Ruby: `# @param user [User] the user` on private methods. YARD types may be a project's only type information, so delete them only where no YARD docs are published, and keep every `@!` directive.
- **Null and emptiness ladders** (§11, medium). Exact rewrites on plain variables and arrays, not on magic properties or ArrayAccess objects, where each check runs user code: `isset($x) && !empty($x)` to `!empty($x)`; `isset($x) && $x !== null` to `isset($x)`; Ruby `!x.nil? && x.present?` to `x.present?`. An `is_array($items)` check on a parameter declared `array` and never reassigned is dead, since PHP coerces only scalars; `?array` and a `= null` default both let null in (https://www.php.net/manual/en/language.types.declarations.php). Remove Ruby `&.` only when the receiver was just assigned from a literal, or from `.new` on a class that does not redefine `new`.
- **Boolean ceremony** (§20, weak alone). `$valid === true` becomes `$valid` only for a native `bool`. Leave `=== false` after `strpos` and other `int|false` functions, where 0 is a match. Ruby `x.length == 0` becomes `x.empty?` on Array, Hash, and String.
- **Ruby written like Python** (§20, weak alone; counts when several share a method). Drop `return` only from the last expression of a `def` or lambda. Keep it in a block or proc (it leaves the enclosing method), in Ruby's cleanup clause (whose value is discarded without `return`), and in `return a, b`. Drop `self.` only on reads with no same-named local in scope, and never before a keyword, as in `self.class`. Turn `for` into `each` only when nothing the loop assigns, the loop variable included, is read after it or captured by a block in the body, since `for` opens no new scope (https://docs.ruby-lang.org/en/3.4/syntax/control_expressions_rdoc.html, https://docs.ruby-lang.org/en/3.4/syntax/exceptions_rdoc.html).

  ```ruby
  def full_name
    return "#{self.first_name} #{self.last_name}"
  end
  ```
  ```ruby
  def full_name
    "#{first_name} #{last_name}"
  end
  ```

- **Catch or rescue that only rethrows** (§10). `catch (\Exception $e) { throw $e; }`, or `rescue => e` followed only by `raise`. Remove it under §10's conditions, and only when no later catch or rescue clause in the same statement would then take the error: placed first, a rethrowing clause lets that error skip the broader one (https://www.php.net/manual/en/language.exceptions.php, https://docs.ruby-lang.org/en/3.4/syntax/exceptions_rdoc.html). Keep PHP `finally` and Ruby's cleanup clause. Never change the caught class: `\Exception` misses `\Error`, and a bare `rescue` catches StandardError only.
- **Debug leftovers** (§22). Ruby `p` and `pp` print to `$stdout`, not to the web response; remove them under §22's conditions. They return their argument, so `p(total)` as a method's last line becomes `total` (https://docs.ruby-lang.org/en/3.4/Kernel.html). In Rake tasks and scripts, `p`, `pp`, and `puts` are output. Report PHP `var_dump`, `print_r`, `dump()`, and `echo`: they can write into the HTTP response, and output before a `header()` call can stop that header (https://www.php.net/manual/en/function.header.php). `print_r($x, true)` only returns a string. Also report `dd()`, `die()`, `binding.pry`, and `debugger`, which stop or pause execution (https://laravel.com/docs/12.x/helpers#method-dd).
- **Suppressions that arrive with the code** (§25, report only). `# rubocop:disable all`, `@phpstan-ignore-next-line`, `@psalm-suppress`, or `// phpcs:ignore` with no reason, added in the same diff as the line it hides. Also report directives that RuboCop's Lint/RedundantCopDisableDirective or PHPStan's unmatched-ignore check flags.
- **Idioms older than the project** (§21). `array()` in PHP 8 code, `:key => value` hashes in Ruby. Apply only the allowlist below.

## What people write instead

- PHP: native types, docblocks only for generics and array shapes, `===` by default, `??` for optional keys, `?->` on PHP 8, validation at the edge (form requests, validator constraints).
- Ruby: implicit return, `each` and `map(&:name)`, `return unless user` guards, `unless` for one negation, predicates ending in `?`, `fetch` for required keys; in Rails, `present?`, `presence`, and scopes.
- Few comments in either. Full PHPDoc and YARD belong to published libraries.

## Comments that do things

PHP:
- The `#!/usr/bin/env php` shebang, and `declare(strict_types=1);`, which is code that looks like a header.
- PHP_CodeSniffer `phpcs:ignore`, `phpcs:disable`, `phpcs:enable`, `phpcs:ignoreFile`, and the older `@codingStandardsIgnore*` forms.
- PHPStan and Psalm: `@phpstan-ignore`, `@phpstan-ignore-line`, `@phpstan-ignore-next-line`, `@psalm-suppress`, every `@phpstan-*` and `@psalm-*` tag, `@template`, `@extends`, `@implements`, `@property`, `@method`, `@mixin`, inline `/** @var Foo $x */`. PhpStorm `@noinspection`.
- PHPUnit doc-comment metadata such as `@test`, `@dataProvider`, `@depends`, `@group`, and `@covers` (read through PHPUnit 11), and the `@codeCoverageIgnore` family.
- Runtime annotations: Doctrine `@ORM\...`, Symfony `@Route`, `@Assert\...`, `@Groups`, `@IsGranted`, and any `@Vendor\Name(...)` tag a library parses (JMS Serializer, API Platform, swagger-php `@OA\...`).
- `__halt_compiler();` and the bytes after it.
- HTML comments in templates outside `<?php ?>`, which are output.

Ruby:
- The shebang and encoding comments (`# encoding:`, `# coding:`, `# -*- coding: utf-8 -*-`) on line 1, or line 2 after a shebang.
- `# frozen_string_literal:` in the first comment section; `# warn_indent:` and `# shareable_constant_value:`, which act on the code that follows them; `__END__` and the `DATA` after it.
- `# rubocop:disable`, `# rubocop:enable`, `# rubocop:todo`, their end-of-line forms and `-- reason` notes, the next-statement forms (`disable-next`, `todo-next`, `enable-next`, `next`), and `push`/`pop`; Standard's `# standard:disable` and `# standard:enable`.
- Sorbet `# typed:` sigils, rbs-inline `# rbs_inline: enabled` with `#:` and `# @rbs` comments, Steep `# @type` annotations.
- YARD directives (`@!method`, `@!attribute`, `@!macro`, `@!parse`, `@!scope`, `@!visibility`, `@!group`, `@!endgroup`) and output tags (`@private`, `@api`, `@overload`, `@deprecated`).
- RDoc `:nodoc:`, `:doc:`, `:stopdoc:`, `:startdoc:`, `:enddoc:`, `:call-seq:`, `:yields:`, `:section:`, `:markup:`.
- SimpleCov `# :nocov:` pairs and `# simplecov:disable` / `# simplecov:enable`.
- The `# == Schema Information` block the annotate gem maintains.
- HTML comments in ERB templates, which are output.

## Looks cosmetic, isn't

PHP:
- Swapping `==` and `===`, adding `true` to `in_array()`, or turning `switch` into `match`. Loose comparison reads numeric strings as numbers; `match` uses `===` and throws UnhandledMatchError when no arm matches. `"1" == "01"` is true, and `0 == "foo"` was true before PHP 8 and is false since (https://www.php.net/manual/en/migration80.incompatible.php, https://www.php.net/manual/en/control-structures.match.php).
- Treating `isset`, `empty`, `!$x`, `=== null`, and `array_key_exists` as one check. `isset` is false for a key holding null. `empty()` means `!isset($x) || $x == false`, so `'0'` is empty. `isset` and `empty` are silent on missing variables and call `__isset()`; `!$x` and `=== null` warn and call `__get()` (https://www.php.net/manual/en/function.empty.php, https://www.php.net/manual/en/language.oop5.overloading.php).
  ```php
  $a = ['k' => null];
  isset($a['k']);             // false
  array_key_exists('k', $a);  // true
  ```
- Swapping `?:` and `??`. `'0' ?: 'd'` is `'d'`; `'0' ?? 'd'` is `'0'` (https://www.php.net/manual/en/language.operators.comparison.php).
- Turning `count($items) > 0` into `if ($items)`. Objects convert to true, so an empty Collection passes (https://www.php.net/manual/en/language.types.boolean.php).
- Adding, removing, or moving `declare(strict_types=1)`. It must be the first statement, and it picks coercion or TypeError for calls made from that file and returns from functions defined in it: `sum(1.5, 2.5)` with `int` parameters returns `int(3)` without it and throws with it (https://www.php.net/manual/en/language.types.declarations.php, https://wiki.php.net/rfc/scalar_type_hints_v5).
- Deleting a docblock with annotations. Doctrine ORM 2.x reads `@ORM\Column` from the property docblock at runtime; the opcache docs say dropping comments breaks Doctrine and PHPUnit. Moving to `#[...]` attributes is a migration, since Doctrine ORM 3 and Symfony 7 removed annotations (https://www.doctrine-project.org/projects/doctrine-orm/en/2.20/reference/annotations-reference.html, https://www.php.net/manual/en/opcache.configuration.php, https://github.com/doctrine/orm/blob/3.0.0/UPGRADE.md, https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md).
- Renaming. PHP 8 callers may pass arguments by name; `compact('user')`, `extract()`, and `$$name` use local names; an included template shares the caller's scope; Laravel route model binding matches `/users/{user}` to `User $user` (https://www.php.net/manual/en/functions.arguments.php, https://www.php.net/manual/en/function.include.php, https://laravel.com/docs/routing#implicit-binding).
- Rewording a `//` or `#` comment to contain `?>`. That ends the comment and PHP mode, so the text after it is printed (https://www.php.net/manual/en/language.basic-syntax.comments.php).
- Adding a line under a directive. `// phpcs:ignore` alone on a line covers it and the next line; a lone `@phpstan-ignore` or `@phpstan-ignore-next-line` covers the next line (https://github.com/PHPCSStandards/PHP_CodeSniffer/wiki/Advanced-Usage, https://phpstan.org/user-guide/ignoring-errors).

Ruby:
- Dropping `self.` from a write. `status = :done` creates a local instead of calling the writer, and later bare `status` reads it even if that line never ran: `a = 0 if false; a # => nil` (https://docs.ruby-lang.org/en/3.4/syntax/assignment_rdoc.html).
- Swapping `and`/`or` and `&&`/`||`. `and` and `or` bind looser than `=` and share one level; `&&` binds tighter than `||`. `ok = true and false` leaves `ok` true (https://docs.ruby-lang.org/en/3.4/syntax/precedence_rdoc.html).
- Swapping `try` and `&.`, or `a && a.b` and `a&.b`. ActiveSupport's `try` returns nil when a non-nil receiver lacks a public method; `&.` raises. `&.` skips only nil, so `false&.b` calls `b` (https://api.rubyonrails.org/classes/Object.html, https://docs.ruby-lang.org/en/3.4/syntax/calling_methods_rdoc.html).
  ```ruby
  5.try(:upcase)  # => nil
  5&.upcase       # NoMethodError
  ```
- Simplifying conditions as in PHP. Only `nil` and `false` are falsy, so `if items.any?` is not `if items` (https://docs.ruby-lang.org/en/3.4/syntax/control_expressions_rdoc.html).
- Touching `# frozen_string_literal: true`. With it, literals without interpolation are frozen and allocated once; without it, each evaluation builds a new mutable string (Ruby 3.4 warns on mutation only when deprecation warnings are on, as with `-W:deprecated`). It counts only in the first comment section (https://docs.ruby-lang.org/en/3.4/syntax/comments_rdoc.html, https://www.ruby-lang.org/en/news/2024/12/25/ruby-3-4-0-released/).
- Adding a blank line after `# rubocop:disable-next` or `todo-next`. It detaches the directive from its statement (https://docs.rubocop.org/rubocop/latest/usage/source_code_directives.html).
- Turning `h.fetch(:k, nil)` into `h[:k]`. `fetch` ignores the hash's default: `Hash.new(0)[:x]` is 0, `Hash.new(0).fetch(:x, nil)` is nil (https://docs.ruby-lang.org/en/3.4/Hash.html).
- Deleting a `respond_to_missing?` that nothing calls. `respond_to?` calls it for undefined methods, so duck-typed callers stop using the `method_missing` methods (https://docs.ruby-lang.org/en/3.4/Object.html). Report, rather than make, any swap between `method_missing` and real methods.
- Renaming. Keyword parameter names are part of every call; `f(name:)` and `{ name: }` read a local by name (Ruby 3.1); `send`, `before_action`, `validate`, and `permit` name methods and fields by symbol; Rails views read the controller's instance variables (https://www.ruby-lang.org/en/news/2021/12/25/ruby-3-1-0-released/, https://guides.rubyonrails.org/layouts_and_rendering.html).

## Safe modernizations

- PHP 5.4+: `array(...)` to `[...]`.
- PHP 7.0+: `isset($a['k']) ? $a['k'] : $d` to `$a['k'] ?? $d`, when `$a` is a plain array variable (not ArrayAccess or magic properties) and the key has no side effects.
- PHP 7.1+: `list($a, $b) = $x` to `[$a, $b] = $x`.
- PHP 8.0+: `strpos($h, $n) !== false` to `str_contains($h, $n)`; `strpos($h, $n) === 0` to `str_starts_with($h, $n)`.
- Ruby 1.9+: `{ :a => 1 }` to `{ a: 1 }` for plain identifier keys; `lambda { |x| }` to `->(x) { }` (https://docs.ruby-lang.org/en/3.4/NEWS/NEWS-1_9_1.html).
- Ruby 3.1+: `{ x: x }` to `{ x: }`, and `f(x: x)` to `f(x:)`.
- Any Ruby: `if !x` to `unless x` when the whole condition is `!x` and there is no `else` or `elsif`.

Not equivalent, besides the swaps above:
- Constructor promotion: promoted properties are set before the constructor body runs, and defaults stay on the parameter (https://www.php.net/manual/en/language.oop5.decon.php).
- `{ "a" => 1 }` to `{ "a": 1 }`: the quoted label makes a Symbol key.
- `map { |x| x.f }` to `map(&:f)` when the iterator yields several values: `Symbol#to_proc` passes the extras as arguments.
- `inject(:+)` to `sum`: `sum` starts from 0, so it raises TypeError on strings that `inject(:+)` joins; it may ignore a redefined `+`, compensates float rounding, and returns 0 for `[]` where `inject` returns nil (https://docs.ruby-lang.org/en/3.4/Array.html, https://github.com/ruby/spec/blob/master/core/array/sum_spec.rb, https://github.com/ruby/spec/blob/master/core/enumerable/inject_spec.rb).
- `x.length > 0` to `x.any?`: `[nil].any?` is false.

## Verify

PHP:
- `php -l file.php` checks syntax only.
- After a comment-only pass, diff token streams without comments and whitespace (PHP 8.0+). Docblocks and template text stay in, so expect only the docblocks you meant to change. Check that each directive the grep prints survived on the same target line.
  ```php
  <?php // tokens.php, in your scratch directory
  foreach (PhpToken::tokenize(file_get_contents($argv[1])) as $t) {
      if (!$t->is([T_COMMENT, T_WHITESPACE])) echo $t->getTokenName(), ' ', $t->text, "\n";
  }
  ```
  ```sh
  git show HEAD:src/Order.php > old.php
  php tokens.php old.php > a.txt && php tokens.php src/Order.php > b.txt && diff a.txt b.txt
  git diff -U0 | grep -E '^[+-].*(phpcs|@codingStandards|@phpstan|@psalm|@noinspection|@ORM|@Route|@Assert|@codeCoverage|strict_types)'
  ```
- After a rename pass, run the repo's `vendor/bin/phpstan analyse`, `vendor/bin/psalm`, `vendor/bin/phpcs`, and `vendor/bin/phpunit`, and diff `bin/console debug:router` or `php artisan route:list --json`, plus `bin/console doctrine:mapping:info`.
- Do not count on these to catch names used as strings (`compact`, `$$name`, named arguments from outside the repo) or loose comparisons on untested data.

Ruby:
- `ruby -wc file.rb` checks syntax only.
- After a comment-only or rename pass, diff compiled instructions with line numbers stripped, on one Ruby version, without running the file. Expect no diff after comments and only the renamed names after renames. Comments are not compiled, so grep the diff for directives and check that each one it prints survived on the same target line.
  ```ruby
  # iseq.rb, in your scratch directory
  asm = RubyVM::InstructionSequence.compile_file(ARGV[0]).disasm
  puts asm.gsub(/\(\s*\d+\)(\[\w+\])?$/, "").gsub(/@\S*?:\d+|\(\d+,\d+\)-\(\d+,\d+\)/, "")
  ```
  ```sh
  git show HEAD:app/models/order.rb > old.rb
  ruby iseq.rb old.rb > a.txt && ruby iseq.rb app/models/order.rb > b.txt && diff a.txt b.txt
  git diff -U0 | grep -E '^[+-].*#(:| *(frozen_string_literal|-\*-|encoding:|coding:|warn_indent|shareable_constant|rubocop:|standard:|typed:|rbs_inline|@rbs|@type|@!|:[a-z-]+:|simplecov:))'
  ```
- Run `bundle exec rubocop` with the repo config, the tests, `bundle exec srb tc` when files have `# typed:`, and diff `bin/rails routes`.
- Do not count on these to catch `send` or `method_missing` on names built at runtime, or instance variables a view reads.
