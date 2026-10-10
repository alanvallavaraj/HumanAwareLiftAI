#!/usr/bin/env python3
"""Join, verify and unpack the legacy campaign's retained event records."""
import hashlib,json,tarfile,urllib.request,gzip
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data/passenger_event_archive.json'
def main():
 m=json.loads(MANIFEST.read_text());target=ROOT/'data/passenger-events.tar.xz'
 if not target.exists() and m.get('repository_parts') and all((ROOT/p['path']).exists() for p in m['repository_parts']):
  with target.open('wb') as f:
   for p in m['repository_parts']:
    content=(ROOT/p['path']).read_bytes()
    if hashlib.sha256(content).hexdigest()!=p['sha256']:raise ValueError('Archive part checksum mismatch')
    f.write(content)
 if not target.exists():raise SystemExit('Archive parts are missing from data/passenger-event-parts')
 h=hashlib.sha256()
 with target.open('rb') as f:
  while chunk:=f.read(1024*1024):h.update(chunk)
 if h.hexdigest()!=m['sha256']:raise ValueError('Passenger archive checksum mismatch')
 with tarfile.open(target,'r:xz') as archive:
  for member in archive.getmembers():
   if not member.name.startswith('results/censoring_validation/passengers/') or member.issym() or member.islnk():raise ValueError('Unexpected archive path')
  for member in archive.getmembers():
   if not member.isfile():continue
   path=ROOT/(member.name+'.gz');path.parent.mkdir(parents=True,exist_ok=True)
   if '..' in Path(member.name).parts:raise ValueError('Unsafe archive path')
   with archive.extractfile(member) as src,gzip.open(path,'wb') as dst:
    while chunk:=src.read(1024*1024):dst.write(chunk)
 print('Passenger archive verified and extracted.')
if __name__=='__main__':main()
