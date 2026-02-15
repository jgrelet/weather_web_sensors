# Git Workflow Memo (feature → dev → main + PR/MR)

## 1️⃣ Synchronise local branches

``` bash
git checkout main
git pull origin main

git checkout dev
git pull origin dev
```

------------------------------------------------------------------------

## 2️⃣ Create a feature branch (from dev)

``` bash
git checkout -b feature/news
# ... work ...
git add -A
git commit -m "Add news feature"
```

Push the feature branch:

``` bash
git push -u origin feature/news
```

------------------------------------------------------------------------

## 3️⃣ Open a Pull Request / Merge Request

In GitHub / GitLab UI:

-   **Target branch**: `dev`
-   **Source branch**: `feature/news`
-   Add description
-   Request review
-   Wait for CI if applicable
-   Merge (according to team policy: Merge commit or Squash)

------------------------------------------------------------------------

## 4️⃣ After merge (cleanup)

``` bash
git checkout dev
git pull origin dev

git branch -d feature/news
git push origin --delete feature/news   # optional
```

------------------------------------------------------------------------

# 🚀 Release Process (dev → main)

## 1️⃣ Create PR/MR from dev → main

In UI: - Target: `main` - Source: `dev` - Review + Merge

Then locally:

``` bash
git checkout main
git pull origin main
```

------------------------------------------------------------------------

## 2️⃣ Create and push a tag (release)

``` bash
git tag -a v1.x.x -m "Release v1.x.x"
git push origin v1.x.x
```

To push all tags:

``` bash
git push --tags
```

------------------------------------------------------------------------

# 🔎 If local branch has diverged from origin

## Option 1 --- Rebase (linear history, recommended in many cases)

``` bash
git pull --rebase origin main
```

## Option 2 --- Merge (creates a merge commit)

``` bash
git pull --no-rebase origin main
```

## Option 3 --- Fast-forward only (fails if divergence)

``` bash
git pull --ff-only origin main
```

To inspect history before deciding:

``` bash
git log --oneline --graph --decorate --all | head -n 30
```

------------------------------------------------------------------------

# ⚙️ Recommended Global Git Configuration

These settings apply to all repositories on your machine.

## Rebase by default (clean linear history)

``` bash
git config --global pull.rebase true
```

## OR Merge by default

``` bash
git config --global pull.rebase false
```

## OR Fast-forward only (strict mode)

``` bash
git config --global pull.ff only
```

------------------------------------------------------------------------

# 📌 Notes

-   `git tag` alone lists tags.
-   Always `git pull` before merging.
-   Prefer PR/MR over direct merge in team projects.
-   Delete feature branches after merge to keep repository clean.
-   Use semantic versioning for tags: `vMAJOR.MINOR.PATCH`
