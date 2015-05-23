# :coding: utf-8
# :copyright: Copyright (c) 2013 Martin Pengelly-Phillips
# :license: See LICENSE.txt.

import string


class Formatter(string.Formatter):
    def get_field(self, field_name, args, kwargs):
        ''' Given a `field_name`, find the object it references.

        This is an exact copy of the implementation of ``string.Formatter.get_field`` except that it uses dictionary
        access when the object is a dictionary.
        '''
        first, rest = field_name._formatter_field_name_split()

        obj = self.get_value(first, args, kwargs)

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        for is_attr, i in rest:
            if isinstance(obj, dict):   # when the object is a dictionary use dictionary access
                obj = obj[i]
            elif is_attr:
                obj = getattr(obj, i)
            else:
                obj = obj[i]

        return obj, first