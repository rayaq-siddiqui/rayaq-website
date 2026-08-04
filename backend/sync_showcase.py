"""Copy the Assembly digest from an assembly-agents checkout into this site.

assembly-agents authors docs/showcase.json as its published contract with this
page, so the digest is copied verbatim rather than regenerated — a sync diff is
then exactly the upstream diff. The copy is gated on the file still building a
view, so an upstream schema change fails here instead of on the live page.
"""

import argparse
import json
import os
import sys

import assembly

UPSTREAM_RELATIVE_PATH = os.path.join("docs", "showcase.json")


def sync(checkout_path, destination=None):
    destination = destination or assembly.SHOWCASE_PATH
    source_path = os.path.join(checkout_path, UPSTREAM_RELATIVE_PATH)

    with open(source_path, encoding="utf-8") as handle:
        contents = handle.read()

    assembly.build_view(json.loads(contents))

    try:
        with open(destination, encoding="utf-8") as handle:
            if handle.read() == contents:
                return False
    except OSError:
        pass

    with open(destination, "w", encoding="utf-8") as handle:
        handle.write(contents)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Sync the Assembly showcase digest.")
    parser.add_argument("checkout", help="path to an assembly-agents checkout")
    args = parser.parse_args(argv)

    try:
        changed = sync(args.checkout)
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(f"refusing to sync: {error}", file=sys.stderr)
        return 1

    print("updated" if changed else "unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
