"""Decompress the committed historical campaign CSV and verify its SHA-256."""
import argparse, gzip, hashlib, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/historical-results.csv.gz"
EXPECTED_GZ = "fece0e4c4032b157aebaff2a96dd7939fd92b1c95fea1da04d44f809d41e3e4d"
EXPECTED = "7654ba08d904362a1f463d9816ed936c83338682571c83b637bb214a37fe740d"
def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--out", default="data/full/results.csv"); a=parser.parse_args()
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    if not out.exists():
        if sha256(ARCHIVE)!=EXPECTED_GZ: raise SystemExit("FAILED compressed dataset checksum")
        temp=out.with_suffix(".partial")
        with gzip.open(ARCHIVE,"rb") as src, temp.open("wb") as dst: shutil.copyfileobj(src,dst)
        temp.replace(out)
    digest=sha256(out)
    if digest!=EXPECTED: raise SystemExit("FAILED dataset checksum; remove incorrect file and retry")
    print("PASS SHA-256:",out,digest)
if __name__=="__main__": main()
