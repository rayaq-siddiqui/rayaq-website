import os

MAX_AGE_SECONDS = 365 * 24 * 60 * 60


def version(static_folder, filename):
    try:
        return int(os.stat(os.path.join(static_folder, filename)).st_mtime)
    except OSError:
        return None


def add_version(static_folder, values):
    if "v" in values:
        return
    asset_version = version(static_folder, values.get("filename", ""))
    if asset_version is not None:
        values["v"] = asset_version
