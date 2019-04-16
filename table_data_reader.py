from collections import OrderedDict


class TableDataReader:
    def __init__(self, filename='table_data.txt', encoding='utf-8'):
        self.table = self.__read_table(filename, encoding)

    @staticmethod
    def validate_table(table, fieldnames):
        for i in range(len(table)):
            if len(fieldnames) < len(table[i]):
                raise ValueError(f'TableDataError: no column name '
                                 f'in row !{i}!')
            elif len(fieldnames) > len(table[i]):
                raise ValueError(f'TableDataError: no column value '
                                 f'in row !{i}!')
            else:
                pass

    @staticmethod
    def __convert_file(fin):
        split_text = (line for line in fin.read().split('#'))
        # got rid of extra space symbols and ''
        text_lines = filter(None, (map(str.strip, split_text)))
        res_lines = (line.split(',') for line in text_lines)
        return list(res_lines)

    def __read_table(self, filename, encoding):
        with open(filename, 'r', encoding=encoding, newline='') as fin:
            try:
                fieldnames = fin.readline().rstrip().upper().split(',')
                lines = self.__convert_file(fin)

                # Handling excessive fields
                self.validate_table(lines, fieldnames)

                res = [OrderedDict(zip(fieldnames, line)) for line in lines]
                return res
            except ValueError as error:
                print(error)
                return None
