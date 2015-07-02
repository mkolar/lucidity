# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

from . import Template, Resolver
from . import error
from .vendor import yaml
from .core import *


class Schema(dict):
    '''A schema.'''

    def __init__(self, templates=None):
        '''Initialise with optional *templates*.

        *templates* must be a list of instantiated :py:class:`~lucidity.template.Template` objects.
        Similar to the one returned from :py:function:`~luciditiy.discover_templates`.
        '''
        super(Schema, self).__init__()
        self.references = {}
        self.template_resolver = SchemaReferenceResolver(self)
        if templates is not None:
            assert isinstance(templates, list)
            for template in templates:
                self.add_template(template)

    def __setitem__(self, key, value):
        # Ensure we only assign templates to this schema.
        assert isinstance(value, Template)
        assert key == value.name
        super(Schema, self).__setitem__(key, value)

    def add_reference(self, reference):
        '''Add the *reference* to this Schema instance.

        References are only used to resolve referenced keys in Templates and won't be used to parse/format against.

        *reference* must be a an instance of :py:class:`~lucidity.template.Template`.
        '''
        assert isinstance(reference, Template)
        reference.template_resolver = self.template_resolver
        self.references[reference.name] = reference

    def add_template(self, template):
        '''Add the *template* to this Schema instance.

        *template* must be a an instance of :py:class:`~lucidity.template.Template`.
        '''
        assert isinstance(template, Template)
        template.template_resolver = self.template_resolver
        self[template.name] = template

    def parse(self, path):
        '''Parse *path* against all templates in this schema and return first correct match.

        See: :py:function:`~luciditiy.parse` for more information.
        '''
        return parse(path, self.templates)

    def parse_all(self, path):
        '''Parse *path* against all templates in this schema and returns a list of all matches.

        This is equivalent to performing ``list(schema.parse_iter(path))``.
        '''
        return list(self.parse_iter(path))

    def parse_iter(self, path):
        '''Parse *path* against all templates in this schema and yields all matches.

        See: :py:function:`~luciditiy.parse_iter` for more information.
        '''
        return parse_iter(path, self.templates)

    def format(self, data):
        '''Format *data* using the templates in this schema and return the first match.

        See: :py:function:`~luciditiy.format` for more information.
        '''
        return format(data, self.templates)

    def format_iter(self, data):
        '''Format *data* using the templates in this schema and return the first match.

        See: :py:function:`~luciditiy.format_iter` for more information.
        '''
        return format_iter(data, self.templates)

    def format_all(self, data):
        '''Format *data* using the templates in this schema and return all matches.

        This is equivalent to performing ``list(schema.format_iter(data))``.
        '''
        return list(self.format_iter(data))

    def get_template(self, name):
        '''Retrieve a template from *templates* by *name*.

        See: :py:function:`~luciditiy.get_template` for more information.
        '''
        return self[name]

    @property
    def templates(self):
        return self.values()

    def map_iter(self, paths, other_schema):
        ''' For each path parse it with this schema and format it with the other schema and yield each result.

        Each individual path results in yielding a 5-tuple:
        ``data, original_path, original_template, other_path, other_template``

        You can use this to remap paths from one schema to another.

        See: :py:function:`~luciditiy.get_template` for more information.
        '''
        for original_path in paths:
            matches = self.parse_all(original_path)
            for data, original_template in matches:
                name = original_template.name
                try:
                    other_template = other_schema.get_template(name)
                except error.NotFound:
                    continue

                try:
                    other_path = other_template.format(data)
                except error.FormatError:
                    continue

                yield (data,
                       original_path,
                       original_template,
                       other_path,
                       other_template)

            else:
                raise error.NotFound()

    def map(self, *args, **kwargs):
        return list(self.map_iter(*args, **kwargs))

    @classmethod
    def from_dict(cls, data):
        """ Instantiate a schema pre-loaded with the *data* dictionary.

        Instantiate a Schema from a dictionary loading all `paths` as templates
        Also supports setting a separate default for all paths in the schema using `defaults`.

        Return ``lucidity.schema.Schema`` initialized with all path templates defined in the *data* dictionary.
        """

        schema = cls()

        if not data:
            return schema

        convert_anchor = {'start': Template.ANCHOR_START,
                          'both': Template.ANCHOR_BOTH,
                          'end': Template.ANCHOR_END}
        convert_mode = {'relaxed': Template.ANCHOR_START,
                        'strict': Template.ANCHOR_BOTH}

        conversions = {'anchor': convert_anchor,
                       'mode': convert_mode}

        defaults = {'anchor': Template.ANCHOR_START,
                    'mode': Template.RELAXED}

        if 'defaults' in data:
            for key, value in data['defaults'].iteritems():
                defaults[key] = conversions[key][value]

        if 'paths' in data:
            for name, template_data in data['paths'].iteritems():

                # pattern
                pattern = template_data['pattern']

                # anchor
                anchor = defaults['anchor']
                if 'anchor' in template_data:
                    anchor_raw = template_data['anchor']
                    anchor = conversions['anchor'][anchor_raw]

                # mode
                mode = defaults['mode']
                if 'mode' in template_data:
                    mode_raw = template_data['mode']
                    mode = conversions['mode'][mode_raw]

                template = Template(name,
                                             pattern,
                                             anchor=anchor,
                                             duplicate_placeholder_mode=mode)
                schema.add_template(template)

        if 'references' in data:
            for name, pattern in data['references'].iteritems():
                template = Template(name, pattern)
                schema.add_reference(template)

        return schema


    @classmethod
    def from_yaml(cls, filepath):
        ''' Parse a Schema from a YAML file at the given *filepath*.

        Return ``lucidity.schema.Schema`` initialized with all path templates defined in the YAML file.
        '''
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)


class SchemaReferenceResolver(Resolver):
    def __init__(self, schema):
        assert isinstance(schema, Schema)
        self.schema = schema

    def get(self, template_name, default=None):
        # Retrieve Templates first
        template = self.schema.get(template_name, None)
        if template:
            return template

        # If no Template found with that name, check if we have a reference Template
        template = self.schema.references.get(template_name, None)
        if template:
            return template

        return None
