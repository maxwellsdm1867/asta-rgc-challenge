---
slug: write-report
status: done
---

# Goal

Write `index.qmd`: the equation, method, fitted parameters, per-condition held-out metrics, and
failure modes; render with Quarto.

# Instructions

1. State the explicit equation with every term defined and units.
2. Explain data → model selection (dynamic I–V, phase plot, STA) and the fitting method.
3. Report the fitted parameter table and per-condition held-out metrics (VP@q=4, Γ, subthreshold
   RMSE/R², rate match) with figures.
4. State limitations and separate data-derived facts from prior knowledge; fill `references.bib`.
5. Render with `quarto render`.

# Results

## Summary
`index.qmd` written and rendered to `_site/index.html` (Quarto 1.9.38). Includes the equation,
parameter table, method, held-out metrics table, four figures, limitations, and a data-vs-prior
section. `references.bib` holds the eight sources actually relied on.

## Artifacts
- `index.qmd`, `_site/index.html` (rendered), `figures/fig_*.png`, `references.bib`.

# Assessment
Renders cleanly; the .qmd source is the committed deliverable.
