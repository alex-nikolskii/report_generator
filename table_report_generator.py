from collections import OrderedDict, defaultdict
from table_pattern_reader import TablePatternReader
from table_data_reader import TableDataReader
from copy import deepcopy
import operator

ALIGN = {
    'c': str.center,
    'r': str.rjust,
    'l': str.ljust,
    'с': str.center
}


def avg(lst):
    return round(sum(lst) / len(lst), 2)


AGGR_FUNC = {
    'sum': sum,
    'avg': avg
}

OPERATIONS = {
    '=': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le
}

TYPES = {
    'int': int,
    'float': float,
    'str': str
}
VERT_BORDER = '|'
HORIZ_BORDER = '-'
EMPTY_STR = ''
NOTHING_FOUND = 'Ничего не найдено. Проверьте шаблон и данные'


# Подставляет данные только с LF разделителем. Поэтому нужны файлы с таким
# разделителем(для переводов строк)
class TableReportGenerator:
    def __init__(self, p_filename, d_filename, output_filename,
                 p_enc='utf-8', d_enc='utf-8', default_field_width=20):
        self.pattern = TablePatternReader(p_filename, p_enc,
                                          default_field_width)
        self.data = TableDataReader(d_filename, d_enc)
        self.columns = self.pattern.columns
        self.format_data_values()

        self.grouped_table = self.initialize_grouped_table()

        if self.grouped_table is not None:
            self.filtered_table = self.filter_table(self.grouped_table)
        else:
            self.filtered_table = self.filter_table(self.data.table)
        self.format_column_data(self.filtered_table)

        self.make_report(self.filtered_table, output_filename)
        self.generated_report = self.make_report(self.filtered_table,
                                                 output_filename)

    def initialize_grouped_table(self):
        if self.pattern.group_by is not None:
            return self.group_by_columns(
                *self.pattern.group_by.grouped_fields,
                aggr_func=self.pattern.group_by.aggr_func,
                aggr_column=self.pattern.group_by.aggr_column)

    def format_data_values(self):
        for line in self.data.table:
            for column in line:
                _column = self.columns[column]
                try:
                    line[column] = TYPES[_column.type](line[column])
                except ValueError as err:
                    print(f'It is not possible to convert "{line[column]}"" to'
                          f' type "{TYPES[_column.type]}" in line:\n"{line}"')
                    # Инициализирую дефолтное значение типа.
                    line[column] = TYPES[_column.type]()

    @staticmethod
    def align_value(value, column):
        if len(value) >= column.width:
            temp_value = value[:column.width]
        else:
            temp_value = ALIGN[column.align](value, column.width)
        return temp_value

    def format_value(self, value, column):
        if '\n' in value:
            value = value.split('\n')
            formatted_values = [self.align_value(elem, column) for
                                elem in value]
            result = '\n'.join(formatted_values)
        else:
            result = self.align_value(value, column)
        return result

    # Если значение составное, придется сдвигать остальные части поля под
    # нужное место в таблице при отображении.
    def format_column_data(self, table=None):
        if table is not None:
            for line in table:
                for column_name in self.columns:
                    # getting value of current column
                    _column = self.columns[column_name]
                    if _column.name not in line:
                        continue
                    # This method called after all group/filter operations
                    # That's why cast to str is possible
                    value = str(line[_column.name])
                    line[_column.name] = self.format_value(value, _column)

    def get_temp_table(self, fields, aggr_column):
        temp_table = [OrderedDict() for _ in self.data.table]
        for i in range(len(self.data.table)):
            for field in fields:
                temp_table[i][field] = self.data.table[i].get(field)
            temp_table[i][aggr_column] = self.data.table[i].get(aggr_column)
        return temp_table

    @staticmethod
    def use_aggr_func(table, fields, aggr_func, aggr_column):
        grouped_fields_dict = defaultdict(list)
        for line in table:
            aggr_value = line[aggr_column]
            group_fields = tuple((field, line[field]) for field in fields)
            grouped_fields_dict[group_fields].append(aggr_value)
        result = {
            k: AGGR_FUNC[aggr_func](v) for k, v in grouped_fields_dict.items()}
        return result

    @staticmethod
    def cast_to_ordered(table, aggr_column):
        result = []
        for line in table:
            _line = OrderedDict(line)
            _line[aggr_column] = table[line]
            result.append(_line)
        return result

    # Группировка как в примере.
    def group_by_columns(self, *args, aggr_func, aggr_column):
        temp_table = self.get_temp_table(args, aggr_column)
        aggregated_dict = self.use_aggr_func(temp_table, args, aggr_func,
                                             aggr_column)
        result_table = self.cast_to_ordered(aggregated_dict, aggr_column)
        return result_table

    def filter_func(self, filter_unit):
        column_name = filter_unit.field
        op = filter_unit.op
        value = TYPES[self.columns[column_name].type](filter_unit.value)
        return lambda table: OPERATIONS[op](table[column_name], value)

    # filter instructions
    def filter_table(self, table):
        conditions = self.pattern.filter
        if conditions is not None:
            filtered_table = deepcopy(table)
            for cond in conditions:
                # Проверка наличия поля фильтрации в таблице.
                if cond.field in filtered_table[0]:
                    filtered_table = filter(self.filter_func(cond),
                                            filtered_table)
            return list(filtered_table)
        return table  # Если нет фильтров

    # Методы для отрисовки таблицы
    def table_name(self, width):
        return f'{self.pattern.table_name}'.center(width, HORIZ_BORDER)

    def columns_names(self, table=None):
        columns = [EMPTY_STR]
        if table:
            line = table[0]  # Беру первую запись таблицы.
            for column in line:
                _column = self.columns[column]
                if _column.unit != EMPTY_STR:
                    value = ','.join([_column.name, _column.unit])
                else:
                    value = _column.name
                formatted_name = self.align_value(value, _column)
                columns.append(formatted_name)
            columns.append(EMPTY_STR)
            return VERT_BORDER.join(columns)
        else:
            columns.append(NOTHING_FOUND)
            columns.append(EMPTY_STR)
            return VERT_BORDER.join(columns)

    def table_width(self, table):
        return len(self.columns_names(table))

    def table_values(self, table=None):
        separator = HORIZ_BORDER * self.table_width(table)
        res = [separator]
        if table is not None:
            for line in table:
                # Хотя бы 1 значение должен напечатать.
                _values = [line.split('\n') for line in line.values()]
                line_feed_count = [line.count('\n') + 1
                                   for line in line.values()]
                _string_res = [[] for _ in range(max(line_feed_count))]
                for j in range(max(line_feed_count)):
                    for i in range(len(line_feed_count)):
                        if line_feed_count[i] > 0:
                            # Empty string for adding front border
                            _string_res[j].append(
                                VERT_BORDER.join([EMPTY_STR, _values[i][j]]))
                            line_feed_count[i] -= 1
                        else:
                            empty_field = ' ' * len(_values[i][0])
                            _string_res[j].append(
                                VERT_BORDER.join([EMPTY_STR, empty_field]))
                        # add back line border
                    _string_res[j].append(VERT_BORDER)
                    _string_res[j] = ''.join(_string_res[j])
                value_line = '\n'.join(_string_res)
                res.append(value_line)
                res.append(separator)
        return '\n'.join(res)

    def make_report(self, table, output_filename):
        table_width = self.table_width(table)
        table_name = self.table_name(table_width)
        table_columns = self.columns_names(table)
        table_values = self.table_values(table)
        result = '\n'.join([table_name, table_columns, table_values])

        # Поправить имя выходного файла в случае чего.
        with open(f'{output_filename}', 'w', encoding='utf-8') as file:
            file.write(result)

        return result
