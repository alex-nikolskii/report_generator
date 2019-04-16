import re

DATA_PATTERN = re.compile(r'''(?P<name>[\w\s\-,]+)\s*=\s*
                              (?P<value>[\d\w\s\-,]+)
                          ''', re.X)


class DataReader:
    def __init__(self, filename, encoding='utf-8'):
        self.__file_data = self.read_data(filename, encoding)
        self.fields = self.extract_values()

    @staticmethod
    def read_data(filename, encoding):
        with open(filename, 'r', encoding=encoding) as file:
            return filter(None, file.read().split('#'))

    def extract_values(self):
        fields_dict = {}
        for line in self.__file_data:
            match = DATA_PATTERN.match(line)
            if match is not None:
                field_name = match.group('name').strip().upper()
                field_value = match.group('value').strip()
                fields_dict[field_name] = field_value
            else:
                print(f'Line is not in right condition: {line}. '
                      f'Can\'t extract data.\n')
        return fields_dict
