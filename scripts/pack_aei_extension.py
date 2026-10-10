"""Losslessly archive the corrected-campaign event records with portable archive metadata."""
import argparse,gzip,tarfile,io,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args();root=Path(a.directory);target=root/'passenger-events.tar.xz'
with tarfile.open(target,'w:xz',preset=6) as archive:
 for i,path in enumerate(sorted((root/'passengers').glob('*.csv.gz')),1):
  b=gzip.decompress(path.read_bytes());entry=tarfile.TarInfo('passengers/'+path.stem);entry.size=len(b);entry.mtime=0;archive.addfile(entry,io.BytesIO(b))
  if i%2000==0:print('Archived',i,'event files',flush=True)
 h=hashlib.sha256()
with target.open('rb') as stream:
 while chunk:=stream.read(1048576):h.update(chunk)
manifest={'filename':target.name,'bytes':target.stat().st_size,'sha256':h.hexdigest(),'format':'xz-compressed tar of per-case uncompressed CSV','event_files':len(list((root/'passengers').glob('*.csv.gz'))),'restoration':'Per-case CSV content is lossless; gzip headers and filesystem ownership are not research data.'}
(root/'archive_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest,indent=2))
