import re

UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj-vfs-poc",
    "commit": "37b8f8625556778f5ce41cbb2d5220bcea245675",
    "commit_date": "2026-09-03",
    "version": "0.1.0",
    "jj_lib_version": "0.43.0",
    "analyzed_on": "2026-10-03",
}

JJ_REPO = "https://github.com/jj-vcs/jj"

PAGES = [
    {
        "slug": "mounting",
        "title": "Starting and mounting",
        "summary": "What jjfsd does from main() to a live mount: arguments, tracing, mount options, the tokio runtime, loading the repo, and unmounting.",
        "sources": ["src/main.rs"],
        "ready": False,
    },
    {
        "slug": "fuse",
        "title": "The FUSE adapter",
        "summary": "JjFuse: every FUSE operation it answers, how each maps onto the virtual file system, the async bridge, attributes and errno mapping.",
        "sources": ["src/fuse.rs", "src/jj_error.rs"],
        "ready": False,
    },
    {
        "slug": "inodes",
        "title": "Inodes",
        "summary": "How InodeMap hands out inode numbers, maps them to paths and back, and what it never forgets.",
        "sources": ["src/inode_map.rs"],
        "ready": False,
    },
    {
        "slug": "vfs-layer",
        "title": "The virtual file layer",
        "summary": "The VirtualFilesystem, VirtualFile and PathMapper traits, PathMappedVfs, and how reads are served from async streams.",
        "sources": ["src/vfs.rs", "src/virtual_file.rs", "src/path_mapper.rs"],
        "ready": False,
    },
    {
        "slug": "namespace",
        "title": "The mount's namespace",
        "summary": "What lives at each path of a mounted repository, how a path is resolved to a file, and which repo snapshot every lookup sees.",
        "sources": [
            "src/path_mapper_all_commits.rs",
            "src/static_directory.rs",
            "src/commits_directory.rs",
            "src/workspaces_directory.rs",
        ],
        "ready": True,
    },
    {
        "slug": "commit-trees",
        "title": "Commits as directory trees",
        "summary": "How a commit's tree becomes directories, files and symlinks, how conflicts and other value kinds are shown, and how content is streamed.",
        "sources": ["src/commit_tree_file.rs"],
        "ready": False,
    },
    {
        "slug": "testing",
        "title": "Tests and CI",
        "summary": "The test helpers, the unit tests per module, the mounted integration test, and the CI workflow.",
        "sources": ["src/test_helpers.rs", "tests/", ".github/workflows/", "rustfmt.toml"],
        "ready": False,
    },
]

FUSE_OPS = [
    "init",
    "lookup",
    "getattr",
    "read",
    "readdir",
    "readlink",
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
        template = "jj_vfs/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"jj_vfs/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "upstream": UPSTREAM,
        "src": source_url,
        "jj_lib": jj_lib_url,
        "fuse_ops": FUSE_OPS,
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
        "jj_vfs/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
