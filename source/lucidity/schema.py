import lucidity


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
            assert all(isinstance(x, lucidity.Template) for x in templates)
            self._templates = templates

    def parse(self, path):
        '''Parse *path* against all templates in this schema and return first correct match.

        See: :py:function:`~luciditiy.parse` for more information.
        '''
        return lucidity.parse(path, self._templates)

    def parse_all(self, path):
        '''Parse *path* against all templates in this schema and returns a list of all matches.

        This is similar to performing ``list(schema.parse_iter(path))``.
        '''
        return list(self.parse_iter(path))

    def parse_iter(self, path):
        '''Parse *path* against all templates in this schema and yields all matches.

        See: :py:function:`~luciditiy.parse_iter` for more information.
        '''
        return lucidity.parse_iter(path, self.templates)

    def format(self, data):
        '''Format *data* using all templates in this schema.

        See: :py:function:`~luciditiy.format` for more information.
        '''
        return lucidity.format(data, self.templates)

    def get_template(self, name):
        '''Retrieve a template from *templates* by *name*.

        See: :py:function:`~luciditiy.get_template` for more information.
        '''
        return lucidity.get_template(name, self.templates)

    @property
    def templates(self):
        return self._templates
