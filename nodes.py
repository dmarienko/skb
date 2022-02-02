import pandas as pd

from skb.structs import mstruct
from skb.utils import generate_id, get_short_id


def knode(
    n_type,
    n_description,
    n_data,
    n_data_type='text',
    tags=None,    
    parent=None,
    timespan=None,
    autodestroy=False,
) -> mstruct:
    
    n_type = n_type.upper()
    
    if n_type not in ['P', 'R', 'D', 'C', 'T', 'I']:
        raise ValueError(f"Wrong type of node {n_type} !")
        
    created_time = pd.Timestamp('now').isoformat()
    if timespan:
        pd.Timedelta(timespan)
        
    def _repr_(s):
        return description
    
    node = mstruct(
        parent='Root' if parent is None or n_type.upper()=='P' else parent,
        children=[],
        linked=[],
        description=n_description,
        node_type=n_type,
        tags=tags if tags else [],
        data_type=n_data_type,
        data=n_data,
        created=created_time,
        last_modified=created_time,
        timespan=None,
    )
    node.id = generate_id(node.description)
    # item.id = get_short_id(item.name)
    return node


class R_struct(mstruct):
    
    def td(self, descr, tags=[], timespan=None):
        n = knode('D', descr, '', '', timespan=timespan, tags=tags)
        self.__setattr__(n.id, n)
        return self
    
    def __floordiv__(self, node: mstruct):
        self.__setattr__(node.id, node)
        return self
    
def D(descr: str, tags=[], timespan=None):
    return knode('D', descr, '', '', timespan=timespan, tags=tags)

def T(descr, tags=[], ndata=''):
    return knode('T', descr, ndata, 'text', tags=tags)