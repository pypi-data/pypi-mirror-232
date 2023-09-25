''' Implements the existing (base) matching approach

    - first attempt to match on a 'shortcut' key - only if known unique identifier (e.g., from legacy DB)
    - primary key match - whole word/sequence match (ID, name, address, not just zip or street name or number) - majority of weight on primary key match
    - secondary key match - expensive to run, only run if primary key is matched first - weight is much less that primary key

    - keys are grouped - and only the best match is reported per group (instead of aggregated)

    Match key specifications:
        *      Name – A unique value that identifies the match key.

        *      Match Key Group – A value that identifies the category into which the match key falls. For example, all match keys dealing with the entity name would fall into the “Names” match key group.

        *      Sequence Number – this value is used to correlate the match key to the A&G run results and potentials output. Each sequence number identifies which match key bucket stores a value in the AG_RUN_RESULTS or AG_POTENTIALS tables.

        *      Hit Weight – this is a score, weighted to the relative value of this match key against the other match keys entered in the A&G rule configuration.

        *      Match Key Type – this will be one of Shortcut, Primary, or Secondary. This value indicates which AIFs and which taxpayer portfolios are evaluated, and how the total score for an AIF-entity pair is evaluated.
'''
import pandas as pd
import numpy as np
from copy import deepcopy
from difflib import SequenceMatcher
from typing import List, Union, Callable
from enum import Enum, auto

import logging
from rsidatasciencetools.azureutils import az_logging
from rsidatasciencetools.config.baseconfig import log_level_dict

logger = az_logging.get_az_logger(__name__)


class MatchOrder(Enum):
    shortcut = auto()
    primary = auto()
    secondary = auto()

class MatchType(Enum):
    taxid = auto()
    name = auto()
    dob = auto()
    address = auto()
    phone = auto()
    data = auto()



class MatchKey(object):
    def __init__(self, match_data, match_type:MatchType, 
            match_order:MatchOrder=MatchOrder.primary, 
            multimatch:str='any', score_accuml:str='max',
            pre_match:Callable=lambda x:x, 
            match_func:Callable=lambda x,m: (str(m) in str(x)) or (
                str(m)[1:] in str(x)) or (str(m)[:-1] in str(x)), 
            match_score:Callable=lambda x,m: max([float(str(m) in str(x)), 0.8*float(
                str(m)[1:] in str(x)), 0.8*float(str(m)[:-1] in str(x))]), 
            datacols:Union[None,List[str]]=None, debug=0) -> None:
        '''
            match_data
            match_order:MatchOrder=MatchOrder.primary
            multimatch:str=any
            match_func:Callable=lambda x,m: m in x
            match_score:Callable=lambda x,m: float(m in x)
            datacols:Union[None,List]=None
        '''
        self.match_data = (match_data 
            if isinstance(match_data,list) else [match_data])
        self.match_type = match_type
        self.match_order = match_order
        self.multimatch = multimatch
        self.score_accuml = score_accuml
        assert multimatch in ['all', 'any'], (
            'multimatch must be one of ["all", "any"]')
        assert score_accuml in ['mean', 'max', 'sum'], (
            'score_accuml must be one of ["mean", "max", "sum"]')
        self.raw_match_func_score = (match_func, match_score)
        self.match_func, self.match_score = None, None
        self.pre_match = pre_match
        self._type = (type(md) for md in self.match_data)
        self.datacols = datacols if isinstance(datacols,list) else [datacols]
        self.debug = debug
        logger.setLevel(log_level_dict[self.debug])
        self.setup_match_scoring()
    
    def __repr__(self) -> str:
        return (self.__class__.__name__ + 
            f'[{self.match_type},{self.match_order},{self.score_accuml},{self.multimatch}]: ' + 
            ('' if self.pre_match is None else f'(pre_match: {self.pre_match}), ') +
            f'match:{self.match_func}, score:{self.match_score}, ' +
            f'match_data: {self.match_data}' + 
            ('' if self.datacols is None else f' (cols:{self.datacols})')
        ) 

    def setup_match_scoring(self, match_data=None, set_match_data_rec=None):
        ''' repopulate the match and score functions given the matching data'''
        if match_data is None:
            if set_match_data_rec is not None and all(dc in set_match_data_rec 
                    for dc in self.datacols):
                self.match_data = [set_match_data_rec[dc] for dc in self.datacols]
            match_data = self.match_data
        elif not(isinstance(match_data,list)):
            match_data = [match_data]
        if self.datacols:
            assert len(self.datacols) == len(match_data), "match_data and datacols must have the same length"
        if self.match_order != MatchOrder.shortcut:
            self.match_func = lambda x: self.raw_match_func_score[0](x, *match_data)
            self.match_score = lambda x: self.raw_match_func_score[1](x, *match_data)
    
    def compare(self,data:Union[pd.DataFrame,pd.Series,list,np.ndarray]):
        '''return a boolean representation potentiatial matches'''
        if not(isinstance(data,(pd.DataFrame,pd.Series))):
            data = pd.Series(data)
        isDF, isSeries = isinstance(data,pd.DataFrame), isinstance(data,pd.Series)
        isShortcut = self.match_order == MatchOrder.shortcut
        if ((isDF and ((self.datacols is not None) or 
                data.shape[1] == 1)) or isSeries):
            # assert score.shape[0] == data.shape[0], 'reference '
            if self.pre_match:
                if isDF and len(self.datacols):
                    for col in self.datacols:
                        data[col] = data[col].apply(self.pre_match)
                else:
                    data = data.apply(self.pre_match)
            if isSeries:
                rtn = (data.values == self.match_data[0] if isShortcut 
                    else data.apply(self.match_func))
                score = (np.ones(rtn.sum(),dypte=np.float16) if isShortcut
                    else data[rtn].apply(self.match_score).values)
                logger.info(f'series: rtn={rtn} ({rtn.shape}), score={score} ({score.shape})')
                return rtn.values, score
            if self.datacols:
                score = np.zeros(data.shape[0],dtype=np.float16)
                nmatches = (np.zeros(data.shape[0],dtype=np.int16) 
                    if self.score_accuml == 'mean' else None)
                for itr, col in enumerate(self.datacols):
                    isShortcut and logger.info('shortcut compare:', 
                            data[col].values, type(data[col].values), 
                            self.match_data[itr], type(self.match_data[itr]),
                            data[col].values == self.match_data[itr])
                    _rtn = (data[col].values == self.match_data[itr] 
                        if isShortcut else data[col].apply(self.match_func).values)
                    rtn = _rtn if itr == 0 else (
                        rtn | _rtn if self.multimatch == 'any' else rtn & _rtn)
                    scr = (np.ones((1 if not(isinstance(rtn,(np.ndarray,list))) else rtn.sum()),dtype=np.float16) if isShortcut 
                        else data[_rtn][col].apply(self.match_score).values)
                    if nmatches is not None:
                        nmatches[_rtn] += 1
                    if itr == 0:
                        score[_rtn] = scr
                    elif self.multimatch == 'any' or self.score_accuml == 'max':
                        score[_rtn] = np.maximum(scr,score[_rtn])
                    elif self.score_accuml in ('mean','sum'):
                        score[_rtn] += scr
                    else:
                        raise ValueError('unknown option for combining matching results')
                if (len(self.datacols) > 1) and self.score_accuml == 'mean':
                    score[rtn] /= nmatches[rtn]
                logger.debug(f'DF multi col: rtn={rtn} ({rtn.shape}), '
                                         f'score={score} ({score.shape})')
                return rtn, score[rtn]
            if len(data.shape) == 1:
                rtn = (data.values[:,0] == self.match_data[0] if isShortcut
                    else data.apply(self.match_func).values[:,0])
                score = (np.ones(rtn.sum(),dypte=np.float16) if isShortcut
                    else data[rtn].apply(self.match_score).values)
                logger.debug(f'DF 1-col: rtn={rtn} ({rtn.shape}), '
                                         f'score={score} ({score.shape})')
                return rtn, score
        else:
            raise TypeError('untranslatable input type OR unable to convert '
                'input data to one-dimensional data vector OR '
                'other selectors variables insufficient to reduce data')


class MatchKeyGroup(object):
    def __init__(self,matchkeys=List[MatchKey],
            multimatch:str='any', score_accuml:str='max',
            group_weight=1.0) -> None:
        self.matchkeys = matchkeys if isinstance(matchkeys,list) else [matchkeys]
        assert len(set([mk.match_order for mk in self.matchkeys])) == 1, (
            "should only have one unique MatchOrder type")
        self.match_order = self.matchkeys[0].match_order
        self.group_weight = group_weight
        self.multimatch = multimatch
        self.score_accuml = score_accuml
        assert multimatch in ['all', 'any'], (
            'multimatch must be one of ["all", "any"]')
        assert score_accuml in ['max', 'sum'], (
            'score_accuml must be one of ["mean", "max", "sum"]')

    def __repr__(self) -> str:
        return (self.__class__.__name__ + 
            f'[{self.match_order},{self.score_accuml},{self.multimatch},{self.group_weight}]\n   ' + 
            '\n   '.join(repr(mk) for mk in self.matchkeys)
        ) 

    def run_compare_and_score(self, 
            data, scores:Union[None,np.ndarray], 
            return_data:bool=False):

        for i, mk in enumerate(self.matchkeys):
            _rtn, score = mk.compare(data)
            if i == 0:
                rtn = _rtn
                if scores is None:
                    scores = np.zeros_like(rtn,dtype=float)
                scores[rtn] = score
            else:
                _rtn, score = mk.compare(data)
                rtn = _rtn | rtn if self.multimatch == 'any' else _rtn & rtn
                if self.score_accuml == 'max':
                    scores[_rtn] = np.maximum(score,scores[_rtn]) 
                else:
                    scores[_rtn] += score

        scores[rtn] *= self.group_weight
        if return_data:
            df = data[rtn].copy()
            df['score'] = scores[rtn]
            return df
        else:
            return rtn, scores[rtn]

class MatchDataSource(object):
    def __init__(self, name, matchrules:List[MatchKeyGroup], 
            group_weights=None, debug=0) -> None:
        self.name = name
        self.matchrules = matchrules
        self.group_weights = group_weights
        self.debug = debug
        if self.group_weights is None:
            non_sc_mrs = len([mr for mr in self.matchrules 
                if mr.match_order != MatchOrder.shortcut])
            self.group_weights = [1.0
                if mr.match_order == MatchOrder.shortcut else 1./non_sc_mrs 
                for mr in self.matchrules]
        for wt, mr in zip(self.group_weights, self.matchrules):
            mr.group_weight = wt

    def __repr__(self) -> str:
        return (self.__class__.__name__ + '\n   ' + 
            '\n   '.join(repr(mr) for mr in self.matchrules)
        ) 

    def search_and_score(self, data):
        data = data.copy()
        scores = np.zeros(data.shape[0],dtype=np.float16)
        logger.warning('running shortcut search')
        df_sc, df_non_sc, keep = self._search_shortcut(data, scores)
        df_sc['score'] = -1.0

        logger.warning('running primary key match')
        scores = scores[~keep]
        df_prim, keep = self._search_primary(df_non_sc, scores)

        logger.warning('running secondary key match')
        scores = scores[keep]
        df_prim_and_sec, keep = self._search_secondary(df_prim,scores)
        return pd.concat([df_sc,df_prim_and_sec])

    def _search_shortcut(self, data, scores):
        shortcut = [mr for mr in self.matchrules if mr.match_order == MatchOrder.shortcut]
        logger.warning(f'shortcut match, incoming data: {data.shape}, {data.columns}')
        if len(shortcut) == 0 or data.shape[0] == 0:
            return pd.DataFrame({}), data, np.zeros(data.shape[0], dtype=bool)
        for i, mr in enumerate(shortcut):
            logger.debug(f'running shortcut match: {mr}')
            if i == 0:
                rtn, _ = mr.run_compare_and_score(data, scores=scores, return_data=False)
            else:
                _rtn, _ = mr.run_compare_and_score(data, scores=scores, return_data=False)
                rtn = _rtn | rtn
        df = data[rtn].copy()
        return df, data[~rtn].copy(), rtn

    def _search_primary(self, data, scores):
        primary = [mr for mr in self.matchrules if mr.match_order == MatchOrder.primary]
        logger.warning(f'primary match, incoming data: {data.shape}, {data.columns}')
        if len(primary) == 0 or data.shape[0] == 0:
            data['score'] = 0.
            return data
        for i, mr in enumerate(primary):
            logger.debug(f'running primary match: {mr}')
            if i == 0:
                rtn, _ = mr.run_compare_and_score(data, scores=scores, return_data=False)
            else:
                _rtn, _ = mr.run_compare_and_score(data, scores=scores, return_data=False)
                rtn = _rtn | rtn
        df = data[rtn].copy()
        df['score'] = scores[rtn]
        return df, rtn

    def _search_secondary(self, data, scores=None):
        secondary = [mr for mr in self.matchrules if mr.match_order == MatchOrder.secondary]
        logger.warning(f'secondary match, incoming data: {data.shape}, {data.columns}')
        if len(secondary) == 0 or data.shape[0] == 0:
            return data, np.zeros(data.shape[0],dtype=bool)
        if scores is None:
            scores = np.zeros(data.shape[0],dtype=np.float16)
        for i, mr in enumerate(secondary):
            logger.debug(f'running secondary match: {mr}')
            if i == 0:
                rtn, _ = mr.run_compare_and_score(data, scores=scores, return_data=False)
            else:
                _rtn, _ = mr.run_compare_and_score(data, scores=scores, return_data=False)
                rtn = _rtn | rtn
        df = data[rtn].copy()
        df['score'] += scores[rtn]
        return df, rtn


def get_id_name_dob_matcher(rec, use_basic=False,
        seq_overlap_match_thres=0.6, id_only=False):
    ''' create a id (shortcut match), name, DOB matcher based
        on a reference input record with fields 
            taxid
            compositename
            birthday
            (maidenname)
        
        the resulting 'matcher' object can then be called on 
        a dataframe, using
        ```
            match = get_matcher(ref_rec)  # ref_rec is a row from a dataframe
            results = match.search_and_score(recs_to_match)
        ```
    '''
    names = rec['compositename'].lower().split()
    names += ([] if rec['maidenname'] is None or (
            isinstance(rec['maidenname'], float) and 
                np.isnan(rec['maidenname'])) or 
            len(rec['maidenname']) == 0 
        else rec['maidenname']) 
    if use_basic:
        kwargs = {} 
    else: 
        kwargs = dict(
            match_func=lambda x,m: SequenceMatcher(None, m, x).ratio() > seq_overlap_match_thres, 
            match_score=lambda x,m: SequenceMatcher(None, m, x).ratio())
    if id_only:
        main_match = MatchKey(rec['taxid'], MatchType.taxid, 
            match_order=MatchOrder.primary, 
            datacols=['taxid'], **kwargs)
    else:
        main_match = [MatchKey(name, MatchType.name,
                pre_match=str.lower, datacols=[col], **kwargs                       
        ) for name, col in zip(names, ['firstname','middlename','lastname'])]
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
        MatchKeyGroup(matchkeys=main_match)]
    if not(id_only):
        match_rules.append(MatchKeyGroup(matchkeys=bday_match))
    matcher = MatchDataSource(
        ('id_match' if id_only else 'id_dob_name'), 
        matchrules=match_rules, debug=0)
    return matcher