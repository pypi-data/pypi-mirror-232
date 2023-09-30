# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
import sys
import copy
import glob
import json
import numpy as np

if hasattr(sys, 'frozen'):
    rootdir = os.path.join(os.path.dirname(sys.executable), 'calm-data')
else:
    thisdir = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
    rootdir = os.path.abspath(os.path.join(thisdir, '..'))

entities_dir = os.path.join(rootdir, 'entities')
translators_dir = os.path.join(rootdir, 'translators')

# If we have softpy, registers entities and translators for CALM
try:
    import softpy
    softpy.register_jsondir(entities_dir)
    softpy.translators.path.append(translators_dir)
    HAVE_SOFTPY = True

except ImportError:
    HAVE_SOFTPY = False

    entities = {}
    for filename in glob.glob(os.path.join(entities_dir, '*.json')):
        #print(filename)
        with open(filename, encoding='utf-8') as fil:
            data = json.load(fil)
        if isinstance(data, dict):
            values = []
            for key in ['namespace', 'version', 'name']:
                value = data.get(key, '')
                if value:
                    values.append(value)
            if len(values) == 3:
                entities['/'.join(values)] = data

def get_entities():
    if hasattr(sys, 'frozen'):
        rootdir = os.path.join(os.path.dirname(sys.executable), 'calm-data')
    else:
        thisdir = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
        rootdir = os.path.abspath(os.path.join(thisdir, '..'))

    entities_dir = os.path.join(thisdir, 'entities')
    translators_dir = os.path.join(rootdir, 'translators')

    # If we have softpy, registers entities and translators for CALM
    try:
        import softpy
        softpy.register_jsondir(entities_dir)
        softpy.translators.path.append(translators_dir)
        HAVE_SOFTPY = True

    except ImportError:
        HAVE_SOFTPY = False

        entities = {}
        for filename in glob.glob(os.path.join(entities_dir, '*.json')):
            #print(filename)
            with open(filename, encoding='utf-8') as fil:
                data = json.load(fil)
            if isinstance(data, dict):
                values = []
                for key in ['namespace', 'version', 'name']:
                    value = data.get(key, '')
                    if value:
                        values.append(value)
                if len(values) == 3:
                    entities['/'.join(values)] = data

    return entities


def entity_ctor(obj, uuid=None, driver=None, uri=None,
                      options=None, **kwargs):
    """ Instantiate an entity (same signature as in softpy) """
    for prop in obj._entity['properties']:
        name = prop['name']
        if name in kwargs:
            if 'dims' in prop:
                value = np.array(kwargs[name], dtype=prop['dtype'])
            else:
                value = prop['pytype'](kwargs[name])
            setattr(obj, name, value)


def get_entity(name, version, namespace):
    """ Return an Entity (Python class)."""
    if HAVE_SOFTPY:
        from softpy.metadata import SoftMissingMetadataError
        cls = softpy.entity(name, version, namespace)
        cls._entity = copy.deepcopy(dict(cls.soft_metadata))
    else:
        key = '/'.join([namespace, version, name])
        
        if entities == {}:
            entities2 = get_entities()
        else:
            entities2 = entities
        entity = entities2[key]
        attr = {
            '__init__': entity_ctor,
            '_entity': entity,
        }
        cls = type(name, (object, ), attr)

    # Add additional type descriptions to _entity['properties']
    #   - dtype: numpy dtype
    #   - pytype: corresponding native python type
    for prop in cls._entity['properties']:
        if 'string' in prop['type']:
            prop['dtype'] = np.dtype('O')  # to allow arbitrary length strings
            prop['pytype'] = str
        else:
            prop['dtype'] = np.dtype(prop['type'])
            prop['pytype'] = type(prop['dtype'].type(0).item())

    # Add also a _property_names attribute
    cls._property_names = [prop['name'] for prop in cls._entity['properties']]

    return cls


def init_zeros(obj, dimensions):
    """Initialize properties of instance `obj` to zero.  `dimensions` provide
    dimension sizes, either as a sequence of ints or dict mapping dimension
    labels to sizes."""
    labels = [d['name'] for d in obj._entity['dimensions']]
    if not hasattr(dimensions, 'keys'):
        dimensions = {label: size for label, size in zip(labels, dimensions)}
    for prop in obj._entity['properties']:
        name = prop['name']
        if not name in obj.__dict__:
            if 'dims' in prop:
                dims = [dimensions[label] for label in prop['dims']]
                value = np.zeros(dims, dtype=prop['dtype'])
            else:
                value = np.zeros((1, ), dtype=prop['pytype']).item()
            obj.__dict__[name] = value


def get_datafiles():
    files = []
    for d, p in [('entities', '*.json',), ('translators', '*.pyt')]:
        dst = os.path.join('calm-data', d)
        files += [(x, dst) for x in glob.glob(os.path.join(rootdir, d, p))]
    return files
