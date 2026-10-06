import re

import jj_docs

UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj-commit-cloud-poc",
    "commit": "4b1c77b9db365e426e49846669a1626698fd5fa6",
    "commit_date": "2026-09-01",
    "jj_lib_version": "0.43.0",
    "analyzed_on": "2026-10-03",
}

JJ_REPO = "https://github.com/jj-vcs/jj"

PAGES = [
    {
        "slug": "protobufs",
        "title": "Every schema",
        "summary": "Both .proto files: every service, RPC, message and field, the jj-lib type each converts to and from, and how the Rust code is generated.",
        "sources": ["common/proto/", "common/build.rs", "common/src/lib.rs"],
        "ready": True,
    },
    {
        "slug": "client-backend",
        "title": "The client Backend",
        "summary": "The commit-cloud implementation of jj-lib's Backend trait, method by method: which RPC each calls, IDs, the root commit, and the sync/async bridge.",
        "sources": ["lib/src/cc_backend.rs", "lib/src/util.rs", "lib/src/lib.rs"],
        "ready": True,
    },
    {
        "slug": "client-op-store",
        "title": "The client OpStore and OpHeadsStore",
        "summary": "How operations, views and op heads are read and written over gRPC, whether op-head updates are atomic, and what is unimplemented.",
        "sources": ["lib/src/cc_op_store.rs", "lib/src/cc_op_heads_store.rs"],
        "ready": True,
    },
    {
        "slug": "cli",
        "title": "The custom jj binary",
        "summary": "How the jj binary is customised with commit-cloud stores and a cc subcommand, what jj cc init does, and how stock commands run on top.",
        "sources": ["cli/src/", "cli/src/commands/", "lib/src/repo.rs"],
        "ready": False,
    },
    {
        "slug": "server",
        "title": "The server",
        "summary": "jj-cc-server's arguments, storage selection and tonic setup, and its backend and op-store services RPC by RPC.",
        "sources": [
            "server/src/main.rs",
            "server/src/backend.rs",
            "server/src/op_store.rs",
            "server/src/error_util.rs",
        ],
        "ready": True,
    },
    {
        "slug": "storage",
        "title": "Server storage engines",
        "summary": "The server's Store trait, the in-memory engine, and which other engines are declared but not implemented.",
        "sources": ["server/src/store/"],
        "ready": True,
    },
    {
        "slug": "object-ids",
        "title": "Object IDs and hashing",
        "summary": "Which IDs exist and who computes them, the exact bytes hashed for commits, trees, files, operations and views, and how they compare with jj's Git backend.",
        "sources": ["server/src/hash_utils.rs"],
        "ready": True,
    },
    {
        "slug": "testing",
        "title": "Tests",
        "summary": "The test utilities, every integration test and what it asserts, and which tests are expected to fail.",
        "sources": ["testutils/", "cli/tests/", "server/tests/"],
        "ready": False,
    },
]

PROTO_ITEMS = [
    "BackendService",
    "RegisterRepository",
    "ReadCommit",
    "WriteCommit",
    "ReadTree",
    "WriteTree",
    "ReadFile",
    "WriteFile",
    "ReadSymlink",
    "WriteSymlink",
    "RegisterRepositoryRequest",
    "RegisterRepositoryResponse",
    "Timestamp",
    "Signature",
    "Commit",
    "ReadCommitRequest",
    "ReadCommitResponse",
    "WriteCommitRequest",
    "WriteCommitResponse",
    "File",
    "TreeValue",
    "TreeEntry",
    "ReadTreeRequest",
    "ReadTreeResponse",
    "WriteTreeRequest",
    "WriteTreeResponse",
    "ReadFileRequest",
    "ReadFileResponse",
    "WriteFileRequest",
    "WriteFileResponse",
    "ReadSymlinkRequest",
    "ReadSymlinkResponse",
    "WriteSymlinkRequest",
    "WriteSymlinkResponse",
    "OpStoreService",
    "ReadOperation",
    "WriteOperation",
    "ReadView",
    "WriteView",
    "GetOpHeads",
    "UpdateOpHeads",
    "ReadOperationRequest",
    "ReadOperationResponse",
    "WriteOperationRequest",
    "WriteOperationResponse",
    "ReadViewRequest",
    "ReadViewResponse",
    "WriteViewRequest",
    "WriteViewResponse",
    "GetOpHeadsRequest",
    "GetOpHeadsResponse",
    "UpdateOpHeadsRequest",
    "UpdateOpHeadsResponse",
    "OperationMetadata",
    "CommitPredecessors",
    "Operation",
    "RefTargetTerm",
    "RefTarget",
    "RemoteRef",
    "View",
]

_HEADING = re.compile(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', re.S)
_TAG = re.compile(r"<[^>]+>")


def _pinned(url, start, end):
    if start is None:
        return url
    if end is None or end == start:
        return f"{url}#L{start}"
    return f"{url}#L{start}-L{end}"


def source_url(path, start=None, end=None):
    return _pinned(f"{UPSTREAM['repo']}/blob/{UPSTREAM['commit']}/{path}", start, end)


def jj_lib_url(path, start=None, end=None):
    return _pinned(f"{JJ_REPO}/blob/v{UPSTREAM['jj_lib_version']}/{path}", start, end)


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
        template = "jj_cloud/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"jj_cloud/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "upstream": UPSTREAM,
        "src": source_url,
        "jj_lib": jj_lib_url,
        "proto_items": PROTO_ITEMS,
        "jj_ready_slugs": {entry["slug"] for entry in jj_docs.ready_pages()},
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
        "jj_cloud/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
