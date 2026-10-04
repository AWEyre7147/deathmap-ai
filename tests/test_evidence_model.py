"""Inspectable evidence boundaries: grouping, truncation and shared references."""
import copy
import unittest
from deathmap_ai.evidence_model import build_evidence, display_value, validate_evidence
from deathmap_ai.orcs_evidence_v6 import adapt


def observation(**updates):
    o={'source':{'name':'BioGRID ORCS','type':'screen','native_record_id':'16','native_url':'https://orcs.thebiogrid.org/Screen/16'},
       'supports':{'entity_type':'screen','entity_id':'SCR-0001','fields':['cell_line_reported']},
       'claim':'ORCS reports CELL_LINE = HCT 116.','supporting_value':'CELL_LINE=HCT 116',
       'raw_record':{'CELL_LINE':'HCT 116'},'evidence_basis':'structured_field','evidence_status':'direct'}
    o.update(updates);return o


class EvidenceTests(unittest.TestCase):
    def build(self,observations):
        return build_evidence(observations,run_id='fixture',profile_id='fixture-v02',profile_version=2)

    def test_grouping_preserves_field_values_and_provenance(self):
        a=observation();b=observation(supports={'entity_type':'screen','entity_id':'SCR-0001','fields':['enzyme_reported']},supporting_value='ENZYME=Cas9')
        rows,ledger=self.build([a,b,a]);self.assertEqual(len(rows),1)
        self.assertEqual(ledger[0]['supports'][0]['fields'],['cell_line_reported','enzyme_reported'])
        self.assertEqual(len(ledger[0]['observations']),3)
        self.assertEqual(ledger[0]['supporting_value_full'],['CELL_LINE=HCT 116','ENZYME=Cas9'])
        self.assertTrue(validate_evidence(rows,ledger))
        self.assertEqual(rows[0]['evidence_id'],self.build([b,a])[0][0]['evidence_id'])

    def test_inference_conflict_and_other_entity_never_merge(self):
        rows,_=self.build([observation(),observation(evidence_basis='inferred',evidence_status='inferred'),
            observation(evidence_status='conflicting'),observation(supports={'entity_type':'screen','entity_id':'SCR-0002','fields':['cell_line_reported']})])
        self.assertEqual(len(rows),4)
        with self.assertRaises(ValueError):self.build([observation(evidence_basis='inferred')])

    def test_truncation_is_display_only(self):
        full='α'*401;rows,ledger=self.build([observation(supporting_value=full)])
        self.assertEqual(len(rows[0]['supporting_value']),300)
        self.assertTrue(rows[0]['supporting_value'].endswith('[…]'))
        self.assertTrue(rows[0]['supporting_value_truncated'])
        self.assertEqual(ledger[0]['supporting_value_full'],full)
        self.assertEqual(display_value('a'*300),('a'*300,False))

    def test_reference_is_one_accession_with_two_ledger_targets(self):
        base=observation(source={'name':'Cellosaurus','type':'cell_line','native_record_id':'CVCL_0291','native_url':'https://www.cellosaurus.org/CVCL_0291'},
            supports={'entity_type':'cell_line','entity_id':'CVCL_0291','fields':['category']},evidence_basis='reference_lookup')
        a=copy.deepcopy(base);b=copy.deepcopy(base)
        a['annotation_targets']=[{'entity_type':'screen','entity_id':'SCR-0001'}]
        b['annotation_targets']=[{'entity_type':'screen','entity_id':'SCR-0002'}]
        rows,ledger=self.build([a,b]);self.assertEqual(len(rows),1)
        self.assertEqual(len(ledger[0]['annotation_targets']),2)
        self.assertNotIn('annotation_targets',rows[0])
        with self.assertRaises(ValueError):self.build([dict(base,evidence_basis='structured_field')])

    def test_v01_rejected(self):
        with self.assertRaises(ValueError):build_evidence([],run_id='x',profile_id='v01',profile_version=1)

    def test_publication_source_url_date_and_year_transform_preserved(self):
        p={'sheets':{'Publications':[{'publication_id':'PUB-0001','pmid':'123','title_original':'Example','publication_year':2020}],
            'Screens':[{'screen_id':'SCR-0001','publication_id':'PUB-0001','cell_line_reported':'unknown'}]},'roles':{'SCR-0001':{'SCREEN_ID':'16'}}}
        raw={'PUBLICATION_ID':'5','PMID':'123','TITLE':'Example','PUBLICATION_DATE':'2020-01-01',
            'PUBLICATION_URL':'https://orcs.thebiogrid.org/Dataset/5','RETRIEVED_AT':'2026-10-04T05:00:00Z','SOURCE_METADATA_FILE':'fixture.html','SOURCE_METADATA_SHA256':'fixture-hash'}
        _,ledger=adapt(p,[{'SCREEN_ID':'16','CELL_LINE':'unknown','SOURCE_TYPE':'pubmed','SOURCE_ID':'123'}],[raw],
            {'cell_lines':[]},{'run_id':'fixture'},{'profile_version':2,'profile_id':'fixture-v02'})
        e=next(e for e in ledger if e['supports'][0]['entity_type']=='publication')
        self.assertEqual(e['source']['native_url'],raw['PUBLICATION_URL'])
        self.assertEqual(e['source']['retrieved_at'],raw['RETRIEVED_AT'])
        self.assertEqual(e['observations'][0]['transformations'][0]['normalized'],2020)

    def test_orcs_adapter_keeps_reference_out_of_native_record(self):
        p={'sheets':{'Publications':[],'Screens':[{'screen_id':'SCR-0001','cell_line_reported':'HCT 116','source_evidence_ids':'old'},
            {'screen_id':'SCR-0002','cell_line_reported':'HCT116','source_evidence_ids':'old'}],
            'Sources & Evidence':[],'Discovery Resources':[]},'roles':{'SCR-0001':{'SCREEN_ID':'16'},'SCR-0002':{'SCREEN_ID':'17'}}}
        native=[{'SCREEN_ID':'16','CELL_LINE':'HCT 116'},{'SCREEN_ID':'17','CELL_LINE':'HCT116'}]
        refs={'retrieval_date':'2026-10-01','cellosaurus_version':'56.0','cell_lines':[
            {'value':'HCT 116','accession':'CVCL_0291','category':'Cancer cell line'},
            {'value':'HCT116','accession':'CVCL_0291','category':'Cancer cell line'}]}
        updated,ledger=adapt(p,native,[],refs,{'run_id':'fixture'},{'profile_version':2,'profile_id':'fixture-v02'})
        self.assertEqual(p['sheets']['Screens'][0]['source_evidence_ids'],'old')
        self.assertEqual(len(updated['sheets']['Evidence']),3)
        annotations=[e for e in ledger if e['source']['name']=='Cellosaurus']
        self.assertEqual(len(annotations),1);self.assertEqual(len(annotations[0]['annotation_targets']),2)
        self.assertEqual(updated['sheets']['Screens'][0]['cellosaurus_accession'],'CVCL_0291')
        orcs=[e for e in ledger if e['source']['name']=='BioGRID ORCS']
        self.assertTrue(all('annotation_targets' not in o for e in orcs for o in e['observations']))


if __name__=='__main__':unittest.main()
