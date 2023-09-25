'''Data generation tools - task data and faux metrics for exercising recommendation algorithms'''
import argparse
from os import listdir, environ, path, PathLike
import numpy as np
from scipy import stats
import pandas as pd
from datetime import datetime
from itertools import chain
from enum import Enum, auto
from warnings import warn
from collections import Counter
from typing import List

from rsidatasciencetools.config.baseconfig import YmlConfig, get_stdout_logger
from rsidatasciencetools.sqlutils.sqlconfig import SQLConfig
from rsidatasciencetools.sqlutils.sql_connect import DbConnectGenerator
from rsidatasciencetools.datautils.datagen import (Record, Source, 
    IdSource, NameSource, random_datetimes, round_dt_to, WorkingSchedule)
from rsidatasciencetools.azureutils.az_logging import get_az_logger


logger = get_az_logger(__name__)


try:
    from tqdm import tqdm 
except ImportError:
    tqdm = None


class Complexity(Enum):
    low = auto()
    medium = auto()
    high = auto()


class ReqExperience(Enum):
    low = auto()
    medium = auto()
    high = auto()


class ReqKnowledge(Enum):
    general = auto()
    specific = auto()


class TimeFrame(Enum):
    less10min = auto()
    less30min = auto()
    less1hour = auto()
    less4hours = auto()
    less1day = auto()
    less2day = auto()
    less1week = auto()
    greater1week = auto()


class UserSpec(Enum):
    username = auto()
    role = auto()
    tenure = auto()
    startdate = auto()


class TaskSpec(Enum):
    taskname = auto()
    complexity = auto()  # {low, medium, high}, 
    requiredexperience = auto()  # {low, medium, high}. 
    backgroundknowledge = auto()  # {general, specific}. 
    expectedtimeframe = auto()  # {<10 min, <30 minutes, <1 hour, <4 hours, <1 day, <2 days, <1 week, >1 week}, 
    tf_variation = auto()
    role = auto()


class TaskMetrics(Enum):
    taskname = auto()
    reporter = auto()
    lastuser = auto()
    lastuserrole = auto()
    usermodlist = auto()
    complexity = auto()  # {low, medium, high}, 
    expectedtimeframe = auto()  # {<10 min, <30 minutes, <1 hour, <4 hours, <1 day, <2 days, <1 week, >1 week}, 
    requiredexperience = auto()  # {low, medium, high}. 
    backgroundknowledge = auto()  # {general, specific}. 
    createdatetime = auto()
    startdatetime = auto()
    updatedatetime = auto()
    closedatetime = auto()
    numupdates = auto()
    elapsedtime_min = auto()
    opentime_days = auto()
    # reopenedcount = auto()    


def is_normal_schedule(thres, rng=np.random, schedule_preference=(
        WorkingSchedule.workhours_weekday,
        WorkingSchedule.workhours,
        WorkingSchedule.unrestricted)):
    draw = rng.uniform()
    assert 0 < thres < 1, 'thres should be: 0 < thres < 1'
    if  thres > draw:
        return schedule_preference[0]
    elif thres + (1.0-thres)/2.0 > draw:
        return schedule_preference[1]
    else:
        return schedule_preference[2]


class Task(Record):
    min_minutes_duration = 2.
    def __init__(self, **kwargs) -> None:
        super().__init__(datatype=TaskSpec, 
            corruptible={}, lenth_changable={}, 
            autopop={},
            **kwargs)

    def get_actual_duration_minutes(self, tenure=None, rng=np.random):
        base_time_minutes = float(Task.get_median_timedelta(self.expectedtimeframe
            ) / pd.Timedelta(minutes=1))
        scale = np.sqrt(self.tf_variation)
        expr_offset =  ((base_time_minutes / 3.) * rng.rayleigh(scale=max(0.01, (
            Task.translate_median_experience(self.requiredexperience) - tenure)))
            if tenure else 0.0)
        dur_min = max(self.min_minutes_duration, rng.normal(
            loc=base_time_minutes + expr_offset, scale=scale))
        err_msg = 'returned duration must be positive'
        dur_min <= 0 and self.logger.error(err_msg)
        assert dur_min > 0, err_msg
        return dur_min

    @staticmethod
    def translate_median_experience(requiredexperience):
        one_year = 1.0  # pd.Timedelta(days=365)
        if requiredexperience == ReqExperience.low:
            return one_year
        elif requiredexperience == ReqExperience.medium:
            return 2*one_year
        elif requiredexperience == ReqExperience.high:
            return 5*one_year
        
    @staticmethod
    def timeframe_to_n_user_augment(timeframe):
        v = timeframe.value
        if v < 3:
            return 0
        elif 3 <= v < 5:
            return 1
        else:
            return 2

    @staticmethod
    def get_median_timedelta(expectedtimeframe):
        if expectedtimeframe == TimeFrame.less10min:
            return pd.Timedelta(minutes=5)
        elif expectedtimeframe == TimeFrame.less30min:
            return pd.Timedelta(minutes=15)
        elif expectedtimeframe == TimeFrame.less1hour:
            return pd.Timedelta(minutes=30)
        elif expectedtimeframe == TimeFrame.less4hours:
            return pd.Timedelta(hours=2)
        elif expectedtimeframe == TimeFrame.less1day:
            return pd.Timedelta(hours=12)
        elif expectedtimeframe == TimeFrame.less2day:
            return pd.Timedelta(days=1)
        elif expectedtimeframe == TimeFrame.less1week:
            return pd.Timedelta(days=3.5)
        elif expectedtimeframe == TimeFrame.greater1week:
            return pd.Timedelta(days=12)

class TaskRecord(Record):
    """The Record class provides a way to store and manipulate
    records of data according to the specified data type. 
    The data type is defined by the `datatype parameter and should be
    an instance of the Enum class.
    
    Args:
        specified in 'TaskMetrics'
    
    Parent class args: passed by definition of this record
    `datatype`: enum class that defines the data fields that the
        Record instance can contain.
    `corruptible` and `lenth_changable` parameters are Enum instances
        that determine whether a specific data field can be corrupted
        and/or have its length changed. 
    `autopop`: dictionary containing functions that can be used to
        automatically generate data for certain fields.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(datatype=TaskMetrics, 
            corruptible={}, lenth_changable={}, 
            autopop={
                'elapsedtime_min': lambda kwargs, rng: float(
                    (kwargs['closedatetime']-kwargs['startdatetime'])/pd.Timedelta(minutes=1)),
                'opentime_days': lambda kwargs, rng: float(
                    (kwargs['closedatetime']-kwargs['createdatetime'])/pd.Timedelta(days=1))             
                },
            **kwargs)


class RoleSource(Source):
    def __init__(self, furl:str = None, rng=None, seed:int = None):
        super().__init__(
            src_data=furl, rng=rng, seed=seed) 
        if furl is None:
            df = pd.DataFrame(dict(
                Role=['csr', 'payments', 'audit', 'supervisor', 'admin'],
                Level=[1,2,3,4,5],
                IsEssential=[0,1,0,1,1],
                Population=[0.4,0.3,0.2,0.05,0.05]))
        else:
            df = pd.read_csv(furl)
        self.data = df
        self.set_weights(df.Population.values)

    def get_level(self, role):
        # role = role if isinstance(role, str) else role.name
        return self.data[self.data.Role == role].to_dict('records')[0]['Level']
    
    def rolelist(self, level_above=None, level_below=None):
        assert (level_below is None) or (level_above is None) or (0 < level_above < level_below), 'levels not aligned'
        data = self.data if level_above is None else self.data[self.data.Level >= level_above]
        if level_below:
            data = data[data.Level <= level_below]
        return data.Role.values

    def get_sample(self, level_above=None) -> str:
        """Gets a random sample of the role set.
        """
        data = weights = None
        if level_above is not None:
            data = self.data if data is None else data
            data = data[data.Level >= level_above]
            weights = data.Population.values / data.Population.sum()

        sample = super().get_sample(sample_weight=weights, data=data)
        return sample['Role']
    
    @property
    def highest_role(self):
        highest_level_role = self.data[self.data.Level == self.data.Level.max()]['Role']
        assert highest_level_role.shape[0], (
            'multiple roles have the same numeric level')
        return highest_level_role.values[0]

    @property
    def essential_roles(self):
        ess_roles = self.data[self.data.IsEssential > 0]['Role']
        return ess_roles.values


class TaskDatabase(IdSource):
    """It generates a random ID database with the specifications provided.

    Args:
        role_source (RoleSource): the RoleSource object for drawing 
            role types.
        furl (str or Path): The file location of the data source,
            if needed. Default to None.
        rng (np.random.Generator): The random number generator.
        seed (int): The seed for the random number generator.
    """
    def __init__(self,role_source:RoleSource=None,*args,**kwargs) -> None:
        super().__init__(*args,**kwargs)
        self.role_source = role_source
        self.tasks = []
        self.tasks_df = None

    def reset_id_db(self):
        self.tasks = []
        return super().reset_id_db()
    
    def generate_task_db(self, N):
        self.reset_id_db()
        for _ in range(N+10):
            _id = self.get_sample()
            if _id is not None:
                task = self.generate_task(_id)
                self.tasks.append(task)
            if len(self.tasks) == N:
                break

    @property
    def taskdata(self):
        '''return a DataFrame representation of the task type objects'''
        if (self.tasks is not None and 
                len(self.tasks) > 0):
            if self.tasks_df is None or len(self.tasks_df) != len(self.tasks):
                # print('elements names/types: ', [(k, v, type(v)) 
                #     for k, v in self.tasks[0].iteritems()])
                converters = {k: lambda x: x.name 
                    for k in self.tasks[0] 
                    if isinstance(self.tasks[0][k], Enum)
                }
                self.tasks_df = TaskRecord.as_dataframe(self.tasks)
                # print('converting enums to strings')
                for k, conv  in converters.items():
                    # print(conv, k)
                    self.tasks_df[k] =  self.tasks_df[k].apply(conv)
                # print('creating DataFrame data:\n', self.tasks_df.head())
            return self.tasks_df.copy()
        else:
            raise AttributeError('tasks attribute is not populated '
                                 'or contains no elements')
    
    def sample_task_from_db(self):
        return self.rng.choice(self.tasks)

    def generate_task(self, name):
        expr = self.rng.choice(list(ReqExperience))
        if expr.value <= ReqExperience.medium.value:
            complx = self.rng.choice(list(Complexity)[:-1])
        else:
            complx = self.rng.choice(list(Complexity)[1:])
        know = (self.rng.choice(list(ReqKnowledge))
            if complx.value >= Complexity.medium.value else ReqKnowledge.general)
        
        # complexity: {low, medium, high}, 
        # requiredexperience: {low, medium, high}. 
        # backgroundknowledge: {general, specific}. 
        base_time = self.rng.randint(1, know.value + expr.value + complx.value)
        variation = self.rng.uniform(0.25, (expr.value + complx.value)/3.0)
        tf = [k for k in list(TimeFrame) if k.value == base_time][0]
        role = self.role_source.get_sample()
        return Task(taskname=name, role=role, complexity=complx,
                    requiredexperience=expr, backgroundknowledge=know,
                    expectedtimeframe=tf, tf_variation=variation)


class TenureSource(Source):
    """Randomly generates age and birthdays of people.

    Args:
        furl (str): the file URL of the data source
        start (pd.Timestamp): the inception date of the agency. 
            Default is ten years ago from the current system time.
        now (pd.Timestamp): the current time. 
            Default is the current system time.
        rng: an optional random number generator instance
        seed (int): an optional seed value for the random number generator
    """
    def __init__(self, furl:str = None, start=None,  now=None, 
                 rng:np.random.mtrand.RandomState = None, seed:int = None) -> None:
        super().__init__(furl, rng, seed)
        self.now = (pd.Timestamp.now() if now is None else now)
        self.agency_start = (self.now - pd.Timedelta(days=10*365) 
            if start is None else (
                start if isinstance(start, (datetime,pd.Timestamp)) 
                else pd.Timestamp(start)))
        assert isinstance(self.now, pd.Timestamp)
        assert isinstance(self.agency_start, pd.Timestamp)
        self.data = pd.read_csv(furl)
        # only keep tenure ranges that are within the timeframe that the agency has existed
        self.data = self.data[self.data['TenureYearsFrom'] < (
            (self.now - self.agency_start).days / 365.)]
        self.set_weights(self.data.Population.values/self.data.Population.sum())

    def get_tenure_startdate(self, round_to_weekdays=True) -> tuple:
        """Returns a tuple of a random tenure and startdate
        """
        tenure_range = super().get_sample()
        # print('tenure_range', tenure_range)
        start,end = self.now-pd.Timedelta(
            days=365*tenure_range['TenureYearsTo']), self.now - pd.Timedelta(
            days=365*tenure_range['TenureYearsFrom']) 
        # print('start/end:', start,end)
        startdate = random_datetimes(start, end, rng=self.rng)
        if round_to_weekdays:
            startdate = round_dt_to(startdate, round_up=True)
        sday = (startdate.month, startdate.day, startdate.year)
        tenure_years = np.round((self.now - startdate).days / 365.,decimals=2) 
        return tenure_years, sday


class User(Record):
    def __init__(self, **kwargs) -> None:
        super().__init__(datatype=UserSpec, 
            corruptible={}, lenth_changable={}, 
            autopop={},
            **kwargs)


class UserSource(Source):
    
    """
    A class for generating contact information:
    email and phone numbers.

    Args:
        first:NameSource
        last:NameSource
        tenure:TenureSource
        role:RoleSource
        furl:str = None  # pass-through variable, not used 
        rng:RandomState = None
        seed:int = None

    Attributes:
        user_db (list): A list of generated email addresses.

    Methods:
        reset_user_db(self):
            Resets the global email database. This database contains
            generated cases to avoid repetition.

        get_sample(self,area_code):
            Generates a 'User' sample.

        sample_user_from_db(self,role=None):
            Get User sample from pre-generated DB, restrict to 'role' 
            specific if provided.

    """
    def __init__(self, first:NameSource, last:NameSource, tenure:TenureSource, 
                role:RoleSource, furl:str = None, rng=None, seed:int = None) -> None:
        super().__init__(furl,rng=rng,seed=seed)
        self.first = first
        self.last = last
        self.tenure = tenure
        self.role = role
        self.user_db = []
        self.username_db = []

    def reset_global_user_db(self):
        self.user_db = []
        self.username_db = []
        self.user_source = None

    def generate_user_db(self, N):
        self.reset_global_user_db()
        self.add_baseline_users()
        for _ in range(N+10):
            usern = self.get_sample_username()
            if usern is not None:
                user = self.get_sample(usern)
                self.user_db.append(user)
            if len(self.user_db) == N:
                break
        self.user_source = Source(rng=self.rng, seed=self.seed)
        self.user_source.data = pd.DataFrame(dict(
            username=[u.username for u in self.user_db],
            role=[u.role for u in self.user_db],
            tenure=[u.tenure for u in self.user_db],
            startdate=[datetime(
                    year=u.startdate[2],month=u.startdate[0],day=u.startdate[1])
                for u in self.user_db]
        ))

    @property
    def userdata(self):
        if (self.user_source.data is not None and 
                len(self.user_source.data) > 0):
            if isinstance(self.user_source.data, pd.DataFrame):
                return self.user_source.data.copy()
            else:
                return self.user_source.data
        else:
            err_msg = ('user_source.data attribute is not populated '
                'or contains no rows/elements')
            self.logger.error(err_msg)
            raise AttributeError(err_msg)

    def role_daterange(self, role):
        role = role if isinstance(role,str) else role.name
        data = self.userlist(role)
        return data.startdate.min(), data.startdate.max()

    def userlist(self, role):
        data = self.user_source.data
        role = role if isinstance(role,str) else role.name
        return data[data['role'] == role]

    def sample_user_from_db(self, as_df=False, startdate=None, role=None):
        err_msg = 'user database not generated'
        len(self.user_db) <= 0 and self.logger.error(err_msg)
        assert len(self.user_db) > 0, err_msg 
        # assert len(role_subset) > 0, 'no user roles in the database of the type requested'
        if role is None and startdate is None:
            u = self.rng.choice(self.user_db)
            if as_df:
                return self.user_source.data[self.user_source.data == u.username].iloc[0]
            else:
                return u 
        data = self.user_source.data
        if role is not None:
            if isinstance(role, str):
                data = data[data.role == role]
            elif isinstance(role, (np.ndarray,list)):
                data = data[data.role.apply(lambda x: x in role)]
            else:
                err_msg = f'unknown use for type [{type(role)}] for input filter "role"'
                self.logger.error(err_msg)
                raise TypeError(err_msg)
        if startdate is not None:
            # print(f'sample_user_from_db: data \n {data}')
            # print(f'sample_user_from_db: startdate \n {data.startdate}')
            # print('startdate:', startdate)
            data = data[data.startdate <= startdate]
        if data.shape[0] == 0:
            err_msg = 'empty user data from which to sample'
            self.logger.error(err_msg)
            raise Exception(err_msg)
        # NOTE: sample user from the list of users limited by date and role
        u_df = self.user_source.get_sample(sample_weight=None, data=data)
        if u_df is None:
            return None
        if as_df:
            return u_df
            # return pd.DataFrame({k:[v] for k,v in u_df.items()}) if isinstance(u_df,dict) else u_df
        else:
            return [u for u in self.user_db if u.username == u_df['username']][0]
            
    def add_baseline_users(self):
        startdate = self.tenure.agency_start
        startdate = round_dt_to(startdate, st=startdate, round_up=True)
        ten, sday = (
            np.round((self.tenure.now - startdate).days / 365.,decimals=2) ,
            (startdate.month, startdate.day, startdate.year))   

        essential = self.role.essential_roles
        s_i = 0
        for i in range(len(essential)+10):
            usern = self.get_sample_username()
            if usern is not None:
                user = User(
                        username=usern,
                        role=essential[s_i],
                        tenure=ten,
                        startdate=sday
                    )
                self.user_db.append(user)
                s_i += 1
            if s_i == len(essential):
                break
            
    def get_sample(self, username):
        ten, stdt = self.tenure.get_tenure_startdate()
        return User(
            username=username,
            role=self.role.get_sample(),
            tenure=ten,
            startdate=stdt
        )                
                
    def get_sample_username(self, tries:int=10):
        """
        Generates an username sample. Saves in internal DB and 
        forces unique result relative to DB. 

        Args:
            tries: no. of attempts to find unique username

        Returns:
            str: An username.

        """
        for j in range(3):
            first = self.first.get_sample()['Name']
            last = self.last.get_sample()['Name']
            # print(first,last)
            n_digits = 1
            add_numeric = 1
            for i in range(tries//3+1):
                user = (first[:n_digits] + last + (
                    '' if add_numeric <= 1 else str(add_numeric))).lower()
                if user not in self.username_db:
                    self.username_db.append(user)
                    return user
                else:
                    if n_digits > 2:
                        add_numeric += 1
                    else:
                        n_digits += 1
        return None


class TaskRecordGenerator(object):
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
    
    def __init__(self, config:YmlConfig, rng=None, seed:int = None, 
                 df_column_converters=dict(updatedatetime=str), 
                 debug=0, logger=None) -> None:
        
        self.debug = debug
        self.seed = (np.random.randint(0,np.iinfo(np.int32).max) if seed is None and rng is None else seed)
        self.rng = rng if rng else np.random.RandomState(seed=self.seed)
        rseed = lambda: self.rng.randint(0,np.iinfo(np.int32).max)
        self.logger = get_stdout_logger(self.__class__.__name__,self.debug) if logger is None else (
            logger(self.__class__.__name__, self.debug) if callable(logger) else logger)
        # get the config data
        self.firstname = self.lastname = self.user_tenure = self.user_role = \
            self.user_db = self.task_db = None

        # read in data and populate random generation objects
        for src, furl in config.items(contains=['source']):
            if self.debug:
                self.logger.debug(f'{src:20s} | reading in data from: {furl}')
            if src == 'source_firstname':
                assert self.firstname is None
                self.firstname = NameSource(furl,seed=rseed())
            elif src == 'source_lastname':
                assert self.lastname is None
                self.lastname = NameSource(furl,seed=rseed())
            elif src == 'source_user_tenure':
                assert self.user_tenure is None
                self.user_tenure = TenureSource(furl,start=config['agency_start'],seed=rseed())
            elif src == 'source_user_roles':
                assert self.user_role is None
                self.user_role = RoleSource(furl,seed=rseed())
            else:
                err_msg = f'could not find a place for configuration data: {src}: {furl}'
                self.logger.error(err_msg)
                raise KeyError(err_msg)
        
        self.N_users, self.N_tasks = config['number_of_users'], config['number_of_tasks']
        self.M_user_touches = config['avg_num_touches_per_task']
        self.avg_days_to_start_task = config['avg_days_to_start_task']

        self.task_db = TaskDatabase(role_source=self.user_role, seed=rseed())
        self.user_db = UserSource(self.firstname, self.lastname, 
            self.user_tenure, self.user_role, seed=rseed())
        self.df_column_converters = df_column_converters

    def get_record(self):
        """Generates a task record with metrics.
        """

        task = self.task_db.sample_task_from_db()

        # get a viable startdatetime (starting endpoint) for this task
        # given the role which (typically) designated to complete it
        start_dt = self.user_db.role_daterange(task.role)[0]

        # get the task create datetime
        createdttm = random_datetimes(start_dt, 
            self.user_tenure.now,
            roundto=is_normal_schedule(1.0 - 0.05*task.complexity.value, self.rng), 
            rng=self.rng)
        err_msg = (f'new task created datetime[{createdttm}|{createdttm.day_name()}] '
            f'is before the earliest user employment startdate[{start_dt}|{start_dt.day_name()}]')
        createdttm < start_dt and self.logger.error()
        assert createdttm >= start_dt, err_msg
        roles = self.user_role.rolelist(level_above=self.user_role.get_level(task.role))        
        rprt_user = self.user_db.sample_user_from_db(role=roles, startdate=createdttm)

        # get the datetime at which the work begins
        startdatetime = createdttm + pd.Timedelta(days=self.rng.rayleigh(
            scale=self.avg_days_to_start_task))
        
        # poentially update begin work datetime to a weekday on work 
        # hours (to maintain a realistic representation)
        startdatetime = round_dt_to(startdatetime,
            rto=is_normal_schedule(1.0 - 0.05*task.complexity.value, self.rng, 
                schedule_preference=(
                    WorkingSchedule.morning_weekday,
                    WorkingSchedule.workhours,
                    WorkingSchedule.unrestricted)),
            round_up=True, rng=self.rng)

        primary_executor = self.user_db.sample_user_from_db(
            role=self.user_role.rolelist(level_above=self.user_role.get_level(task.role),
                                         level_below=self.user_role.get_level(task.role)+1),
            startdate=startdatetime)
        
        n_users_updated = max(1,self.rng.poisson(lam=self.M_user_touches + 
            max(0, (Task.translate_median_experience(task.requiredexperience) - primary_executor.tenure)) * task.complexity.value/3 + 
            Task.timeframe_to_n_user_augment(task.expectedtimeframe) - 1))

        users = [self.user_db.sample_user_from_db(role=task.role, startdate=startdatetime) 
                for _ in range(n_users_updated-1)]
        users = [u for u in users if u is not None]
        users.append(primary_executor)

        _n_users_updated = len(users)
        assert _n_users_updated == n_users_updated, 'error during additional task user generation'
            
        self.logger.info(f'generation for task: {task}')
        self.logger.info(f'attempted to use createdatetime: {createdttm}')
        self.logger.info(f'users of this role type and their start dates:')
        self.logger.info(f'{self.user_db.userlist(role=task.role)}')
        err_msg = 'no valid users generated for this role and start datetime'
        not(n_users_updated) and self.logger.error(err_msg)
        assert n_users_updated, err_msg
        _elapsedtime_min = task.get_actual_duration_minutes(users[-1].tenure, rng=self.rng)
        
        closedatetime = round_dt_to(startdatetime + pd.Timedelta(minutes=_elapsedtime_min),
                st=startdatetime, minutes_from_edge=Task.min_minutes_duration, 
                rto=is_normal_schedule(1.0 - 0.05*task.complexity.value, self.rng, 
                    schedule_preference=(
                        WorkingSchedule.morning_weekday,
                        WorkingSchedule.workhours,
                        WorkingSchedule.unrestricted)), 
                round_up=True, rng=self.rng)

        elapsedtime_min = float((closedatetime - startdatetime)/pd.Timedelta(minutes=1))
        err_msg = 'final elapsed minutes must be positive'
        elapsedtime_min <= 0 and self.logger.error()
        assert elapsedtime_min > 0, err_msg 

        updatedatetime = []
        if n_users_updated > 1:
            updatedatetime.extend([dt for dt in random_datetimes(
                startdatetime, closedatetime, n=max(2,n_users_updated-1), 
                roundto=True, rng=self.rng)][:(n_users_updated-1)])
        updatedatetime = list(sorted(updatedatetime))
        updatedatetime.append(closedatetime)
    
        return TaskRecord(    
            taskname=task.taskname,
            reporter=rprt_user.username,
            lastuser=users[-1].username,
            lastuserrole=users[-1].role,
            usermodlist=','.join([u.username for u in users]),
            complexity=task.complexity.name,  # {low, medium, high}, 
            expectedtimeframe=task.expectedtimeframe.name,  # {<10 min, <30 minutes, <1 hour, <4 hours, <1 day, <2 days, <1 week, >1 week}, 
            requiredexperience=task.requiredexperience.name,  # {low, medium, high}. 
            backgroundknowledge=task.backgroundknowledge.name,  # {general, specific}. 
            createdatetime=createdttm,
            startdatetime=startdatetime,
            updatedatetime=[str(pd.Timestamp(
                year=ut.year,month=ut.month,day=ut.day, 
                hour=ut.hour,minute=ut.minute)) for ut in updatedatetime],
            closedatetime=closedatetime,
            numupdates=len(users)
            # these are auto-populated:
            # , elapsedtime_min=elapsedtime_min,
            # opentime_days=float((closedatetime - createdttm) / pd.Timedelta(days=1)),
        )


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
        self.task_db.generate_task_db(self.N_tasks)
        self.user_db.generate_user_db(self.N_users)
        iterator = (tqdm(range(num),total=num,desc='Generating task execution records') 
            if tqdm is not None and num > 30 and self.debug else range(num))
        recs = []
        for _ in iterator:
            recs.append(self.get_record())

        df = None
        if as_df:
            df = Record.as_dataframe(recs)
            for k, conv in self.df_column_converters.items():
                df[k] = df[k].apply(conv)
        if num == 1:
            return recs[0], df
        else:
            return recs, df


# ---------  "main" functions  --------
# -------------------------------------
def gen_records_from_data(data_config, debug=0, numrec=1, as_df=True, 
        write_to_db=False, overwrite=False, 
        # add_unique_label=False,
        seed=42, display=False, **kwargs):
    
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
    add_unique_label : bool, default False -- !!!not in use for this gen tool!!!
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
        yml = YmlConfig(data_config,base_str='task_user', 
            auto_update_paths=True,logger=get_az_logger, debug=max(0,debug-1))
    sqlcfg = SQLConfig(yml['dbconfig'], auto_update_paths=True, logger=get_az_logger, 
                       debug=max(0,debug-1)) if write_to_db else None
    debug > 1 and print(sqlcfg)
    data = dbconn = None

    if write_to_db and not(overwrite):
        dbconn = DbConnectGenerator(config=sqlcfg)

        with dbconn.gen_connection(create_nonexist=True) as conn:
            if sqlcfg['reftable'] in conn.table_names():
                # debug and print('retrieving existing reference records')
                data = pd.read_sql(sqlcfg['reftable'],con=conn.connection)
                if not(as_df) and data.shape[0]:
                    data = Record.from_dataframe(data)
        if (data is not None) and len(data):
            logger.debug('found existing records in sql DB, returning these...')
            # if add_unique_label and ('metric_id' not in data.columns):
            #     warn('metric_id requested but not found in the extant data')
            return data, yml
    rec_gen = TaskRecordGenerator(config=yml, seed=seed, debug=max(debug-1,0))
    recs, data = rec_gen.gen_records(num=numrec, as_df=(write_to_db or as_df))
    # if add_unique_label:
    #     debug and print('adding unique (uncorruptible) metric label/id')
    #     if data is not None:
    #         data['metric_id'] = np.arange(data.shape[0])
    #     for _id, rec in enumerate(recs):
    #         rec.update(dict(metric_id=_id))

    if write_to_db:
        if dbconn is None:
            dbconn = DbConnectGenerator(config=sqlcfg)
        with dbconn.gen_connection(create_nonexist=True) as conn:
            conn.upload_df_to_table(data, sqlcfg['reftable'], 
                if_exists=('replace' if overwrite else 'append'))
            logger.debug(f'wrote task metrics data to SQL table: {sqlcfg["reftable"]}')

            conn.upload_df_to_table(rec_gen.task_db.taskdata, sqlcfg['tasks'], 
                if_exists=('replace' if overwrite else 'append'))
            logger.debug(f'wrote reference task data to SQL table: {sqlcfg["tasks"]}')
            
            conn.upload_df_to_table(rec_gen.user_db.userdata, sqlcfg['users'], 
                if_exists=('replace' if overwrite else 'append'), debug=1)
            logger.debug(f'wrote reference user data to SQL table: {sqlcfg["users"]}')
            
    elif display and data is not None:
        logger.debug(f'data | columns: {data.columns}, shape: {data.shape}')
        logger.info(data.head())
    if as_df:
        return data, yml
    else:
        return recs, yml
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='''
generate fake task/user data with variation for recommendation engine algorithm dev
        
example call:
    python datagen.py --data-dir ../tests/task_user_metrics.yml --add-unique-label --numrec 100000 --write-to-db
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
    parser.add_argument('--write-to-db', nargs='?', dest='write_to_db', 
        type=bool, const=True, default=False, required=False, 
        help='whether to write to the DB, default is False')
    parser.add_argument('--overwrite', '-o', nargs='?', type=bool, required=False, const=True, 
        default=False, help='overwrite existing records (default is False, which will append records)')
    # parser.add_argument('--add-unique-label', '-l', nargs='?', dest='add_unique_label', 
    #     type=bool, required=False, const=True, default=False, help=('add unique id/label that '
    #     'cannot be corrupted, used for validating metrics on attempted matching'))
    args = parser.parse_args()
    if args.debug > 1:
        print("args:", args.__dict__)
    
    # For local debug testing VS code:
    # if args.__dict__['data_config'] is None:
    #     args.__dict__['data_config'] = path.join(path.dirname(path.abspath(__file__)), '..', 'tests')
    #     args.__dict__['debug'] = 2
    #     args.__dict__['numrec'] = 10000
    
    recs, yml = gen_records_from_data(display=True, **args.__dict__)