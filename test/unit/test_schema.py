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

TEST_SCHEMA_YAML_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'fixture', 'schema.yaml'
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


def test_schema_from_yaml():
    '''Valid initializing from yaml'''
    schema = lucidity.Schema.from_yaml(TEST_SCHEMA_YAML_PATH)