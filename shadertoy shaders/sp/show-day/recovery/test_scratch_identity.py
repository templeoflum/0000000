"""Offline verification against native empty-slot conventions."""
import json,tempfile,unittest
from pathlib import Path
import xml.etree.ElementTree as ET
from verify_show_pair import verify,ROOT
from dependencies import build_contract

class ScratchTests(unittest.TestCase):
    def test_native_empty_slot_allowed_nonempty_id_rejected(self):
        source=ROOT/'sp/engine/patches/Feedback shaping.avc'
        base=ROOT/'sp/design/heart-performance-plan/baseline'
        sources=json.loads((base/'installed-sources.json').read_text())
        effects=json.loads((base/'installed-effects.json').read_text())
        data=json.loads(source.with_suffix('.json').read_text())
        data['effects']={};data['dependencies']=build_contract(source,layers=data['layers'])
        tree=ET.parse(source)
        clip=next(c for c in tree.getroot().findall('Deck/Clip') if not list(c))
        clip.set('uniqueId','1788780038810')
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as td:
            avc=Path(td)/source.name;avc.with_suffix('.json').write_text(json.dumps(data))
            tree.write(avc);verify(avc,sources,effects)
            primary=ET.SubElement(ET.SubElement(clip,'VideoTrack'),'PrimarySource')
            tree.write(avc);verify(avc,sources,effects)
            ET.SubElement(primary,'VideoSource',{'type':'GeneratorVideoSource'})
            tree.write(avc)
            with self.assertRaisesRegex(AssertionError,'Scratch identity'):verify(avc,sources,effects)

if __name__=='__main__':unittest.main()
