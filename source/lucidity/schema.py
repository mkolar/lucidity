# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import lucidity

import lucidity.error
import lucidity.vendor.yaml as yaml


class Schema(object):
    '''A schema.'''

    def __init__(self, templates=None):
        '''Initialise with optional *templates*.

        *templates* must be a list of instantiated :py:class:`~lucidity.template.Template` objects.
        Similar to the one returned from :py:function:`~luciditiy.discover_templates`.
        '''
        self._templates = []
        if templates is not None:
            assert isinstance(templates, list)
            for template in templates:
                self.add_template(template)

    def add_template(self, template):
        '''Add the *template* to this Schema instance.

        *template* must be a an instance of :py:class:`~lucidity.template.Template`.
        '''
        assert isinstance(template, lucidity.Template)
        self._templates.append(template)

    def parse(self, path):
        '''Parse *path* against all templates in this schema and return first correct match.

        See: :py:function:`~luciditiy.parse` for more information.
        '''
        return lucidity.parse(path, self.templates)

    def parse_all(self, path):
        '''Parse *path* against all templates in this schema and returns a list of all matches.

        This is equivalent to performing ``list(schema.parse_iter(path))``.
        '''
        return list(self.parse_iter(path))

    def parse_iter(self, path):
        '''Parse *path* against all templates in this schema and yields all matches.

        See: :py:function:`~luciditiy.parse_iter` for more information.
        '''
        return lucidity.parse_iter(path, self.templates)

    def format(self, data):
        '''Format *data* using the templates in this schema and return the first match.

        See: :py:function:`~luciditiy.format` for more information.
        '''
        return lucidity.format(data, self.templates)

    def format_iter(self, data):
        '''Format *data* using the templates in this schema and return the first match.

        See: :py:function:`~luciditiy.format_iter` for more information.
        '''
        return lucidity.format_iter(data, self.templates)

    def format_all(self, data):
        '''Format *data* using the templates in this schema and return all matches.

        This is equivalent to performing ``list(schema.format_iter(data))``.
        '''
        return list(self.format_iter(data))

    def get_template(self, name):
        '''Retrieve a template from *templates* by *name*.

        See: :py:function:`~luciditiy.get_template` for more information.
        '''
        return lucidity.get_template(name, self.templates)

    @property
    def templates(self):
        return self._templates

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
                except lucidity.error.NotFound:
                    continue

                try:
                    other_path = other_template.format(data)
                except lucidity.error.FormatError:
                    continue

                yield (data,
                       original_path,
                       original_template,
                       other_path,
                       other_template)

            else:
                raise lucidity.error.NotFound()

    def map(self, *args, **kwargs):
        return list(self.map_iter(*args, **kwargs))

    @classmethod
    def from_yaml(cls, filepath):
        # TODO: Implement yaml parsing. See: test/fixture/schema.yaml (#20)
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            return None

        schema = cls()

        # parse the paths from the yaml
        if 'paths' in data:
            for name, template_data in data['paths'].iteritems():

                # pattern
                pattern = template_data['pattern']

                # anchor
                anchor = lucidity.Template.ANCHOR_START
                if 'anchor' in template_data:
                    anchor_raw = template_data['anchor']
                    if anchor_raw == 'start':
                        anchor = lucidity.Template.ANCHOR_START
                    if anchor_raw == 'end':
                        anchor = lucidity.Template.ANCHOR_BOTH
                    if anchor_raw == 'both':
                        anchor = lucidity.Template.ANCHOR_END

                # mode
                mode = lucidity.Template.RELAXED
                if 'mode' in template_data:
                    mode_raw = template_data['mode']
                    if mode_raw == 'relaxed':
                        mode = lucidity.Template.RELAXED
                    if mode_raw == 'strict':
                        mode = lucidity.Template.STRICT

                template = lucidity.Template(name,
                                             pattern,
                                             anchor=anchor,
                                             duplicate_placeholder_mode=mode)
                schema.add_template(template)

        return schema