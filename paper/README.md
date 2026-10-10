# Elsevier manuscript source

Build with `latexmk -pdf -halt-on-error manuscript.tex` from this directory.

Submission source: manuscript.tex, body.tex, supplement.tex, references.bib, elsarticle.cls, elsarticle-num.bst and the four separate PDF figures in ../publishing/figures/: conditional_contrasts.pdf (Figure 1), aei_ablation.pdf (Figure 2), aei_dwell.pdf (Figure 3) and aei_weights.pdf (Figure 4). Highlights.txt contains five bullets, each under 85 characters. `scripts/build_submission_package.py` assembles exactly these files into publishing/submission-source.zip.

The main text reports the corrected matched-arrival campaign as primary evidence and uses the historical campaign only to show how completed-trip means behave. Appendix A lists the experiment history; Appendix B reports the superseded legacy event-recording campaign and the historical replay-parity result.

The April 2024 elsarticle class source and numeric bibliography style accompany the manuscript; their upstream licence is retained. The template files are unmodified. Analysis and experiment instructions are in ../REPRODUCING.md.
