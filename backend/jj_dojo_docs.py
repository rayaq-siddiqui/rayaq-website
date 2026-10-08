import re

UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj-dojo",
    "commit": "67c5c1f1223f1f077e86511a30d6979b52863501",
    "commit_date": "2026-10-06",
    "version": "0.0.1",
    "analyzed_on": "2026-10-07",
}

PAGES = [
    {
        "slug": "activation",
        "title": "Activation and wiring",
        "summary": "What the extension contributes to VS Code, what happens when it activates, and how logging and errors are set up.",
        "sources": ["package.json", "src/extension.ts", "src/ui/ui.ts", "src/logging/", "src/error/"],
        "ready": True,
    },
    {
        "slug": "graph-protocol",
        "title": "The graph webview protocol",
        "summary": "Every type and method in the contract between the extension host and the commit graph webview.",
        "sources": [
            "src/ui/commit_graph/api/",
            "src/ui/commit_graph_provider/",
            "src/ui/commit_graph/webview_module.ts",
        ],
        "ready": True,
    },
    {
        "slug": "graph-layout",
        "title": "Commit graph layout",
        "summary": "How commits become lanes, edges, glyphs and rows: the preprocessing pipeline, drawing, ranges and focus mode.",
        "sources": ["src/ui/commit_graph/algorithms/"],
        "ready": True,
    },
    {
        "slug": "graph-webview",
        "title": "The graph webview UI",
        "summary": "The component tree of the commit graph webview, from the app shell down to rows, chips, search and drag and drop.",
        "sources": ["src/ui/commit_graph/components/", "src/ui/commit_graph/utils/"],
        "ready": True,
    },
    {
        "slug": "merge-conflicts",
        "title": "Merge conflict support",
        "summary": "How conflict markers are parsed, tracked, decorated and resolved in the editor.",
        "sources": ["src/ui/merge_conflict/"],
        "ready": True,
    },
    {
        "slug": "icon-theme",
        "title": "Icon theme service",
        "summary": "How the active file-icon theme is found, parsed and served to webviews.",
        "sources": ["src/ui/icon_theme_service/"],
        "ready": True,
    },
    {
        "slug": "build-and-test",
        "title": "Build, test and packaging",
        "summary": "The Bazel build, the test setup with its fake VS Code API, and CI.",
        "sources": [
            "BUILD.bazel",
            "MODULE.bazel",
            "tools/bazel/",
            "spec/support/jasmine.json",
            "src/testing/",
            ".github/workflows/",
        ],
        "ready": True,
    },
    {
        "slug": "roadmap",
        "title": "Externalization plan",
        "summary": "The planned UI, API and client layers from the upstream design notes, and what has landed so far.",
        "sources": ["docs/intro.md", "docs/resources/architecture.svg"],
        "ready": False,
    },
    {
        "slug": "utils",
        "title": "Shared utilities",
        "summary": "The small shared helpers the rest of the extension builds on.",
        "sources": ["src/utils/"],
        "ready": True,
    },
]

PROTOCOL_TYPES = [
    "Commit",
    "IconButton",
    "ChipColors",
    "VSCodeCommand",
    "CommitMetadataTextStyle",
    "CommitGraphOptions",
    "RenderMode",
    "CalloutType",
    "Callout",
    "TopBarButton",
    "WebviewState",
    "WebviewOptions",
    "CommitGraphState",
    "Chip",
    "SplitChip",
    "File",
    "CommitNode",
    "CommitChildNode",
    "TileGroup",
    "InsertAction",
    "Tile",
    "Line",
    "LineType",
    "CommitRowType",
]

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
        template = "jj_dojo/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"jj_dojo/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "upstream": UPSTREAM,
        "src": source_url,
        "protocol_types": PROTOCOL_TYPES,
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
        "jj_dojo/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
