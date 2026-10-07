"""Shared ORCS reported-field mapping and narrow technology crosswalks.

These transformations describe source metadata, not study eligibility or screen
group membership. Preserve the native values alongside normalized fields.
"""
DIRECT = {'SCREEN_NAME':'screen_name_reported','METHODOLOGY':'methodology_reported',
 'ENZYME':'enzyme_reported','LIBRARY':'library_name_reported','LIBRARY_TYPE':'library_type_reported',
 'CELL_LINE':'cell_line_reported','ORGANISM_OFFICIAL':'organism_reported',
 'CONDITION_NAME':'condition_name_reported','CONDITION_DOSAGE':'condition_dosage_reported',
 'DURATION':'duration_reported','PHENOTYPE':'phenotype_original','ANALYSIS':'statistical_analysis_reported'}
CROSSWALKS={'SCREEN_FORMAT':{'Pool':'pooled','Array':'arrayed'},
            'METHODOLOGY':{'Knockout':'CRISPR knockout'}}
