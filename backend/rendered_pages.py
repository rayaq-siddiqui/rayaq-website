# Reference pages are a pure function of their slug for the life of the process: templates and
# static assets only change on a deploy, which restarts it. Only successful renders are kept, so
# the cache is bounded by the number of ready pages and unknown slugs never grow it.
_pages = {}


def get(key, build):
    html = _pages.get(key)
    if html is None:
        html = build()
        if html is not None:
            _pages[key] = html
    return html


def clear():
    _pages.clear()
