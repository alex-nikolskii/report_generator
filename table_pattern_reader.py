from collections import namedtuple, OrderedDict
import re

FilterUnit = namedtuple('FilterUnit', 'field op value')
GroupUnit = namedtuple('GroupUnit', 'grouped_fields aggr_func aggr_column')
GROUP = 'group'
TABLE_COLUMNS = 'table columns'
TABLE_NAME = 'table name'
COLUMN_FILTERS = 'filter'

COLUMN_PATTERN = re.compile(r'''(?P<name>[\w\-\s,]+)\|(?P<type>\w+)
                                -?(?P<width>\d+)?  # field width
                                -?(?P<align>[rcl])?  # align type
                                -?(?P<unit>\w+)?  # measurement type
                            ''', re.X)
FILTER_PATTERN = re.compile(r'''(?P<name>[\w\-\s,]+)\s*
                                (?P<op>[=><!]+)\s*
                                (?P<value>\w+[\s\d\w\-.]*)
                            ''', re.X)
GROUP_PATTERN = re.compile(r'''\s*fields\|(?P<groups>[\w;\s]+)
                               data\|(?P<func>\w+);\s*
                               (?P<column>[\w,\s\-]+)
                            ''', re.X)

# Возможные операции при фильтрации
# >, <, >=, <= -- для чисел только. Не только. Строки будут в
# лексикографическом порядке.
FILTER_OPS = {'=', '!=', '>', '<', '>=', '<='}
AGGR_FUNC = {'sum', 'avg'}


class Column:
    def __init__(self, name, _type='str', width=20, alignment='c', unit=''):
        self.name = name
        self.type = _type
        self.width = width
        self.align = alignment
        self.unit = unit

    def __str__(self):
        return f'Имя столбца: {self.name}\n' \
            f'Тип столбца: {self.type}\n'\
            f'Ширина столбца: {self.width}\n' \
            f'Выравнивание столбца: {self.align}\n' \
            f'Единица измерения: {self.unit}\n'


class TablePatternReader:
    def __init__(self, filename, encoding='utf-8', default_field_width=20):
        self.__fields_dict = self.read_fields(filename, encoding)
        self.table_name = self.get_field_value(TABLE_NAME)
        self.columns = self.extract_columns_items(
            self.get_field_value(TABLE_COLUMNS), default_field_width)
        self.group_by = self.extract_group(self.get_field_value(GROUP))
        self.filter = self.extract_filter_conditions(
            self.get_field_value(COLUMN_FILTERS))

    def extract_group(self, value):
        if value is None:
            return
        match = GROUP_PATTERN.match(value)
        if match is not None:
            fields_to_group = tuple(
                filter(None, (line.strip().upper() for line
                              in match.group('groups').split(';'))))

            aggr_column = match.group('column').upper()
            aggr_func = match.group('func')
            try:
                if aggr_func not in AGGR_FUNC:
                    raise ValueError(f'Unknown aggregation function: '
                                     f'{aggr_func}\n')
                if aggr_column not in self.columns:
                    raise ValueError(f'Unknown table field: {aggr_column}\n')
                for field in fields_to_group:
                    if field not in self.columns:
                        raise ValueError(f'Unknown table field: {field}\n')
            except ValueError as err:
                print(str(err))
            else:
                return GroupUnit(fields_to_group, aggr_func, aggr_column)

    def get_field_value(self, field_name):
        value = self.__fields_dict.get(field_name)
        return value.strip() if value is not None else value

    def extract_filter_conditions(self, values=None, delimiter=';'):
        if values is None:
            return
        filter_cases = tuple(cond.strip() for cond in values.split(delimiter))
        filters = []
        for case in filter_cases:
            _filter = FILTER_PATTERN.match(case)
            if _filter is not None:
                _filter_name = _filter.group('name').upper().strip()
                _filter_op = _filter.group('op')
                _filter_value = _filter.group('value')
                try:
                    if _filter_op not in FILTER_OPS:
                        raise ValueError(f'Unknown operation: {_filter_op}\n')
                    if _filter_name not in self.columns:
                        raise ValueError(f'Unknown table field: '
                                         f'{_filter_name}\n')
                except ValueError as err:
                    print(f'{err} in case: {case}')
                else:
                    filters.append(FilterUnit(_filter_name, _filter_op,
                                              _filter_value))
        return filters

    @staticmethod
    def none_check(field, default):
        return field if field is not None else default

    def extract_columns_items(self, values, default_field_len, delimiter=';'):
        if values is None:
            print('No columns entered in pattern!')
            return
        fields_list = list(map(str.strip, values.split(delimiter)))
        columns = OrderedDict()
        for str_column in fields_list:
            column = COLUMN_PATTERN.match(str_column)
            if column is not None:
                name = column.group('name').upper()
                _type = column.group('type')
                # Всегда int
                width = int(self.none_check(column.group('width'),
                                            default_field_len))
                align = self.none_check(column.group('align'), 'c')
                unit = self.none_check(column.group('unit'), '')
                columns[name] = Column(name, _type, width, align, unit)
            else:
                print(f'Not valid column: "{str_column}". '
                      f'Check it for correctness')
        return columns

    @staticmethod
    def read_fields(filename, encoding):
        with open(filename, 'r', encoding=encoding) as file:
            # убрал проверку на utf with BOM. Сделал по дефолту.
            # if encoding.startswith('utf'):
            #     file_data = file.read()[1:]  # убрать BOM
            # else:
            #     file_data = file.read()
            file_data = file.read()
            # шарп(#) символ разделения определения полей.
            pattern_data = list(map(str.strip, file_data.split('#')))
            # Убрал пустые строки.
            pattern_data = filter(None, pattern_data)
            # Словарь полей в шаблоне
            fields = dict(map(lambda x: x.strip().split(':'), pattern_data))
            return fields

    def __str__(self):
        return f'{self.table_name}\n' \
            f'{self.columns}\n' \
            f'{self.group_by}\n' \
            f'{self.filter}\n'
