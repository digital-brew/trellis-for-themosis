# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function, unicode_literals)
__metaclass__ = type

import types
import yaml

from ansible import errors
from ansible.compat.six import string_types
from ansible.module_utils._text import to_text
from ansible.parsing.yaml.dumper import AnsibleDumper


class TrellisDumper(AnsibleDumper):
    '''Dumper with indentless=False to increase indent on list items'''
    # http://stackoverflow.com/a/39681672/6847025
    # http://pyyaml.org/ticket/64#comment:5
    def increase_indent(self, flow=False, indentless=False):
        return super(TrellisDumper, self).increase_indent(flow, False)

def to_env(dict_value):
    envs = ["{0}='{1}'".format(key.upper(), str(value).replace("'","\\'")) for key, value in sorted(dict_value.items())]
    return "\n".join(envs)

def to_trellis_yaml(a, indent=2, *args, **kw):
    '''Ansible's to_nice_yaml, with increased indent on list items'''
    transformed = yaml.dump(a, Dumper=TrellisDumper, indent=indent, allow_unicode=True, default_flow_style=False, **kw)
    return to_text(transformed)

def underscore(value):
    ''' Convert dots to underscore in a string '''
    return value.replace('.', '_')

class FilterModule(object):
    ''' Trellis jinja2 filters '''

    def filters(self):
        return {
            'to_env': to_env,
            'to_trellis_yaml': to_trellis_yaml,
            'underscore': underscore,
        }
