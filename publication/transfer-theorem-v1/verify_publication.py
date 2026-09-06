"""Portable release/presentation identity checks; no browser or network needed."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
LAB=ROOT/'website/transfer-theorem-lab'
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[];self.assets=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag=='script' and 'src' in a:self.assets.append(a['src'])
        if tag=='link' and a.get('rel')=='stylesheet':self.assets.append(a['href'])
def run():
    page=Page();page.feed((LAB/'index.html').read_text())
    assert len(page.ids)==len(set(page.ids)),'duplicate HTML id'
    for ref in page.assets:
        assert not urlsplit(ref).scheme and (LAB/ref).is_file(),'nonlocal runtime asset'
    for ref in page.links:
        if ref.startswith('#'):assert ref[1:] in page.ids,'broken page anchor'
    e=json.loads((LAB/'evidence.json').read_text())
    assert e['schema']=='transfer-theorem-lab-evidence-v1'
    assert len(e['paths'])==5 and len(e['history'])==9
    refs=list(e['proofLinks'].values())+[r['url'] for r in e['paths']+e['history']+e['links']]
    source_links=0
    for ref in refs:
        token='/blob/'+e['tag']+'/'
        if token in ref:
            name=unquote(ref.split(token,1)[1]);assert (ROOT/name).is_file(),'missing public evidence: '+name
            source_links+=1
    for name,wanted in e['inputSha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
    manifest=json.loads((LAB/'lab-manifest.json').read_text())
    for name,wanted in manifest['asset_sha256'].items():assert hashlib.sha256((LAB/name).read_bytes()).hexdigest()==wanted,name
    seal=json.loads((ROOT/'publication/transfer-theorem-v1/VALIDATION.json').read_text())
    for name,wanted in seal['files_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==wanted,name
    assert seal['research_tests']==33 and seal['lab_tests']==19
    # New public prose must use portable evidence links. Historical archives
    # intentionally preserve their original local paths, documented in the guide.
    for p in [ROOT/'TRANSFER_THEOREM_PUBLIC_COMPANION.md',LAB/'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in target or target.startswith('#'):continue
            assert not target.startswith('/Volumes/') and (p.parent/target.split('#')[0]).exists(),str(p)+' '+target
    return {'verified':True,'html_ids':len(page.ids),'local_runtime_assets':len(page.assets),
      'pinned_source_links':source_links,'research_inputs':len(e['inputSha256']),
      'sealed_publication_files':len(seal['files_sha256']),
      'scope':'Static identity and portability checks. Browser findings are recorded separately.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
