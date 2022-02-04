import pandas as pd

from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic, line_cell_magic)
from IPython import get_ipython
from IPython.core.display import display, HTML
from datetime import datetime 
from os.path import join, split
import getpass
import re
from ira.utils.nb_functions import z_ld, z_save

from skb.structs import mstruct
from skb.utils import generate_id, get_short_id

import platform


def get_user_and_path():
    try:
        import re
        from os.path import basename, split
        from IPython.core.display import HTML, display
        from notebook import notebookapp

        servers = list(notebookapp.list_running_servers())
        ex = re.compile('http[s]?://(.+:?\d+)(/.+)')
        b_url = ex.match(servers[0]['url']).groups()[1]
        basic_path = servers[0]['notebook_dir']
        user = list(filter(lambda x: x, b_url.split('/')))[-1]
        return user, basic_path
    except:
        print("Error getting data ...")
        return None, None
    

@magics_class
class _KNodes(Magics):
    """
    %%k jupyter cell magic (as some first experimenting) 
    """
    
    @cell_magic
    def k(self, line, cells):
        return self._k(line, cells, True)
    
    @cell_magic
    def k_(self, line, cells):
        return self._k(line, cells, False)
    
    def _k(self, line, cells, store=True):
        if line:
            args = [s.strip() for s in line.split(' ') if s]
            if len(args) < 2:
                raise ValueError('First line must contain type and path for node')
            _type = args[0]
            _path = args[1]
        else:
            raise ValueError('First line must not be empty')
            
        _tags = []
        _name, _descr, _data, _data_type, _refs = None, '', None, None, []
        _time_span = None
        lns = [l.strip() for l in cells.split('\n') if l]
        
        is_guarded = lambda s: s.startswith('`')
        is_text = lambda s: s.startswith('\'') or s.startswith('"')
        
        for l in lns:
            if l.startswith('#'): continue
                
            # check any tagged lines
            matches = re.match('([\w,:]*)\ *:\ *(.*)', l)
            if matches:
                _t, d = matches.groups()
                d = d.strip()
                
                if _t in ['s', 'span']:
                    _time_span = d
                    
                if _t in ['t', 'tag', 'tags']:
                    [_tags.append(s.strip()) for s in d.split(' ') if s]
                    
                elif _t in ['r', 'ref']:
                    _refs.append(d)
                    
                elif _t in ['::', 'data']:
                    if not _data:
                        _data = d
                        _d_s = re.match('(.*)\ *:\ *(\w+)$', d)
                        if _d_s:
                           _data_type = _d_s.group(2) 
                    else:
                        print(f'\n\tWarning: data tag is already declared earlier for {_data}\n')
                        
                continue
                
            # check any descriptions after name was declared
            dcs = re.match('\ *-(.*)', l)
            if _name and dcs:
                _descr += dcs.group(1) + "\n"
                continue
                
            # if just a line - use first non empy as name
            _name = l if _name is None else _name
            
        # process data etc
        if _data is not None and _data:
            ipy = get_ipython()

            if is_guarded(_data):
                _data = eval(_data[1:], ipy.user_global_ns)

            elif _data_type != 'text' and not is_text(_data):
                if _data not in ipy.user_global_ns:
                    raise ValueError(f"Can't find variable '{_data}' in current namespace !")
                _data = ipy.user_global_ns.get(_data)
        
        user, path = get_user_and_path()
        _id = generate_id(_name + _descr + _type, suffix=None)
        d2s = {
            'id': _id, 'path': _path,
            'type': _type, 'name': _name, 'description': _descr,
            'data': _data, 'data_type': _data_type,
            'tags': list(set(_tags)), 'reference': _refs,
            'created': datetime.now().isoformat(),
            'timespan': _time_span,
            'author': user, 
            'meta': {
                'cwd': path,
                'python': platform.python_version(),
                'node': platform.node(),
                'version': platform.version(),
                'os': platform.system(), 
            }
        }
#         db_dest = join('knodes', _path) + '.' + _id 
        if store:
            z_save(f"knodes/{_id}", d2s, dbname='skb')
            print(f'> saved to {_id}')
        else:
            print(d2s)

get_ipython().register_magics(_KNodes)
