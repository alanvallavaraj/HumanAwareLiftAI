"""Assemble the editable submission source into publishing/submission-source.zip.

Editorial Manager compiles LaTeX submissions itself and cannot follow
subfolders, so the archive holds a single flattened manuscript.tex (body and
appendices inlined), the bibliography, the compiled .bbl, the Elsevier class
and style, and each figure as a separate PDF, all at the archive root. The
same files can be uploaded one by one: the .tex, .bib, .bbl, .cls and .bst
files as the manuscript item and the PDFs as figures.
"""
import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
FIGURES = ROOT / "publishing/figures"
SUPPORT = ["references.bib", "manuscript.bbl", "elsarticle.cls", "elsarticle-num.bst"]
FIGS = ["rule_structure.pdf", "component_ablation.pdf", "delay_contrasts.pdf",
        "bonus_sensitivity.pdf", "conditional_contrasts.pdf"]
STAMP = (2026, 1, 1, 0, 0, 0)


def flattened_manuscript() -> str:
    text = (PAPER / "manuscript.tex").read_text()
    for name in ("body.tex", "supplement.tex"):
        token = "\\input{" + name + "}"
        if text.count(token) != 1:
            raise SystemExit(f"expected one {token} in manuscript.tex")
        part = (PAPER / name).read_text().rstrip("\n")
        text = text.replace(token, f"\n%% ---- begin {name}\n{part}\n%% ---- end {name}\n")
    text = text.replace("\\graphicspath{{../publishing/figures/}{./}}", "\\graphicspath{{./}}")
    if "\\input{" in text or "../" in text:
        raise SystemExit("flattened manuscript still refers to other files")
    return text


def add(z: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=STAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, data)


def main() -> None:
    out = ROOT / "publishing/submission-source.zip"
    with zipfile.ZipFile(out, "w") as z:
        add(z, "manuscript.tex", flattened_manuscript().encode())
        for name in SUPPORT:
            add(z, name, (PAPER / name).read_bytes())
        for name in FIGS:
            add(z, name, (FIGURES / name).read_bytes())
    print(out.relative_to(ROOT), hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
