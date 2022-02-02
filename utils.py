import hashlib
from time import gmtime, strftime, sleep, monotonic, perf_counter
from collections import OrderedDict, namedtuple
import re
import pandas as pd

from skb.structs import mstruct


def dict2struct(d: dict):
    """
    Convert dictionary to structure
    >>> s = dict2struct({'f_1_0': 1, 'z': {'x': 1, 'y': 2}})
    >>> print(s.z.x)
    1
    
    """
    m = mstruct()
    for k, v in d.items():
        if isinstance(v, dict):
            v = dict2struct(v)
        m.__setattr__(k, v)
    return m


def dict_to_frame(x: dict, index_type=None, orient='index', columns=None, column_types={}):
    """
    Utility for convert dictionary to indexed DataFrame
    It's possible to pass columns names and type of index
    """
    y = pd.DataFrame().from_dict(x, orient=orient)
    if index_type:
        if index_type in ['ns', 'nano']:
            index_type = 'M8[ns]'

        y.index = y.index.astype(index_type)
    # rename if need
    if columns:
        columns = [columns] if not isinstance(columns, (list, tuple, set)) else columns
        if len(columns) == len(y.columns):
            y.rename(columns=dict(zip(y.columns, columns)), inplace=True)
        else:
            raise ValueError('dict_to_frame> columns argument must contain %d elements' % len(y.columns))

    # if additional conversion is required
    if column_types:
        _existing_cols_conversion = {c: v for c, v in column_types.items() if c in y.columns}
        y = y.astype(_existing_cols_conversion)

    return y


def generate_id(salt):
    """
    Unique ID generator
    """
    return 'i' + hashlib.sha256((salt + f"{(monotonic() + perf_counter()):.25f}").encode('utf-8')).hexdigest()[:12].upper()


def get_short_id(s: str):
    skip = ['the', 'a', 'for', 'an', 'in', 'at', 'from', 'by', 'of', 'this', 'is', 'that', 'are']
    ss = re.split(r'[\ \[\]\(\)\*\+\-\,\.]', s)
    return ''.join([i[0].upper() for i in ss if i not in skip and i.isalnum()])