import json

import assembly as assembly_module
import pytest


def fake_showcase():
    return {
        "schema_version": 1,
        "updated_at": "2026-08-02",
        "project": {
            "name": "Assembly",
            "tagline": "A tagline.",
            "repo_url": "https://github.com/rayaq-siddiqui/assembly-agents",
            "playbook_url": "https://github.com/rayaq-siddiqui/assembly-agents/blob/main/docs/DAILY_AGENT.md",
            "summary": "First paragraph.\n\nSecond paragraph.",
            "technical_highlights": [{"title": "Spec-first", "detail": "Specs before code."}],
        },
        "status": {
            "current_milestone": "M0",
            "current_milestone_title": "Design and benchmark setup",
            "runs_to_date": 7,
            "cycles_last_run": 14,
            "tests_passing": 99,
            "verification": "pytest 99 passed",
        },
        "in_progress": {
            "headline": "The type layer is finished",
            "body": "Blog paragraph one.\n\nBlog paragraph two.",
        },
        "milestones": [
            {"id": "M0", "title": "Design and benchmark setup", "state": "active"},
            {"id": "M1", "title": "Sequential prototype", "state": "planned"},
        ],
        "recent_work": [{"sha": "8fe571a", "title": "Contract tests", "detail": "All types."}],
        "next_up": ["Define the policy rule set"],
    }


@pytest.fixture(autouse=True)
def clear_cache():
    assembly_module._cache.clear()
    yield
    assembly_module._cache.clear()


def write_showcase(tmp_path, monkeypatch, payload):
    path = tmp_path / "showcase.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(assembly_module, "SHOWCASE_PATH", str(path))
    return path


def test_get_showcase_splits_prose_into_paragraphs(tmp_path, monkeypatch):
    write_showcase(tmp_path, monkeypatch, fake_showcase())

    view = assembly_module.get_showcase()

    assert view["summary_paragraphs"] == ["First paragraph.", "Second paragraph."]
    assert view["in_progress_paragraphs"] == ["Blog paragraph one.", "Blog paragraph two."]


def test_get_showcase_builds_commit_urls(tmp_path, monkeypatch):
    write_showcase(tmp_path, monkeypatch, fake_showcase())

    view = assembly_module.get_showcase()

    assert view["recent_work"][0]["url"].endswith("/commit/8fe571a")


def test_get_showcase_counts_completed_milestones(tmp_path, monkeypatch):
    payload = fake_showcase()
    payload["milestones"][0]["state"] = "done"
    write_showcase(tmp_path, monkeypatch, payload)

    view = assembly_module.get_showcase()

    assert view["milestones_completed"] == 1
    assert view["milestones_total"] == 2


def test_get_showcase_returns_none_when_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(assembly_module, "SHOWCASE_PATH", str(tmp_path / "absent.json"))

    assert assembly_module.get_showcase() is None


def test_get_showcase_returns_none_when_file_is_malformed(tmp_path, monkeypatch):
    path = tmp_path / "showcase.json"
    path.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(assembly_module, "SHOWCASE_PATH", str(path))

    assert assembly_module.get_showcase() is None


def test_get_showcase_keeps_last_good_view_when_file_goes_bad(tmp_path, monkeypatch):
    path = write_showcase(tmp_path, monkeypatch, fake_showcase())
    good = assembly_module.get_showcase()

    path.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(assembly_module.os.path, "getmtime", lambda _: 1.0)

    assert assembly_module.get_showcase() == good


def test_get_showcase_rereads_after_the_file_changes(tmp_path, monkeypatch):
    path = write_showcase(tmp_path, monkeypatch, fake_showcase())
    assert assembly_module.get_showcase()["status"]["runs_to_date"] == 7

    updated = fake_showcase()
    updated["status"]["runs_to_date"] = 8
    path.write_text(json.dumps(updated), encoding="utf-8")
    monkeypatch.setattr(assembly_module.os.path, "getmtime", lambda _: 99.0)

    assert assembly_module.get_showcase()["status"]["runs_to_date"] == 8


def test_shipped_showcase_file_renders(monkeypatch):
    """The committed showcase.json must actually build a view — it is the page."""
    view = assembly_module.get_showcase()

    assert view is not None
    assert view["name"]
    assert view["in_progress_paragraphs"]
    assert view["highlights"]
