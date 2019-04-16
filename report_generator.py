import re

from data_reader import DataReader
from pymorphy2 import MorphAnalyzer

ALIGN = {
    'c': str.center,
    'r': str.rjust,
    'l': str.ljust,
    'с': str.center
}

FIELD_PATTERN = re.compile(r'''(?P<screen>!!)?
                             {{(?P<name>[\w\s\-,]+)\|?\s*
                               (?P<width>\d+)?-?\s*
                               (?P<align>[rcl])?-?\s*
                               (?P<unit>\w+[\w\s\-,]*)?}}
                            ''', re.X)


class ReportGenerator:
    def __init__(self, d_filename, p_filename,
                 output_filename='generated_report.txt',
                 d_enc='utf-8', p_enc='utf-8', default_field_width=20):
        self.pattern = self.read_pattern(p_filename, p_enc)
        self.sub_data = DataReader(d_filename, d_enc).fields
        self.generated_report = self.make_report(output_filename,
                                                 default_field_width)

    @staticmethod
    def read_pattern(filename, encoding):
        with open(filename, 'r', encoding=encoding) as file:
            return file.read()

    @staticmethod
    def align_value(value, width, align):
        if len(value) >= width:
            temp_value = value[:width]
        else:
            temp_value = ALIGN[align](value, width)
        return temp_value

    # Склонение
    @staticmethod
    def declension(value, word):
        morph = MorphAnalyzer()
        if word != '':
            obj_name = morph.parse(word)[0]
            return obj_name.make_agree_with_number(int(value))[0]
        return word

    def format_value(self, value, width, align, unit):
        if value.isdigit():
            unit = self.declension(value, unit)
        value = ' '.join([value, unit]) if unit != '' else value
        if '\n' in value:
            _value = [self.align_value(line, width, align) for line
                      in value.split('\n')]
            aligned_value = '\n'.join(_value)
        else:
            aligned_value = self.align_value(value, width, align)
        return aligned_value

    @staticmethod
    def none_check(field, default):
        return field if field is not None else default

    def initialize_match_fields(self, match):
        name = match.group('name').upper()
        align = self.none_check(match.group('align'), 'c')
        unit = self.none_check(match.group('unit'), '')
        return name, align, unit

    @staticmethod
    def write_report(filename, report):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(report)

    def make_report(self, output_filename, _default_key_len):
        pattern = self.pattern.split('#')
        for i in range(len(pattern)):
            fields = FIELD_PATTERN.finditer(pattern[i])
            for match in fields:
                if match.group('screen') is not None:
                    pattern[i] = pattern[i].replace('!!', '')
                    continue
                name, align, unit = self.initialize_match_fields(match)
                value = self.sub_data.get(name, None)
                try:
                    if value is None:
                        raise ValueError(f'No value for name: '
                                         f'{match.group("name")}')

                    # only int acceptable
                    width = int(self.none_check(match.group('width'),
                                                _default_key_len))
                except ValueError as err:
                    print(str(err))
                else:
                    format_value = self.format_value(value, width, align, unit)
                    sub_pattern = re.compile(
                        fr'''{{{{(?P<name>{match.group('name')})\|?\s*
                                 (?P<width>{match.group('width')})?-?\s*
                                 (?P<align>{match.group('align')})?-?\s*
                                 (?P<unit>{match.group('unit')})?\s*}}}}
                          ''', re.X)
                    pattern[i] = sub_pattern.sub(format_value, pattern[i])
        result = ''.join(pattern)
        self.write_report(output_filename, result)
        return result
