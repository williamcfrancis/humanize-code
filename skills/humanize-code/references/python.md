# Python: humanize-code reference

Read this with SKILL.md before you edit Python beyond comments. Python reads docstrings, annotations, names and import order at runtime, so many tidy-looking edits change behavior.

## Tells

- **Docstring on every function** (§6, medium). `Args:` and `Returns:` blocks on private helpers, `"""Initialize the Foo."""` on `__init__`. Delete one only when nothing reads it: grep for `__doc__` and `inspect.getdoc`, and skip argparse `description=__doc__`, Click and Typer commands, FastAPI routes, pydantic models, LLM tool decorators (`@tool`, `@function_tool`, `@mcp.tool`), `>>>` doctests, Sphinx autodoc, Django admindocs and PLY grammar rules. A docstring that is the whole body becomes `pass`, or `...` in a Protocol or stub.
- **Narrated imports and steps** (§5, medium). `# Import necessary libraries`, `# Step 2: Process the data`. Delete them and leave any directive on the line.
- **Demo blocks** (§15, medium). `# Example usage:` under `if __name__ == "__main__":` in a library module. Remove the block only under §15's conditions.
- **Emoji in print strings** (§4, one sighting). On Windows, `print("\u2705 Done")` raises UnicodeEncodeError when stdout goes to a file or pipe and UTF-8 mode is off, so removing the emoji changes behavior there: report it as a fix, not as cosmetic.
- **Catch, log, re-raise** (§10, medium). Remove the `try` only when its one handler is a bare `raise` or `raise e` and nothing else (`raise e` adds a traceback entry). A bare `raise` handler listed before a broader one stops that one from catching the exception, so it stays. For a handler that logs first, follow §10. Never narrow `except:` or `except Exception`, and never add `from e`.
- **Errors turned into defaults** (§12, report only). `except Exception: return None`, `except: pass`, `warnings.filterwarnings("ignore")` at import time.
- **Guards on your own values** (§11, medium). `isinstance` prologues in private functions, `.get("k", {})` chains on a dict built above. `getattr(obj, "name")` with a literal and no default is exactly `obj.name`, unless the name starts with `__` inside a class.
- **Ceremony** (§20, weak alone). Exact rewrites: `True if c else False` to `bool(c)`; `isinstance(x, A) or isinstance(x, B)` to `isinstance(x, (A, B))` when `x` has no side effects and `B` always evaluates cleanly (the tuple form evaluates it even when `x` is an `A`); `a <= b and b <= c` to `a <= b <= c` when `b` has none; `for k in d.keys()` to `for k in d` on a dict. Annotations on function locals are never evaluated, so `n: int = 0` to `n = 0` is runtime-identical; §20 still requires that the checker infer the same type. Keep a bare `n: int` with no value: it makes `n` local to the function. Class and module annotations are different (see below).
- **Names** (§17, medium). `user_data_dict`, `result_list`, a local named `list` or `id`. Parameter names are API in a library, because callers pass them by keyword; in an application, rename them only together with every caller (§17). Always keep: pytest fixture and `parametrize` names, dataclass, pydantic and ORM fields, `f"{x=}"`, Flask views, Celery tasks, Django `clean_<field>` and template filters.
- **Old idioms** (§21, medium). `List[int]`, `Optional[str]`, `class Foo(object)`, `super(Foo, self)`. Use the allowlist below.
- **Progress chatter** (§22, medium). `logger.info("Starting process_order...")`, `print("=" * 50)` in library code. A `basicConfig()` outside the entry point is report only, unless (in an application) none of the module's log calls can ever print and nothing else in the process logs; then it goes with them (§22).

## What people write instead

Use this to judge voice and to write new code. It is not a list of rewrites: change existing code only as a pattern's fix allows.

- `log = logging.getLogger(__name__)` per module, `log.info("loaded %d rows", n)`, logging configured once in the entry point.
- A `try` around the one line that raises, catching the narrowest exception.
- Module functions with `_private` names, not static-method classes; `@dataclass` for records.
- One-line imperative docstrings on public API, none on obvious helpers. Annotated signatures, bare locals.
- `if not items:` for a list the code built; `is None` when None is possible.
- pytest: plain `assert`, fixtures in `conftest.py`, `parametrize`, `pytest.raises(..., match=...)`.

## Comments that do things

- The shebang on line 1 (the Windows `py` launcher reads it too) and the encoding cookie (`# -*- coding: latin-1 -*-`), which counts only on line 1, or on line 2 under a comment line.
- The PEP 723 block from `# /// script` to `# ///`, which runners such as uv read for dependencies.
- Type checkers: `# type: ignore[...]`, type comments (`# type: list[int]`, `# type: (int) -> str`), `# mypy:`, `# pyright:`, `# pyre-ignore`, `# pyre-fixme`, `# pyre-strict`, `# pytype: disable=`, `# ty: ignore`, `# pyrefly: ignore`.
- Linters and formatters: `# noqa`, `# ruff: noqa`, `# flake8: noqa`, `# pylint: disable=`, `# pylint: disable-next=`, `# pylint: skip-file`, `# fmt: off`, `# fmt: on`, `# fmt: skip`, `# yapf: disable`, `# yapf: enable`, `# autopep8: off`, `# autopep8: on`, `# isort: skip`, `# isort: skip_file`, `# isort: split`.
- Scanners: `# nosec`, `# nosemgrep`, `# NOSONAR`, `# codespell:ignore`.
- Coverage: `# pragma: no cover`, `# pragma: no branch`, and any pattern in the coverage config's `exclude_lines` or `exclude_also`.
- Doctest directives inside docstrings: `# doctest: +ELLIPSIS`, `+SKIP`, `+NORMALIZE_WHITESPACE`.
- Tool input: Sphinx `#:` attribute comments, comments tagged for Babel's `--add-comments` (often `# TRANSLATORS:`), `# %%` cell markers.

## Looks cosmetic, isn't

Claims without a link were run on CPython 3.13 and 3.14.

- **Deleting or moving a docstring.** `__doc__` becomes None, also when any statement lands above it. argparse (`description=__doc__`) and Click lose their help text; Click cuts help at `\f` (https://click.palletsprojects.com/en/stable/documentation/), so deleting or moving the `\f` publishes the text after it. pydantic drops the schema `description` (field docstrings too, under `use_attribute_docstrings=True`). FastAPI shows it in OpenAPI (https://fastapi.tiangolo.com/tutorial/path-operation-configuration/). The OpenAI Agents SDK sends it to the model and parses `Args:` into argument descriptions (https://openai.github.io/openai-agents-python/tools/). `python -OO` strips all of them.
- **Removing `from __future__ import annotations`.** Before 3.14, annotations then evaluate at def and class time, so forward references and `if TYPE_CHECKING:` imports raise NameError. Keeping it only defers evaluation: pydantic, FastAPI and `get_type_hints` still evaluate the strings, and it never covers `isinstance(x, int | None)`.
- **Class annotations are fields.** Dropping `: int` from `retries: int = 3` in a dataclass silently removes the field from `__init__`, `repr`, `==` and `asdict()`. pydantic v2 raises instead.
- **Declaration order.** Swapping dataclass fields turns `D(1, 2)` from `x=1, y=2` into `y=1, x=2`. Reordering `Enum` members that use `auto()` changes their values.
- **Truthiness and equality.** `if x:` rejects 0, '' and [] where `if x is not None:` does not. `if len(a) > 0` to `if a` breaks on a NumPy array: it raises unless the array has exactly one element, and then tests that element (https://numpy.org/doc/stable/reference/arrays.ndarray.html). `x == True` is False for `x = 2`. SQLAlchemy turns `col == None` into `IS NULL`, while `col is None` is just False (https://docs.sqlalchemy.org/en/20/core/operators.html#identity-comparisons).
- **Mutable defaults.** `items=[]` to `items=None` changes results when the function mutates or returns the default, which some code uses as a cache. Report it.
- **`+=` aliasing.** `a += b` changes a list or NumPy array in place, so aliases see it; `a = a + b` builds a new object. NumPy `int_arr += 0.5` raises TypeError (https://numpy.org/doc/stable/release/1.10.0-notes.html#default-casting-rule-change), `int_arr + 0.5` returns floats.
- **Float sums.** Since 3.12, `sum()` compensates rounding (https://docs.python.org/3/whatsnew/3.12.html): `sum([0.1] * 10)` is 1.0, a `+=` loop gives 0.9999999999999999.
- **Short-circuiting.** `all([check(x) for x in xs])` calls `check` on every item; `all(check(x) for x in xs)` stops at the first False. Ruff marks this fix unsafe (https://docs.astral.sh/ruff/rules/unnecessary-comprehension-in-call/).
- **`else` clauses.** Dropping `else` from a loop that `break`s runs it after a match too. Moving code from `try ... else:` into the `try` puts it under the `except`.
- **Exceptions.** `except:` to `except Exception:` lets KeyboardInterrupt and SystemExit escape. Adding `from e` sets `__cause__`, adding `from None` hides `__context__`, and both change the traceback text. `getattr(cfg, "retries", 3)` or `d.get("k", 3)` to direct access raises instead of defaulting.
- **Logging.** `basicConfig` does nothing once the root logger has handlers, unless `force=True`, and `logging.info()` calls it implicitly (https://docs.python.org/3/library/logging.html#logging.basicConfig), so adding, moving or removing one changes level and format. `print` to a logger moves output to stderr and, with default settings, drops it below WARNING. An f-string message runs `__str__` even when the level is off; `%s` arguments do not.
- **Imports.** An "unused" import may register models, signals or plugins, and import order is initialization order. A function-level import may be lazy on purpose (optional dependency, startup time, circular import); hoisting it can break the module's import. Dropping a re-export from `__init__.py` breaks `from pkg import name`; dropping a name from `__all__` removes it from `import *`.
- **Empty `__init__.py`.** Deleting it makes a namespace package, which setuptools `find_packages()` leaves out of the wheel.
- **The main guard.** Without `if __name__ == "__main__":` the code runs on import, and under spawn (Windows, macOS) or forkserver (the default on other POSIX systems from 3.14) the child process raises RuntimeError (https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods).
- **Pickled functions.** multiprocessing pickles functions by qualified name, so moving one into a closure or lambda breaks it.
- **Names read as strings.** `f"{user_id=}"` prints `user_id=5`. `mock.patch` targets the name where it is looked up (https://docs.python.org/3/library/unittest.mock.html#where-to-patch): switch `from helpers import fetch` to `import helpers` and `mock.patch("svc.fetch")` raises AttributeError. `self.__token` is stored as `_Cls__token`, so renaming it or the class changes pickles and `vars()`. Flask endpoints default to the view function's name (https://flask.palletsprojects.com/en/stable/api/#flask.Flask.add_url_rule). Celery names tasks by module and function (https://docs.celeryq.dev/en/stable/userguide/tasks.html#task-names), so renaming one changes the `task` header its messages carry (https://docs.celeryq.dev/en/stable/internals/protocol.html#message-protocol-task-v2).
- **Django.** Editing `help_text`, `verbose_name` or `choices` makes `makemigrations` write a new migration (https://docs.djangoproject.com/en/stable/topics/migrations/). Reordering `INSTALLED_APPS` changes which app's templates win (https://docs.djangoproject.com/en/stable/ref/settings/#installed-apps).
- **Directive placement.** A `# type: ignore` before any statement silences mypy for the whole module; a docstring above it ends that (https://mypy.readthedocs.io/en/stable/common_issues.html). A trailing `# noqa` covers only its own line (https://flake8.pycqa.org/en/latest/user/violations.html), so joining lines or inlining a variable can detach it from its target.
- **Merging pasted blocks (§16).** A lambda or nested function made in a loop looks names up when it runs, so `for key, default in pairs: fns[key] = lambda q: q.get(key, default)` gives every function the last pair; bind them with `lambda q, key=key, default=default:`. A module-level dict or list shared by two callers that used to build their own leaks every `append` and item assignment between them.
- **Lookup tables (§20).** `d.get(x, fallback)` raises `TypeError: unhashable type` for a list or dict where the `==` ladder fell through to its else. A branch that returned a fresh list or dict must not become one shared value.
- **Constructors can return anything.** A class that defines `__new__` or a metaclass `__call__` can make `Codec("zstd")` evaluate to `None`, so a `None` check after construction is not always dead.
- **Small syntax.** Whitespace inside triple-quoted strings is data. `return x,` returns a tuple. A "missing" comma between string literals is implicit concatenation. Dropping an `f` with no fields changes output when the string has doubled braces: `f"{{x}}"` prints `{x}`, `"{{x}}"` prints `{{x}}`. `list(set(xs))` loses order.
- **`open()` encoding.** Adding `encoding="utf-8"` changes decoding where the locale encoding is not UTF-8, such as Windows cp1252, through 3.14. UTF-8 mode becomes the default in 3.15 (https://peps.python.org/pep-0686/).

## Safe modernizations

The lowest Python in `requires-python` or the CI matrix decides.

- `List`, `Dict`, `Set`, `Tuple`, `Type[...]` to `list[...]` and the rest: 3.9+, unless repo code compares annotation objects (`List[int] == list[int]` is False).
- `Optional[X]`, `Union[X, Y]` to `X | None`, `X | Y`: 3.10+, and never when a member is a quoted forward reference (`"Foo" | None` raises TypeError). On 3.10 to 3.13, `get_origin()` returns `types.UnionType` instead of `typing.Union`, so check for in-repo annotation introspection.
- `typing.Text` to `str`; `IOError`, `EnvironmentError`, `socket.error` to `OSError`; `class Foo(object):` to `class Foo:`; `u"x"` to `"x"`: any Python 3.
- `socket.timeout` to `TimeoutError`: 3.10+. `asyncio.TimeoutError` to `TimeoutError`, and `timezone.utc` to `UTC` from the `datetime` module (the `datetime` class has no `UTC`): 3.11+.
- `lru_cache(maxsize=None)` to `functools.cache`: 3.9+.
- `super(Foo, self)` to `super()`: when the call sits directly in a method defined in Foo's body (not in a nested function, lambda or generator expression), the method never reassigns its first parameter, and nothing rebinds the name Foo (a class decorator that returns a new class, or a later assignment).
- `"{}".format(a)` to `f"{a}"`: 3.6+, when every argument is a plain name and there are no index fields like `{0[key]}`.

Not equivalent:

- `"%s" % x` to `f"{x}"`: for `x = (5,)`, `%` prints `5`.
- `{**a, **b}` to `a | b`: `|` keeps a defaultdict's type and raises on a plain `Mapping`.
- `loop.run_until_complete(m())` to `asyncio.run(m())`, which creates a new loop and closes it (https://docs.python.org/3/library/asyncio-runner.html#asyncio.run).
- `if not ok: raise ValueError(msg)` to `assert ok, msg`: the error becomes AssertionError, and `-O` removes the check.
- `datetime.utcnow()` to `datetime.now(UTC)`: subtracting or ordering aware and naive values raises TypeError, `==` between them is always False, and `isoformat()` gains `+00:00`.
- `os.path` to `pathlib`, which returns `Path` objects.

## Verify

Comment-only pass: compare ASTs. `ast.dump` omits comments and line numbers but keeps docstrings and strings. Bytecode stores line numbers, so do not compare `.pyc` files.

```sh
git show HEAD:pkg/mod.py > before.py
python -c "import ast,sys; d=[ast.dump(ast.parse(open(p,'rb').read())) for p in sys.argv[1:]]; sys.exit(d[0]!=d[1])" before.py pkg/mod.py
```

The AST cannot see comments that do things. This should print nothing:

```sh
git diff -U0 -- '*.py' | grep -iE '^[-+](#!|.*#:|.*#.*(noqa|type:|pragma|fmt:|isort:|pylint:|pyright:|mypy:|pyre-|ty:|pyrefly:|yapf:|autopep8:|nosec|nosemgrep|nosonar|codespell|doctest:|translators|coding[:=]|///|%%))'
```

A changed docstring shows in the AST on purpose. Prove nothing reads it: save every CLI's `--help`, `app.openapi()` and `Model.model_json_schema()` before and after, and run `pytest --doctest-modules` if the project has doctests.

Rename pass: map old names to new in the before tree, then compare. The map covers variable, parameter, function, class and `except ... as` names only.

```sh
python - before.py pkg/mod.py result_list=out <<'EOF'
import ast, sys
old, new, *pairs = sys.argv[1:]
names = dict(p.split("=") for p in pairs)
tree = ast.parse(open(old, "rb").read())
for node in ast.walk(tree):
    if isinstance(node, ast.Name):
        node.id = names.get(node.id, node.id)
    elif isinstance(node, ast.arg):
        node.arg = names.get(node.arg, node.arg)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.ExceptHandler)):
        node.name = names.get(node.name, node.name)
    elif isinstance(node, (ast.Global, ast.Nonlocal)):
        node.names = [names.get(n, n) for n in node.names]
sys.exit(ast.dump(tree) != ast.dump(ast.parse(open(new, "rb").read())))
EOF
```

Attributes, keyword arguments, imports and strings must come out unchanged, so the check fails on a renamed attribute or method (check those by hand) and on any edited string, `f"{x=}"` included. A renamed parameter still needs §17's check for keyword callers. A string that still names the old identifier, such as `getattr(self, "_old")` or `mock.patch("pkg.mod._old")`, passes. So also run `ruff check --select F821` for undefined names, the project's mypy or pyright config, the tests with CI's flags, and `git grep -n -w old_name` across tests, templates and config. None of these sees names built at runtime, like `getattr(self, f"handle_{kind}")`, and tests miss what they do not cover.
