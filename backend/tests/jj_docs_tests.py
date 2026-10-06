import os
import re
from datetime import date

import app as app_module
import jj_docs

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "templates", "jj")
SOURCE_LINK = re.compile(r'href="(https://github\.com/jj-vcs/jj/[^"]*)"')


def all_urls():
    return ["/jj"] + [f"/jj/{page['slug']}" for page in jj_docs.ready_pages()]


def test_pin_is_well_formed():
    assert re.fullmatch(r"[0-9a-f]{40}", jj_docs.UPSTREAM["commit"])
    date.fromisoformat(jj_docs.UPSTREAM["commit_date"])
    date.fromisoformat(jj_docs.UPSTREAM["analyzed_on"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", jj_docs.UPSTREAM["version"])
    assert jj_docs.UPSTREAM["repo"] == "https://github.com/jj-vcs/jj"


def test_every_page_has_a_unique_slug_summary_and_sources():
    slugs = [page["slug"] for page in jj_docs.PAGES]
    assert len(slugs) == len(set(slugs))
    for page in jj_docs.PAGES:
        assert re.fullmatch(r"[a-z][a-z-]*", page["slug"])
        assert page["kind"] in ("topic", "command")
        assert page["title"].strip()
        assert page["summary"].strip()
        assert page["sources"]


def test_every_ready_page_has_a_template():
    for page in jj_docs.ready_pages():
        name = jj_docs.page_template(page).removeprefix("jj/")
        assert os.path.isfile(os.path.join(TEMPLATES_DIR, name)), page["slug"]


def test_a_page_can_name_its_own_template():
    assert jj_docs.page_template({"slug": "rebase"}) == "jj/rebase.html"
    index = next(page for page in jj_docs.PAGES if page["slug"] == "index")
    assert jj_docs.page_template(index) == "jj/commit-index.html"


def test_source_url_is_pinned():
    sha = jj_docs.UPSTREAM["commit"]
    base = f"https://github.com/jj-vcs/jj/blob/{sha}/lib/src/fix.rs"

    assert jj_docs.source_url("lib/src/fix.rs") == base
    assert jj_docs.source_url("lib/src/fix.rs", 10) == f"{base}#L10"
    assert jj_docs.source_url("lib/src/fix.rs", 10, 10) == f"{base}#L10"
    assert jj_docs.source_url("lib/src/fix.rs", 10, 20) == f"{base}#L10-L20"


def test_find_page_only_returns_ready_pages(monkeypatch):
    pages = [
        {"slug": "a", "title": "A", "summary": "a", "sources": ["x"], "ready": True},
        {"slug": "b", "title": "B", "summary": "b", "sources": ["x"], "ready": False},
    ]
    monkeypatch.setattr(jj_docs, "PAGES", pages)

    assert jj_docs.find_page("a") is pages[0]
    assert jj_docs.find_page("b") is None
    assert jj_docs.find_page("missing") is None


def test_table_of_contents_reads_h2_and_h3_with_ids():
    html = '<h1>T</h1><h2 id="one">One <code>x</code></h2><h3 id="two" class="c">Two</h3><h2>No id</h2>'

    assert jj_docs.table_of_contents(html) == [
        {"level": 2, "id": "one", "text": "One x"},
        {"level": 3, "id": "two", "text": "Two"},
    ]


def test_render_returns_none_for_an_unknown_slug():
    assert jj_docs.render("does-not-exist", lambda *args, **kwargs: "") is None


def test_proto_messages_cover_seven_files():
    assert len(jj_docs.PROTO_MESSAGES) == 7
    assert all(names for names in jj_docs.PROTO_MESSAGES.values())


def test_every_jj_url_returns_200():
    client = app_module.app.test_client()

    for url in all_urls():
        assert client.get(url).status_code == 200, url


def test_unknown_jj_slug_returns_404():
    client = app_module.app.test_client()

    assert client.get("/jj/not-a-page").status_code == 404


def test_every_source_link_is_pinned_to_the_analyzed_commit():
    client = app_module.app.test_client()
    sha = jj_docs.UPSTREAM["commit"]

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert "blob/main" not in body, url
        for link in SOURCE_LINK.findall(body):
            if "/blob/" in link or "/tree/" in link:
                assert f"/{sha}/" in link or link.endswith(f"/{sha}"), (url, link)


def test_index_lists_every_page_and_links_ready_ones():
    client = app_module.app.test_client()

    body = client.get("/jj").get_data(as_text=True)

    for page in jj_docs.PAGES:
        if page["kind"] == "topic":
            assert page["title"] in body
        else:
            assert f"jj {page['command']}" in body
    for page in jj_docs.ready_pages():
        assert f'href="/jj/{page["slug"]}"' in body


def test_pages_show_the_pinned_commit_and_license():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        assert jj_docs.UPSTREAM["commit"][:12] in body
        assert "Apache-2.0" in body


def test_protobufs_page_names_every_message_and_enum():
    if jj_docs.find_page("protobufs") is None:
        return
    client = app_module.app.test_client()

    body = client.get("/jj/protobufs").get_data(as_text=True)

    for filename, names in jj_docs.PROTO_MESSAGES.items():
        assert filename in body
        for name in names:
            leaf = name.split(".")[-1]
            assert re.search(rf"\b(message|enum) {re.escape(leaf)}\b", body), (filename, name)


def test_render_places_the_header_before_the_table_of_contents():
    def fake_render(template, **context):
        if template == "jj/base.html":
            return f"{context['intro']}|TOC|{context['content']}"
        return '<header><h1>T</h1></header><h2 id="a">A</h2><h2 id="b">B</h2>'

    html = jj_docs.render(None, fake_render)

    assert html.index("<h1>") < html.index("|TOC|") < html.index('id="a"')


def test_index_has_an_accessible_architecture_diagram():
    client = app_module.app.test_client()

    body = client.get("/jj").get_data(as_text=True)

    assert 'role="img"' in body
    assert '<title id="arch-title">' in body
    assert '<desc id="arch-desc">' in body


def test_every_internal_jj_link_resolves():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        for link in set(re.findall(r'href="(/jj[^"#?]*)', body)):
            assert client.get(link).status_code == 200, (url, link)


def test_diagram_titles_and_descriptions_are_plain_text():
    client = app_module.app.test_client()

    for url in all_urls():
        body = client.get(url).get_data(as_text=True)
        for tag, text in re.findall(r"<(title|desc)\b[^>]*>(.*?)</\1>", body, re.S):
            assert "<" not in text, (url, tag, text[:80])


def test_every_command_has_a_registry_page():
    slugs = {page["slug"] for page in jj_docs.PAGES if page["kind"] == "command"}

    for entry in jj_docs.COMMANDS:
        assert jj_docs.command_slug(entry["command"]) in slugs, entry["command"]
        assert entry["category"] in jj_docs.COMMAND_CATEGORIES
        assert entry["tier"] in ("A", "B", "C")
        assert entry["summary"].strip()


def test_topic_slugs_never_collide_with_command_slugs():
    topics = {page["slug"] for page in jj_docs.PAGES if page["kind"] == "topic"}
    commands = {page["slug"] for page in jj_docs.PAGES if page["kind"] == "command"}

    assert not topics & commands


def test_command_slug_uses_dashes():
    assert jj_docs.command_slug("operation log") == "operation-log"
    assert jj_docs.command_slug("workspace update-stale") == "workspace-update-stale"
    assert jj_docs.command_slug("simplify_parents") == "simplify-parents"


def test_index_groups_commands_by_category():
    client = app_module.app.test_client()

    body = client.get("/jj").get_data(as_text=True)

    for number, category in enumerate(jj_docs.COMMAND_CATEGORIES, start=1):
        assert f'<h3 id="commands-{number}">{category}</h3>' in body


def test_ready_tier_a_command_pages_cover_every_section():
    tiers = {jj_docs.command_slug(entry["command"]): entry["tier"] for entry in jj_docs.COMMANDS}
    client = app_module.app.test_client()

    for page in jj_docs.ready_pages():
        if page["kind"] != "command" or tiers[page["slug"]] != "A" or page["slug"] == "fix":
            continue
        body = client.get(f"/jj/{page['slug']}").get_data(as_text=True)
        for anchor in ["cli", "configuration", "flow", "touchpoints", "transaction", "algorithm", "errors", "example"]:
            assert f'<h2 id="{anchor}"' in body, (page["slug"], anchor)
        assert body.count('role="img"') >= 2, page["slug"]


def test_ready_tier_b_command_pages_cover_every_section():
    tiers = {jj_docs.command_slug(entry["command"]): entry["tier"] for entry in jj_docs.COMMANDS}
    client = app_module.app.test_client()

    for page in jj_docs.ready_pages():
        if page["kind"] != "command" or tiers[page["slug"]] != "B":
            continue
        body = client.get(f"/jj/{page['slug']}").get_data(as_text=True)
        for anchor in ["cli", "configuration", "flow", "touchpoints", "reads", "algorithm", "errors", "example"]:
            assert f'<h2 id="{anchor}"' in body, (page["slug"], anchor)
        assert 'role="img"' in body, page["slug"]


def test_ready_tier_c_command_pages_cover_every_section():
    tiers = {jj_docs.command_slug(entry["command"]): entry["tier"] for entry in jj_docs.COMMANDS}
    client = app_module.app.test_client()

    for page in jj_docs.ready_pages():
        if page["kind"] != "command" or tiers[page["slug"]] != "C":
            continue
        body = client.get(f"/jj/{page['slug']}").get_data(as_text=True)
        for anchor in ["cli", "flow", "touchpoints"]:
            assert f'<h2 id="{anchor}"' in body, (page["slug"], anchor)
        assert 'role="img"' in body, page["slug"]
