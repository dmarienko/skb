import hashlib
from time import gmtime, strftime, sleep, monotonic, perf_counter
from collections import OrderedDict, namedtuple, defaultdict
import re
import pandas as pd

from skb.structs import mstruct
from ira.utils.nb_functions import z_ls, z_ld, z_save


def __wrap_with_color(code):
    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)

    return inner


red, green, yellow, blue, magenta, cyan, white = (
    __wrap_with_color('31'),
    __wrap_with_color('32'),
    __wrap_with_color('33'),
    __wrap_with_color('34'),
    __wrap_with_color('35'),
    __wrap_with_color('36'),
    __wrap_with_color('37'),
)


def kls(host=None):
    """
    Temporary records display utility
    """
    paths = defaultdict(list)
    for n in z_ls('knodes', host=host, dbname='skb'):
        d = z_ld(n, host=host, dbname='skb')
        paths[d['path']].append(d)
        
    for p, vs in sorted(paths.items()): 
        hdr = yellow(f" ---[ ") + magenta(p) + yellow(" ]".ljust(20, '-'))
        print(hdr)
        for d in vs:
            descr = '\n\t\t\t'.join(d['description'].split('\n'))
            tags = '|'.join(d['tags'])
            print(f"    {blue(d['id'])} {red(pd.Timestamp(d['created']).strftime('%d/%b/%y %H:%M:%S'))} <|{yellow(d['name'])}|> {cyan(tags)}\n\t\t\t{ green(descr) }")
            refs = d.get('reference')
            if refs is not None and refs:
                refs = '\n\t\t'.join([refs] if not isinstance(refs, list) else refs)
                print(f"\t\tlinks: {blue(refs)}")
        print('\n')
        

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


def generate_id(salt, n=12, suffix='i'):
    """
    Unique ID generator
    """
    return (suffix if suffix else '') + hashlib.sha256((salt + f"{(monotonic() + perf_counter()):.25f}").encode('utf-8')).hexdigest()[:n].upper()


def get_short_id(s: str):
    skip = ['the', 'a', 'for', 'an', 'in', 'at', 'from', 'by', 'of', 'this', 'is', 'that', 'are']
    ss = re.split(r'[\ \[\]\(\)\*\+\-\,\.]', s)
    return ''.join([i[0].upper() for i in ss if i not in skip and i.isalnum()])