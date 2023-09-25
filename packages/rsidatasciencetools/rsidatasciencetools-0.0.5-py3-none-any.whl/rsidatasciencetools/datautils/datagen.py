'''Data generation tools - e.g., form records for exercising matching algorithms'''
import argparse
from os import listdir, environ, path, PathLike
import numpy as np
from scipy import stats
import pandas as pd
from datetime import datetime
from pytz import utc
from itertools import chain
from enum import Enum, auto
from warnings import warn
from collections import Counter
from typing import List, Union
from dateutil.parser import ParserError

from rsidatasciencetools.datautils.clean import fix_lists
from rsidatasciencetools.config.baseconfig import YmlConfig, get_stdout_logger, log_level_dict
from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig
from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.azureutils.az_logging import get_az_logger


logger = get_az_logger(__name__)


try:
    from tqdm import tqdm 
except ImportError:
    tqdm = None

ethnicities = ['White','Black','API','Asian','TwoOrMoreRaces','Hispanic']
alphabet = 'abcdefghijklmnopqrstuvwxyz'

class DataValidationException(Exception):
    pass


class WorkingSchedule(Enum):
    unrestricted = auto()
    workhours = auto()
    morning = auto()
    weekday = auto()
    workhours_weekday = auto()
    morning_weekday = auto()
    
class TaxPayerType(Enum):
    individual = auto()
    soleproprietorship = auto()
    corporation = auto()

class NameIdDataType(Enum):
    taxpayertype = auto()
    firstname = auto()
    lastname = auto()
    middlename = auto()
    ethnicity = auto()
    compositename = auto()
    maidenname = auto()
    birthday = auto()
    taxid = auto()
    compositeaddress = auto()
    streetno = auto()
    aptno = auto()
    streetname = auto()
    city = auto()
    state = auto()
    zipcode = auto()
    phoneno = auto()
    email = auto()
    metric_id = auto()

class NameIdDataCorruptible(Enum):
    firstname = auto()
    lastname = auto()
    middlename = auto()
    compositename = auto()
    maidenname = auto()
    birthday = auto()
    taxid = auto()
    streetno = auto()
    aptno = auto()
    streetname = auto()
    city = auto()
    zipcode = auto()
    phoneno = auto()
    email = auto()

class NameIdDataLengthChangable(Enum):
    firstname = auto()
    lastname = auto()
    middlename = auto()
    compositename = auto()
    maidenname = auto()
    streetno = auto()
    aptno = auto()
    streetname = auto()
    city = auto()
    email = auto()


step = 1./6
distribution_addr_digits = stats.beta.pdf(np.arange(step,1.0,step),3.8,4.)
distribution_addr_digits /= distribution_addr_digits.sum()
step = 1./4
distribution_apt_digits = stats.beta.pdf(np.arange(step,1.0,step),5.,4.)
distribution_apt_digits /= distribution_apt_digits.sum()
step = 1./7
distribution_num_mf = stats.expon.pdf(np.arange(step,1.0,step), step)
distribution_num_mf /= distribution_num_mf.sum()

# --------- utility functions ---------
# -------------------------------------

def get_no(rng,length,base=10,return_int=False, join_char='',
        reject=(lambda x: x.startswith('0'), lambda y: y.lstrip('0')), tries=10):
    no = ''
    for _ in range(10):
        if isinstance(rng, np.random._generator.Generator):
            no = rng.integers(low=0, high=base, size=length)
        else: 
            no = rng.randint(0,base,size=length)

        if not(return_int):
            no = join_char.join([str(n) for n in no])
        if reject is not None:
            if reject[0](no):
                no = reject[1](no)
        if len(no):
            break
    if len(no) == 1:
        return no[0]
    return no


def get_alphanum(rng, length, base=None, return_int=False, 
        join_char='', alpha=False, num=True,
        reject=(lambda x: False, lambda y: ''), tries=10):
    no = ''
    low = 0
    if base is None:
        base = 36 if alpha else 10
        low = 0 if num else 10
    for _ in range(tries):
        if isinstance(rng, np.random._generator.Generator):
            no = rng.integers(low=low, high=base, size=length)
        else: 
            no = rng.randint(0,base,size=length)

        if not(return_int):
            if alpha:
                no = join_char.join([(str(n) if n < 10 else alphabet[n-10]) 
                    for n in no])
            else:
                no = join_char.join([str(n) for n in no])
        if reject is not None:
            if reject[0](no):
                no = reject[1](no)
        if len(no):
            break
    if len(no) == 1:
        return no[0]
    return no


def remove_cities_without_zips(df):
    zips = []
    for i, row in df.iterrows():
        if (len(df.ZipCodes.values) == 0) or all((len(v) == 0) for v in row.ZipCodes):
            zips.append(None)
        else:
            zips.append(row.ZipCodes)
    df['ZipCodes'] = zips
    return df.drop(df[df.ZipCodes.apply(lambda x: x is None)].index)


def round_dt_to(dt:pd.Timestamp, 
                rto:Union[Enum,List[Enum]]=[WorkingSchedule.workhours_weekday], 
                st:pd.Timestamp=None, end:pd.Timestamp=None,
                minutes_from_edge:float=None, round_up=True, rng:np.random.RandomState=np.random):
    assert (end is None) or (st is None) or (st < end), (
        'restrictive start end datetimes incomptible, start is after end')
    if rng is None:
        rng = np.random
    if isinstance(rto, int):
        if rto == WorkingSchedule.unrestricted:
            return dt
    if isinstance(rto,(list,tuple)):
        for rt in rto:
            dt = round_dt_to(dt, rt, st=st, end=end, 
                minutes_from_edge=minutes_from_edge, round_up=round_up, rng=rng)
    elif isinstance(dt, (pd.DatetimeIndex, np.ndarray, list)):
        out = []
        for _dt in dt:
            out.append(round_dt_to(_dt, rto, st=st, end=end, 
                minutes_from_edge=minutes_from_edge, round_up=round_up, rng=rng))
        if isinstance(dt, np.ndarray):
            dt = np.array(out) 
        elif isinstance(dt, pd.DatetimeIndex):
            out = pd.DatetimeIndex(out)
        return out
    else:
        if (rto in WorkingSchedule):
            if rto in [WorkingSchedule.weekday, WorkingSchedule.workhours_weekday]:  # weekday
                if dt.day_of_week == 5:
                    dt += (pd.Timedelta(hours=48) if round_up else -pd.Timedelta(hours=24))
                elif dt.day_of_week == 6:
                    dt += pd.Timedelta(hours=24)
            if rto in [WorkingSchedule.morning, WorkingSchedule.morning_weekday]:  # morning
                if dt.hour < 6 or dt.hour > 12:
                    hour = dt.hour
                    dt = pd.Timestamp(year=dt.year,month=dt.month,day=dt.day, 
                        hour=rng.randint(6,12),minute=dt.minute,second=dt.second)
                    if round_up and hour > 12:
                        dt += pd.Timedelta(days=1) 
            if rto in [WorkingSchedule.workhours, WorkingSchedule.workhours_weekday]:  # workhours
                if dt.hour < 6 or dt.hour > 18:
                    hour = dt.hour
                    dt = pd.Timestamp(year=dt.year,month=dt.month,day=dt.day, 
                        hour=rng.randint(6,18),minute=dt.minute,second=dt.second)
                    if round_up and hour > 18:
                        dt += pd.Timedelta(days=1) 
        else:
            raise ValueError(f'unknown option: {rto}, round to option '
                             f'(rto) must be one of {list(WorkingSchedule)}')
        if end is not None:
            if dt > end:
                dt = end
            if minutes_from_edge is not None and (end - dt) < pd.Timedelta(minutes=minutes_from_edge):
                dt -= pd.Timedelta(minutes=minutes_from_edge)
        elif st is not None:
            if dt < st:
                dt = st
            if minutes_from_edge is not None and (dt - st) < pd.Timedelta(minutes=minutes_from_edge):
                dt += pd.Timedelta(minutes=minutes_from_edge)

    return dt


def random_datetimes(start:Union[datetime, pd.Timestamp], 
                     end:Union[datetime, pd.Timestamp], 
                     out_format='datetime', roundto=None,
                     rng:np.random.mtrand.RandomState=None, n=1):
        
    '''
    unix timestamp is in ns by default. 
    I divide the unix time value by 10**9 to make it seconds (or 24*60*60*10**9 to make it days).
    The corresponding unit variable is passed to the pd.to_datetime function. 
    Values for the (divide_by, unit) pair to select is defined by the out_format parameter.
    for 1 -> out_format='datetime'
    for 2 -> out_format=anything else
    '''
    (divide_by, unit) = (10**9, 's') if out_format=='datetime' else (24*60*60*10**9, 'D')
    assert start <= end, "start datetime is not before end datetime"
    assert type(start) == type(end), 'start and end datetimes should be the same type'
    if not(isinstance(start,pd.Timestamp)):
        start = pd.Timestamp.timestamp(utc.localize(start).timestamp())
        end = pd.Timestamp.timestamp(utc.localize(end).timestamp())
    start_u = start.value//divide_by
    end_u = end.value//divide_by
    if rng is None:
        rng = np.random
    if n == 1:
        rand_ns = rng.randint(start_u, end_u) 
    else:
        rand_ns = rng.randint(start_u, end_u, size=n)
    dt = pd.to_datetime(rand_ns, unit=unit) 

    if roundto is not None:
        # optionally round the random draw to a specific day of 
        # week and/or time of day
        if isinstance(roundto,(tuple,list)):
            for rt in roundto:
                dt = round_dt_to(dt, rt, st=start, end=end, rng=rng)
        elif isinstance(roundto, (bool,int)):
            if roundto:
                dt = round_dt_to(dt, st=start, end=end, rng=rng)
        else:
            dt = round_dt_to(dt, roundto, st=start, end=end, rng=rng)

    return dt

# @dataclass
# class Record:
#     """Class storing user data used for matching."""
#     name: str
#     unit_price: float
#     quantity_on_hand: int = 0

#     def total_cost(self) -> float:
#         return self.unit_price * self.quantity_on_hand


class Record(object):
    """The Record class provides a way to store and manipulate
    records of data according to the specified data type.
    The data type is defined by the `_datatype` parameter and should be

    an instance of the Enum class.
    
    Args:
    `_datatype`: enum class that defines the data fields that the
        Record instance can contain.
    `_corruptible` and `_lenth_changable` parameters are Enum instances
        that determine whether a specific data field can be corrupted
        and/or have its length changed. 
    `autopop`: dictionary containing functions that can be used to
        automatically generate data for certain fields. For example,
        a string concatenation of members that already are being passed.
    **kwargs: the fields to be included in the record, listed as:
        field1=value1, field2=value2,... where field1, field2 are fields 
        listed in the corresponding `_datatype` enum class.

    """
    def __init__(self, datatype=NameIdDataType, corruptible=NameIdDataCorruptible,
            lenth_changable=NameIdDataLengthChangable, state_for_stringify='MD',
            autopop=['compositeaddress'],
            rng:np.random.mtrand.RandomState = None, _debug=0, _logger=None, **kwargs) -> None:
        self._datatype = datatype 
        self._data_entries_check = [k.name for k in datatype]
        self._is_corruptible = [k.name for k in corruptible]
        self._is_length_changable = [k.name for k in lenth_changable]
        self.debug = _debug
        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if _logger is None else (
            _logger(self.__class__.__name__, self.debug) if callable(_logger) else _logger)
        if isinstance(autopop,list):
            _autopop = {}
            for el in autopop:
                if el == 'compositeaddress':
                    _autopop[el] = lambda x, rng: AddressSource.state_stringify_address(
                        state_for_stringify)(**x, rng=rng)
                else:
                    raise Exception('unknown autopop list item')
            autopop = _autopop

        kwargs.update({k: f(kwargs,rng) for k, f in autopop.items()})
        self.populate(**kwargs)

    def populate(self,**kwargs):
        """Set the data fields for the Record object in a
        dictionary. The fields are passed as keyword arguments,
        and only fields that match the data type are allowed.
        """
        for k,v in kwargs.items():
            if k not in self._data_entries_check:
                raise DataValidationException(f'input {k} is not a valid {self._datatype} field')
            self.__dict__[k] = v

    @staticmethod
    def as_dataframe(recs:List, state='MD') -> pd.DataFrame:
        """Static method that converts a list of Record objects into
        a pandas DataFrame.
        
        Args:
            recs: list of `Record` instances

        Returns:
            The list of Records transformed to a DataFrame
        """
        if not(isinstance(recs,list)):
            recs = [recs]
        recs = [r if isinstance(r, Record) else Record(**r,state_for_stringify=state) 
            for r in recs]
        return pd.DataFrame({k: [rec.__dict__[k] for rec in recs]
            for k in recs[0]})
    
    @staticmethod
    def from_dataframe(data: pd.DataFrame, state='MD') -> List:
        """This static method creates a list of Record objects
        from a pandas DataFrame.

        Args:
            data (DatFrame): the Records to set into a List

        Returns:
            List with the DataFrame rows
        """
        return [Record(**{k: row[k] for k in data.columns}, state_for_stringify=state)
            for _, row in data.iterrows()]

    def __repr__(self) -> str:
        """ This method returns a string representation of the
        Record object that includes the class name and a
        comma-separated list of key-value pairs for all data fields
        that match the data type.
        """

        return self.__class__.__name__ + ': ' + ', '.join(
            [f'{k}:{v}' for k,v in self.__dict__.items() 
                if k not in ['_data_entries_check', '_is_corruptible', '_is_length_changable']])

    def iteritems(self):
        for k in self.__dict__:
            if k in self._data_entries_check:
                yield k, self.__dict__[k]

    def __iter__(self):
        for k in self.__dict__:
            if k in self._data_entries_check:
                yield k
    
    def __getitem__(self,k):
        return self.__dict__[k]
    
    def items(self):
        return {k:v for k,v in self.__dict__.items() if k in self._data_entries_check}

    def update(self,dictin):
        for k in dictin:
            if k in self._data_entries_check:
                self.__dict__[k] = dictin[k]    
            else:
                print(f'skipping field: {k}, not a valid {self._datatype} field')


# -------  data source classes  -------
# -------------------------------------

class Source(object):
    """The Source class represents a data source that is flexible
    and can be used to represent different types of data sources, 
    such as static data files, dynamically generated data, or
    sampled data from a specified distribution.
    It contains methods to set weights for data points or to specify
    a probability distribution, from which data points are sampled.
    
    Args:
        src_data: The source data from which the samples are drawn.
        rng: The random number generator used for sampling data
            points.
        seed: int. The seed value used for random number generation.
        outcomes:  The possible outcomes or labels for the data points
            in src_data.
    """
    
    
    def __init__(self, src_data=None, rng: np.random.mtrand.RandomState=None, seed: int=None,
                 outcomes=None, use_cdf=False, _debug=0, _logger=None) -> None:
        # print('"Source" inputs:', src_data, type(src_data), rng, type(rng), seed, type(seed))
        self.src_data = src_data
        self.sample_weight = None
        self.sample_distribution = None
        self.shape_params = {}
        self.distribution_constraints = []
        # self.cdf = None
        self.data = None
        self.seed = np.random.randint(0,np.iinfo(np.int32).max) if (seed is None)  and (rng is None) else seed
        self.rng = (rng if rng is not None else np.random.RandomState(seed=self.seed))
        self.outcomes = outcomes
        self.use_cdf = use_cdf
        self.debug = _debug
        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if _logger is None else (
            _logger(self.__class__.__name__, self.debug) if callable(_logger) else _logger)
        # print('Source object - RNG, seed:', self.rng, seed)
        try:
            if (self.data is None and self.src_data is not None) and path.exists(self.src_data):
                self.data = pd.read_csv(self.src_data)
        except (TypeError,ValueError,FileNotFoundError,ParserError):
            pass

    def __repr__(self) -> str:
        """Return a string representation of the Source object.
        The string includes information about the source data,
        sample weight, sample distribution, shape parameters, 
        and the data obtained from the source.

        Returns:
            str: A string representation of the Source object.
        """
        
        return self.__class__.__name__ + '\n   '.join([
            ('File loc:' + self.src_data if isinstance(self.src_data,PathLike) 
                else ' src:' + str(self.src_data)[:min(len(str(self.src_data)),40)]), 
            'sample_weight: ' + str(self.sample_weight) if self.sample_weight 
                else 'distribution: ' + str(self.sample_distribution) + '(' + ','.join(
                    [f'{k}={v}' for k,v in self.shape_params.items()]) + ')',
            f'data: {(self.data.shape if isinstance(self.data, pd.DataFrame) else "")}' + (
                '\n' + str(self.data.head() if isinstance(self.data, pd.DataFrame) 
                else self.data) if self.data is not None else '')
        ])

    
    def calculate_weights(self):
        """Calculate the weights for each data point in the
        source data based on the frequency of outcomes.
        For example, in an experiment of Head/Tail we can
        get something like: {'TAIL': 0.49, 'HEAD': 0.51}
        It sets the `sample_weight` attribute to an array of the
        outcome frequencies sorted in descending order. 
        The `data` attribute is also set to a pandas
        DataFrame that contains the outcomes and their
        frequencies.

        Returns:
            None.
        """
        
        # Use the Counter function to count the occurrences of each outcome
        outcome_counts = Counter(self.outcomes)

        # Calculate the frequency of each outcome
        outcome_freqs = {outcome: count/len(self.outcomes) for outcome, count in outcome_counts.items()}
        
        # Sort the outcomes by frequency
        outcome_freq = sorted(outcome_freqs.items(), key=lambda x: x[1], reverse=True)
        outcome_freq_df = pd.DataFrame(outcome_freq, columns=['n','freq'])
        self.data = outcome_freq_df[['n']]
        self.sample_weight = np.array(outcome_freq_df['freq'])
        
    def set_weights(self, weights):
        if self.sample_distribution is not None:
            msg = 'trying to set weights, but sample distribution is also specified, setting to None'
            self.logger.warning(msg)
            warn(msg)
            self.sample_distribution = None
        self.sample_weight = weights
        if self.use_cdf:
            self.cdf = np.cumsum(weights) / weights.sum()

    def set_distribution(self, rv_func, shape_params={}, constraints=[]):
        if self.sample_distribution is not None:
            msg = ('trying to set distribution, but sample weight is also '
                'specified, setting to None')
            self.logger.warning(msg)
            warn(msg)
            self.sample_weight = None
        self.shape_params = shape_params
        self.distribution_constraints = constraints
        self.sample_distribution = rv_func
        # self.cdf = np.cumsum(weights) / weights.sum()

    def get_sample(self, sample_weight=None, data=None, restrict=None, shape_params={}):
        """
        Get a single sample from the source data based on the
        assigned weights or probability distribution function.

        If the `sample_weight` attribute is `None` and a
        `sample_distribution` function has been specified, the
        method samples a single data point from the distribution
        function and applies any specified constraints to it. 
        If both `sample_weight` and `data` attributes are available,
        the method selects a single data point randomly from the
        data according to the assigned weights.

     Args:
        sample_weight (list or numpy.ndarray, optional): The weights
            assigned to each data point in the source data.
        data (pd.DataFrame, list, or numpy.ndarray, optional): 
            The data from which to sample.
        shape_params (dict, optional): A dictionary of shape
            parameters used in the probability distribution function.

    Returns:
        object: A single random choice from the source data.
    
        """
        if self.sample_weight is None and self.sample_distribution is not None:
            shape_params = (shape_params 
                if len(shape_params) or len(self.shape_params) == 0 
                else self.shape_params)
            sample = self.sample_distribution(**shape_params)
            for _type, f in self.distribution_constraints:
                if isinstance(sample, _type):
                    sample = f(sample)
            return sample
        
        data = self.data if data is None else data
        data_is_df = isinstance(data,pd.DataFrame)
        
        if (data_is_df and data.shape[0] == 0) or (not(data_is_df) and len(data) == 0):
            self.logger.debug('no data in DataFrame passed or availabe in object')
            return None
        err_msg = ('if data is not DataFrame, '
            'then need sample weights are needed to calculate CDF for drawing a sample' )
        not((sample_weight is not None) or data_is_df) and self.logger.error(err_msg)
        assert (sample_weight is not None) or data_is_df, err_msg
        sample_weight = (self.sample_weight if sample_weight is None else sample_weight)
        weight_is_array = isinstance(sample_weight, (list,np.ndarray))
        err_msg = f'invalid type: {type(sample_weight)}'
        not(sample_weight is None or isinstance(sample_weight, (float,list,np.ndarray))) and self.logger.error(
            err_msg)
        assert sample_weight is None or isinstance(sample_weight, (float,list,np.ndarray)), err_msg

        if data_is_df:
            if not(weight_is_array) and sample_weight == 1.0:
                sample_weight = None
            if restrict is not None and restrict[1] is not None:
                data = data[data[restrict[0]] == restrict[1]]
                err_msg = f'no data after applying restrction [{restrict[0]}={restrict[1]}]'
                self.logger.error(err_msg)
                assert data.shape[0] > 0, err_msg
            return data.sample(weights=sample_weight,random_state=self.rng,
                ignore_index=True).loc[0:1].to_dict('records')[0]
        else:
            err_msg = ('if not a pd.DataFrame, then data should be one of a list '
                'or ndarray[object] types with the same length as sample_weight')
            not(isinstance(data,(np.ndarray,list))) and self.logger.error(err_msg)
            assert isinstance(data,(np.ndarray,list)), err_msg
            if not(weight_is_array) and sample_weight == 1.0:
                sample_weight = None
            elif self.use_cdf and (sample_weight is not None):
                cdf = (np.cumsum(sample_weight) / sample_weight.sum() 
                    if (not(data_is_df) and (sample_weight is not None) and weight_is_array) 
                    else self.cdf)
                idx = np.argwhere(cdf - self.rng.uniform(size=1) > 0.)[0][0]
                return data.iloc[idx:idx+1].to_dict('records')[0]
            # print('sample weight', sample_weight) 

            try:
                return self.rng.choice(data,p=sample_weight)
            except ValueError as e:
                if 'probabilities do not sum' in str(e):
                    return data[np.argwhere(self.rng.multinomial(
                        1, sample_weight) == 1)[0][0]]
                else:
                    raise e


class CitySource(Source):
    """ Randomly generates a city and its zip code.

    Args:
        furl (str): The URL or file path to the source data file.
        ignore_city_if_zip_missing (bool, optional): Whether to
            remove cities without associated zip codes from the data. 
            Default is True.
        rng (np.random.Generator, optional): The random number
            generator to use. If None, a new one is created.
        seed (int, optional): The seed value for the random number
            generator. If None, a random seed is generated.

    Attributes:
        data (pd.DataFrame): The data obtained from the source after
            the weights have been set.

    Methods:
        get_sample(): Get a random sample consisting of a city and
            its associated zip code.

    """
    
    
    def __init__(self,furl:str,ignore_city_if_zip_missing=True,
                 rng:np.random.mtrand.RandomState = None, seed:int = None) -> None:
        super().__init__(furl,rng=rng,seed=seed)

        df = pd.read_csv(furl)
        df['ZipCodes'] = df.ZipCodes.apply(fix_lists)
        if ignore_city_if_zip_missing:
            df = remove_cities_without_zips(df)
        self.data = df
        self.set_weights(df.Population.values)
        
    def get_sample(self) -> tuple:
        """Gets a random sample consisting of
        a city and its zip code.
        """
        city_data = super().get_sample()
        return city_data['Name'], super().get_sample(1.0, city_data['ZipCodes'])

class ZipSource(Source):
    """Randomly generates Area Codes for a given ZIP code or
    for a given city.
    
    Attributes:
        furl: The file URL from which the source data is loaded.
        rng: The random number generator used for sampling data points.
        seed (int): The seed value used for random number generation.
        data: The source data from which the samples are drawn,
            represented as a pandas DataFrame.
        all_cities: A list of all cities in the source data.
        all_areacodes: A list of all area codes in the source data.
        all_zips: A list of all ZIP codes in the source data.
    """
    
    def __init__(self, furl:str, rng:np.random.mtrand.RandomState = None, seed:int = None) -> None:
        super().__init__(furl,rng=rng,seed=seed)

        # if isinstance(furl,list):

        df = pd.read_csv(furl)
        df['AreaCodes'] = df.AreaCodes.apply(fix_lists)
        self.data = df
        self.all_cities = list(chain.from_iterable([v 
            for v in self.data.CommonCities.values]))
        self.all_areacodes = list(chain.from_iterable([v 
            for v in self.data.AreaCodes.values]))
        self.all_zips = self.data.ZIPCode.values
        
    def get_sample(self, zip=None, city=None):
        """Generate a sample area code from a provided
        zip code or city name.
        Args:
            zip (str, optional): The zip code for which to generate
                an area codes sample. Defaults to None.
            city (str, optional): The city for which to generate
                an area code sample. Defaults to None.
        Returns:
            Dict[str, Union[str, List[str]]]: A dictionary
                containing the area code and associated zip code or
                city name.

        Raises:
            AssertionError: If both zip and city arguments are None.
        """
        
        if zip is None and city:
            if city not in self.all_cities:
                areacodes = self.all_areacodes
            else:
                areacodes = self.data[np.array([(city in row.CommonCities) 
                    for i, row in self.data.iterrows()], 
                        dtype=bool)].AreaCodes.values
        else:
            assert not((zip is None) and (city is None))
            if zip not in self.all_zips:
                areacodes = self.all_areacodes
            else:
                areacodes = self.data[self.data.ZIPCode == zip]['AreaCodes'].values
        return super().get_sample(1.0, data=areacodes)


class AgeSource(Source):
    """Randomly generates age and birthdays of people.

    Args:
        furl (str): the file URL of the data source
        now (pd.Timestamp): the current time. 
            Default is the current system time.
        rng: an optional random number generator instance
        seed (int): an optional seed value for the random number generator
    """
    def __init__(self, furl:str = None, now=None, rng:np.random.mtrand.RandomState = None, seed:int = None) -> None:
        super().__init__(furl, rng, seed)
        self.now = (pd.Timestamp.now() if now is None else now)
        assert isinstance(self.now, pd.Timestamp)
        self.data = pd.read_csv(furl)
        self.set_weights(self.data.Population.values/self.data.Population.sum())

    def get_age_birthday(self) -> tuple:
        """Returns a tuple of a random age and birthday
        """
        age_range = super().get_sample()
        # print('age_range', age_range)
        start,end = self.now-pd.Timedelta(
            days=365*age_range['AgeYearsTo']), self.now - pd.Timedelta(
            days=365*age_range['AgeYearsFrom']) 
        # print('start/end:', start,end)
        birth = random_datetimes(start, end, rng=self.rng)
        # print('    birth:',birth)
        bday = (birth.month, birth.day, birth.year)
        age_years = np.round((self.now - birth).days / 365.,decimals=2) 
        return age_years, bday


class IdSource(Source):
    """It generates a random ID with the specifications provided.

    Args:
        furl (str or Path): The file location of the data source,
            if needed. Default to None.
        rng (np.random.Generator): The random number generator.
        seed (int): The seed for the random number generator.
        base (str): A string containing the characters to be used
            for generating the ID. Default to None.
        join_char (str): A string used to join the ID parts, 
            if needed.
        is_num (bool): A boolean value indicating if the ID should
            contain numbers.
        is_alpha (bool): A boolean value indicating if the ID should
            contain alphabets.
        repeating (int): The number of times to repeat the ID parts.
            Default to one.
        check_unique (bool): A boolean value indicating if the
            generated ID should be unique. Default to True.
        length (int): The number of characters of the ID.
    """
    def __init__(self, furl=None, rng:np.random.mtrand.RandomState = None, 
                 seed=None, base=None, join_char='',
                is_num=True, is_alpha=False, repeating=1, 
                check_unique=True, length=9) -> None:
        super().__init__(furl, rng, seed)
        self.global_id_db = []
        self.check_unique = check_unique
        self.length = length
        self.repeating = repeating
        self.base = base
        self.join_char = join_char
        self.is_num = is_num
        self.is_alpha = is_alpha

    def reset_id_db(self):
        """Resets the global_id_db attribute to an empty list.
        The global_id_db is the history of generated IDs used
        for unicity"""
        self.global_id_db = []

    def get_sample(self, return_int=False, tries=10, shape_params={}, **kwargs):
        """Generates a new ID. 
        Args:
           return_int (bool): A boolean value indicating if the ID
               should be returned as an integer. Default to False
        Returns:
            the generated ID. If return_int is True, the ID is
            returned as an integer, otherwise it is returned as a string.
        """
        err_msg = ('this NameSource has not be initialized to support '
            'ID generation, see `id_db` parameter')
        self.logger.error(err_msg)
        assert self.global_id_db is not None, err_msg
            
        check_unique = lambda x: x in self.global_id_db,lambda y: ''
        for _ in range(tries):
            _id = ''
            for _ in range(self.repeating):
                __id = get_alphanum(self.rng, length=self.length, base=self.base,
                    num=self.is_num, alpha=self.is_alpha, join_char=self.join_char,
                    reject=(check_unique if (self.check_unique and 
                            self.repeating <= 1) else None))
                _id = __id if len(_id) == 0 else self.join_char.join([_id, __id])
            if self.check_unique and self.repeating > 1 and check_unique[0](_id):
                _id = check_unique[1](_id)
            if _id:
                if self.check_unique:
                    self.global_id_db.append(_id)
                break
        if return_int:
            return int(_id)
        else:
            return _id


class NameSource(Source):
    """The NameSource class generates names based on a provided
    frequency distribution. The class reads in a csv file containing
    the frequency distribution of names and assigns weights to each
    name based on their frequency. 
    
    Args:
        furl: the file path or url to the csv file containing the
            frequency distribution of names.
        surl: the file path or url to the csv file containing the
            frequency distribution of last names.
        ismiddle: a boolean flag indicating whether the names are
            for the middle name or not.
        islastprob: the probability of generating a last name
            instead of a middle name.
        rng: a random number generator.
        seed: a seed for the random number generator.
    """
    def __init__(self, furl:str = None, surl:str = None, ismiddle:bool = False,
                 islastprob:float = 0.05, rng:np.random.mtrand.RandomState = None, seed:int = None) -> None:
        super().__init__(furl,rng=rng,seed=seed)

        self.data = pd.read_csv(furl)
        if (surl is not None) and ismiddle:
            self.data['Freq'] = self.data['Freq'] * (1. - islastprob)
            data2 = pd.read_csv(surl)
            data2['Gender'] = 'L'
            data2['Freq'] = data2.Count / data2.Count.sum() * islastprob
            self.data = pd.concat([self.data,data2], ignore_index=True)
            self.islastprob = islastprob
        else:
            self.islastprob = 0.
        if 'Gender' not in self.data.columns:  
            # the last name data source does not have 'Gender' or 'Freq'
            self.data['Freq'] = self.data.Count.values / self.data.Count.sum()
            self.islastprob = 1.
        self.set_weights(self.data.Freq.values)

    def get_sample(self, gender=None, ethnicity=None):
        reweights = None
        # print(self.data.sample(5).head())
        if gender or ethnicity:
            reweights = self.data.Freq.values
            gender = gender and ('Gender' in self.data.columns)
            if gender:
                # conditional restriction of names based on gender
                reweights[self.data.Gender == ('M' if gender == 'F' else 'F')] = 0.
                reweights[self.data.Gender == ('F' if gender == 'F' else 'M')] /= reweights[
                    self.data.Gender == ('F' if gender == 'F' else 'M')].sum() 
                reweights[self.data.Gender == ('F' if gender == 'F' else 'M')] *= (
                    1. - self.islastprob)
            
            if ethnicity and all((k in self.data.columns) for k in ethnicities):
                # conditional distribution of names based on ethnicity
                assert ethnicity in ethnicities, f'invalid ethnicity: {ethnicity}'
                if gender:
                    counts = self.data[self.data.Gender == 'L'].Count * self.data[
                        self.data.Gender == 'L'][ethnicity]
                    reweights[self.data.Gender == 'L'] = (
                        counts / counts.sum() * self.islastprob)
                else:
                    counts = self.data.Count * self.data[ethnicity]
                    reweights = counts / counts.sum() * self.islastprob

        return super().get_sample(reweights)



class StreetNameSource(Source):
    """Provides the name of a street randomly selected from a 
       also randomly selected city.
      Args:
          furl: the url address providing data on city and streets
    """
    def __init__(self, furl:str, rng:np.random.mtrand.RandomState = None, seed:int = None) -> None:
        super().__init__(furl,rng=rng,seed=seed)

        self.data = pd.read_csv(furl)
        self.set_weights(self.data.Count.values)

    def get_sample(self, city_name):
        # streets = self.data[self.data.city == city_name]['streets'].values
        # sample_weight = np.maximum(0.001,stats.zipf.pmf(np.arange(streets.shape[0]),2))
        # sample_weight /= sample_weight.sum()
        # return super().get_sample(sample_weight, data=streets)
        return super().get_sample()['Street Name']


class StreetNumberSource(object):
    """Generates street number, and apartment numbers when applicable"""
    def __init__(self,furl=None,rng=None,seed=None,is_residence=True) -> None:
        self.rng = {}
        self.rng['number_length'] = np.random.RandomState(seed=seed)
        self.rng['number'] = np.random.RandomState(seed=seed+1)
        self.is_residence = is_residence

    def get_sample(self, isapartment=False, is_multifam=False):
        """
        Generates a street number sample.

        Args:
            isapartment (bool, optional): A flag to indicate if the
                address is an apartment. Defaults to False.
            is_multifam (bool, optional): A flag to indicate if the
                address is for a multifamily building. Defaults to False.

        Returns:
            tuple: A tuple containing the street number and apartment number (if applicable).

        """
        length = max(1+int(self.is_residence), self.rng['number_length'].choice(
            np.arange(1,7),p=distribution_addr_digits))
        address = get_no(self.rng['number'],length)
        if isapartment:
            length = self.rng['number_length'].choice(
                np.arange(1,4),p=distribution_apt_digits)
            apt_no = get_no(self.rng['number'],length)
            return address, apt_no
        elif is_multifam:
            num_mf  = 1 + self.rng['number_length'].choice(
                np.arange(1,8), p=distribution_num_mf)
            address += chr(ord('@')+get_no(self.rng['number'],1,base=num_mf,
                reject=None,return_int=True)+1)
        return address, None


class AddressSource(Source):
    """Generate addresses"""
    def __init__(self,furl=None,apartment_prob=0.145, multifam_prob=0.1,
            is_residence=True, rng=None,seed=None) -> None:
        super().__init__(furl,rng=rng,seed=seed)

        self.streetname = StreetNameSource(furl,rng=rng,seed=seed+1)
        self.streetnumber = StreetNumberSource(rng=rng,seed=seed+2,is_residence=is_residence)
        self.apartment_prob = apartment_prob
        self.multifam_prob = multifam_prob

    def get_sample(self, city):
        """Generates an street name along with the street number
        and apartment number if applicable from a provided city.
        Returns:
            Tuple of street name, street number, and apartment number
        """
        no, apt = self.streetnumber.get_sample(
            self.rng.uniform(size=1) < self.apartment_prob,
            self.rng.uniform(size=1) < self.multifam_prob)
        return self.streetname.get_sample(city), no, apt

    @staticmethod
    def state_stringify_address(_state='MD'):
        def stringify_address(streetname, streetno, aptno, city=None, 
                state=_state, zipcode=None, rng=None, **kwargs):
            """Converts an address to a string format."""
            
            address = ''.join([f'{streetno} ', streetname, (
                '' if (aptno is None or (
                    isinstance(aptno, float) and np.isnan(aptno)) or aptno <= 0)
                else (f" Apt {(int(aptno) if isinstance(aptno,float) else aptno)}" 
                    if (np.random if rng is None else rng).uniform(size=1) > 0.5 
                    else f" #{aptno}"))])
            if city:
                address += f', {city}'
            if state:
                address += f', {state}'
            if zipcode:
                address += f' {zipcode}'
            return address
        return stringify_address


class ContactInfoSource(Source):
    
    """
    A class for generating contact information:
    email and phone numbers.

    Attributes:
        global_email_db (list): A list of generated email addresses.

    Methods:
        reset_global_email_db(self):
            Resets the global email database. This database contains
            generated cases to avoid repetition.

        get_sample_ph(self,area_code):
            Generates a phone number sample.

        get_sample_email(self,first,last,byear,age):
            Generates an email sample.

    """
    def __init__(self, furl:str = None, rng=None, seed:int = None) -> None:
        super().__init__(furl,rng=rng,seed=seed)
        self.global_email_db = []

    def reset_global_email_db(self):
        self.global_email_db = []

    def get_sample_ph(self,area_code:str) -> str:
        """
        Generates a phone number sample from the area code
        provided as string. 
        Returns a phone number as string.
        """
        if area_code is None or np.isnan(float(area_code)):
            return
        return area_code + get_no(self.rng,7,reject=(lambda x: '911' in x, lambda y: ''))

    def get_sample_email(self, first:str, last:str, byear:int, age:int):
        """
        Generates an email sample.

        Args:
            first: A string specifying the first name.
            last: A string specifying the last name.
            byear: An integer specifying the birth year.
            age: An integer specifying the age.

        Returns:
            str: An email address.

        """
        
        for tryno in range(5):
            etype = self.rng.randint(0,5)
            ext = ['com','net']
            if age < 29:
                ext.append('edu')
            ext = self.rng.choice(ext)
            domain = (self.rng.choice(['msu', 'umd']) 
                if ext == 'edu' else (
                    self.rng.choice(['protonmail',last]) 
                    if ext == 'net' else 
                    self.rng.choice(['gmail', 'hotmail', 'msn', 'aol'])))
            if etype == 1:
                email = '@'.join(['.'.join([last,first]), '.'.join([domain,ext])])
            if etype == 2:
                email = '@'.join([self.rng.choice(['.','_']).join([
                    first,
                    self.rng.choice([
                        get_no(self.rng,self.rng.randint(2,5)),
                        self.rng.choice([str(byear)[-2:], str(byear)])])
                    ]), 
                    '.'.join([domain,ext])])
            if etype == 3:
                email = '@'.join([self.rng.choice(['.','_']).join([
                    last,
                    self.rng.choice([
                        get_no(self.rng,self.rng.randint(2,5)),
                        self.rng.choice([str(byear)[-2:], str(byear)])])
                    ]), 
                    '.'.join([domain,ext])])
            else:
                email = '@'.join(['.'.join([first,last]), '.'.join([domain,ext])])
            if email not in self.global_email_db:
                self.global_email_db.append(email)
                break
        return email


class RecordGenerator(object):
    """A class for generating tax payer records.
    
    Args:
        config (YmlConfig): An instance of YmlConfig class
            containing the configuration data.
        rng (np.random.RandomState, optional): An instance of numpy's
            random number generator. Defaults to None. If not
            provided, it will be generated with the seed.
        _type (TaxPayerType, optional): An instance of TaxPayerType
            enum class representing the type of tax payer.
            Defaults to TaxPayerType.individual.
        seed (int, optional): A seed value for the random number
            generator. Defaults to None. If rng and seed are not provided,
            a random seed will be generated.
        debug (int, optional): A flag to enable debug mode. Defaults to 0.
    """
    
    def __init__(self, config:YmlConfig, rng=None, _type=TaxPayerType.individual, seed:int = None, 
                 state=None, debug=0, logger=None) -> None:
        
        assert _type in TaxPayerType, f'input {_type} is not a valid TaxPayerType'
        self._type = _type
        self.debug = debug
        self.state = state
        self.seed = (np.random.randint(0,np.iinfo(np.int32).max) if seed is None and rng is None else seed)
        self.rng = rng if rng else np.random.RandomState(seed=self.seed)
        rseed = lambda: self.rng.randint(0,np.iinfo(np.int32).max)
        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if logger is None else (
            logger(self.__class__.__name__, self.debug) if callable(logger) else logger)
        # get the config data
        self.firstname = self.lastname = self.city = self.address = self.zip = \
            self.age = self.middlename = self.contactinfo = None

        # read in data and populate random generation objects
        if _type == TaxPayerType.individual:
            for src, furl in config.items(contains=['source']):
                self.logger.debug(f'{src:20s} | reading in data from: {furl}')
                if src == 'source_firstname':
                    assert self.firstname is None
                    self.firstname = NameSource(furl,seed=rseed())
                elif src == 'source_lastname':
                    assert self.lastname is None
                    self.lastname = NameSource(furl,seed=rseed())
                elif src == 'source_city':
                    assert self.city is None
                    self.city = CitySource(furl,seed=rseed())
                elif src == 'source_streetname':
                    assert self.address is None
                    self.address = AddressSource(furl,seed=rseed())
                elif src == 'source_zipcode':
                    assert self.zip is None
                    self.zip = ZipSource(furl,seed=rseed())
                elif src == 'source_age':
                    assert self.age is None
                    self.age = AgeSource(furl,seed=rseed())
                else:
                    err_msg = f'could not find a place for configuration data: {src}: {furl}'
                    self.logger.error(err_msg)
                    raise KeyError(err_msg)

            self.contactinfo = ContactInfoSource(seed=rseed())
            self.middlename = NameSource(
                furl=self.firstname.src_data, surl=self.lastname.src_data, 
                ismiddle=True,seed=rseed())
        else:
            raise NotImplementedError(f'{_type} is not currently impelmented')
        self.id = IdSource(seed=rseed())

    def get_record(self, _type=None):
        """Generates a tax payer record based on the provided type.
        """
        if _type is None:
            _type = self._type
        if _type == TaxPayerType.individual:
            age = 0
            while age < 18:
                # we won't have tax records for folks under age 18
                age, bday = self.age.get_age_birthday()

            firstname_rec = self.firstname.get_sample()
            firstname, gender = firstname_rec['Name'], firstname_rec['Gender']
            lastname_rec = self.lastname.get_sample()
            ethn_distb = np.array([lastname_rec[k] for k in ethnicities])
            lastname, ethnicity = lastname_rec['Name'], self.rng.choice(ethnicities,
                p=ethn_distb/ethn_distb.sum())
            lastname, maiden = (self.lastname.get_sample()['Name'] if gender == 'F' else lastname), (
                lastname if gender == 'F' else None)
            middle = self.middlename.get_sample(gender=gender,ethnicity=ethnicity)
            city, zipcode = self.city.get_sample()
            acode = self.zip.get_sample(city=city)
            street, streetno, aptno = self.address.get_sample(city)
            taxid = self.id.get_sample(return_int=True)
            try:
                phno, email = self.contactinfo.get_sample_ph(acode), self.contactinfo.get_sample_email(firstname,lastname,bday[-1],age)
            # try:
                return Record(
                        taxpayertype=_type._name_,
                        firstname=firstname,
                        lastname=lastname,
                        middlename=middle['Name'],
                        ethnicity=ethnicity,
                        compositename=' '.join([firstname, middle['Name'], lastname]),
                        maidenname=maiden,
                        birthday=pd.Timestamp(bday[-1],bday[0],bday[1]),
                        taxid=taxid,
                        streetno=streetno,
                        aptno=int(aptno) if aptno else aptno,
                        streetname=street,
                        city=city,
                        state=self.state,
                        zipcode=int(zipcode),
                        phoneno=int(phno) if phno else phno,
                        email=email,
                        rng=self.rng
                        )
            except TypeError as e:
                self.logger.critical(f'''Error creating record:
firstname_rec = {firstname_rec}
firstname, gender = {firstname}, {gender}
lastname_rec = {lastname_rec}
ethn_distb = {ethn_distb}
lastname, ethnicity = {lastname}, {ethnicity}
maiden = {maiden}
middle = {middle["Name"]}
city, zipcode = {city}, {zipcode}
acode = {acode}
street, streetno, aptno = {street}, {streetno}, {aptno}
birthday = {bday}
                ''')
                raise e
        else:
            raise NotImplementedError(f'{self._type} is not currently implemented')

    def gen_records(self, num:int = 1, as_df:bool = False):
        """Generates multiple tax payer records and returns as a
        list of Record objects or a DataFrame if as_df is True.
        Args:
            num: int. The number of records
            as_df: bool.A flag to indicate a DataFrame format for
                 the output. Default to False. 
        Returns:
            If num is 1, it returns a single Record object. If num
            is greater than 1, it returns a list of Record objects
            of length num, or a DataFrame if as_df is True.
        """
        recs = []
        iterator = (tqdm(range(num),total=num,desc='Generating reference records') 
            if tqdm is not None and num > 30 and self.debug else range(num))
        for n in iterator:
            recs.append(self.get_record(self._type))

        df = None
        if as_df:
            df = Record.as_dataframe(recs)
        if num == 1:
            return recs[0], df
        else:
            return recs, df


# ---------  "main" functions  --------
# -------------------------------------
def gen_records_from_data(data_config, debug=0, numrec=1, as_df=False, 
        write_to_db=False, overwrite=False, add_unique_label=False,
        seed=42, display=False, state='MD', **kwargs):
    
    """
    Generate synthetic records using the configuration specified in
    data_config.

    Args:
    -----------
    data_config : YmlConfig or str
        The configuration file or object for the RecordGenerator.
    debug : int, default 0
        The debug level.
    numrec : int, default 1
        The number of records to generate.
    as_df : bool, default False
        If True, return the generated records as a pandas dataframe.
        Otherwise, return a list of Record objects.
    write_to_db : bool, default False
        If True, write the generated records to an SQL database.
    overwrite : bool, default False
        If True, overwrite the existing records in the SQL database.
    add_unique_label : bool, default False
        If True, add a unique metric label/id to the generated records.
    seed : int, default 42. 
        The random seed to use for generating records.
    display : bool, default False
        If True, display the generated records.

    Returns:
    --------
    If as_df is True:
        data : pandas dataframe
            The generated records as a pandas dataframe.
        yml : YmlConfig
            The configuration object used for generating the records.
    Else:
        recs : list of Record objects
            The generated records as a list of Record objects.
        yml : YmlConfig
            The configuration object used for generating the records.
    """
    
    if isinstance(data_config, YmlConfig):
        yml = data_config
    else:
        yml = YmlConfig(data_config,base_str='rec_gen', 
            auto_update_paths=True,debug=max(debug-1,0),logger=get_az_logger)
    sqlcfg = SQLConfig(yml['dbconfig'], logger=get_az_logger, auto_update_paths=True) if write_to_db else None
    data = dbconn = None

    if write_to_db and not(overwrite):
        dbconn = DbConnectGenerator(config=sqlcfg)

        with dbconn.gen_connection(create_nonexist=True) as conn:
            if sqlcfg['reftable'] in conn.table_names():
                # logger.debug('retrieving existing reference records')
                data = pd.read_sql(sqlcfg['reftable'],con=conn.connection)
                if not(as_df) and data.shape[0]:
                    data = Record.from_dataframe(data)
        if (data is not None) and len(data):
            logger.debug('found existing records in sql DB, returning these...')
            if add_unique_label and ('metric_id' not in data.columns):
                warn('metric_id requested but not found in the extant data')
            return data, yml
    rec_gen = RecordGenerator(config=yml, seed=seed, state=state, logger=get_az_logger, debug=max(debug-1,0))
    recs, data = rec_gen.gen_records(num=numrec, as_df=(write_to_db or as_df))
    if add_unique_label:
        logger.debug('adding unique (uncorruptible) metric label/id')
        if data is not None:
            data['metric_id'] = np.arange(data.shape[0])
        for _id, rec in enumerate(recs):
            rec.update(dict(metric_id=_id))

    if write_to_db:
        if dbconn is None:
            dbconn = DbConnectGenerator(config=sqlcfg)
        with dbconn.gen_connection(create_nonexist=True) as conn:
            conn.upload_df_to_table(data, sqlcfg['reftable'], 
                if_exists=('replace' if overwrite else 'append'))
            logger.debug(f'wrote reference data to SQL table: {sqlcfg["reftable"]}')

            
    elif display:
        print(data.head())
    if as_df:
        return data, yml
    else:
        return recs, yml
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''
generate fake name/record data with deviations for matching algorithm dev
        
example call:
    python datagen.py --data-dir ./tests/ --add-unique-label --numrec 100000 --write-to-db
''')
    parser.add_argument('--data-dir' ,'-d', dest='data_config', 
        nargs='?', required=False, default=None, 
        help='directory containing name and street distributional data')
    parser.add_argument('--debug', '-v', nargs='?', type=int, required=False, const=1, 
        default=0, help='level of debug output printing')
    parser.add_argument('--seed', '-s', type=int, required=False, 
        default=None, help='seed for generating random data, default is None')
    parser.add_argument('--numrec', '-n', type=int, required=False, 
        default=5, help='number of records to generate, default is 5')
    parser.add_argument('--state', type=str, required=False, 
        default='MD', help='the state which is represented in the records, default is "MD"')
    parser.add_argument('--write-to-db', nargs='?', dest='write_to_db', 
        type=bool, const=True, default=False, required=False, 
        help='whether to write to the DB, default is False')
    parser.add_argument('--overwrite', '-o', nargs='?', type=bool, required=False, const=True, 
        default=False, help='overwrite existing records (default is False, which will append records)')
    parser.add_argument('--add-unique-label', '-l', nargs='?', dest='add_unique_label', 
        type=bool, required=False, const=True, default=False, help=('add unique id/label that '
        'cannot be corrupted, used for validating metrics on attempted matching'))
    
    args = parser.parse_args()
    if args.debug > 1:
        print("args:", args.__dict__)

    recs, df_reference, yml = gen_records_from_data(display=True, **args.__dict__)



