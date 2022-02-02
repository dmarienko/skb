import hashlib
from time import gmtime, strftime, sleep, monotonic, perf_counter
from collections import OrderedDict, namedtuple
import re


class mstruct:
    """
    Dynamic structure (similar to matlab's struct it allows to add new properties dynamically)

    >>> a = mstruct(x=1, y=2)
    >>> a.z = 'Hello'
    >>> print(a)

    mstruct(x=1, y=2, z='Hello')
    
    >>> mstruct(a=234, b=mstruct(c=222)).to_dict()
    
    {'a': 234, 'b': {'c': 222}}

    """

    def __init__(self, **kwargs):
        _odw = OrderedDict(**kwargs)
        self.__initialize(_odw.keys(), _odw.values())

    def __initialize(self, fields, values):
        self._fields = list(fields)
        self._meta = namedtuple('mstruct', ' '.join(fields))
        self._inst = self._meta(*values)

    def __getattr__(self, k):
        return getattr(self._inst, k)

    def __dir__(self):
        return self._fields

    def __repr__(self):
        return self._inst.__repr__()

    def __setattr__(self, k, v):
        if k not in ['_inst', '_meta', '_fields']:
            new_vals = {**self._inst._asdict(), **{k: v}}
            self.__initialize(new_vals.keys(), new_vals.values())
        else:
            super().__setattr__(k, v)

    def __getstate__(self):
        return self._inst._asdict()

    def __setstate__(self, state):
        self.__init__(**state)

    def __ms2d(self, m):
        r = {}
        for f in m._fields:
            v = m.__getattr__(f)
            r[f] = self.__ms2d(v) if isinstance(v, mstruct) else v
        return r

    def to_dict(self):
        """
        Return this structure as dictionary
        """
        return self.__ms2d(self)

    def copy(self):
        """
        Returns copy of this structure
        """
        return dict2struct(self.to_dict())

