import pandas as pd
import numpy as np
from os import path, remove

from rsidatasciencetools.datautils.matching_base import (
    MatchKey, MatchKeyGroup, MatchDataSource, MatchType, MatchOrder)
from rsidatasciencetools.datautils.formsource import gen_noisy_documents_from_records

fdir = path.dirname(path.abspath(__file__))


def test_base_matchkey():
    df = pd.read_csv(path.join(fdir,'lastnames_clean.csv'))
    name_match = MatchKey('brown', MatchType.name,
        pre_match=str.lower, datacols=['Name'])
    is_common = MatchKey(1e6, MatchType.data, datacols=['Count'],
        match_func=lambda x, m: x > m, 
        match_score=lambda x, m: min(0.5, (x - m)/m * 0.5) + 0.5)

    match_grp = MatchKeyGroup(matchkeys=[name_match,is_common])

    match = MatchDataSource('common-name-brown', matchrules=[match_grp])
    results = match.search_and_score(df)
    results.to_csv('./temp.csv',index=False)
    results = pd.read_csv('./temp.csv')
    remove('./temp.csv')
    check = pd.read_csv(path.join(fdir,'test_matching_output_names.csv'))
    assert (check.values == results.values).all(), 'verification of results failed'


def test_shortcut_matchkey_group_rule():
    ref_recs = pd.read_csv(path.join(fdir,'test_output_seed42.csv'))
    ref_recs['taxid'] = ref_recs.taxid.apply(int)
    ref_recs['birthday'] = ref_recs.birthday.apply(pd.Timestamp)
    # print('ref_recs:\n', ref_recs)
    form_recs, yml = gen_noisy_documents_from_records(fdir, ref_recs,
        as_df=True, prob_e=0.1,seed=45)

    form_recs['taxid'] = form_recs.taxid.apply(int)
    form_recs['birthday'] = form_recs.birthday.apply(pd.Timestamp)
    # form_recs should match what is in test_output_seed42.corrupted.csv    
    
    _, rec = next(ref_recs.iterrows())
    names = rec['compositename'].lower().split()

    names_match = [MatchKey(name, MatchType.name,
        pre_match=str.lower, datacols=[col]) 
        for name, col in zip(names, ['firstname','middlename','lastname'])]
    bday_match = MatchKey(rec['birthday'], MatchType.dob, 
        match_order=MatchOrder.secondary,
        match_func=lambda x,m: any(xx == mm for xx, mm in zip(
            (x.day, x.month, x.year),(m.day, m.month, m.year))), 
        match_score=lambda x,m: sum(xx == mm for xx, mm in zip(
            (x.day, x.month, x.year),(m.day, m.month, m.year)))/3.0, 
        datacols=['birthday'])
    id_match = MatchKey(rec['taxid'], MatchType.taxid, 
        match_order=MatchOrder.shortcut, 
        datacols=['taxid'])

    match_rules = [
        MatchKeyGroup(matchkeys=id_match),
        MatchKeyGroup(matchkeys=names_match),
        MatchKeyGroup(matchkeys=bday_match)]
    match = MatchDataSource('id_dob_name', matchrules=match_rules, debug=0)
    match_rules_no_id = [
        MatchKeyGroup(matchkeys=names_match),
        MatchKeyGroup(matchkeys=bday_match)]
    match_noid = MatchDataSource('dob_name', matchrules=match_rules_no_id, debug=0)

    results1 = match.search_and_score(ref_recs)
    results1['birthday'] = results1.birthday.apply(lambda x: f'{x.year}-{x.month:02d}-{x.day:02d}')

    results2 = match_noid.search_and_score(ref_recs) #form_recs)
    results2['birthday'] = results2.birthday.apply(str)
    try:

        results1.to_csv('./temp.csv',index=False)
        results = pd.read_csv('./temp.csv')
        check = pd.read_csv(path.join(fdir,'test_multi_matching_id.csv'))
        # assert (results == check).all().all()   # doesn't work for Nan vs. None
        for col in check.columns:
            for v1,v2 in zip(results[col].values.tolist(), check[col].values.tolist()):
                assert ((isinstance(v1,float) and np.isnan(v1) and 
                        isinstance(v2,float) and np.isnan(v2)) or v1==v2), (
                    f"for column: {col}: {v1} != {v2}")

        results2.to_csv('./temp.csv',index=False)
        results = pd.read_csv('./temp.csv')
        check = pd.read_csv(path.join(fdir,'test_multi_matching_name_dob.csv'))
        # assert (check == results).all().all()
        for col in check.columns:
            for v1,v2 in zip(results[col].values.tolist(), check[col].values.tolist()):
                assert ((isinstance(v1,float) and np.isnan(v1) and 
                        isinstance(v2,float) and np.isnan(v2)) or v1==v2), (
                    f"for column: {col}: {v1} != {v2}")
    except AssertionError as ae:
        remove('./temp.csv')
        raise ae
    else:
        remove('./temp.csv')
        
# if __name__ == '__main__':
#     test_shortcut_matchkey()