import re

UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj",
    "commit": "0cb02a837f28459cd698734264c9fcd3712ec0d1",
    "commit_date": "2026-10-01",
    "version": "0.45.1",
    "analyzed_on": "2026-10-02",
}

PAGES = [
    {
        "slug": "storage",
        "title": "On-disk layout",
        "summary": "What lives where under .jj/, which component owns each path, and in what format.",
        "sources": [
            "lib/src/repo.rs",
            "lib/src/workspace.rs",
            "lib/src/simple_op_store.rs",
            "lib/src/simple_op_heads_store.rs",
            "lib/src/default_index/store.rs",
            "lib/src/local_working_copy.rs",
            "lib/src/simple_workspace_store.rs",
        ],
        "ready": False,
    },
    {
        "slug": "commits",
        "title": "Commits and change IDs",
        "summary": "The Commit object field by field, content-addressed commit IDs versus stable change IDs, and how commits are built and signed.",
        "sources": [
            "core/src/backend.rs",
            "lib/src/commit.rs",
            "lib/src/commit_builder.rs",
            "lib/src/signing_factory.rs",
        ],
        "ready": False,
    },
    {
        "slug": "trees",
        "title": "Trees, files and copies",
        "summary": "Tree objects, the TreeValue variants, merged trees and tree diffs, and copy tracking.",
        "sources": [
            "core/src/backend.rs",
            "lib/src/merged_tree.rs",
            "lib/src/merged_tree_builder.rs",
            "lib/src/tree.rs",
            "lib/src/copies.rs",
            "docs/design/copy-tracking.md",
        ],
        "ready": False,
    },
    {
        "slug": "conflicts",
        "title": "First-class conflicts",
        "summary": "Merge<T>, the alternating add/remove representation behind conflicted trees, refs and files.",
        "sources": [
            "core/src/merge.rs",
            "core/src/conflict_labels.rs",
            "lib/src/conflicts.rs",
            "lib/src/tree_merge.rs",
            "docs/technical/conflicts.md",
        ],
        "ready": False,
    },
    {
        "slug": "operations",
        "title": "The operation log",
        "summary": "Operations, their metadata, op heads, and how concurrent operations are detected and merged.",
        "sources": [
            "core/src/op_store.rs",
            "lib/src/operation.rs",
            "lib/src/op_heads_store.rs",
            "lib/src/simple_op_heads_store.rs",
            "lib/src/simple_op_store.rs",
            "lib/src/op_walk.rs",
            "docs/technical/concurrency.md",
            "docs/operation-log.md",
        ],
        "ready": False,
    },
    {
        "slug": "view",
        "title": "Views, bookmarks and tags",
        "summary": "The View each operation points at: heads, bookmarks, tags, remotes, Git refs and working-copy commits.",
        "sources": [
            "core/src/op_store.rs",
            "lib/src/view.rs",
            "lib/src/refs.rs",
            "docs/bookmarks.md",
        ],
        "ready": False,
    },
    {
        "slug": "transactions",
        "title": "Repos, transactions and rewriting",
        "summary": "ReadonlyRepo, MutableRepo and Transaction, and how rewrites propagate to descendants.",
        "sources": ["lib/src/repo.rs", "lib/src/transaction.rs", "lib/src/rewrite.rs"],
        "ready": False,
    },
    {
        "slug": "working-copy",
        "title": "The working copy",
        "summary": "Snapshot and checkout, the tree state file, file states, and stale working copies.",
        "sources": [
            "lib/src/working_copy.rs",
            "lib/src/local_working_copy.rs",
            "lib/src/fsmonitor.rs",
            "docs/working-copy.md",
        ],
        "ready": False,
    },
    {
        "slug": "index",
        "title": "The commit index",
        "summary": "Index segments, the change-ID index, the changed-path index, and short ID prefixes.",
        "sources": ["lib/src/index.rs", "lib/src/default_index/", "lib/src/id_prefix.rs"],
        "ready": False,
    },
    {
        "slug": "revsets",
        "title": "Revset engine",
        "summary": "From revset text to evaluated commits: grammar, expression tree, symbol resolution and evaluation.",
        "sources": [
            "lib/src/revset.rs",
            "lib/src/revset_parser.rs",
            "lib/src/revset.pest",
            "lib/src/default_index/revset_engine.rs",
            "lib/src/fileset.rs",
            "docs/technical/revset-evaluation.md",
        ],
        "ready": False,
    },
    {
        "slug": "backends",
        "title": "Storage backends",
        "summary": "The Backend trait, the Store caching layer, and the Git and simple backends.",
        "sources": [
            "core/src/backend.rs",
            "lib/src/store.rs",
            "lib/src/git_backend.rs",
            "lib/src/simple_backend.rs",
            "lib/src/secret_backend.rs",
            "lib/src/default_backend_factories.rs",
        ],
        "ready": False,
    },
    {
        "slug": "protobufs",
        "title": "Every schema",
        "summary": "All seven .proto files, every message, enum and field, and the Rust types they map to.",
        "sources": [
            "lib/src/protos/",
            "lib/src/simple_backend.rs",
            "lib/src/simple_op_store.rs",
            "lib/src/git_backend.rs",
            "lib/src/local_working_copy.rs",
            "lib/src/default_index/store.rs",
            "lib/src/simple_workspace_store.rs",
            "lib/src/secure_config.rs",
        ],
        "ready": True,
    },
    {
        "slug": "fix",
        "title": "How jj fix works",
        "summary": "End to end: tool configuration, choosing files, running formatters, changed-line ranges, and rewriting history.",
        "sources": [
            "lib/src/fix.rs",
            "cli/src/commands/fix.rs",
            "cli/src/config/revsets.toml",
            "docs/config.md",
        ],
        "ready": True,
    },
]

PROTO_MESSAGES = {
    "default_index.proto": ["SegmentControl"],
    "git_store.proto": ["Commit"],
    "local_working_copy.proto": [
        "FileType",
        "MaterializedConflictData",
        "FileState",
        "FileStateEntry",
        "SparsePatterns",
        "TreeState",
        "WatchmanClock",
        "Checkout",
    ],
    "secure_config.proto": ["ConfigMetadata"],
    "simple_op_store.proto": [
        "RefConflictLegacy",
        "RefConflict",
        "RefConflict.Term",
        "RefTarget",
        "RefTargetTerm",
        "RemoteRefState",
        "RemoteBookmark",
        "Bookmark",
        "GitRef",
        "GitHead",
        "RemoteRef",
        "Tag",
        "View",
        "RemoteView",
        "Operation",
        "Timestamp",
        "OperationMetadata",
        "CommitPredecessors",
    ],
    "simple_store.proto": [
        "TreeValue",
        "TreeValue.File",
        "Tree",
        "Tree.Entry",
        "Commit",
        "Commit.Timestamp",
        "Commit.Signature",
    ],
    "simple_workspace_store.proto": ["Workspace", "Workspaces"],
}

_HEADING = re.compile(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
_TAG = re.compile(r"<[^>]+>")


def source_url(path, start=None, end=None):
    url = f"{UPSTREAM['repo']}/blob/{UPSTREAM['commit']}/{path}"
    if start is None:
        return url
    if end is None or end == start:
        return f"{url}#L{start}"
    return f"{url}#L{start}-L{end}"


def ready_pages():
    return [page for page in PAGES if page["ready"]]


def find_page(slug):
    return next((page for page in ready_pages() if page["slug"] == slug), None)


def table_of_contents(html):
    return [
        {"level": int(level), "id": anchor, "text": _TAG.sub("", text).strip()}
        for level, anchor, text in _HEADING.findall(html)
    ]


def _neighbours(slug):
    pages = ready_pages()
    slugs = [page["slug"] for page in pages]
    if slug not in slugs:
        return None, None
    position = slugs.index(slug)
    previous = pages[position - 1] if position > 0 else None
    following = pages[position + 1] if position + 1 < len(pages) else None
    return previous, following


def render(slug, render_template):
    if slug is None:
        page = None
        template = "jj/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"jj/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "upstream": UPSTREAM,
        "src": source_url,
        "proto_messages": PROTO_MESSAGES,
        "previous_page": previous,
        "next_page": following,
    }
    content = render_template(template, **context)
    intro, separator, body = content.partition("</header>")
    if not separator:
        intro, body = "", content
    else:
        intro += separator
    return render_template(
        "jj/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
