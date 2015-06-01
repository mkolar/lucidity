# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import os
import operator

import pytest

import lucidity


TEST_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'fixture', 'template'
)

TEST_SCHEMA_ROOT = os.path.join(
    os.path.dirname(__file__), '..', 'fixture', 'schema'
)

@pytest.fixture
def templates():
    '''Return candidate templates.'''
    return [
        lucidity.Template('model', '/jobs/{job.code}/assets/model/{lod}'),
        lucidity.Template('rig', '/jobs/{job.code}/assets/rig/{rig_type}')
    ]


def test_schema():
    '''Valid initializing.'''
    schema = lucidity.Schema(templates())
    assert isinstance(schema, lucidity.Schema)


def test_schema_from_yaml_simple():
    '''Valid initializing from yaml without nesting'''
    schema = lucidity.Schema.from_yaml(os.path.join(TEST_SCHEMA_ROOT, 'schema_simple.yaml'))


@pytest.mark.parametrize(('template_id', 'data', 'expected'), [
    ('optional1',   # #1 (1/1 optionals)
     {'project': {'name': 'foobar'}, 'variation': 'evil'},
     'foobar/art/var_evil/concept'),
    ('optional1',   # #1 (0/1 optionals)
     {'project': {'name': 'foobar'}},
     'foobar/art/concept'),
    ('optional2',   # #2 (0/2 optionals)
     {'project': {'name': 'swag'}, 'asset': {'name': 'dude'}, 'version': 1912},
     'swag/model/dude_v1912.mb'),
    ('optional2',   # #2 (1/2 optionals)
     {'project': {'name': 'transformers'}, 'asset': {'name': 'lolly'}, 'version': 471, 'variation': 'blue'},
     'transformers/model/lolly_blue_v0471.mb'),
    ('optional2',   # #2 (2/2 optionals)
     {'project': {'name': 'foobar'}, 'asset': {'name': 'johny'}, 'date': '20150601', 'version': 5, 'variation': 'red'},
     'foobar/model/johny_20150601_red_v0005.mb'),
    ], ids=[
            '#1 (1/1 optionals)',
            '#1 (0/1 optionals)',
            '#2 (0/2 optionals)',
            '#2 (1/2 optionals)',
            '#2 (2/2 optionals)'
    ])
def test_schema_from_yaml_optional(template_id, data, expected):
    '''Valid initializing from yaml'''
    schema = lucidity.Schema.from_yaml(os.path.join(TEST_SCHEMA_ROOT, 'schema_optional.yaml'))

    template = schema.get_template(template_id)
    path = template.format(data)
    assert path == expected


@pytest.mark.parametrize(('template_id', 'data', 'expected'), [
    ('doc.notes',
     {'project': {'name': 'foobar'}},
     'foobar/documents/notes'),
    ('doc.contracts',
     {'project': {'name': 'transformers'}},
     'transformers/documents/contracts'),
    ('extensive',
     {'project': {'name': 'swag'}, 'code': 'abc'},
     'abc/swag/documents/backup/swag/documents/contracts'),
    ('deepnest',
     {'project': {'name': 'a'}, 'code': 'b'},
     'b/a/documents/backup/a/documents/contracts/a/documents/a/documents/notes'),
    ('nest',
     {'project': {'name': 'abc'}},
     'abc/documents')
    ], ids=[
            'doc.contracts (1 nested)',
            'doc.notes (1 nested)',
            'extensive (2 nested)',
            'deepnest (3 nested, long)',
            'nest (only 1 nest)'
    ])
def test_schema_from_yaml_referenced(template_id, data, expected):
    '''Valid initializing from yaml'''
    schema = lucidity.Schema.from_yaml(os.path.join(TEST_SCHEMA_ROOT, 'schema_referenced.yaml'))

    template = schema.get_template(template_id)
    path = template.format(data)
    assert path == expected