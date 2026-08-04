import json
import os

SHOWCASE_PATH = os.path.join(os.path.dirname(__file__), "showcase.json")
REPO_URL = "https://github.com/rayaq-siddiqui/assembly-agents"

_cache = {}


def _read_showcase():
    with open(SHOWCASE_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def _paragraphs(text):
    return [block.strip() for block in (text or "").split("\n\n") if block.strip()]


def _commit_url(sha):
    return f"{REPO_URL}/commit/{sha}"


def build_view(showcase):
    project = showcase["project"]
    milestones = showcase["milestones"]
    in_progress = showcase["in_progress"]

    return {
        "name": project["name"],
        "tagline": project["tagline"],
        "repo_url": project["repo_url"],
        "playbook_url": project["playbook_url"],
        "summary_paragraphs": _paragraphs(project["summary"]),
        "highlights": project["technical_highlights"],
        "status": showcase["status"],
        "in_progress_headline": in_progress["headline"],
        "in_progress_paragraphs": _paragraphs(in_progress["body"]),
        "milestones": milestones,
        "milestones_completed": sum(1 for m in milestones if m["state"] == "done"),
        "milestones_total": len(milestones),
        "recent_work": [
            {**entry, "url": _commit_url(entry["sha"])} for entry in showcase["recent_work"]
        ],
        "next_up": showcase["next_up"],
        "updated_at": showcase["updated_at"],
    }


def get_showcase():
    try:
        modified_at = os.path.getmtime(SHOWCASE_PATH)
    except OSError:
        return _cache.get("view")

    cached = _cache.get("view")
    if cached and _cache.get("modified_at") == modified_at:
        return cached

    try:
        view = build_view(_read_showcase())
    except (OSError, KeyError, TypeError, ValueError):
        return cached

    _cache["view"] = view
    _cache["modified_at"] = modified_at
    return view
