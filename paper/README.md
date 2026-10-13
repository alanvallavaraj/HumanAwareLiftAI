# Elsevier manuscript source

The manuscript is prepared for double-anonymised review. `manuscript.tex` (with `body.tex`, `supplement.tex` and `references.bib`) carries no author names, affiliations, contact details or repository links; the dataset reference is anonymised and the real record is given on the title page. Build with `latexmk -pdf -halt-on-error manuscript.tex` from this directory.

Submission files:

| File | Submission item |
| --- | --- |
| `manuscript.pdf` | Manuscript without author details |
| `../publishing/submission-source.zip` | LaTeX source as one flattened `manuscript.tex` with its `.bib`, `.bbl`, class, style and figure files, all at the root (anonymised; built by `scripts/build_submission_package.py`) |
| `title_page.pdf` / `title_page.docx` (source `title_page.tex`) | Title page with author and affiliation details |
| `Highlights.txt` / `Highlights.docx` | Highlights (five bullets, each under 85 characters) |

The five figures are separate PDFs in `../publishing/figures/`: rule_structure.pdf (Figure 1, source in `figures/src/rule_structure.tex`), component_ablation.pdf (Figure 2), delay_contrasts.pdf (Figure 3), bonus_sensitivity.pdf (Figure 4) and conditional_contrasts.pdf (Figure 5). The Word copies are written by `scripts/build_word_files.py` (requires python-docx).

The main text reports the corrected matched-arrival campaign as primary evidence and uses the historical campaign only to show how completed-trip means behave. Appendix A gives the historical factorial design, its all-arrival bounds and fairness summaries; Appendix B lists the experiment history; Appendix C reports the superseded legacy event-recording campaign and the historical replay-parity result.

The April 2024 elsarticle class source and numeric bibliography style accompany the manuscript; their upstream licence is retained. The template files are unmodified. Analysis and experiment instructions are in ../REPRODUCING.md.
