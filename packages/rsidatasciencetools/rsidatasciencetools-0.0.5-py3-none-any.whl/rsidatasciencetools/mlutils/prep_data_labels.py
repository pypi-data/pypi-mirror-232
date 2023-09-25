'''clean and prep labels for audit data'''
import pandas as pd
import numpy as np
import os
from ..sqlutils import sql_connect, sqlconfig
# from mlutils.corp_tax_audit_features import get_query_lut


def convert(x,debug=0):
    if debug:
        print(type(x),x)
    if isinstance(x,float):
        if np.isnan(x):
            return np.nan
        else:
            return x
    elif '.' not in x:
        return 0.0
    else:
        stripstr = (x.replace(',','').replace('$','').strip())
        if ('(' in stripstr) and (')' in stripstr):
            return -float(stripstr.strip('()'))
        else:
            return float(stripstr)

def fix_code(code):
    code = code.lower()
    if code.endswith('interpretation'):
        return 'code interpretation'
    elif code.startswith('misclass'):
        return 'misclassification'
    elif code.startswith('voluntary dis'):
        return 'voluntary disclosure'
    else:
        return code

def fix_date(date):
    dash, slash = '-' in date, '/' in date
    if len(date.split('-')) == 3 or len(date.split('/')) == 3:
        d,m,y = date.split('-' if dash else '/')
        if len(y) != 4:
            if not(y.startswith('2')):
                y = '2' + y
            return ('-' if dash else '/').join([d,m,y])
        return date
    if dash:
        if len(date.split('-')) < 2:
            raise ValueError('this date is indecipherable')
        m,dy = date.split('/')
        d,y = dy[:-4], dy[-4:]
        return '-'.join([d,m,y])        
    elif slash:
        if len(date.split('/')) < 2:
            raise ValueError('this date is indecipherable')
        m,dy = date.split('/')
        d,y = dy[:-4], dy[-4:]
        return '/'.join([d,m,y])


def add_period_of_interest(audit_labels, dbconn):
    # add period of investigation from varied sources (SLIM_AUDIT_EXTRACT 
    # for legacy audits, AUDIT_DATAMART for more current audits)
    period_from_date, period_to_date, is_legacy = [], [], []
    to_remove = []
    to_remove_code = []
    has_alt_case_id = []
    with dbconn.gen_connection() as conn:
        for i, row in audit_labels.iterrows():
            if np.isnan(row.case_id) or row.case_id is None:
                data = pd.read_sql(f'''
                    SELECT *
                    FROM dbo.SLIM_AUDIT_EXTRACT
                    WHERE business_id={row.business_id}
                    ''', conn.connection)
                is_legacy.append(True)
                # print('>>>>>>>> no case_id', row.business_id)
                if data.shape[0] > 1:
                    data['original_completed_date'] = data['original_completed_date'].apply(pd.Timestamp)
                    data = data[np.abs(data.original_completed_date - row.initial_approval_date) < pd.Timedelta(days=2)]
                    # print('new data shape: ', data.shape[0])
                if data.shape[0] == 0:
                    period_from_date.append(None)
                    period_to_date.append(None)
                    to_remove.append(i)
                    to_remove_code.append(row.issue_code)
                    has_alt_case_id.append(False)
                    continue
                if data.shape[0] > 1: 
                    print('>>>>>>>> no case_id', row.business_id)
                    print('audit label:', row.initial_approval_date)
                    print(f'retrieved cases:\n{data.original_completed_date}')
                    raise AssertionError('SLIM_AUDIT_EXTRACT: wrong number of elements '
                                        f'retrieved: no data or ambiguous ({data.shape[0]})')
                period_from_date.append(data['period_from_date'].iloc[0])
                period_to_date.append(data['period_to_date'].iloc[0])
            else:
                data = pd.read_sql(f'''
                SELECT *
                FROM dbo.AUDIT_DATAMART
                WHERE case_id={int(row.case_id)}
                ''', conn.connection)

                is_legacy.append(False)
                if data.shape[0] == 0:
                    data = pd.read_sql(f'''
                        SELECT *
                        FROM dbo.AUDIT_DATAMART
                        WHERE primary_id={int(row.business_id)} AND 
                            last_approval_updated_date='{row.initial_approval_date}'
                        ''', conn.connection)
                    # print('attempted to find alt case_id, recs found: ', data.shape[0])
                    if data.shape[0] > 0:
                        assert audit_labels.business_id.loc[i] == row.business_id
                        audit_labels.loc[i, 'case_id'] = data.iloc[0].case_id
                if data.shape[0] == 0:
                    period_from_date.append(None)
                    period_to_date.append(None)
                    to_remove.append(i)
                    to_remove_code.append(row.issue_code)
                    has_alt_case_id.append(pd.read_sql(f'''
                        SELECT *
                        FROM dbo.AUDIT_DATAMART
                        WHERE primary_id={int(row.business_id)}
                        ''', conn.connection).shape[0] > 0)
                    continue
                if data.shape[0] > 1: 
                    # print('case_id', row.case_id, row.business_id)
                    raise AssertionError('AUDIT_DATAMART: wrong number of elements retrieved: '
                                        f'no data or ambiguous ({data.shape[0]})')
                period_from_date.append(data['first_period'].iloc[0])
                period_to_date.append(data['last_period'].iloc[0])

    audit_labels['first_period'] = period_from_date
    audit_labels['last_period'] = period_to_date
    audit_labels['first_period'] = audit_labels['first_period'].apply(
        lambda x: None if x is None else pd.Timestamp(x)) 
    audit_labels['last_period'] = audit_labels['last_period'].apply(
        lambda x: None if x is None else pd.Timestamp(x))

    print(f'total rows {audit_labels.shape[0]} (those with invalid periods defined: '
        f'{pd.isnull(audit_labels.first_period).sum()})')

    audit_labels_toWrite = audit_labels.copy()
    audit_labels_toWrite.drop(audit_labels.index[pd.isnull(audit_labels.first_period)],inplace=True)
    print(f'total rows {audit_labels_toWrite.shape[0]}')
    # audit_labels_toWrite.head()

    return audit_labels, audit_labels_toWrite

def clean_audit_label_data(
        audit_files='SEA-audit-labeled-citations.csv',
        audit_data_loc='/home/dtladmin/Work/projects/SEA-audit',
        outfile='SEA-audit-labeled-cit-cleaned.csv',
        write_to_file=False):

    # labels = pd.read_csv(os.path.join(audit_data_loc))
    if isinstance(audit_files,(os.PathLike,str)):
        audit_files = [audit_files]
    # clean the column labels and extract the assessment amounts as floats
    audit_labels = pd.DataFrame({})
    for f in audit_files:
        if not(os.path.exists(f)):
            _df = pd.read_csv(os.path.join(
                audit_data_loc, f), delimiter=',')
        else:
            _df = pd.read_csv(f, delimiter=',')

        _df.rename(columns={k:k.strip().replace(' ', '_').lower() 
            for k in _df.keys()}, inplace=True)
        # print(_df.columns.tolist())
        assess_vals = _df.assessment_amount.apply(convert)
        _df['assessment_amount'] = assess_vals
        NAICS_int = _df['naics'].apply(lambda x: np.nan if isinstance(
            x,(float,float)) and np.isnan(x) else int(str(x).split('.')[0]))
        _df['NAICS'] = NAICS_int
        _df.rename(columns={'primary_id1':'business_id',
                            'primary_id':'business_id',
                            'initial_approval_date1':'initial_approval_date',
                            'case_id1': 'case_id', 'entity_name1': 'entity_name',
                            'case_type1': 'case_type', 'case_sub_type1': 'case_sub_type',
                            'reapproval_date1': 'reapproval_date'
                            }, inplace=True)
        _df['issue_code'] = [fix_code(code) for code in _df.issue_code.values]
        _df['initial_approval_date'] = _df.initial_approval_date.apply(
            fix_date).apply(pd.Timestamp)
        audit_labels = pd.concat([audit_labels,_df],ignore_index=True)

    db = sql_connect.DbConnectGenerator(config=sqlconfig.SQLConfig(audit_data_loc))
    print('DB connector info:', db.connection_str)
    _, audit_labels = add_period_of_interest(audit_labels, db)

    audit_labels.sort_values(by=['assessment_amount','NAICS','business_id'],inplace=True)
    if write_to_file:
        audit_labels.to_csv(audit_data_loc + outfile, index=False)

    return audit_labels #.sort_values(by=['entity_name1'],ascending=True) #['assessment_amount','NAICS'])
