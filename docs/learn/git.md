# git

**What it is.** A distributed version-control system: every clone holds the full history as a
graph of immutable *commits*, each a snapshot of the tree plus a pointer to its parent(s).

**Why here.** One repo holds code, config, seeds and docs, so a commit records *what the
pipeline was* at a point in time. With `.env` git-ignored and `.env.example` committed, the
repo can go public without leaking credentials.

## Concepts that matter

1. **Working tree → index (staging) → commit.** `git add` copies a change into the index;
   `git commit` snapshots the index. `git status` shows all three.
2. **Commits are snapshots, identified by a hash** of their content + parent. Changing history
   (rebase, amend) makes *new* commits; that's why rewriting pushed history hurts others.
3. **Branches are movable pointers** to a commit. `HEAD` is where you are.
4. **Remote-tracking branches** (`origin/main`) are your last-known copy of the server.
   `fetch` updates them; `pull` = fetch + merge (or rebase).
5. **Merge vs rebase.** Merge keeps true history with a merge commit; rebase replays your
   commits on top for a linear history. Never rebase commits others have pulled.
6. **`.gitignore`** stops untracked files from being added; it does nothing for files already
   committed (`git rm --cached` first).
7. **Hooks** run scripts at events (`pre-commit` before a commit). This repo installs them with
   `make setup` (see ruff-and-pre-commit.md).
8. **Large/binary files** bloat history forever. Data lives in `data/` (ignored); a 1 MB
   hook limit catches accidents.

## Commands you'll run

```bash
git status                       # what changed, what's staged
git switch -c feat/coverage      # new branch for a piece of work
git add -p                       # stage hunk by hunk (review your own diff)
git commit -m "Add coverage audit sections 1-2"
git log --oneline --graph -15    # recent history
git diff main...HEAD             # what this branch changes vs main
git fetch origin && git rebase origin/main   # update a private branch
git push -u origin feat/coverage
git restore --staged file        # unstage;  git restore file  # discard local edits (careful)
```

## Common mistakes

- Committing `.env` or a data file. If it happens: rotate the secret *first*, then remove it
  from history; deleting it in a new commit leaves it in the old ones.
- `git add .` without reading `git status`. Use `git add -p`.
- Huge "WIP" commits. Small commits with messages saying *why* are easier to review and revert.
- Force-pushing a shared branch. Use `--force-with-lease` and only on your own branches.

## Interview questions

- *What's the difference between `git merge` and `git rebase`, and when would you avoid rebase?*
- *A secret was committed and pushed an hour ago. Walk me through what you do.*
  (Rotate it immediately; then purge history with `git filter-repo`, force-push, and ask
  collaborators to re-clone. Assume it's compromised regardless.)
