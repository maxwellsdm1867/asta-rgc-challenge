---
name: asta-research-setup
description: >-
  Scaffold a NEW research repository for an Asta research project — the front
  bookend to `asta-challenge-wrapup`. Use this whenever the user wants to start a
  research project and says things like "set up a research repo", "start a new
  research project", "scaffold a research repository", "create a research
  project", "make me a Quarto research repo", "init the research environment", or
  "new Asta challenge repo". It creates (or clones) a git repo, drops in a Quarto
  scaffold so reports render with citations, sets up a sane .gitignore and a clean
  Python env, adds a data/ folder with a data dictionary, and — only if asked —
  the optional GitHub Pages workflow and devcontainer. Defaults to PRIVATE
  (research/blind-challenge data shouldn't be public up front). Reach for it even
  if the user only names one piece (e.g. "just add the Quarto scaffold").
---

# Asta research-project setup

Scaffold a research repo the same clean way every time, so the *finish* (packaging + submission via
`asta-challenge-wrapup`) is easy. The two skills are bookends: this one sets the project up; that one
wraps it up.

Skip any step the user has already done. Ask only for what you can't infer (repo name, public vs
private) — default sensibly otherwise.

## 1. The repo

- **New repo on GitHub:** `gh repo create <name> --private --clone && cd <name>`.
  Default **private** — research data and blind-challenge answers shouldn't be public at the start.
  Only pass `--public` if the user explicitly says so.
- **Existing local dir → GitHub:** from inside it, `gh repo create <name> --private --source=. --remote=origin --push`.
- **Local only (no GitHub yet):** `git init`. You can create the remote later with the same command.

## 2. Quarto scaffold (so reports render with citations)

Use `.qmd` (not `.md`) for anything you want rendered with citations. Fetch the canonical assets, or
write the sensible defaults below if offline:

```bash
curl -fsSL -o _quarto.yml \
  https://raw.githubusercontent.com/allenai/asta-plugins/main/skills/preview/assets/_quarto.yml \
  || cat > _quarto.yml <<'YML'
project:
  type: website
  output-dir: _site
format:
  html:
    theme: cosmo
    toc: true
    code-fold: true
bibliography: references.bib
YML

printf -- '---\ntitle: "My Research"\n---\n\n# My Research\n' > index.qmd
touch references.bib
```

Note for later: render a **self-contained** report with `quarto render index.qmd -M embed-resources:true`
so it works as a single file on GitHub Pages (no `site_libs` dependency).

## 3. .gitignore — keep generated + heavy stuff out

These are the ones that bite: build output, the venv, and scratch dirs. A `git clean`/reset will wipe
anything ignored/untracked, so keep **deliverables** tracked and only ignore throwaways:

```bash
cat >> .gitignore <<'EOF'
_site/
.quarto/
.pier/
venv/
scratch/
__pycache__/
*.pyc
.DS_Store
EOF
```

## 4. Clean Python environment

The system Anaconda often ships a broken numpy/pandas ABI (`import pandas` crashes). Standardize on a
venv from the start:

```bash
python3 -m venv venv && source venv/bin/activate
pip install "numpy<2" "pandas>=2" scipy matplotlib   # add numba if you'll do heavy fits
```

## 5. Data + a data dictionary

```bash
mkdir -p data
cat > data/DATA_DICTIONARY.md <<'EOF'
# Data dictionary
Describe each file and column: units, sampling, what is input vs. what must be predicted,
and how records/trials are separated.
EOF
```

Drop the actual data into `data/`. If it's a blind challenge, keep the answer out of the repo.

## 6. Commit

```bash
git add -A && git commit -m "init research project"
```

## 7. Optional add-ons (only if asked)

- **GitHub Pages / PR previews** — a docs workflow that builds and publishes the Quarto site:
  ```bash
  mkdir -p .github/workflows
  curl -fsSL -o .github/workflows/docs.yml \
    https://raw.githubusercontent.com/allenai/asta-plugins/main/skills/preview/assets/docs.yml
  ```
  Pages is **public** — don't enable it for a blind challenge until grading is done.
- **DevContainer / Codespaces** (VS Code + Asta skills + Quarto preview):
  ```bash
  mkdir -p .devcontainer
  curl -fsSL -o .devcontainer/devcontainer.json \
    https://raw.githubusercontent.com/allenai/asta-plugins/main/skills/workspace/assets/devcontainer.json
  ```

## Hand-off

When the research is done, package it with **`asta-challenge-wrapup`** — it verifies deliverables,
writes and *grounds* the tools feedback, captures the session trace, and scaffolds the submission.
