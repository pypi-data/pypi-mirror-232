''' code to build and run FastText-based transformer/embedding for sentence-embeddings

- digest papers (https://arxiv.org/abs/1803.11175, https://arxiv.org/abs/1908.10396v5)
- find relevant code in google-research/scann
- implement parser to grab data from reference and target records
- histogram the similarity scores to see what threshold usually correspond to a highly certain match
- compare to base matching
DONE^

- add quantization (query sort order -aware reduction of model size and increase in speed)
- autotune-able (hyperparameter search - may not be possible with unsupervised approach)

'''
import argparse
import logging
import time
from typing import Union

import os
from time import time
from copy import deepcopy

import numpy as np
import pandas as pd
from warnings import warn

from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig
from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.config.baseconfig import YmlConfig, log_level_dict
from rsidatasciencetools.mlutils.text import get_text_data_from_records

import logging
from rsidatasciencetools.azureutils import az_logging

build_scann_searcher = None
try:
    from rsidatasciencetools.mlutils.scann import build_scann_searcher
except ImportError:
    warn('unable to import scann functions and modules, canno perform quantized querying')

logger = az_logging.get_az_logger(__name__)


try:
    import fasttext as ft
except (ImportError,ModuleNotFoundError):
    from subprocess import Popen, SubprocessError
    warn('Could not find "fasttext", attempting to install...')
    try:
        install_missing = Popen("python -m pip install fasttext", shell=True).wait()
    except (SubprocessError,ModuleNotFoundError):
        raise ImportError('could not install missing "fasttext" via subprocess')
    import fasttext as ft


embed_model = None

ft_embed_defaults = dict(
    embedding_model='rec_embed',
    embed_dim=100,
    minn=3,
    maxn=6,
    char_ngrams_only=True,
    shuffle=False,
    merge_fields=[
        'compositename',
        'maidenname',
        'birthday',
        'taxid',
        'compositeaddress']
)


def get_ft_embed_model_params(yml, ext='model', **kwargs):
    ''' merge parameters from yml config and kwargs
        (and update the config where params are missing)
        returns a full-path model_name which includes the model extension

        returns:
            model_path_name, yml_updated, embed_dim, char_ngrams_only, 
            minn, merge_fields
    '''
    yml = deepcopy(yml)
    params = {}
    for k in ['embedding_model', 'embed_dim', 'minn', 'maxn', 
              'char_ngrams_only', 'merge_fields']:
        # use settings to determine whether to use a parameter, 
        # override if set in arguments
        if kwargs.get(k, None) is None:
            params[k] = yml.get(k, ft_embed_defaults[k])
        else:
            params[k] = kwargs[k]

        if k not in yml:
            yml.setkeyvalue(k, params[k])
    return_values = tuple([params[k] 
        for k in ['embed_dim', 'char_ngrams_only', 'minn', 'merge_fields']])            
    params.update({k:str(params[k]) for k in [
        'embedding_model', 'embed_dim']})

    params['minn'] = f'minn-{params["minn"]}'
    params['char_ngrams_only'] = f'ch_ngram-{params["char_ngrams_only"]}'
    params['merge_fields'] = '-'.join(params['merge_fields'])            

    if os.path.sep not in params['embedding_model']:
        params['embedding_model'] = os.path.join(yml.primary_path, 
            params['embedding_model'])

    return '.'.join([*[params[k] for k in ['embedding_model','embed_dim','minn',
        'char_ngrams_only', 'merge_fields']],ext]), yml, *return_values


def build_fasttext_record_embedding(
        yml=os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'tests/embed.yml'),
        in_df=None,
        embed_dim=None,
        minn=None,
        char_ngrams_only=None,
        override_model_name=None,
        shuffle=False,
        load=None,
        save=False,
        merge_fields=None,
        use_all_data=True,
        leave_training_file=False,
        debug=1,
        **kwargs):
    '''
        Args:
            yml (path or YmlConfig object)
            in_df=None,
            embed_dim=None, default of 100 will be set from 
                'ft_embed_defaults' (above in this file)
            minn=None, default of 3
            char_ngrams_only=None, default of True 
            override_model_name=None, default of 'rec_embed'
            shuffle=False,
            load=None, if model_name file exist, will be set to True (if 
                incoming is None)
            save=False,
            merge_fields=None, default of ['compositename','maidenname',
                'birthday','taxid','compositeaddress']
            use_all_data=True,
            debug=1,

        Returns:
            yml             the embedding configuration, updated 
                            where params were missing)
            emb_model       the FastText embedding model
            full_dataset    (pd.DataFrame) the complete dataset 
                            preprocess/extracted textual data
    '''
    logger.setLevel(log_level_dict[debug])
    
    logger.debug('build_fasttext_record_embedding args:' 
        'embed_dim:',embed_dim,
        'minn:',minn,
        'char_ngrams_only:',char_ngrams_only,
        'override_model_name:',override_model_name,
        'shuffle:',shuffle,
        'load:',load,
        'save:',save,
        'merge_fields:',merge_fields,
        'use_all_data:',use_all_data,
        'debug:',debug,'other kwargs:', kwargs)
    
    if not(isinstance(yml,YmlConfig)):
        yml = YmlConfig(yml, auto_update_paths=True)

    if override_model_name is not None and (os.path.sep not in 
                                            override_model_name):
        logger.warning(f'updated override model name: {override_model_name}')
    else:
        override_model_name = None
    _, DATASET_SIZE, full_dataset, train_examples, val_examples, test_examples \
            = get_text_data_from_records(
            yml, in_df=in_df, as_df=True, shuffle=shuffle, 
            merge_fields=merge_fields, debug=max(0,debug-1), 
            preprocess=lambda x: x.replace(';','').replace('-',' '
                                ).replace('"',' ').replace('#','apt ').lower())
    logger.debug(full_dataset.head())

    st = time()
    # update the model filename/path and the model parameters
    model_name, yml, embed_dim, char_ngrams_only, minn, merge_fields =\
        get_ft_embed_model_params(yml, 
            embedding_model=override_model_name, embed_dim=embed_dim,
            char_ngrams_only=char_ngrams_only,minn=minn,merge_fields=merge_fields)
    if save:
        yml.setkeyvalue('saved_model_filename',os.path.splitext(os.path.split(model_name)[-1])[0])
    if load is None:
        load = os.path.exists(model_name)
        load and logger.warning('"load" not specified, but found matching model '
                       'name - attempting load')
    if load:
        if not(os.path.exists(model_name)):
            raise FileNotFoundError('could not find Embedding Model file for '
                                    f'settings provided: {model_name}')
        emb_model = ft.load_model(model_name)
        logger.warning(f'embedding model loaded from: {yml["embedding_model"]} '
                            f'with filename: {model_name}')
    else:
        if use_all_data:
            full_dataset.sentence_data.to_csv('./records.all', 
                header=False, index=False)
        else:
            train_examples.sentence_data.to_csv('./records.all', 
                header=False, index=False)
        # update the FT embedding model training parameters
        for k,v in dict(minn=minn, dim=embed_dim).items():
            if k not in kwargs or kwargs[k] is None:
                kwargs[k] = v
        if char_ngrams_only:
            kwargs.update(dict(
                minCount=full_dataset.shape[0], maxn=kwargs['minn']    
            ))
        # remove kwargs not associated with FastText embedding call
        kwargs = {k:v for k,v in kwargs.items() if k in [
                'input', 'model', 'lr', 'dim', 'ws', 'epoch', 'minCount',
                'minCountLabel', 'minn', 'maxn', 'neg', 'wordNgrams', 'loss', 'bucket',
                'thread', 'lrUpdateRate', 't', 'label', 'verbose', 'pretrainedVectors']}
        logger.debug(f'embedding model train parameters: {kwargs}')
        emb_model = ft.train_unsupervised('./records.all', **kwargs)
        logger.warning(f'embedding model train time: {time() - st:.4f} '
                            'seconds')
    
    if save and not(load):
        emb_model.save_model(model_name)
        logger.warning(f'saving FT embedding model to: {model_name}')

    try:
        leave_training_file or os.remove('./records.all')
    except FileNotFoundError:
        pass

    return yml, emb_model, full_dataset


class EmbeddingMatchFT(object):
    ''' EmbeddingMatchFT
        Wraps the FastText unsupervised embedding model train and inference 
    '''
    def __init__(self, yml:Union[os.PathLike,YmlConfig], debug:int=0) -> None:
        self.yml = yml
        self.debug = debug
        self.emb_model = self.model_data = self.embedding_data = \
            self.embedding = None

    def init_model(self, **kwargs):
        _kwargs = {k:v for k,v in kwargs.items() if k not in ['debug', 'quantize']}
        debug = self.debug if 'debug' not in kwargs else kwargs['debug']
        assert 'dbconfig' in self.yml, 'no database configuration file specified in yml config'
        st = time()
        self.yml, self.emb_model, self.model_data = \
            build_fasttext_record_embedding(
                yml=self.yml, debug=max(0, debug - 1), **_kwargs)
        assert self.yml['char_ngrams_only'], ('character n-grams must be used '
            'for accurate record matching - this is not a language problem '
            '(whole words), but rather a problem of recognizing partial '
            'records which may have been corrupted')

        # NOTE: since the embedding model only recognizes character n-grams, 
        # it will not store the embeddings of long record texts/sentences, 
        # thus we must extract the averaged embedding vector for the variable 
        # length text segment
        embeddings = self.model_data.sentence_data.apply(
            self.emb_model.get_sentence_vector)

        kvalcols = [('description', 'sentence_data')]
        if 'metric_id' in self.model_data:
            kvalcols.append(('metric_id', 'metric_id'))
        d = {k: self.model_data[valk].values for k, valk in  kvalcols}
        d.update({f'embed_{i}': embeddings.apply(lambda x: x[i]).values 
                for i in range(embeddings.loc[0].size)})
        self.embedding_data = pd.DataFrame(d)
        logger.debug(self.embedding_data.head(2))
        embed_cols = [k for k in self.embedding_data.columns 
            if k.startswith('embed')]
        self.embedding = self.embedding_data[embed_cols].values
        self.embedding_data = self.embedding_data[[c 
            for c in self.embedding_data.columns if (c not in embed_cols)]]

        if kwargs.get('quantize',False) or (('quantize' not in kwargs) and 
                self.yml and self.yml.get('quantize',False)):
            # Anisotropic quantization as described in the paper; see 
            # header information in rsidatasciencetools/mlutils/scann.py
            if build_scann_searcher is None:
                raise ImportError('unable to import the required ScANN module functions')
            scann_params = {k.strip('scann_'):  v 
                for k,v in self.yml.items(contains=['scann'])}
            self.quantz_searcher, self.quantz_yml = build_scann_searcher(
                self.embedding, yml=scann_params, debug=max(0,debug-1))
        else:
            self.quantz_searcher, self.quantz_yml = None, None
        logger.debug(f'Embedding Model initialization time: {time()-st:.3f} seconds')
            
    def get_embed_tablename(self, embedtable=None, sqlcfg=None):
        sqlcfg = SQLConfig(self.yml['dbconfig'],debug=max(self.debug-1,0),
            auto_update_paths=True) if sqlcfg is None else sqlcfg

        assert 'embedtable' in sqlcfg or embedtable is not None, (
            'no "embedtable" parameter provided to which the embedding ' 
            'data should be written')
                
        return (sqlcfg['embedtable'] if embedtable is None 
            else embedtable) + ('__' + self.yml['saved_model_filename']
            if 'saved_model_filename' in self.yml else '')

    def write_embedding_data_to_db(self, embedtable=None):
        emb_to_write = self.embedding_data.copy()
        emb_df = pd.DataFrame({f'embed_{col}': self.embedding[:,col] 
                               for col in range(self.embedding.shape[1])})
        emb_to_write = emb_to_write.join(emb_df)
        assert emb_to_write.shape[0] == self.embedding.shape[0], ('embedding '
            'dataset to write: mismatched number of rows')
        assert 'dbconfig' in self.yml, ('could not find a "dbconfig" config '
            'file url')
        sqlcfg = SQLConfig(self.yml['dbconfig'],debug=max(self.debug-1,0),
                           auto_update_paths=True)
        db = DbConnectGenerator(config=sqlcfg,debug=max(self.debug-2,0))
        embedtable = self.get_embed_tablename(embedtable, sqlcfg)
        with db.gen_connection() as conn:
            rows_modified = emb_to_write.to_sql(
                embedtable, 
                if_exists='replace', con=conn.connection)
        logger.debug(f'wrote {rows_modified} of '
            f'{emb_to_write.shape[0]} to table: {embedtable}')
        del db

    def find_nearest_records(self, df_or_text:Union[pd.DataFrame,str], 
                             n_return=10, thres=0.015, as_records=False, debug=0):
        '''
        find_nearest_records

        Args:
            df_or_text:Union[pd.DataFrame,str]  data with yml['merge_fields'] as 
                columns (one or more rows), or single line of text (as str or 
                column of DataFrame with column label 'sentence_data') 
            n_return=10 (int)   number of potential matches to return        
            debug=0 (int)       the debug level
        
        Returns:
            (debug = 0) 
                query_hits

            (debug > 1)
                query_hits, score_distb, runtimes 
            (debug > 2)
            query_hits, score_distb, runtimes, proc_data, example_non_match 
        '''
        debug = max(self.debug, debug)
        assert n_return > 0, 'number of query_hits to return must be positive'
        if isinstance(df_or_text, pd.DataFrame):
            N = df_or_text.shape[0]
            if 'sentence_data' not in df_or_text:
                data = get_text_data_from_records(self.yml, 
                    in_df=df_or_text, as_df=True,
                    shuffle=False, 
                    merge_fields=self.yml['merge_fields'], 
                    debug=max(debug-2,0))
            else:
                data = df_or_text
            if N > 1:
                data = data[2]
        else:
            N = 1
            data = pd.DataFrame({'sentence_data':[df_or_text]})
        st_all = st = time()
        query_emb_vecs = data.sentence_data.apply(
            self.emb_model.get_sentence_vector)
        total_rt = time() - st
        query_hits = [None] * N
        M = self.embedding_data.shape[0]
        if debug > 2:
            example_non_match = pd.DataFrame(dict())
        scores = np.zeros(M)  # number of previously seen embedding vectors
        if debug > 1:
            score_distb = dict(best=np.zeros(M,dtype=np.float16), 
                            middle=np.zeros(M,dtype=np.float16),
                            total_found=0)
        has_tqdm = None
        if debug:
            found_topN = 0
            has_metric_ids = ('metric_id' in data) and (
                'metric_id' in self.embedding_data)

            # for a lot of vectors (and if debug is on), show the progress
            if (debug > 1 and N >= 100) or debug > 2:
                try:
                    from tqdm import tqdm
                    progress = tqdm(total=N)
                    update_step = int(max(1,N/200 if N > 200 else N/3))
                    has_tqdm = True
                except ImportError:
                    pass
        if self.quantz_searcher is not None:
            runtimes = None

            queries = query_emb_vecs.to_list()
            ratio = max(1.0,float(n_return) / self.quantz_yml['num_neighbors'])
            leaves_to_search, pre_reorder_num_neighbors, final_num_neighbors = \
                int(self.quantz_yml['num_leaves_to_search'] * ratio), \
                    int(self.quantz_yml['reordering_num_neighbors'] * ratio), \
                        n_return
            st = time()
            if N > 1:
                neighbors, scores = self.quantz_searcher.search_batched(queries, 
                    final_num_neighbors=final_num_neighbors,
                    leaves_to_search=leaves_to_search, 
                    pre_reorder_num_neighbors=pre_reorder_num_neighbors)
            else:
                neighbors, scores = self.quantz_searcher.search(queries[0],  
                    final_num_neighbors=final_num_neighbors,
                    leaves_to_search=leaves_to_search, 
                    pre_reorder_num_neighbors=pre_reorder_num_neighbors)
            total_rt = dict(convert_text_to_embeddings=total_rt,
                            scann_search=time() - st)

            assert ((N == 1 and neighbors.shape[0] == n_return) or 
                        neighbors.shape[0] == N), (
                f'number of returned "neighbors"({neighbors.shape[0]}) '
                f'queries mismatched from number of data rows ({N})')
            if debug > 1:
                score_distb.update(n_return=np.zeros(M,dtype=np.float16))
            # convert to numpy for the final analysis and storage of the neighbor search
            neighbors, scores = neighbors.numpy(), scores.numpy()
            if len(neighbors.shape) == 1:
                neighbors, scores = np.expand_dims(neighbors, axis=0), \
                    np.expand_dims(scores, axis=0)

            st = time()
            for set_idx, (r,row) in zip(range(N),data.iloc[:N].iterrows()):
                n = min((scores[set_idx,:n_return] >= thres).sum(), n_return)
                matches = self.embedding_data.iloc[neighbors[set_idx,:n]].copy()
                matches['neigh_index'] = neighbors[set_idx,:n].copy()
                matches['score'] = scores[set_idx,:n]
                matches.reset_index()
                query_hits[set_idx] = matches
                
                if debug:
                    if debug > 1:
                        score_distb['best'][set_idx] = scores[set_idx,0]
                        score_distb['middle'][set_idx] = scores[set_idx,int(n_return/2)]
                        score_distb['n_return'][set_idx] = scores[set_idx,-1]
                    if has_metric_ids:
                        found = row.metric_id in self.embedding_data.iloc[
                            neighbors[set_idx,:n]].metric_id.values

                        # assert self.embedding_data.iloc[idx[:n]
                        #     ].metric_id.values == matches.metric_id.values

                        found_topN += int(found)
                        if (debug > 3 and not(found) and 
                                example_non_match.shape[0] < 10):
                            example_non_match = pd.concat(
                                [example_non_match,pd.DataFrame({
                                k:[v] for k,v in zip(['desc','metric_id'],row)})])

                    if has_tqdm and np.mod(set_idx,update_step) == 0:
                        progress.update(update_step)
                        if has_metric_ids:
                            progress.set_description(
                                'Catloging query matches | found fraction:'
                                f'{found_topN/(1+set_idx):.3f}')
                        else:
                            progress.set_description('Cataloging query matches')                            

            total_rt['catalog_query_matches'] = time() - st
            logger.warning('Get embeddings + SCANN query time: '
                f'{total_rt["convert_text_to_embeddings"]:.3g}sec + '
                f'{total_rt["scann_search"]:.3g}sec, '
                f'total per record: {(total_rt["convert_text_to_embeddings"]+total_rt["scann_search"])/N/1e3:.4g}ms'
                f' | catalogging time: {total_rt["catalog_query_matches"]:.2f}sec')
            total_rt = total_rt["convert_text_to_embeddings"] + total_rt["scann_search"]
            
        else:
            # standard (non-quantized) retrieval
            runtimes = total_rt/N * np.zeros(N, dtype=np.float16)
            total_rt = 0.

            iterate_rows = zip(range(N),data.iloc[:N].iterrows(), query_emb_vecs)

            if debug > 1:
                score_distb.update(last=np.zeros(M,dtype=np.float16))

            for ii, (_,row), _emb_vec in iterate_rows:
                st = time()
                scores[:] = self.embedding.dot(_emb_vec)
                idx = np.argsort(-scores)
                runtimes[ii] += time() - st

                if debug > 1:
                    score_distb['best'][ii] = scores[idx[0]]
                    score_distb['middle'][ii] = scores[idx[9]]
                    score_distb['last'][ii] = scores[idx[-1]]
                # NOTE: limit matches to those above a certain threshold, 
                # i.e., don't just match incoming before-unseen data to 
                # random records in the embedding
                n = min((scores[idx[:n_return]] >= thres).sum(), n_return)
                matches = self.embedding_data.iloc[idx[:n]].copy()
                matches['neigh_index'] = idx[:n].copy()                
                matches['score'] = scores[idx[:n]]
                matches.reset_index()
                query_hits[ii] = matches

                if debug:
                    if has_metric_ids:
                        found = row.metric_id in self.embedding_data.iloc[
                            idx[:n]].metric_id.values

                        # assert self.embedding_data.iloc[idx[:n]
                        #     ].metric_id.values == matches.metric_id.values

                        found_topN += int(found)
                        if (debug > 3 and not(found) and 
                                example_non_match.shape[0] < 10):
                            example_non_match = pd.concat(
                                [example_non_match,pd.DataFrame({
                                k:[v] for k,v in zip(['desc','metric_id'],row)})])
                    total_rt += runtimes[ii]
                    if has_tqdm and np.mod(ii,update_step) == 0:
                        progress.update(update_step)
                        if has_metric_ids:
                            progress.set_description(
                                'Record matching | found fraction:'
                                f'{found_topN/(1+ii):.3f} (avg rt: '
                                f'{total_rt/(ii+1):.3g}s)')
                        else:
                            progress.set_description('Record matching | '
                                f'avg rt: {total_rt/(ii+1):.3g}s')
        if debug and has_metric_ids:
            score_distb['total_found'] = found_topN
        has_metric_ids and logger.warning(
            f'Record matching performance: found {found_topN} of {N} to be '
            f'contained in the first {n_return} similar records via MIP '
            f'on embedding vectors with threshold: {thres:.3f}')
        logger.warning(f'Record matching runtime: {total_rt:.3f} seconds for '
            f'{N} records' + (f' (avg: {total_rt/N:.3g} sec)' if N > 1 else '') + 
            f'(total runtime with overhead: {time()-st_all:.2f}s)')

        if n_return == 1:
            for ii in range(N):
                query_hits[ii] = query_hits[ii].to_dict('records')[0]
        elif as_records:
            for ii in range(N):
                query_hits[ii] = query_hits[ii].to_dict('records')

        if len(query_hits) == 1:
            query_hits = query_hits[0]

        if debug > 1:
            if debug > 2:
                return query_hits, score_distb, runtimes, data, example_non_match
            else:
                return query_hits, score_distb, runtimes
        else:
            return query_hits

def main_embed_call(config:Union[str,YmlConfig],text_or_df:Union[str,pd.DataFrame]=None,
                    reload:bool=False,check_model:bool=False,shell_query:str=None,debug:int=0, 
                    **kwargs):
    ''' main function for calling embedding train / search from command line'''
    global embed_model
    if check_model:
        return embed_model is not None
    if isinstance(config, YmlConfig):
        yml = config
    else:
        yml = YmlConfig(config,base_str='match', 
            auto_update_paths=True,debug=max(debug-1,0))

    kwargs.update(dict(debug=debug))
    search = (text_or_df is not None) or (shell_query is not None)
    if embed_model is None or reload:
        embed_model = EmbeddingMatchFT(yml)
        if 'load' not in kwargs:
            kwargs.update(dict(load=None))
        embed_model.init_model(**kwargs)
        if kwargs.get('write_to_db', False):
            embed_model.write_embedding_data_to_db(
                embedtable=yml.get('embedtable','embedding_vectors'))
    if search:
        _n_return = (yml.get('n_return', 10) if kwargs.get('n_return', None) is None
            else kwargs.get('n_return', None))
        if shell_query is not None:
            if ':' in shell_query and ';' in shell_query:
                d = {el.split(':')[0].strip(): el.split(':')[1].strip()
                    for el in shell_query.split(';') if len(el.split(':')) == 2}
                assert all(k in yml['merge_fields'] for k in d.keys()), 'input data keys not in search key set'
                d = {k: [d.get(k,None)] for k in yml['merge_fields']}  # fill in missing data with None
                text_or_df = pd.DataFrame(d)
                logger.debug(f'parsed dictionary:\n {text_or_df}')
            else:
                text_or_df = shell_query
        return embed_model.find_nearest_records(text_or_df, n_return=_n_return,
            thres=kwargs.get('thres',0.015), as_records=kwargs.get('as_records', False), debug=debug)
    return yml


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
    description='''
generate fake name/record data with deviations for matching algorithm dev
        
example call:
    python datagen.py --data-dir ./tests/MD_rec_gen.yml --add-unique-label --numrec 100000 --write-to-db
''')
    parser.add_argument('--config-dir' ,'-c', dest='config', 
        nargs='?', required=False, default=None, 
        help='directory containing embedding and matching configuration file')
    parser.add_argument('--shell-query' ,'-q', dest='shell_query', 
        nargs='?', required=False, default=None, 
        help='''test query, need to be structured similar to: "compositename: fredrick philip stephens; 
maidenname: null; birthday: 1959 04 01; taxid: 844323683;  compositeaddress: 123 Main St, Frederick, MD"
so that the data can be appropriately split up, or just the string with no ":" or ";"s.''')
    parser.add_argument('--debug', '-d', nargs='?', type=int, required=False, const=1, 
        default=0, help='level of debug output printing')
    parser.add_argument('--write-to-db', nargs='?', dest='write_to_db', 
        type=bool, const=True, default=False, required=False, 
        help='whether to write the embedding vectors to DB table, default is False')
    parser.add_argument('--save', '-s', nargs='?', type=bool, required=False, const=True, 
        default=False, help='whether to save embedding model')
    parser.add_argument('--load', '-l', nargs='?', 
        type=int, required=False, const=1, default=None, 
        help=('whether to attempt to load model from previously saved model '
              '(using filename from yml config with auto-updated path); '
              'not provided=choose automatically if matching model file found,'
              '1=load model, 0=skip load'))
    parser.add_argument('--n-return', '-n', dest='n_return', nargs='?', 
        type=bool, required=False, default=None, 
        help=('when building the more efficient quantized ScaNN embedding, knowing '
        'the number of returns items requested affects how the model is built/configured, ' 
        'by default uses the value in the YML mnatching config'))
    parser.add_argument('--thres', '-t', 
        type=float, required=False, default=0.015,
        help=('the lower threshold for inner-product matches'))

    args = parser.parse_args()
    logger.setLevel(log_level_dict[args.__dict__['debug']])
    logger.info("args:", args.__dict__)

    # call primary embedding functionality
    yml_or_queriedRecs = main_embed_call(**args.__dict__)
    
    found = None
    if isinstance(yml_or_queriedRecs,tuple):
        found = yml_or_queriedRecs[0]
    elif isinstance(yml_or_queriedRecs, (dict, pd.DataFrame)):
        found = yml_or_queriedRecs
    if found is not None:
        logger.critical(f'search results:\n {found}')
