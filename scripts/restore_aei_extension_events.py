"""Restore and verify retained corrected-campaign passenger events without rerunning simulation."""
import gzip,hashlib,json,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'results/aei_extension';parts=root/'data/aei-extension-event-parts'
manifest=json.loads((out/'archive_manifest.json').read_text());archive=out/manifest['filename']
if not archive.exists():
 with archive.open('wb') as target:
  for p in sorted(parts.glob('part-*')):
   with p.open('rb') as source:
    while block:=source.read(1048576):target.write(block)
h=hashlib.sha256()
with archive.open('rb') as stream:
 while block:=stream.read(1048576):h.update(block)
assert h.hexdigest()==manifest['sha256'], 'Event archive checksum mismatch'
n=0
with tarfile.open(archive,'r:xz') as source:
 for member in source:
  relative=Path(member.name)
  assert member.isfile() and len(relative.parts)==2 and relative.parts[0]=='passengers' and relative.suffix=='.csv'
  target=out/relative;target.parent.mkdir(parents=True,exist_ok=True)
  with source.extractfile(member) as stream,gzip.open(str(target)+'.gz','wb') as dest:
   while block:=stream.read(1048576):dest.write(block)
  n+=1
assert n==manifest['event_files']
print('Restored and checksum-verified',n,'passenger event files.')
