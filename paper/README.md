# Elsevier manuscript source

The manuscript is prepared for double-anonymised review. `manuscript.tex` (with `body.tex`, `supplement.tex` and `references.bib`) carries no author names, affiliations, contact details or repository links; the dataset reference is anonymised and the real record is given on the title page. Build with `latexmk -pdf -halt-on-error manuscript.tex` from this directory.

Submission files:

| File | Submission item |
| --- | --- |
| `manuscript.pdf` | Manuscript without author details |
| `../publishing/submission-source.zip` | LaTeX source files (anonymised; built by `scripts/build_submission_package.py`) |
| `title_page.pdf` / `title_page.docx` (source `title_page.tex`) | Title page with author and affiliation details |
| `Highlights.txt` / `Highlights.docx` | Highlights (five bullets, each under 85 characters) |

The four figures are separate PDFs in `../publishing/figures/`: conditional_contrasts.pdf (Figure 1), aei_ablation.pdf (Figure 2), aei_dwell.pdf (Figure 3) and aei_weights.pdf (Figure 4). The Word copies are written by `scripts/build_word_files.py` (requires python-docx).

The main text reports the corrected matched-arrival campaign as primary evidence and uses the historical campaign only to show how completed-trip means behave. Appendix A lists the experiment history; Appendix B reports the superseded legacy event-recording campaign and the historical replay-parity result.

The April 2024 elsarticle class source and numeric bibliography style accompany the manuscript; their upstream licence is retained. The template files are unmodified. Analysis and experiment instructions are in ../REPRODUCING.md.
