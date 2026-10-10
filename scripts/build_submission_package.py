"""Assemble the editable submission source into publishing/submission-source.zip.

The archive holds the LaTeX source, bibliography, Elsevier class and style,
the compiled .bbl, the highlights file and each figure as a separate PDF, all
at the archive root so that the source compiles as uploaded.
"""
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
FIGURES = ROOT / "publishing/figures"
SOURCE = ["manuscript.tex", "body.tex", "supplement.tex", "references.bib", "manuscript.bbl",
          "elsarticle.cls", "elsarticle-num.bst", "Highlights.txt"]
FIGS = ["conditional_contrasts.pdf", "aei_ablation.pdf", "aei_dwell.pdf", "aei_weights.pdf"]


def main() -> None:
    out = ROOT / "publishing/submission-source.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name in SOURCE:
            z.write(PAPER / name, name)
        for name in FIGS:
            z.write(FIGURES / name, name)
    print(out.relative_to(ROOT), hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
