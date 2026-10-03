import re

UPSTREAM = {
    "repo": "https://github.com/jj-vcs/jj",
    "commit": "69abfbedcc615bb562c31d488b98abb1ab854089",
    "commit_date": "2026-10-03",
    "version": "0.45.1",
    "analyzed_on": "2026-10-03",
}

TOPICS = [
    {
        "slug": "cli",
        "title": "How a command runs",
        "kind": "topic",
        "summary": "The lifecycle every command shares: dispatch, loading the workspace, snapshotting, transactions, and publishing the operation.",
        "sources": [
            "cli/src/main.rs",
            "cli/src/cli_util.rs",
            "cli/src/commands/mod.rs",
            "cli/src/command_error.rs",
            "lib/src/transaction.rs",
            "lib/src/working_copy.rs",
        ],
        "ready": True,
    },
    {
        "slug": "storage",
        "title": "On-disk layout",
        "kind": "topic",
        "summary": "What lives where under .jj/, which component owns each path, and in what format.",
        "sources": [
            "lib/src/repo.rs",
            "lib/src/workspace.rs",
            "lib/src/simple_op_store.rs",
            "lib/src/simple_op_heads_store.rs",
            "lib/src/default_index/store.rs",
            "lib/src/local_working_copy.rs",
            "lib/src/simple_workspace_store.rs",
        ],
        "ready": False,
    },
    {
        "slug": "commits",
        "title": "Commits and change IDs",
        "kind": "topic",
        "summary": "The Commit object field by field, content-addressed commit IDs versus stable change IDs, and how commits are built and signed.",
        "sources": [
            "core/src/backend.rs",
            "lib/src/commit.rs",
            "lib/src/commit_builder.rs",
            "lib/src/signing_factory.rs",
            "lib/src/settings.rs",
            "core/src/signing.rs",
            "core/src/hex_util.rs",
            "lib/src/git_backend.rs",
        ],
        "ready": True,
    },
    {
        "slug": "trees",
        "title": "Trees, files and copies",
        "kind": "topic",
        "summary": "Tree objects, the TreeValue variants, merged trees and tree diffs, and copy tracking.",
        "sources": [
            "core/src/backend.rs",
            "lib/src/merged_tree.rs",
            "lib/src/merged_tree_builder.rs",
            "lib/src/tree.rs",
            "lib/src/copies.rs",
            "docs/design/copy-tracking.md",
        ],
        "ready": True,
    },
    {
        "slug": "conflicts",
        "title": "First-class conflicts",
        "kind": "topic",
        "summary": "Merge<T>, the alternating add/remove representation behind conflicted trees, refs and files.",
        "sources": [
            "core/src/merge.rs",
            "core/src/conflict_labels.rs",
            "lib/src/conflicts.rs",
            "lib/src/tree_merge.rs",
            "docs/technical/conflicts.md",
        ],
        "ready": False,
    },
    {
        "slug": "operations",
        "title": "The operation log",
        "kind": "topic",
        "summary": "Operations, their metadata, op heads, and how concurrent operations are detected and merged.",
        "sources": [
            "core/src/op_store.rs",
            "lib/src/operation.rs",
            "lib/src/op_heads_store.rs",
            "lib/src/simple_op_heads_store.rs",
            "lib/src/simple_op_store.rs",
            "lib/src/op_walk.rs",
            "docs/technical/concurrency.md",
            "docs/operation-log.md",
            "lib/src/repo.rs",
            "lib/src/transaction.rs",
            "cli/src/commands/undo.rs",
            "cli/src/commands/redo.rs",
            "cli/src/commands/operation/",
            "cli/src/commands/util/gc.rs",
        ],
        "ready": True,
    },
    {
        "slug": "view",
        "title": "Views, bookmarks and tags",
        "kind": "topic",
        "summary": "The View each operation points at: heads, bookmarks, tags, remotes, Git refs and working-copy commits.",
        "sources": [
            "core/src/op_store.rs",
            "lib/src/view.rs",
            "lib/src/refs.rs",
            "docs/bookmarks.md",
            "core/src/merge.rs",
            "lib/src/repo.rs",
        ],
        "ready": True,
    },
    {
        "slug": "transactions",
        "title": "Repos, transactions and rewriting",
        "kind": "topic",
        "summary": "ReadonlyRepo, MutableRepo and Transaction, and how rewrites propagate to descendants.",
        "sources": ["lib/src/repo.rs", "lib/src/transaction.rs", "lib/src/rewrite.rs"],
        "ready": True,
    },
    {
        "slug": "working-copy",
        "title": "The working copy",
        "kind": "topic",
        "summary": "Snapshot and checkout, the tree state file, file states, and stale working copies.",
        "sources": [
            "lib/src/working_copy.rs",
            "lib/src/local_working_copy.rs",
            "lib/src/fsmonitor.rs",
            "docs/working-copy.md",
            "cli/src/config/misc.toml",
        ],
        "ready": True,
    },
    {
        "slug": "index",
        "title": "The commit index",
        "kind": "topic",
        "summary": "Index segments, the change-ID index, the changed-path index, and short ID prefixes.",
        "sources": ["lib/src/index.rs", "lib/src/default_index/", "lib/src/id_prefix.rs"],
        "ready": False,
    },
    {
        "slug": "revsets",
        "title": "Revset engine",
        "kind": "topic",
        "summary": "From revset text to evaluated commits: grammar, expression tree, symbol resolution and evaluation.",
        "sources": [
            "lib/src/revset.rs",
            "lib/src/revset_parser.rs",
            "lib/src/revset.pest",
            "lib/src/default_index/revset_engine.rs",
            "lib/src/fileset.rs",
            "docs/technical/revset-evaluation.md",
        ],
        "ready": False,
    },
    {
        "slug": "backends",
        "title": "Storage backends",
        "kind": "topic",
        "summary": "The Backend trait, the Store caching layer, and the Git and simple backends.",
        "sources": [
            "core/src/backend.rs",
            "lib/src/store.rs",
            "lib/src/git_backend.rs",
            "lib/src/simple_backend.rs",
            "lib/src/secret_backend.rs",
            "lib/src/default_backend_factories.rs",
        ],
        "ready": False,
    },
    {
        "slug": "protobufs",
        "title": "Every schema",
        "kind": "topic",
        "summary": "All seven .proto files, every message, enum and field, and the Rust types they map to.",
        "sources": [
            "lib/src/protos/",
            "lib/src/simple_backend.rs",
            "lib/src/simple_op_store.rs",
            "lib/src/git_backend.rs",
            "lib/src/local_working_copy.rs",
            "lib/src/default_index/store.rs",
            "lib/src/simple_workspace_store.rs",
            "lib/src/secure_config.rs",
        ],
        "ready": True,
    },
]

COMMAND_CATEGORIES = [
    'Creating and editing changes',
    'Moving and combining changes',
    'Content and conflicts',
    'Inspecting history',
    'Operation log',
    'Bookmarks and tags',
    'Git and remotes',
    'Workspaces',
    'Signing',
    'Configuration',
    'Utilities and internals',
]

COMMANDS = [
    {
        "command": 'new',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Create a new, empty change and (by default) edit it in the working copy',
        "source": ('cli/src/commands/new.rs', 53),
    },
    {
        "command": 'edit',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Sets the specified revision as the working-copy revision',
        "source": ('cli/src/commands/edit.rs', 36),
    },
    {
        "command": 'describe',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Update the change description or other metadata [default alias: desc]',
        "source": ('cli/src/commands/describe.rs', 51),
    },
    {
        "command": 'commit',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Update the description and create a new change on top [default alias: ci]',
        "source": ('cli/src/commands/commit.rs', 55),
    },
    {
        "command": 'metaedit',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Modify the metadata of a revision without changing its content',
        "source": ('cli/src/commands/metaedit.rs', 41),
    },
    {
        "command": 'next',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Move the working-copy commit to the child revision',
        "source": ('cli/src/commands/next.rs', 52),
    },
    {
        "command": 'prev',
        "category": 'Creating and editing changes',
        "tier": 'A',
        "summary": 'Change the working copy revision relative to the parent revision',
        "source": ('cli/src/commands/prev.rs', 51),
    },
    {
        "command": 'rebase',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Move revisions to different parent(s)',
        "source": ('cli/src/commands/rebase.rs', 268),
    },
    {
        "command": 'squash',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Move changes from a revision into another revision',
        "source": ('cli/src/commands/squash.rs', 88),
    },
    {
        "command": 'split',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Split a revision in two',
        "source": ('cli/src/commands/split.rs', 106),
    },
    {
        "command": 'absorb',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Move changes from a revision into the stack of mutable revisions',
        "source": ('cli/src/commands/absorb.rs', 52),
    },
    {
        "command": 'duplicate',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Create new changes with the same content as existing ones',
        "source": ('cli/src/commands/duplicate.rs', 55),
    },
    {
        "command": 'abandon',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Abandon a revision',
        "source": ('cli/src/commands/abandon.rs', 47),
    },
    {
        "command": 'parallelize',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Parallelize revisions by making them siblings',
        "source": ('cli/src/commands/parallelize.rs', 59),
    },
    {
        "command": 'simplify-parents',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Simplify parent edges for the specified revision(s).',
        "source": ('cli/src/commands/simplify_parents.rs', 23),
    },
    {
        "command": 'arrange',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Interactively arrange the commit graph.',
        "source": ('cli/src/commands/arrange.rs', 75),
    },
    {
        "command": 'converge',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Converge divergent changes',
        "source": ('cli/src/commands/converge.rs', 94),
    },
    {
        "command": 'revert',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Apply the reverse of the given revision(s)',
        "source": ('cli/src/commands/revert.rs', 50),
    },
    {
        "command": 'restore',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Restore paths from another revision',
        "source": ('cli/src/commands/restore.rs', 51),
    },
    {
        "command": 'diffedit',
        "category": 'Moving and combining changes',
        "tier": 'A',
        "summary": 'Touch up the content changes in a revision with a diff editor',
        "source": ('cli/src/commands/diffedit.rs', 49),
    },
    {
        "command": 'fix',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Update files with formatting fixes or other changes',
        "source": ('cli/src/commands/fix.rs', 162),
    },
    {
        "command": 'run',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Run a command across a set of revisions.',
        "source": ('cli/src/commands/run.rs', 645),
    },
    {
        "command": 'resolve',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Resolve conflicted files with an external merge tool',
        "source": ('cli/src/commands/resolve.rs', 50),
    },
    {
        "command": 'file annotate',
        "category": 'Content and conflicts',
        "tier": 'B',
        "summary": 'Show the source change for each line of the target file.',
        "source": ('cli/src/commands/file/annotate.rs', 39),
    },
    {
        "command": 'file chmod',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Sets or removes the executable bit for paths in the repo',
        "source": ('cli/src/commands/file/chmod.rs', 46),
    },
    {
        "command": 'file list',
        "category": 'Content and conflicts',
        "tier": 'B',
        "summary": 'List files in a revision',
        "source": ('cli/src/commands/file/list.rs', 30),
    },
    {
        "command": 'file search',
        "category": 'Content and conflicts',
        "tier": 'B',
        "summary": 'Search for content in files',
        "source": ('cli/src/commands/file/search.rs', 43),
    },
    {
        "command": 'file show',
        "category": 'Content and conflicts',
        "tier": 'B',
        "summary": 'Print contents of files in a revision',
        "source": ('cli/src/commands/file/show.rs', 50),
    },
    {
        "command": 'file track',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Start tracking specified paths in the working copy',
        "source": ('cli/src/commands/file/track.rs', 40),
    },
    {
        "command": 'file untrack',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Stop tracking specified paths in the working copy',
        "source": ('cli/src/commands/file/untrack.rs', 34),
    },
    {
        "command": 'sparse edit',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Start an editor to update the patterns that are present in the working copy',
        "source": ('cli/src/commands/sparse/edit.rs', 33),
    },
    {
        "command": 'sparse list',
        "category": 'Content and conflicts',
        "tier": 'B',
        "summary": 'List the patterns that are currently present in the working copy',
        "source": ('cli/src/commands/sparse/list.rs', 30),
    },
    {
        "command": 'sparse reset',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Reset the patterns to include all files in the working copy',
        "source": ('cli/src/commands/sparse/reset.rs', 25),
    },
    {
        "command": 'sparse set',
        "category": 'Content and conflicts',
        "tier": 'A',
        "summary": 'Update the patterns that are present in the working copy',
        "source": ('cli/src/commands/sparse/set.rs', 32),
    },
    {
        "command": 'log',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Show revision history',
        "source": ('cli/src/commands/log.rs', 73),
    },
    {
        "command": 'show',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Show revision metadata and diff',
        "source": ('cli/src/commands/show.rs', 34),
    },
    {
        "command": 'diff',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Compare file contents between two revisions',
        "source": ('cli/src/commands/diff.rs', 55),
    },
    {
        "command": 'interdiff',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Show differences between the diffs of two revisions',
        "source": ('cli/src/commands/interdiff.rs', 62),
    },
    {
        "command": 'status',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Show high-level repo status [default alias: st]',
        "source": ('cli/src/commands/status.rs', 61),
    },
    {
        "command": 'evolog',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Show how a change has evolved over time',
        "source": ('cli/src/commands/evolog.rs', 49),
    },
    {
        "command": 'root',
        "category": 'Inspecting history',
        "tier": 'B',
        "summary": 'Show the current workspace root directory (shortcut for `jj workspace root`)',
        "source": ('cli/src/commands/root.rs', 27),
    },
    {
        "command": 'bisect run',
        "category": 'Inspecting history',
        "tier": 'A',
        "summary": 'Run a given command to find the first bad revision',
        "source": ('cli/src/commands/bisect/run.rs', 60),
    },
    {
        "command": 'undo',
        "category": 'Operation log',
        "tier": 'A',
        "summary": 'Undo the last operation',
        "source": ('cli/src/commands/undo.rs', 49),
    },
    {
        "command": 'redo',
        "category": 'Operation log',
        "tier": 'A',
        "summary": 'Redo the most recently undone operation',
        "source": ('cli/src/commands/redo.rs', 44),
    },
    {
        "command": 'operation abandon',
        "category": 'Operation log',
        "tier": 'A',
        "summary": 'Abandon operation history',
        "source": ('cli/src/commands/operation/abandon.rs', 45),
    },
    {
        "command": 'operation diff',
        "category": 'Operation log',
        "tier": 'B',
        "summary": 'Compare changes to the repository between two operations',
        "source": ('cli/src/commands/operation/diff.rs', 70),
    },
    {
        "command": 'operation integrate',
        "category": 'Operation log',
        "tier": 'A',
        "summary": 'Make an operation part of the operation log',
        "source": ('cli/src/commands/operation/integrate.rs', 33),
    },
    {
        "command": 'operation log',
        "category": 'Operation log',
        "tier": 'B',
        "summary": 'Show the operation log',
        "source": ('cli/src/commands/operation/log.rs', 53),
    },
    {
        "command": 'operation restore',
        "category": 'Operation log',
        "tier": 'A',
        "summary": 'Create a new operation that restores the repo to an earlier state',
        "source": ('cli/src/commands/operation/restore.rs', 31),
    },
    {
        "command": 'operation revert',
        "category": 'Operation log',
        "tier": 'A',
        "summary": 'Create a new operation that reverts an earlier operation',
        "source": ('cli/src/commands/operation/revert.rs', 35),
    },
    {
        "command": 'operation show',
        "category": 'Operation log',
        "tier": 'B',
        "summary": 'Show changes to the repository in an operation',
        "source": ('cli/src/commands/operation/show.rs', 34),
    },
    {
        "command": 'bookmark advance',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Advance the closest bookmarks to a target revision',
        "source": ('cli/src/commands/bookmark/advance.rs', 54),
    },
    {
        "command": 'bookmark create',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Create a new bookmark',
        "source": ('cli/src/commands/bookmark/create.rs', 32),
    },
    {
        "command": 'bookmark delete',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Delete an existing bookmark and propagate the deletion to remotes on the next push',
        "source": ('cli/src/commands/bookmark/delete.rs', 37),
    },
    {
        "command": 'bookmark forget',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Forget a bookmark without marking it as a deletion to be pushed',
        "source": ('cli/src/commands/bookmark/forget.rs', 38),
    },
    {
        "command": 'bookmark list',
        "category": 'Bookmarks and tags',
        "tier": 'B',
        "summary": 'List bookmarks and their targets',
        "source": ('cli/src/commands/bookmark/list.rs', 51),
    },
    {
        "command": 'bookmark move',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Move existing bookmarks to target revision',
        "source": ('cli/src/commands/bookmark/move.rs', 46),
    },
    {
        "command": 'bookmark rename',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Rename `old` bookmark name to `new` bookmark name',
        "source": ('cli/src/commands/bookmark/rename.rs', 34),
    },
    {
        "command": 'bookmark set',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Create a new bookmark, or update an existing one by name',
        "source": ('cli/src/commands/bookmark/set.rs', 39),
    },
    {
        "command": 'bookmark track',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Start tracking given remote bookmarks',
        "source": ('cli/src/commands/bookmark/track.rs', 44),
    },
    {
        "command": 'bookmark untrack',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Stop tracking given remote bookmarks',
        "source": ('cli/src/commands/bookmark/untrack.rs', 41),
    },
    {
        "command": 'tag delete',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Delete existing tags',
        "source": ('cli/src/commands/tag/delete.rs', 30),
    },
    {
        "command": 'tag list',
        "category": 'Bookmarks and tags',
        "tier": 'B',
        "summary": 'List tags and their targets',
        "source": ('cli/src/commands/tag/list.rs', 54),
    },
    {
        "command": 'tag set',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Create or update tags',
        "source": ('cli/src/commands/tag/set.rs', 31),
    },
    {
        "command": 'tag track',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Start tracking given remote tags',
        "source": ('cli/src/commands/tag/track.rs', 38),
    },
    {
        "command": 'tag untrack',
        "category": 'Bookmarks and tags',
        "tier": 'A',
        "summary": 'Stop tracking given remote tags',
        "source": ('cli/src/commands/tag/untrack.rs', 38),
    },
    {
        "command": 'git clone',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Create a new repo backed by a clone of a Git repo',
        "source": ('cli/src/commands/git/clone.rs', 59),
    },
    {
        "command": 'git colocation',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Manage Jujutsu repository colocation with Git',
        "source": ('cli/src/commands/git/colocation.rs', 61),
    },
    {
        "command": 'git export',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Update the underlying Git repo with changes made in the repo',
        "source": ('cli/src/commands/git/export.rs', 29),
    },
    {
        "command": 'git fetch',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Fetch from a Git remote',
        "source": ('cli/src/commands/git/fetch.rs', 70),
    },
    {
        "command": 'git import',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Update repo with changes made in the underlying Git repo',
        "source": ('cli/src/commands/git/import.rs', 38),
    },
    {
        "command": 'git init',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Create a new Git backed repo.',
        "source": ('cli/src/commands/git/init.rs', 56),
    },
    {
        "command": 'git push',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Push to a Git remote',
        "source": ('cli/src/commands/git/push.rs', 123),
    },
    {
        "command": 'git remote',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Manage Git remotes',
        "source": ('cli/src/commands/git/remote/mod.rs', 41),
    },
    {
        "command": 'git root',
        "category": 'Git and remotes',
        "tier": 'B',
        "summary": 'Show the underlying Git directory of a repository using the Git backend',
        "source": ('cli/src/commands/git/root.rs', 28),
    },
    {
        "command": 'gerrit upload',
        "category": 'Git and remotes',
        "tier": 'A',
        "summary": 'Upload changes to Gerrit for code review, or update existing changes',
        "source": ('cli/src/commands/gerrit/upload.rs', 85),
    },
    {
        "command": 'workspace add',
        "category": 'Workspaces',
        "tier": 'A',
        "summary": 'Add a workspace',
        "source": ('cli/src/commands/workspace/add.rs', 59),
    },
    {
        "command": 'workspace forget',
        "category": 'Workspaces',
        "tier": 'A',
        "summary": "Stop tracking a workspace's working-copy commit in the repo",
        "source": ('cli/src/commands/workspace/forget.rs', 36),
    },
    {
        "command": 'workspace list',
        "category": 'Workspaces',
        "tier": 'B',
        "summary": 'List workspaces',
        "source": ('cli/src/commands/workspace/list.rs', 28),
    },
    {
        "command": 'workspace remove',
        "category": 'Workspaces',
        "tier": 'A',
        "summary": 'Remove a workspace and its working-copy files from disk',
        "source": ('cli/src/commands/workspace/remove.rs', 43),
    },
    {
        "command": 'workspace rename',
        "category": 'Workspaces',
        "tier": 'A',
        "summary": 'Renames the current workspace',
        "source": ('cli/src/commands/workspace/rename.rs', 25),
    },
    {
        "command": 'workspace root',
        "category": 'Workspaces',
        "tier": 'B',
        "summary": 'Show the workspace root directory',
        "source": ('cli/src/commands/workspace/root.rs', 31),
    },
    {
        "command": 'workspace update-stale',
        "category": 'Workspaces',
        "tier": 'A',
        "summary": 'Update a workspace that has become stale',
        "source": ('cli/src/commands/workspace/update_stale.rs', 29),
    },
    {
        "command": 'sign',
        "category": 'Signing',
        "tier": 'A',
        "summary": 'Cryptographically sign a revision',
        "source": ('cli/src/commands/sign.rs', 42),
    },
    {
        "command": 'unsign',
        "category": 'Signing',
        "tier": 'A',
        "summary": 'Drop a cryptographic signature',
        "source": ('cli/src/commands/unsign.rs', 39),
    },
    {
        "command": 'config edit',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'Start an editor on a jj config file.',
        "source": ('cli/src/commands/config/edit.rs', 30),
    },
    {
        "command": 'config gc',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'Find and optionally delete repo-level config directories whose repo path no longer exists.',
        "source": ('cli/src/commands/config/gc.rs', 36),
    },
    {
        "command": 'config get',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'Get the value of a given config option.',
        "source": ('cli/src/commands/config/get.rs', 38),
    },
    {
        "command": 'config list',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'List variables set in config files, along with their values.',
        "source": ('cli/src/commands/config/list.rs', 38),
    },
    {
        "command": 'config path',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'Print the paths to the config files',
        "source": ('cli/src/commands/config/path.rs', 36),
    },
    {
        "command": 'config set',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'Update a config file to set the given option to a given value.',
        "source": ('cli/src/commands/config/set.rs', 32),
    },
    {
        "command": 'config unset',
        "category": 'Configuration',
        "tier": 'B',
        "summary": 'Update a config file to unset the given option.',
        "source": ('cli/src/commands/config/unset.rs', 29),
    },
    {
        "command": 'help',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Print this message or the help of the given subcommand(s)',
        "source": ('cli/src/commands/help.rs', 32),
    },
    {
        "command": 'version',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Display version information',
        "source": ('cli/src/commands/version.rs', 25),
    },
    {
        "command": 'util backend',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Commands relating to the backend used in the current repo',
        "source": ('cli/src/commands/util/backend/mod.rs', 28),
    },
    {
        "command": 'util completion',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Print a command-line-completion script',
        "source": ('cli/src/commands/util/completion.rs', 50),
    },
    {
        "command": 'util config-schema',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Print the JSON schema for the jj TOML config format.',
        "source": ('cli/src/commands/util/config_schema.rs', 24),
    },
    {
        "command": 'util diff',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Compare two files on disk',
        "source": ('cli/src/commands/util/diff.rs', 40),
    },
    {
        "command": 'util exec',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Execute an external command via jj',
        "source": ('cli/src/commands/util/exec.rs', 68),
    },
    {
        "command": 'util gc',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Run backend-dependent garbage collection.',
        "source": ('cli/src/commands/util/gc.rs', 31),
    },
    {
        "command": 'util install-man-pages',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": "Install Jujutsu's manpages to the provided path",
        "source": ('cli/src/commands/util/install_man_pages.rs', 23),
    },
    {
        "command": 'util markdown-help',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Print the CLI help for all subcommands in Markdown',
        "source": ('cli/src/commands/util/markdown_help.rs', 23),
    },
    {
        "command": 'util snapshot',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Snapshot the working copy if needed',
        "source": ('cli/src/commands/util/snapshot.rs', 82),
    },
    {
        "command": 'debug',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Low-level commands not intended for users',
        "source": ('cli/src/commands/debug/mod.rs', 73),
    },
    {
        "command": 'bench',
        "category": 'Utilities and internals',
        "tier": 'C',
        "summary": 'Commands for benchmarking internal operations',
        "source": ('cli/src/commands/bench/mod.rs', 42),
    },
]

COMMAND_PAGE_OVERRIDES = {
    "commit": {
        "title": "How jj commit works",
        "sources": [
            "cli/src/commands/commit.rs",
            "cli/src/description_util.rs",
            "cli/src/cli_util.rs",
            "cli/src/merge_tools/mod.rs",
            "lib/src/repo.rs",
            "lib/src/commit_builder.rs",
            "cli/src/config/misc.toml",
        ],
        "ready": True,
    },
    "describe": {
        "title": "How jj describe works",
        "sources": [
            "cli/src/commands/describe.rs",
            "cli/src/description_util.rs",
            "cli/src/cli_util.rs",
            "lib/src/repo.rs",
            "lib/src/commit_builder.rs",
            "lib/src/rewrite.rs",
            "cli/src/config/templates.toml",
            "cli/src/config/misc.toml",
        ],
        "ready": True,
    },
    "edit": {
        "title": "How jj edit works",
        "sources": [
            "cli/src/commands/edit.rs",
            "cli/src/cli_util.rs",
            "cli/src/revset_util.rs",
            "lib/src/repo.rs",
        ],
        "ready": True,
    },
    "new": {
        "title": "How jj new works",
        "sources": [
            "cli/src/commands/new.rs",
            "cli/src/cli_util.rs",
            "lib/src/rewrite.rs",
            "lib/src/repo.rs",
            "lib/src/commit_builder.rs",
            "cli/src/description_util.rs",
            "cli/src/config/templates.toml",
            "cli/src/config/misc.toml",
        ],
        "ready": True,
    },
    "fix": {
        "title": "How jj fix works",
        "sources": [
            "lib/src/fix.rs",
            "cli/src/commands/fix.rs",
            "cli/src/config/revsets.toml",
            "docs/config.md",
        ],
        "ready": True,
    },
}


def command_slug(command):
    return command.replace(" ", "-").replace("_", "-")


def _command_page(entry):
    page = {
        "slug": command_slug(entry["command"]),
        "title": f"jj {entry['command']}",
        "kind": "command",
        "command": entry["command"],
        "category": entry["category"],
        "tier": entry["tier"],
        "summary": entry["summary"],
        "sources": [entry["source"][0]],
        "ready": False,
    }
    page.update(COMMAND_PAGE_OVERRIDES.get(page["slug"], {}))
    return page


PAGES = TOPICS + [_command_page(entry) for entry in COMMANDS]

PROTO_MESSAGES = {
    "default_index.proto": ["SegmentControl"],
    "git_store.proto": ["Commit"],
    "local_working_copy.proto": [
        "FileType",
        "MaterializedConflictData",
        "FileState",
        "FileStateEntry",
        "SparsePatterns",
        "TreeState",
        "WatchmanClock",
        "Checkout",
    ],
    "secure_config.proto": ["ConfigMetadata"],
    "simple_op_store.proto": [
        "RefConflictLegacy",
        "RefConflict",
        "RefConflict.Term",
        "RefTarget",
        "RefTargetTerm",
        "RemoteRefState",
        "RemoteBookmark",
        "Bookmark",
        "GitRef",
        "GitHead",
        "RemoteRef",
        "Tag",
        "View",
        "RemoteView",
        "Operation",
        "Timestamp",
        "OperationMetadata",
        "CommitPredecessors",
    ],
    "simple_store.proto": [
        "TreeValue",
        "TreeValue.File",
        "Tree",
        "Tree.Entry",
        "Commit",
        "Commit.Timestamp",
        "Commit.Signature",
    ],
    "simple_workspace_store.proto": ["Workspace", "Workspaces"],
}

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
        template = "jj/index.html"
    else:
        page = find_page(slug)
        if page is None:
            return None
        template = f"jj/{slug}.html"

    previous, following = _neighbours(slug)
    context = {
        "page": page,
        "pages": PAGES,
        "ready_slugs": {entry["slug"] for entry in ready_pages()},
        "topics": [entry for entry in PAGES if entry["kind"] == "topic"],
        "command_categories": [
            (category, [entry for entry in PAGES if entry.get("category") == category])
            for category in COMMAND_CATEGORIES
        ],
        "upstream": UPSTREAM,
        "src": source_url,
        "proto_messages": PROTO_MESSAGES,
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
        "jj/base.html",
        intro=intro,
        content=body,
        toc=table_of_contents(body),
        **context,
    )
