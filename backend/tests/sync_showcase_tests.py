import json
import os

import pytest
import sync_showcase
from assembly_tests import fake_showcase


def write_checkout(tmp_path, contents):
    docs = tmp_path / "checkout" / "docs"
    docs.mkdir(parents=True)
    (docs / "showcase.json").write_text(contents, encoding="utf-8")
    return str(tmp_path / "checkout")


def test_sync_copies_the_upstream_digest_verbatim(tmp_path):
    contents = json.dumps(fake_showcase(), indent=2) + "\n"
    checkout = write_checkout(tmp_path, contents)
    destination = tmp_path / "showcase.json"

    assert sync_showcase.sync(checkout, str(destination)) is True
    assert destination.read_text(encoding="utf-8") == contents


def test_sync_reports_no_change_when_the_digest_already_matches(tmp_path):
    contents = json.dumps(fake_showcase(), indent=2) + "\n"
    checkout = write_checkout(tmp_path, contents)
    destination = tmp_path / "showcase.json"
    destination.write_text(contents, encoding="utf-8")

    assert sync_showcase.sync(checkout, str(destination)) is False


def test_sync_refuses_a_malformed_upstream_digest(tmp_path):
    checkout = write_checkout(tmp_path, "{not json")
    destination = tmp_path / "showcase.json"
    destination.write_text("original", encoding="utf-8")

    with pytest.raises(ValueError):
        sync_showcase.sync(checkout, str(destination))

    assert destination.read_text(encoding="utf-8") == "original"


def test_sync_refuses_a_digest_the_page_cannot_render(tmp_path):
    payload = fake_showcase()
    del payload["project"]["tagline"]
    checkout = write_checkout(tmp_path, json.dumps(payload))
    destination = tmp_path / "showcase.json"
    destination.write_text("original", encoding="utf-8")

    with pytest.raises(KeyError):
        sync_showcase.sync(checkout, str(destination))

    assert destination.read_text(encoding="utf-8") == "original"


def test_sync_writes_a_digest_that_the_site_then_renders(tmp_path, monkeypatch):
    import assembly as assembly_module

    checkout = write_checkout(tmp_path, json.dumps(fake_showcase()))
    destination = tmp_path / "showcase.json"
    sync_showcase.sync(checkout, str(destination))

    assembly_module._cache.clear()
    monkeypatch.setattr(assembly_module, "SHOWCASE_PATH", str(destination))

    assert assembly_module.get_showcase()["tagline"] == "A tagline."


def test_main_exits_non_zero_when_the_checkout_has_no_digest(tmp_path, capsys):
    assert sync_showcase.main([str(tmp_path)]) == 1
    assert "refusing to sync" in capsys.readouterr().err


def test_main_reports_the_outcome(tmp_path, monkeypatch, capsys):
    checkout = write_checkout(tmp_path, json.dumps(fake_showcase()))
    destination = tmp_path / "showcase.json"
    monkeypatch.setattr(sync_showcase.assembly, "SHOWCASE_PATH", str(destination))

    assert sync_showcase.main([checkout]) == 0
    assert capsys.readouterr().out.strip() == "updated"

    assert sync_showcase.main([checkout]) == 0
    assert capsys.readouterr().out.strip() == "unchanged"


def test_upstream_path_matches_the_publisher_workflow():
    assert sync_showcase.UPSTREAM_RELATIVE_PATH == os.path.join("docs", "showcase.json")
