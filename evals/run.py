#!/usr/bin/env python3
"""Run the humanize-code evals.

  python evals/run.py prepare <fixture> <dir>   copy a fixture to <dir>, commit a baseline, record its outputs
  python evals/run.py grade <fixture> <dir>     after an agent has worked in <dir>: did behavior change, how did the code change
  python evals/run.py check-traps [fixture...]  make sure every trap mutation breaks the fixture's checks

Needs git, Node 20+ and Python 3.13 (the CLI snapshots were recorded on 3.13).
"""

import argparse
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

EVALS = Path(__file__).resolve().parent
SUITE = json.loads((EVALS / "suite.json").read_text(encoding="utf-8"))["fixtures"]
SCANNER = EVALS.parent / "skills" / "humanize-code" / "scripts" / "scan.py"
GIT_ID = ["-c", "user.name=humanize-code eval", "-c", "user.email=eval@example.invalid"]


def kill_tree(proc):
    # killing only the shell leaves node/python children holding the pipes open
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        os.killpg(proc.pid, signal.SIGKILL)


def sh(cmd, cwd, timeout=300):
    cmd = cmd.replace("{python}", f'"{sys.executable}"')
    proc = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", start_new_session=os.name != "nt")
    try:
        out, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        kill_tree(proc)
        out, _ = proc.communicate()
        return False, f"{out}\ntimed out after {timeout}s: {cmd}"
    return proc.returncode == 0, out


def remove_tree(path):
    # git marks object files read-only, which stops rmtree on Windows
    def make_writable(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=make_writable)
    else:
        shutil.rmtree(path, onerror=make_writable)


def git(cwd, *args):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


def run_checks(spec, cwd):
    results = []
    for check in spec["checks"]:
        ok, out = sh(check["cmd"], cwd)
        results.append((check["name"], ok, out))
    return results


def baseline_dir(dest):
    return dest.with_name(dest.name + ".baseline")


def artifacts_match(spec, dest):
    saved = baseline_dir(dest)
    return all((dest / a).exists() and (dest / a).read_bytes() == (saved / a).read_bytes() for a in spec["artifacts"])


def prepare(name, dest, quiet=False):
    spec = SUITE[name]
    if dest.exists():
        sys.exit(f"{dest} already exists")
    shutil.copytree(EVALS / "fixtures" / name, dest,
                    ignore=shutil.ignore_patterns("node_modules", "dist", ".cache", "__pycache__"))
    git(dest, "init", "-q", "-b", "main")
    git(dest, "config", "core.autocrlf", "false")
    git(dest, "add", "-A")
    git(dest, *GIT_ID, "commit", "-q", "-m", "baseline")

    for cmd in spec["setup"]:
        ok, out = sh(cmd, dest)
        if not ok:
            sys.exit(f"setup failed: {cmd}\n{out}")
    for check, ok, out in run_checks(spec, dest):
        if not ok:
            sys.exit(f"baseline check '{check}' fails, so the fixture is broken:\n{out[-3000:]}")

    saved = baseline_dir(dest)
    saved.mkdir()
    for artifact in spec["artifacts"]:
        target = saved / artifact
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest / artifact, target)

    if not quiet:
        print(f"Prepared {name} in {dest}")
        print(f"Point your agent at that folder with the skill loaded. Tell it not to touch: {', '.join(spec['protected'])}.")
        print(f"Then run: python {Path(__file__).name} grade {name} {dest}")


COMMENT_STARTS = {
    ".py": ("#",),
    ".css": ("/*", "*"),
    ".html": ("<!--",),
}
JS_LIKE = {".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}


def comment_lines(text, suffix):
    count = 0
    in_block = False
    in_doc = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if suffix == ".py":
            quotes = line.count('"""') + line.count("'''")
            if in_doc or quotes or line.startswith("#"):
                count += 1
            if quotes == 1:
                in_doc = not in_doc
            continue
        if in_block:
            count += 1
            in_block = "*/" not in line
            continue
        starts = ("//", "/*", "*", "{/*") if suffix in JS_LIKE else COMMENT_STARTS.get(suffix, ())
        if line.startswith(starts) or re.search(r"/\*.*\*/\s*$", line):
            count += 1
            in_block = line.startswith(("/*", "{/*")) and "*/" not in line
    return count


def source_files(root, spec):
    for top in spec["sources"]:
        for path in sorted((root / top).rglob("*")):
            if path.is_file() and path.suffix in JS_LIKE | {".py", ".css", ".html"}:
                yield path.relative_to(root)


def snapshot_base(dest, commit):
    tmp = Path(tempfile.mkdtemp(prefix="hc-base-"))
    archive = subprocess.run(["git", "archive", commit], cwd=dest, capture_output=True, check=True).stdout
    archive_path = tmp / "base.tar"
    archive_path.write_bytes(archive)
    shutil.unpack_archive(archive_path, tmp / "src")
    return tmp


def scan(root):
    if not SCANNER.exists():
        return None
    r = subprocess.run([sys.executable, str(SCANNER), "--json", str(root)], capture_output=True, text=True, encoding="utf-8")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


def grade(name, dest, as_json=False):
    spec = SUITE[name]
    _, base = git(dest, "rev-list", "--max-parents=0", "HEAD")
    base = base.strip()
    report = {"fixture": name}

    _, untracked = git(dest, "status", "--porcelain", "--", *spec["protected"])
    changed_code, _ = git(dest, "diff", "--quiet", base, "--", *spec["protected"])
    report["protected_untouched"] = changed_code == 0 and not untracked.strip()

    report["checks"] = {}
    failures = {}
    for check, ok, out in run_checks(spec, dest):
        report["checks"][check] = ok
        if not ok:
            failures[check] = out[-2500:]

    report["artifacts_identical"] = artifacts_match(spec, dest) if spec["artifacts"] else None

    tmp = snapshot_base(dest, base)
    try:
        before_root = tmp / "src"
        files = {}
        for rel in sorted(set(source_files(before_root, spec)) | set(source_files(dest, spec))):
            b, a = before_root / rel, dest / rel
            bt = b.read_text(encoding="utf-8") if b.exists() else ""
            at = a.read_text(encoding="utf-8") if a.exists() else ""
            files[str(rel).replace("\\", "/")] = {
                "lines": [sum(1 for l in bt.splitlines() if l.strip()), sum(1 for l in at.splitlines() if l.strip())],
                "comments": [comment_lines(bt, rel.suffix), comment_lines(at, rel.suffix)],
            }
        report["files"] = files
        before_scan, after_scan = scan(before_root), scan(dest)
        if before_scan is not None and after_scan is not None:
            report["scanner_findings"] = [len(before_scan["findings"]), len(after_scan["findings"])]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    _, diff = git(dest, "diff", base, "-U0")
    added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    report["self_referential_comments"] = [
        l.strip() for l in added
        if re.search(r"(//|#|/\*).*\b(simplif|refactor|removed|cleaned up|for readability|humaniz)", l, re.I)
    ]
    _, status = git(dest, "status", "--porcelain")
    report["new_files"] = [l[3:] for l in status.splitlines() if l.startswith("??")]

    if as_json:
        print(json.dumps(report, indent=2))
        return report

    mark = lambda ok: "pass" if ok else "FAIL"
    print(f"{name}")
    print(f"  protected files untouched  {mark(report['protected_untouched'])}")
    for check, ok in report["checks"].items():
        print(f"  {check:<26} {mark(ok)}")
    if report["artifacts_identical"] is not None:
        print(f"  build output identical     {mark(report['artifacts_identical'])}")
    lines = [sum(f["lines"][i] for f in files.values()) for i in (0, 1)]
    comments = [sum(f["comments"][i] for f in files.values()) for i in (0, 1)]
    print(f"  lines                      {lines[0]} -> {lines[1]}")
    print(f"  comment lines              {comments[0]} -> {comments[1]}")
    if "scanner_findings" in report:
        print(f"  scanner findings           {report['scanner_findings'][0]} -> {report['scanner_findings'][1]}")
    if report["self_referential_comments"]:
        print("  comments about the cleanup itself:")
        for line in report["self_referential_comments"]:
            print(f"    {line}")
    if report["new_files"]:
        print(f"  new files: {', '.join(report['new_files'])}")
    for check, out in failures.items():
        print(f"\n--- {check} output (tail) ---\n{out}")
    return report


def apply_edits(root, edits):
    for edit in edits:
        path = root / edit["file"]
        text = path.read_text(encoding="utf-8")
        if edit["find"] not in text:
            return f"pattern not found in {edit['file']}: {edit['find'][:60]!r}"
        count = -1 if edit.get("all") else 1
        path.write_text(text.replace(edit["find"], edit["replace"], count), encoding="utf-8", newline="")
    return None


def check_traps(names):
    missed = 0
    for name in names:
        spec = SUITE[name]
        work = Path(tempfile.mkdtemp(prefix=f"hc-{name}-"))
        dest = work / "fx"
        try:
            prepare(name, dest, quiet=True)
            for mutation in spec["mutations"]:
                problem = apply_edits(dest, mutation["edits"])
                if problem:
                    print(f"  {name}/{mutation['id']:<26} BROKEN MUTATION: {problem}", flush=True)
                    missed += 1
                else:
                    caught = not all(ok for _, ok, _ in run_checks(spec, dest)) or not artifacts_match(spec, dest)
                    missed += not caught
                    print(f"  {name}/{mutation['id']:<26} {'caught' if caught else 'MISSED'}", flush=True)
                git(dest, "checkout", "--", ".")
        finally:
            remove_tree(work)
    print("every trap is caught" if not missed else f"{missed} trap(s) not caught")
    return missed == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("fixture", choices=sorted(SUITE))
    p.add_argument("dir", type=Path)
    g = sub.add_parser("grade")
    g.add_argument("fixture", choices=sorted(SUITE))
    g.add_argument("dir", type=Path)
    g.add_argument("--json", action="store_true")
    t = sub.add_parser("check-traps")
    t.add_argument("fixtures", nargs="*", choices=sorted(SUITE))
    args = parser.parse_args()

    if args.command == "prepare":
        prepare(args.fixture, args.dir.resolve())
    elif args.command == "grade":
        report = grade(args.fixture, args.dir.resolve(), as_json=args.json)
        ok = report["protected_untouched"] and all(report["checks"].values()) and report["artifacts_identical"] is not False
        sys.exit(0 if ok else 1)
    else:
        sys.exit(0 if check_traps(args.fixtures or sorted(SUITE)) else 1)


if __name__ == "__main__":
    main()
