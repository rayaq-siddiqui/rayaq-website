"""Regenerates COMMAND_CATEGORIES and COMMANDS for backend/jj_docs.py from a jj checkout.

Usage: python3 specs/jj-tools/gen_commands.py <path-to-jj-checkout>
Categories and tiers are listed below and follow spec §8A; new upstream commands must be
added to CATEGORIES by hand (the script fails loudly on anything it cannot resolve).
"""
import os
import re
import sys

ROOT = sys.argv[1]
CMD = os.path.join(ROOT, "cli/src/commands")

CATEGORIES = [
    ("Creating and editing changes", ["new", "edit", "describe", "commit", "metaedit", "next", "prev"]),
    ("Moving and combining changes", ["rebase", "squash", "split", "absorb", "duplicate", "abandon", "parallelize", "simplify-parents", "arrange", "converge", "revert", "restore", "diffedit"]),
    ("Content and conflicts", ["fix", "run", "resolve", "file annotate", "file chmod", "file list", "file search", "file show", "file track", "file untrack", "sparse edit", "sparse list", "sparse reset", "sparse set"]),
    ("Inspecting history", ["log", "show", "diff", "interdiff", "status", "evolog", "root", "bisect run"]),
    ("Operation log", ["undo", "redo", "operation abandon", "operation diff", "operation integrate", "operation log", "operation restore", "operation revert", "operation show"]),
    ("Bookmarks and tags", ["bookmark advance", "bookmark create", "bookmark delete", "bookmark forget", "bookmark list", "bookmark move", "bookmark rename", "bookmark set", "bookmark track", "bookmark untrack", "tag delete", "tag list", "tag set", "tag track", "tag untrack"]),
    ("Git and remotes", ["git clone", "git colocation", "git export", "git fetch", "git import", "git init", "git push", "git remote", "git root", "gerrit upload"]),
    ("Workspaces", ["workspace add", "workspace forget", "workspace list", "workspace remove", "workspace rename", "workspace root", "workspace update-stale"]),
    ("Signing", ["sign", "unsign"]),
    ("Configuration", ["config edit", "config gc", "config get", "config list", "config path", "config set", "config unset"]),
    ("Utilities and internals", ["help", "version", "util backend", "util completion", "util config-schema", "util diff", "util exec", "util gc", "util install-man-pages", "util markdown-help", "util snapshot", "debug", "bench"]),
]

READ_ONLY = {
    "file annotate", "file list", "file search", "file show", "sparse list",
    "log", "show", "diff", "interdiff", "status", "evolog", "root",
    "operation diff", "operation log", "operation show",
    "bookmark list", "tag list", "git root", "workspace list", "workspace root",
    "config edit", "config gc", "config get", "config list", "config path", "config set", "config unset",
}


def kebab(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def rust_files(path):
    if os.path.isdir(path):
        for dirpath, _, files in os.walk(path):
            for f in files:
                if f.endswith(".rs"):
                    yield os.path.join(dirpath, f)
    elif os.path.isfile(path):
        yield path


def doc_for(type_name, search_paths):
    pattern = re.compile(rf"^pub(\(crate\))?\s+(struct|enum)\s+{re.escape(type_name)}\b")
    for base in search_paths:
        for f in rust_files(base):
            lines = open(f, encoding="utf-8").read().splitlines()
            for i, line in enumerate(lines):
                if pattern.match(line):
                    j = i - 1
                    while j >= 0 and (lines[j].startswith("#[") or not lines[j].strip() or (lines[j].startswith("//") and not lines[j].startswith("///"))):
                        j -= 1
                    doc = []
                    k = i - 1
                    while k >= 0 and lines[k].startswith("#[") and not lines[k].startswith("#[doc"):
                        k -= 1
                    if k >= 0 and lines[k].rstrip().endswith('"#]'):
                        start = k
                        while not lines[start].lstrip().startswith("#[doc"):
                            start -= 1
                        body = [lines[start].split('r#"', 1)[1]] + lines[start + 1:k]
                        body = [b.strip() for b in body]
                        while body and not body[0]:
                            body.pop(0)
                        first = []
                        for d in body:
                            if not d:
                                break
                            first.append(d)
                        return " ".join(first), os.path.relpath(f, ROOT), i + 1
                    while j >= 0 and lines[j].startswith("///"):
                        doc.insert(0, lines[j][3:].strip())
                        j -= 1
                    first = []
                    for d in doc:
                        if not d:
                            break
                        first.append(d)
                    rel = os.path.relpath(f, ROOT)
                    return " ".join(first), rel, i + 1
    return None, None, None


def variants(enum_file, enum_regex):
    text = open(enum_file, encoding="utf-8").read()
    m = re.search(enum_regex + r"\s*\{(.*?)\n\}", text, re.S)
    out = {}
    for v in re.finditer(r"^\s+([A-Z][A-Za-z]*)\(([A-Za-z_:]+)\)", m.group(1), re.M):
        out[kebab(v.group(1))] = v.group(2).split("::")[-1]
    return out


top = variants(os.path.join(CMD, "mod.rs"), r"enum Command")
entries = []
for category, commands in CATEGORIES:
    for command in commands:
        parts = command.split(" ")
        if len(parts) == 1:
            type_name = top[parts[0]]
            search = [os.path.join(CMD, parts[0].replace("-", "_") + ".rs"), os.path.join(CMD, parts[0].replace("-", "_")), CMD]
        else:
            parent = parts[0].replace("-", "_")
            sub_enum_file = os.path.join(CMD, parent, "mod.rs")
            subs = variants(sub_enum_file, r"enum [A-Za-z]*(?:Command|Subcommand)")
            type_name = subs[parts[1]]
            search = [os.path.join(CMD, parent)]
        summary, rel, line = doc_for(type_name, search)
        assert summary, (command, type_name)
        tier = "C" if category == "Utilities and internals" else ("B" if command in READ_ONLY else "A")
        entries.append((command, category, tier, summary, rel, line))

GROUPED = {"debug", "bench"}
NESTED = {"git colocation", "git remote", "util backend"}
listed = {c for _, cs in CATEGORIES for c in cs}
upstream = set()
for name in top:
    sub_mod = os.path.join(CMD, name.replace("-", "_"), "mod.rs")
    if name in GROUPED or not os.path.isfile(sub_mod):
        upstream.add(name)
        continue
    for sub in variants(sub_mod, r"enum [A-Za-z]*(?:Command|Subcommand)"):
        upstream.add(f"{name} {sub}")
missing = sorted(upstream - listed)
gone = sorted(listed - upstream - NESTED)
if missing or gone:
    sys.exit(f"CATEGORIES is out of date. Missing: {missing}. No longer upstream: {gone}")

print("COMMAND_CATEGORIES = [")
for category, _ in CATEGORIES:
    print(f"    {category!r},")
print("]")
print()
print("COMMANDS = [")
for command, category, tier, summary, rel, line in entries:
    print("    {")
    print(f'        "command": {command!r},')
    print(f'        "category": {category!r},')
    print(f'        "tier": {tier!r},')
    print(f'        "summary": {summary!r},')
    print(f'        "source": ({rel!r}, {line}),')
    print("    },")
print("]")
print(len(entries), file=sys.stderr)
