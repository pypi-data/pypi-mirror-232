''' run tests to verify behavior of vectoring embedding-based matching'''

import os
import pandas as pd
import numpy as np
import sys
from warnings import warn

from rsidatasciencetools.config.baseconfig import YmlConfig
from rsidatasciencetools.datautils.datagen import gen_records_from_data
from rsidatasciencetools.datautils.formsource import gen_noisy_documents_from_records

# NOTE: struggling with pybind11 dependency requirement of
# `fasttext`; removing test for the sake of all the other tests
# that cannot run because of this failed dependency installation
EmbeddingMatchFT = build_scann_searcher = None
try:
    from rsidatasciencetools.datautils.matching_vectorembed import EmbeddingMatchFT, build_scann_searcher
except (ImportError, RuntimeError, ModuleNotFoundError):
    warn(f'missing dependency, can not run tests in {__file__}')
test_path = os.path.abspath(os.path.dirname(__file__))

def test_ft_run_embedding_model():
    if EmbeddingMatchFT is None:
        return
    df, yml_gen = gen_records_from_data(test_path, numrec=100, seed=42, 
                                        add_unique_label=True, as_df=True)

    form_recs, yml_gen = gen_noisy_documents_from_records(yml_gen, df,
        as_df=True, prob_e=0.02,seed=45,debug=0)
    
    df['taxid'] = df.taxid.apply(int)
    df['phoneno'] = df.phoneno.apply(
        lambda x: int(x) if isinstance(x, float) and not(np.isnan(x)) else -1)
    df['aptno'] = df.aptno.apply(
        lambda x: int(x) if isinstance(x, float) and not(np.isnan(x)) else -1)

    form_recs['taxid'] = form_recs.taxid.apply(int)
    form_recs['phoneno'] = form_recs.phoneno.apply(
        lambda x: int(x) if isinstance(x,(float,int)) and not(np.isnan(x)) else -1)
    form_recs['aptno'] = form_recs.aptno.apply(
        lambda x: int(x) if isinstance(x,(float,int)) and not(np.isnan(x)) else -1)
    # form_recs['birthday'] = form_recs.birthday.apply(pd.Timestamp)

    train_df, test_df = df, form_recs

    yml = YmlConfig(os.path.join(test_path, 'embed.yml'), debug=1, auto_update_paths=True)
    yml.setkeyvalue('quantize', build_scann_searcher is not None)
    
    emb_mdl = EmbeddingMatchFT(yml)
    emb_mdl.init_model(in_df=train_df,load=False,save=False, quantize=False)

    n_ret = 3
    query_hits, scores, runtimes = emb_mdl.find_nearest_records(
        test_df, n_return=n_ret, debug=2)

    for ii, qh, (_,row) in zip(range(len(query_hits)),query_hits,test_df.iterrows()):
        assert row.metric_id in qh.metric_id.values
        if ii > 3:
            break
    assert scores['total_found'] > 95, ('did not find expected number '
        f'of matches [{scores["total_found"]}] in the top {n_ret} hits')
    