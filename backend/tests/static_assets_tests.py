import os

import static_assets


def test_version_is_the_file_mtime(tmp_path):
    asset = tmp_path / "style.css"
    asset.write_text("body {}")
    os.utime(asset, (1_700_000_000, 1_700_000_000))

    assert static_assets.version(str(tmp_path), "style.css") == 1_700_000_000


def test_version_changes_when_the_file_changes(tmp_path):
    asset = tmp_path / "style.css"
    asset.write_text("body {}")
    os.utime(asset, (1_700_000_000, 1_700_000_000))
    before = static_assets.version(str(tmp_path), "style.css")

    os.utime(asset, (1_700_000_500, 1_700_000_500))

    assert static_assets.version(str(tmp_path), "style.css") != before


def test_version_is_none_for_a_missing_file(tmp_path):
    assert static_assets.version(str(tmp_path), "missing.css") is None


def test_add_version_sets_v_for_an_existing_file(tmp_path):
    (tmp_path / "app.js").write_text("")
    values = {"filename": "app.js"}

    static_assets.add_version(str(tmp_path), values)

    assert values["v"] == static_assets.version(str(tmp_path), "app.js")


def test_add_version_leaves_a_missing_file_unversioned(tmp_path):
    values = {"filename": "missing.js"}

    static_assets.add_version(str(tmp_path), values)

    assert "v" not in values


def test_add_version_keeps_an_explicit_version(tmp_path):
    (tmp_path / "app.js").write_text("")
    values = {"filename": "app.js", "v": "pinned"}

    static_assets.add_version(str(tmp_path), values)

    assert values["v"] == "pinned"
