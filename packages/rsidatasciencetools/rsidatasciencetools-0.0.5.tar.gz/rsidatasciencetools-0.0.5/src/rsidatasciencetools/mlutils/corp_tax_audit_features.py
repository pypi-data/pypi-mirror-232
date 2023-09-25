'''create business tax audit features from data'''
from urllib.parse import uses_query
import pandas as pd
import numpy as np
from typing import List, Tuple
import os
from collections import defaultdict
from itertools import chain
from warnings import warn
from rsidatasciencetools.sqlutils import sql_connect as sqlutil
# import sqlalchemy_s as sql_schema
# from sqlalchemy_sqlschema import maintain_schema

try:
    from tqdm import tqdm 
except ImportError:
    tqdm = None


if 'SQL_QUERIES_LOC' in os.environ:
    query_loc = os.environ['SQL_QUERIES_LOC']
    # query_loc = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
    #     '../../sqlutils/devel_corp_tax_audit_queries/')
else:
    warn('environment variable: SQL_QUERIES_LOC is not set; set this to define '
        'location of SQL tax audit queries')
    query_loc = None

query_cache = {}

monthstrs = ['01','02','03','04','05','06','07','08','09','10','11','12']

def find_group_key(ws_info, field_code_value, summarize=False, errornotfound=True):
    # print('find_group_key:, field_code_value=',field_code_value)
    if not(summarize):
        return field_code_value
    for k, rng in ws_info.items():
        if rng[0] <= float(field_code_value) < rng[1]:
            return k
    
    if errornotfound:
        raise ValueError('could not find valid range and group key for Worksheet entry')
    else:
        return field_code_value

def get_period_timestamp(year,per,tax_per_type='Q',tupleoflist=False):
    '''get tuple of datetimes corresponding to taxing period

        get_period_timestamp(year,per,tax_per_type='Q',tupleoflist=False)

        tax period types: [A]nnual, [D]aily, [M]onthly, 
            [N]on tax return account, [Q]uarterly, X: non DLIS / utility, 
            [P]er event 
    '''
    # print(f'get_period_timestamp: year[{year}] period[{per}]')
    if isinstance(year,(pd.core.series.Series,list)):
        assert isinstance(per,(pd.core.series.Series,list))
        if tupleoflist:
            ts_ss = [[],[]]
        else:
            ts_ss = []
        if not(isinstance(tax_per_type, (pd.core.series.Series,list))):
            tax_per_type = [tax_per_type] * len(per)
        for yr, p, tptype in zip(year, per, tax_per_type):
            if tupleoflist:
                st,end = get_period_timestamp(yr,p,tax_per_type=tptype)
                ts_ss[0].append(st)
                ts_ss[1].append(end)
            else:
                ts_ss.append(get_period_timestamp(yr,p,tax_per_type=tptype))
        if tupleoflist:
            return tuple(ts_ss)
        else:
            return ts_ss
    else:
        if ~isinstance(per,str):
            per = str(per)
        else:
            per = per.strip()
        if ~isinstance(year,str):
            year = str(year)
        else:
            year = year.strip()
        tax_per_type = tax_per_type.strip()
        if '00' in per or 'A' in tax_per_type:
            if not(per == '00' and tax_per_type=='A'):
                warn(f'tax type[{tax_per_type}] does not match per marker [{per}] - using annual period')
            return pd.Timestamp(year + '-01-01 0:00'),pd.Timestamp(
                str(int(year)+1) + '-01-01 0:00')
        elif 'Q' in tax_per_type:
            if per == '01':
                return pd.Timestamp(year + '-01-01 0:00'),pd.Timestamp(
                    year + '-04-01 0:00')
            elif per == '02':
                return pd.Timestamp(year + '-04-01 0:00'),pd.Timestamp(
                    year + '-07-01 0:00')
            elif per == '03':
                return pd.Timestamp(year + '-07-01 0:00'),pd.Timestamp(
                    year + '-10-01 0:00')
            elif per == '04':
                return pd.Timestamp(year + '-10-01 0:00'),pd.Timestamp(
                    str(int(year)+1) + '-01-01 0:00')
            else:
                raise KeyError(f'unknown period code: {per}')
        elif per in monthstrs:
            if 'M' not in tax_per_type: 
                warn(f'tax period type[{tax_per_type}] is not [M]onth')
            month = [num+1 for num, mstr in enumerate(monthstrs) if mstr == per][0]
            if month == 12:
                return pd.Timestamp(year + f'-{month:02d}-01 0:00'),pd.Timestamp(
                    str(int(year)+1) + f'-01-01 0:00')
            else:
                return pd.Timestamp(year + f'-{month:02d}-01 0:00'),pd.Timestamp(
                    year + f'-{month+1:02d}-01 0:00')

        elif any(per.startswith(let) for let in 'ABCDEFGHIJKL'):
            # print(f'found per event (?) | code: {tax_per_type}')
            assert 'P' in tax_per_type, f'tax period type[{tax_per_type}] is not [P]er event'
            month = [num+1 for num, let in enumerate('ABCDEFGHIJKL') if let == per[0]][0]
            if month == 12:
                return pd.Timestamp(year + f'-{month:02d}-01 0:00'),pd.Timestamp(
                    str(int(year)+1) + f'-01-01 0:00')
            else:
                return pd.Timestamp(year + f'-{month:02d}-01 0:00'),pd.Timestamp(
                    year + f'-{month+1:02d}-01 0:00')
        else:
            if tax_per_type in ['D', 'N', 'X']:
                raise NotImplementedError('currently not handling D, N, or X type tax periods')
            else:
                raise KeyError(f'unknown period code: {per} or tax period type: {tax_per_type}')

class Duration(object):
    '''Duration object to track annual and quarterly datetimes'''
    def __init__(self,time1,time2=None,_type='Q',round2quarter=False):
        if isinstance(time1,str):
            assert time2 is None or isinstance(time2,str)
            if time2 is None:
                time2 = '00'
            if len(time2) == 1:
                time2 = '0'+time2
            self.start, self.end = get_period_timestamp(time1, time2, tax_per_type=_type)
            self.period_str = '-'.join([time1,time2])
        else:
            assert isinstance(time1,(np.datetime64,pd.Timestamp)), 'time1 must be datetime64 or Timestamp'
            assert time2 is None or isinstance(time2,(np.datetime64,pd.Timestamp)), 'time2 must be datetime64 or Timestamp'
            if round2quarter:
                self.start = Duration.roundQuarter(time1, check_duration=pd.Timedelta(weeks=7))
            else:
                self.start = time1
            self.end =(self.roundQuarter(self.start+pd.Timedelta(weeks=13)) if time2 is None else time2)
            if self.end - self.start >= pd.Timedelta(weeks=52):
                self.period_str = f'{self.start.year}-00'
            elif self.end - self.start >= pd.Timedelta(weeks=25):
                self.period_str = f'{self.start.year}-S{self.start.quarter:1d}'
            else:
                self.period_str = f'{self.start.year}-{self.start.quarter:02d}'
    
    def __str__(self):
        return self.__class__.__name__ + f'[{self.period_str}] ' + '->'.join([self.start.strftime('%y/%m/%d'),self.end.strftime('%y/%m/%d')])

    def __repr__(self):
        return f'{self.period_str} ' + '->'.join([self.start.strftime('%y/%m/%d'),self.end.strftime('%y/%m/%d')])

    @property
    def perstr(self):
        return self.period_str.split('-')

    def __lt__(self, other_time):
        if isinstance(other_time,(np.datetime64,pd.Timestamp)):
            return self.end < other_time
        elif isinstance(other_time,Duration):
            return self.end <= other_time.start
        else:
            raise TypeError(f'cannot compare inequality with type: {type(other_time)}')

    def __gt__(self, other_time):
        if isinstance(other_time,(np.datetime64,pd.Timestamp)):
            return self.start > other_time
        elif isinstance(other_time,Duration):
            return other_time.__lt__(self)
        else:
            raise TypeError(f'cannot compare inequality with type: {type(other_time)}')

    def __eq__(self, other_time):
        if isinstance(other_time,(np.datetime64,pd.Timestamp)):
            return self.start == other_time or self.end == other_time
        elif (isinstance(other_time, tuple) and len(other_time) == 2):
            return self.__eq__(Duration(*other_time))
        elif isinstance(other_time,Duration):
            return self.start == other_time.start or self.end == other_time.end
        else:
            raise TypeError(f'cannot compare equality with type: {type(other_time)}')

    @staticmethod
    def nearestQuarters(newtime):
        year = str(newtime.year)
        return [pd.Timestamp(year + '-01-01 0:00'),pd.Timestamp(year + '-04-01 0:00'),
            pd.Timestamp(year + '-07-01 0:00'),pd.Timestamp(year + '-10-01 0:00'),
            pd.Timestamp(str(int(year)-1) + '-01-01 0:00'),pd.Timestamp(str(int(year)+1) + '-01-01 0:00')]

    @staticmethod
    def roundQuarter(newtime, check_duration=pd.Timedelta(days=10), check=True):
        nearest_qtrs = Duration.nearestQuarters(newtime)
        idx = np.argmin(np.abs([nq - newtime for nq in nearest_qtrs]))
        assert not(check) or np.abs(((nearest_qtrs[idx] - newtime)/check_duration)) < 1.0, (
            f'time does not fall on a quarter date marker: nearest[{nearest_qtrs[idx]}], this[{newtime}]')
        return nearest_qtrs[idx]

    @staticmethod
    def ceilQuarter(newtime, check_duration=pd.Timedelta(days=10), check=True):
        nearest_qtrs = Duration.nearestQuarters(newtime)
        idx = np.argmin([nq - newtime for nq in nearest_qtrs if nq - newtime > 0])
        assert not(check) or np.abs(((nearest_qtrs[idx] - newtime)/check_duration)) < 1.0, (
            f'time does not fall on a quarter date marker: nearest[{nearest_qtrs[idx]}], this[{newtime}]')
        return nearest_qtrs[idx]

    def __add__(self,offset=None,weeks=None,quarters=None,years=None,sign=1):
        if offset is None:
            _offset = sign*pd.Timedelta(weeks=(0 if weeks is None else weeks))
            if quarters:
                _offset += sign*pd.Timedelta(weeks=13*quarters)
            if years:
                _offset += sign*pd.Timedelta(weeks=52*years)
        elif isinstance(offset,str):
            _offset = sign*pd.Timedelta(weeks=0)
            terms = offset.split('+')
            if 'week' in offset:
                _offset += sign*pd.Timedelta(weeks=int([t.split('*week')[0] 
                    for t in terms if 'week' in t][0]))
            if 'quarter' in offset:
                _offset += sign*pd.Timedelta(weeks=13*int([t.split('*quarter')[0]
                     for t in terms if 'quarter' in t][0]))
            if 'halfyear' in offset:
                _offset += sign*pd.Timedelta(weeks=26*int([t.split('*halfyear')[0]
                     for t in terms if 'halfyear' in t][0]))
            if 'year' in offset and 'halfyear' not in offset:
                _offset += sign*pd.Timedelta(weeks=52*int([t.split('*year')[0]
                     for t in terms if 'year' in t][0]))
        elif isinstance(offset,pd.Timedelta):
            _offset = sign*offset
            try:
                self.roundQuarter(self.start+_offset,check_duration=pd.Timedelta(days=0))
            except AssertionError as ae:
                warn(str(ae))
                return self.__class__(self.start+_offset, self.end+_offset)
        else:
            raise TypeError(f'unknown offset type: {type(offset)}')
        return self.__class__(self.roundQuarter(self.start+_offset), 
            self.roundQuarter(self.end+_offset))
    
    def __sub__(self,offset=None,weeks=None,quarters=None,years=None):
        return self.__add__(offset=offset,weeks=weeks,quarters=quarters,years=years,sign=-1)


def get_num_locations(data):
    NaT = np.datetime64('NaT')
    num_locs_open = np.zeros(data.shape[0],dtype=int)
    for bid, d in data.groupby('business_id'):
        bloc_openclose = [dd.loc_open_date.unique() for bloc, dd in d.groupby('bus_loc_id')],[
                          dd.loc_close_date.unique() for bloc, dd in d.groupby('bus_loc_id')]
        assert all(len(op) == 1 for op in bloc_openclose[0]) and all(
            len(cl) == 1 for cl in bloc_openclose[1]), (
            'bus loc id should have a single unique open and close date')
        bloc_openclose = [np.array(list(el[0] for el in bloc_openclose[0])),
                          [el[0] for el in bloc_openclose[1]]]
        for yrper, dd in d.groupby(['obl_year','obl_period','tax_period_cd']):
            obl_date = get_period_timestamp(*yrper)
            nopen = ((bloc_openclose[0] <= obl_date[1]) & np.asarray(
                [((dt is None) or isinstance(dt, (type(NaT),type(pd.NaT))) or 
                    obl_date[0] <= dt) for dt in bloc_openclose[1]], dtype=bool)).sum()
            num_locs_open[dd.index.tolist()] = max(1,nopen)
    return num_locs_open


class Encoder(object):
    base_keys = ['business_status_id', 'maxNumLoc', 'naics_code']
    summary_keys = ['audit_review_dur_years', 'n_obligations']
    # NOTE: naics_code comes from SQL queried data
    obl_type_id = [
        1,3,5,6,8,10,12,13,14,16,17,18,19,20,21,22,
        23,24,25,26,27,28,29,34,39,40,46,47,102,116,117,118,119,120,
        121,122,123,124,125,128,129,130,131,132,133,134,135,136,137,
        138,169,170,171,172,173,174]
    obl_source_code_id = [5,9,10,15]
    ded_class_ids = [1, 2, 3, 4, 5, 7, 22, 30, 343, 447, 506, 701]
    ded_type_ids = list(range(1,48))
    ws_info = [
        1, 3, 6, 13, 14, 15, 16, 17, 18, 20, 21, 31, 41, 44, 101, 
        102, 105, 106, 108, 111, 112, 150, 204, 205, 250, 308, 404, 
        405, 406, 450, 500, 501, 507, 509, 750, 6000, 6002, 6004, 6005, 
        6011, 6012, 6021, 6022, 6041, 6042, 6051, 6052, 7001, 7002, 
        7003, 7004, 7005, 7006, 7010, 7011, 7020, 7021, 7030, 9006]
    ws_info_summary = {
        '1-series':(0,10), 'teens':(10,20), 'x-ties':(20,100), 'hund':(100,200), 
        '2-3-4-hund':(200,500), '5-7-hund':(500,800), 
        '6-thous':(6000,7000), '7-thous':(7000,8000), 'nine-thous':(8000,9000)}

    def __init__(self,include_sum_paid=False,qtrs=25,semi=None,years=6, 
            all_time=True, summary_ws=False, debug=0,
            limit_ws_fields=[101, 105, 106, 108, 150, 308, 
                             404, 405, 406, 450, 500, 507, 
                             509, 7001, 7003, 7010, 7020, 7021, 7030, 750],
            limit_obl_type_id=[10, 23], limit_obl_source_code_id=[15],
            limit_ded_type_ids=[2], limit_ded_class_ids=[4]
        ):
        self.summary_ws = summary_ws
        self.keys_for_ref = ['num_locs', 'sumsum_gross', 'sumsum_deduc', 
            'sumsum_taxable', 'sumsum_taxdue', 'obl_type_id','obl_source_code_id', 
            'ded_class_ids', 'ded_type_ids', 'ws_info']
        if include_sum_paid:
            self.keys_for_ref.append('sumsum_paid')
        self.fit_data, self.paired_keys, self.num_entries, self.base_id = None, None, 0, 'base_id'
        if self.summary_ws:
           self.ws_info = self.ws_info_summary 
           limit_ws_fields = None
        self._create_encoding(qtrs=qtrs,semi=semi,years=years,all_time=all_time,
            limit={'ws_info': limit_ws_fields, 'obl_type_id': limit_obl_type_id,
                'obl_source_code_id': limit_obl_source_code_id, 
                'ded_type_ids': limit_ded_type_ids, 'ded_class_ids': limit_ded_class_ids})
        self.debug = debug
        self.metrics = {
            'num_obligation_entries': [],
            'business_no_data': 0}
        if self.debug:
            self.ref_audit_search_periods = None 
    
    def __repr__(self):
        s = self.__class__.__name__
        s += (f'(object) [isFit:{int(self.fit_data is not None)}] | '
            f'encoded variables: {self.num_entries}')
        if self.fit_data is not None:
            s += f', data examples: {self.fit_data.shape[0]}'
        return s

    def _create_encoding(self,qtrs=12,semi=None,years=4,all_time=True,limit=None):
        self.time_periods = dict()
        self.limit = limit
        if all_time:
            self.time_periods['all_time'] = ('all',[('','all')])
        if qtrs is not None:
            self.time_periods['last_quarters'] = (
                '1*quarters',[(back,f'{back}*quarters') for back in range(0,qtrs+1)])
        if semi is not None:
            self.time_periods['last_semiannual'] = (
                '1*halfyears',[(back,f'{back}*halfyears') for back in range(0,semi+1)])
        if years is not None:
            self.time_periods['last_years'] = (
                '1*years',[(back,f'{back}*years') for back in range(0,years+1)])
        idx = 0
        self.paired_keys = {}
        self._rtn_keys = []
        self.paired_keys[self.base_id] = idx
        self._rtn_keys.append(self.base_id)
        idx += 1
        for k in self.base_keys:
            self.paired_keys[k] = idx
            self._rtn_keys.append(k)
            idx += 1
        for k in self.summary_keys:
            self.paired_keys[k] = idx
            self._rtn_keys.append(k)
            idx += 1
        for pername, (_, per_period_set) in self.time_periods.items():
            for bk, _ in per_period_set:
                if pername == 'all_time':
                    time_key = 'all_time'
                else:
                    time_key = pername + str(bk)
                for k in self.keys_for_ref:
                    if 'sumsum' in k or k in ['num_locs']:
                        self.paired_keys[(time_key, k)] = idx
                        self._rtn_keys.append((time_key, k))
                        idx += 1
                    else:
                        for kk in self.__class__.__dict__[k]:
                            if ((limit is not None) and (k in limit) and 
                                    limit[k] is not None and (kk not in limit[k])):
                                continue
                            self.paired_keys[(time_key, k, kk)] = idx
                            self._rtn_keys.append((time_key, k, kk))
                            idx += 1
        self.num_entries = idx

    def clean_and_populate(self,data,clean_bad_periods=False):
        
        # clean fields containing lists of information
        for k in ['ded_class_ids','ded_type_ids']:
            if data[k].apply(lambda d: isinstance(d, (type(None), str))).all():
                data[k] = data[k].apply(lambda d:[int(el) for el in d.split(',')] if d else None)
        if data['ws_info'].apply(lambda d: isinstance(d, (type(None), str))).all():
            data['ws_info'] = data['ws_info'].apply(lambda d:
                {(int(el.split('=')[0].split(':')[0]), int(el.split('=')[0].split(':')[1])):
                int(el.split('=')[1]) for el in d.split(',')} if d else None)
        # print(data.ws_info[data.ws_info.apply(lambda x: x is not None)])
        for k in ['obl_year','obl_period','tax_period_cd']:
            data[k] = data[k].apply(lambda s: s.strip())
        if clean_bad_periods:
            def ck_zero(p):
                try:
                    return int(p) == 0
                except:
                    return False 
            def ck_nonzero(p):
                try:
                    return int(p) > 0
                except:
                    return False 
            remove = data[((data.obl_period.apply(ck_nonzero) & data.tax_period_cd.apply(lambda c: 'A' in c)) | 
                           (data.obl_period.apply(ck_zero) & data.tax_period_cd.apply(lambda c: 'Q' in c)))].index
            print(f'   removed {remove.size} non-sensical tax (periods,codes)')
            data.drop(remove, inplace=True) 
            data.reset_index(inplace=True)
        data['period_st'], data['period_end'] = get_period_timestamp(
            data.obl_year,data.obl_period,tax_per_type=data.tax_period_cd, tupleoflist=True)
        data['num_locs'] = get_num_locations(data)
        return data 
        
    def fit(self, data, base_id, base_id_list, audit_to_date_list, 
            audit_from_date_list=None,
            remove_nonsensical_periods=True, 
            remove_keys=['business_id', 'bus_loc_id',
                  'business_status_id', 'maxNumLoc', 'naics_code', 'dlis_branch_number', 
                  'obligation_id', 'obl_year', 'obl_period', 'TaxRetIDs',
                  'bus_legal_open', 'bus_close_date', 'loc_open_date', 'loc_close_date',
                  'period_st','period_end']):
        ''' Encoder.fit(self, data, base_id, base_id_list, audit_to_date_list, 
                remove_keys=['business_id', 'bus_loc_id',
                  'business_status_id', 'maxNumLoc', 'naics_code', 'dlis_branch_number', 
                  'obligation_id', 'obl_year', 'obl_period', 'TaxRetIDs',
                  'bus_legal_open', 'bus_close_date', 'loc_open_date', 'loc_close_date',
                  'period_st','period_end']
        
            Fields extracted from data to generate features:
                naics, bus_status, maxLoc, numLocs,                     // slots = 4
                    (a set of the following for each time period)
                obl src id (occurance count encode of codes 5,9,10,15), // slots = 4
                obl type id occurrance count in period,                 // slots = 56
                sum_gross, sum_dedeuc, sub_taxable, sum_due, (sum_paid) // slots = 4-5
                12 bins for ded class ids                               // slots = 12
                47 bins for ded type id (" ")                           // slots = 47
                59 bins for tax return worksheet field id               // slots = 59
                    total variables = number of time periods X 182 + 4 (base set)

            Returns: pandas.DataFrame of encoded feature data
        '''
        if self.debug:
            print('running data feature encoder...')
        self.metrics = {
            'num_obligation_entries': [],
            'business_no_data': 0}

        oldid, self.base_id = self.base_id, base_id
        self.paired_keys[self.base_id] = self.paired_keys[oldid]
        if oldid != self.base_id:
            del self.paired_keys[oldid]
            idx = self._rtn_keys.index(oldid)
            self._rtn_keys[idx] = self.base_id
        
        if audit_to_date_list is None:
            audit_to_date_list = []
            for bid in base_id_list:
                dd = data[data[base_id]==bid]
                recent_year = max(dd.obl_year)
                audit_to_date_list.append((recent_year,max([p
                    for y,p in zip(dd.obl_year,data.obl_period) if y==recent_year])))
        else:
            assert len(base_id_list) == len(audit_to_date_list)
        
        data = self.clean_and_populate(data,clean_bad_periods=remove_nonsensical_periods)

        self.keyset_rem = [k for k in data.columns.tolist() if k not in remove_keys]
        rtn_array = np.zeros((len(base_id_list),self.num_entries), dtype=np.int)
        if self.debug:
            self.ref_audit_search_periods = defaultdict(list)
        for i, (bid, audit_to_period) in enumerate(zip(base_id_list,audit_to_date_list)):
            d = data[data[self.base_id] == bid]
            if d.empty:
                d = data[data[self.base_id] == str(bid)]
            # print(d.shape, d.columns.tolist(), base_id, bid, '==?', base_id_list)
            if d.empty:
                warn('no data for this bad id')
                self.metrics['business_no_data'] += 1
                continue

            audit_period = Duration((audit_from_date_list[i] 
                            if audit_from_date_list is not None
                            else audit_to_period - '6*years').start, 
                        audit_to_period.end)
            # print(bid, audit_period)
            rtn_array[i,self.paired_keys[base_id]] = d[base_id].values[0]
           
            #try: 
            #except IndexError as ie:
            #    print(bid, d.keys(), d.shape[0])
            #    raise(ie)
            self.metrics['num_obligation_entries'].append(d.shape[0])
            for k in self.base_keys:
                rtn_array[i,self.paired_keys[k]] = d[k].values[0]
            rtn_array[i,self.paired_keys['audit_review_dur_years']] = float(
                (audit_period.end - audit_period.start)/pd.Timedelta(weeks=52))
            rtn_array[i,self.paired_keys['n_obligations']] = d.shape[0]
            for pername, (base_dur, per_period_set) in self.time_periods.items():
                if pername == 'all_time':
                    time_key = 'all_time'
                    base_period = audit_period
                    # print('base period', base_period)
                else:
                    time_key = pername + str(bk)
                    base_period = Duration((audit_to_period - base_dur).end, audit_to_period.end)
                
                if self.debug:
                    self.ref_audit_search_periods['id'].append(bid)
                    self.ref_audit_search_periods['audit_date'].append(audit_to_period)
                    self.ref_audit_search_periods['period_name'].append(pername)
                    self.ref_audit_search_periods['base_period'].append(base_period)
                    all_periods = []
                for bk, offset in per_period_set:
                    if pername != 'all_time':
                        time_key = pername + str(bk)
                        per = base_period - offset
                        if audit_from_date_list is not None and per < audit_from_date_list[i]:
                            # skip this historic period as it was not considered in the audit
                            # print('skipping this period')
                            continue
                    else:
                        per = base_period
                    dd = d[self.keyset_rem][(d.period_st >= per.start) & (d.period_end <= per.end)]
                    # print(d[self.keyset_rem].shape,per,(d.period_st.min(),d.period_end.max()),
                    #     (d.period_st>=per.start).sum(),(d.period_end <= per.end).sum(),dd.shape)
                    if self.debug:
                        all_periods.append(per)
                    if dd.empty:
                        #print('bid', bid, 'size dd', dd.shape, 'period', per)
                        warn(f'completely empty obligation dataset for at least one base_id and period')
                        continue
                    for k in self.keys_for_ref:
                        if k == 'num_locs':
                            try:
                                rtn_array[i,self.paired_keys[(time_key,k)]] = dd[k][~np.isnan(dd[k])].mean()
                            except ValueError as ve:
                                print('size dd', dd.shape, 'period', per)
                                raise(ve)
                        if 'sumsum' in k:
                            rtn_array[i,self.paired_keys[(time_key,k)]] = dd[k].sum()
                        elif k in ['obl_type_id','obl_source_code_id']:
                            for kk in dd[k].tolist():
                                if (time_key,k,kk) not in self.paired_keys:
                                    continue
                                rtn_array[i,self.paired_keys[(time_key,k,kk)]] += 1
                        elif k in ['ded_class_ids', 'ded_type_ids']:
                            for kk in chain.from_iterable([el for el in dd[k].tolist() if el is not None]):
                                if (time_key,k,kk) not in self.paired_keys:
                                    continue
                                rtn_array[i,self.paired_keys[(time_key,k,kk)]] += 1
                        elif k in ['ws_info']:
                            for ddd in dd[k].tolist():
                                if ddd is not None:
                                    for kk,v in ddd.items():
                                        gkey = find_group_key(self.__class__.__dict__[k], kk[1],
                                            summarize=self.summary_ws, errornotfound=False)
                                        # in this data (-1,1) values represent null data - i.e., not 
                                        # entered, ignore in this case
                                        if ((time_key,k,gkey) not in self.paired_keys) or (abs(v) == 1):
                                            continue
                                        rtn_array[i,self.paired_keys[(time_key,k,gkey)]] += v
                if self.debug:
                    self.ref_audit_search_periods['all_periods'].append(all_periods) 
        if self.debug:
            self.ref_audit_search_periods = pd.DataFrame(self.ref_audit_search_periods) 
        if self.limit is not None:
            assert all([self.limit[k[1]] is None or k[2] in self.limit[k[1]] 
                    for k in self._rtn_keys if isinstance(k,tuple) and len(k) > 2]), (
                'key found which was not allowable based on limit set')
        self.fit_data = pd.DataFrame({k: rtn_array[:,self.paired_keys[k]] for k in self._rtn_keys})
        trans_rtn_keys = {k: ('__'.join([str(kk) for kk in k]) if isinstance(k,tuple) else k)
            for k in self.fit_data.columns}
        self.fit_data.rename(columns=trans_rtn_keys, inplace=True)
        self.rtn_keys = list(trans_rtn_keys.values())
        if self.debug:
            self.metrics['num_obligation_entries'] = np.array(self.metrics['num_obligation_entries'])
            rec_count = self.metrics['num_obligation_entries']
            print(f'    Metrics: \n        '
                f'number of "no data" businesses:         {self.metrics["business_no_data"]}\n        '
                f'avg number of obligations per business: {rec_count.mean():.2g}+/-{rec_count.std():.2g}')
       
        return self.fit_data.copy()

    @property
    def key_mapping(self):
        return {('__'.join([str(kk) for kk in k]) if isinstance(k,tuple) else k): v 
            for k,v in self.paired_keys.items()}
    
    def __get__(self,key:str):
        # if isinstance(key,tuple):
        #     return self.fit_data[self[self.base_id]==key[0]].index, self.paired_keys[key[1]]
        # else:
        return self.paired_keys[(tuple(key.split('__')) if '__' in key else key)]
        
def get_query_lut(qloc:os.PathLike=query_loc):
    if qloc is None:
        raise AssertionError('query location not specified')
    qfiles = os.listdir(qloc)
    qfiles_d = {}
    for fn in qfiles:
        if not(fn.endswith('.sql')):
            continue
        with open(os.path.join(qloc,fn),'r') as fin:
            k = fin.readline().strip('*/ ').strip('\n')
        qfiles_d[k] = os.path.join(qloc,fn)
    return qfiles_d

def add_superclass(df, class_ids):
    mgroups = [[[i for n,i in class_ids.items() if 'no change' in n.lower()], 'no change'],
               [[i for n,i in class_ids.items() if n in [
                   'misclassification','code interpretation', 'square footage', 'unlicensed business']], 'misclass'], 
               [[i for n,i in class_ids.items() if 'apportionment' in n.lower()], 'apportionment'],
               [[i for n,i in class_ids.items() if 'voluntary' in n.lower()],'voluntary'],
               [[i for n,i in class_ids.items() if n in ['exemption','deduction','related party']],'tax ws items'], 
               [[i for n,i in class_ids.items() if n in ['gross income','other income items', 
                    'unreported parking/admissions']],'income']]
    merge = {i: mkey for i,mkey in enumerate(mgroups)}
    rmerge = {}
    for i, mval in merge.items():
        for j in mval[0]:
            rmerge[j] = i
    s1, s2 = set(rmerge.keys()), set(class_ids.keys())
    assert s1.symmetric_difference(s2), f'extra or missed a classification case: {s1.symmetric_difference(s2)}'
    df['superclass'] = df['class'].apply(lambda x: rmerge[x])
    return merge 

def get_labeled_data_features(alabels:pd.DataFrame, db:sqlutil.DbConnectGenerator, encoder=None, debug=1,
        return_raw:bool=False, use_query_cache=False, regr_field:str='assessment_amount', 
        class_field:str='issue_code', type_field=('case_type','case_sub_type'), qname:str='taxDeducBusInfo', 
        basekey:str='business_id', datekeys:Tuple[str]=('first_period','last_period')):
    ''' Query the database using the `db` (`DbConnector`) and pass data through tax data 
        `Encoder` to generate features.
    '''
    if isinstance(use_query_cache, dict):
        query_cache = use_query_cache
        use_query_cache = True
    qfiles_d = get_query_lut()
    qfile, query_str = qfiles_d[qname], ''
    with open(qfile,'r') as qfile:
        query_str = qfile.read()
    labeled_df = pd.DataFrame({})
    if encoder is None:
        encoder = Encoder()
    # last_period_of_audit = [Duration(ad, _type='Q', round2quarter=True) 
    #                     for ad in alabels[datekey].tolist()]
    first_period_of_audit = [Duration(Duration.roundQuarter(pd.Timestamp(t),check=False)) 
        for t in alabels[datekeys[0]].tolist()]
    last_perid_of_audit = [Duration(Duration.roundQuarter(pd.Timestamp(t),check=False)) 
        for t in alabels[datekeys[1]].tolist()]
    with db.gen_connection() as conn:
        # query data from SQL database
        if debug:
            print(f'querying database with: {qname}...')
        qstr = query_str.format(
                ' IN (',','.join([str(bid) for bid in alabels.business_id.tolist()])+')')
        if not(use_query_cache) or qstr not in query_cache:
            data = pd.read_sql(qstr, conn.connection)
        else:
            data = query_cache[0][qstr]
        if use_query_cache:
            query_cache[qstr] = data

        if debug:
            print(f'query returned {(0 if data is None else data.shape[0])} rows')

    labeled_df = encoder.fit(data, basekey, alabels[basekey].tolist(), last_perid_of_audit,
        audit_from_date_list=first_period_of_audit)
    if debug:
        print('    encoder finished running.')
    labeled_df['target'] = alabels[regr_field].tolist()
    if any(alabels[class_field].apply(type) == str):
        class_encoded_ids = {k: v for v, k in enumerate(sorted(set(alabels[class_field].tolist())))}

    type_encoded_ids = None
    if (isinstance(type_field, tuple) and any(alabels[type_field[0]].apply(type) == str)):
        type_encoded_ids = {tuple(k): v for v, k in enumerate(
           set(tuple(el) for el in alabels[list(type_field)].values.tolist()))}
    elif any(alabels[type_field].apply(type) == str):
        type_encoded_ids = {k: v for v, k in enumerate(set(alabels[type_field].tolist()))}
    nochange_code = [v for k,v in class_encoded_ids.items() if 'no change' in k.lower()] 
    labeled_df['class'] = alabels[class_field].apply(lambda d: class_encoded_ids[d]).tolist()
    if type_encoded_ids is not None:
        labeled_df['type'] = [type_encoded_ids[tuple(d)] for d in alabels[list(type_field)].values.tolist()]
    if len(nochange_code):
        labeled_df['is_no_change_label'] = labeled_df['class'] == nochange_code[0]

    labeled_df['is_no_change'] = labeled_df['target'] > 500
    superclass_lut = add_superclass(labeled_df, class_encoded_ids)

    if return_raw:
        return data, labeled_df, class_encoded_ids, type_encoded_ids, superclass_lut
    else:
        return labeled_df, class_encoded_ids, type_encoded_ids, superclass_lut

