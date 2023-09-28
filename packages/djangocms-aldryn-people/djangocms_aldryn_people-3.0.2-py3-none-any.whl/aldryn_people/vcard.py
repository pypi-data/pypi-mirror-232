from itertools import chain
from re import sub


class Vcard:
    def __init__(self):
        self.lines = []

    def add_line(self, key, value, **params):
        key_and_params = ';'.join(chain(
            (key,),
            (f'{k}={v}' for k, v in params.items()),
        ))

        if isinstance(value, str):
            value = self.__escape(value)
        else:
            value = ';'.join(self.__escape(x) for x in value)

        line = f'{key_and_params}:{value}'
        self.lines.append(line)

    def __escape(self, value):
        if value is None:
            return ''
        value = sub(r'[\;,"]', r'\\\0', value)
        return value.replace('\r', r'\r').replace('\n', r'\n')

    def __wrap_logical_line(self, line):
        return '\r\n '.join(line[i:i + 75] for i in range(0, len(line), 75))

    def __str__(self):
        lines = chain(('BEGIN:VCARD', 'VERSION:3.0'),
                      self.lines,
                      ('END:VCARD', ''))
        return '\r\n'.join(self.__wrap_logical_line(x) for x in lines)
