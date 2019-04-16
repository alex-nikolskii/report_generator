import unittest
from collections import OrderedDict, namedtuple

from table_report_generator import TableReportGenerator
from report_generator import ReportGenerator

Column = namedtuple('Column', ['width', 'align'])


class TestTableReportGeneratorMethods(unittest.TestCase):

    def setUp(self):
        self.pattern_name = 'tests_/test_table_pattern.txt'
        self.data_name = 'tests_/test_table_data.txt'
        self.data_name2 = 'tests_/test_table_data2.txt'
        self.output_name = 'tests_/test_generated_report.txt'

    def test_initialize_grouped_table(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name,
            output_filename=self.output_name
        )
        actual = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 38.0)]),
                  OrderedDict([('ПОЛ', 'ж'), ('СТОИМОСТЬ', 21.36)])]
        self.assertEqual(generator.grouped_table, actual)

    def test_none_initialize_grouped_table(self):
        generator = TableReportGenerator(
            p_filename='tests_/test_none_group_pattern.txt',
            d_filename=self.data_name,
            output_filename=self.output_name
        )
        actual = None
        self.assertEqual(generator.grouped_table, actual)

    def test_format_data_values(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        actual = [OrderedDict([('ФИО', 'Никольский А.А.'),
                              ('ТАРИФ', 'Безлимит\nпочти\nна все\n100'),
                              ('СЧЕТ', 1234),
                              ('ПОЛ', 'м'),
                              ('СТОИМОСТЬ', 20)]),
                  OrderedDict([('ФИО', 'Никольский А.А.'),
                              ('ТАРИФ', 'Безлимит'),
                              ('СЧЕТ', 1234),
                              ('ПОЛ', 'м'),
                              ('СТОИМОСТЬ', 20)]),
                  OrderedDict([('ФИО', 'Никольский А.А.'),
                              ('ТАРИФ', 'Безлимит'),
                              ('СЧЕТ', 1234),
                              ('ПОЛ', 'м'),
                              ('СТОИМОСТЬ', 20)])]
        self.assertEqual(generator.data.table, actual)

    def test_align_value(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        column = Column(width=20, align='c')
        value = 'hi!!'
        self.assertEqual(generator.align_value(value, column),
                         '        hi!!        ')

    def test_format_value(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        column = Column(width=5, align='l')
        value = 'hey'
        self.assertEqual(generator.format_value(value, column), 'hey  ')

        value = 'hey\nhoh'
        self.assertEqual(generator.format_value(value, column), 'hey  \nhoh  ')

    def test_format_column_data(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        actual = [OrderedDict([('ПОЛ', '         м          '),
                               ('СТОИМОСТЬ', '        20.0        ')])]
        self.assertEqual(generator.filtered_table, actual)

    def test_get_temp_table(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        actual = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                  OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                  OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)])]
        self.assertEqual(generator.get_temp_table(
            ['ПОЛ'], aggr_column='СТОИМОСТЬ'), actual)

    def test_use_aggr_func(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        table = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)])]
        actual = {(('ПОЛ', 'м'),): 20.0}
        self.assertEqual(generator.use_aggr_func(
            table, ['ПОЛ'], 'avg', 'СТОИМОСТЬ'), actual)

    def test_cast_to_ordered(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        _dict = {(('ПОЛ', 'м'),): 20.0}
        actual = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20.0)])]
        self.assertEqual(generator.cast_to_ordered(_dict, 'СТОИМОСТЬ'), actual)

    def test_filter_table(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        table = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)])]

        actual = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                  OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                  OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)])]
        self.assertEqual(generator.filter_table(table), actual)

    def test_table_name(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        width = 21
        actual = '----Годовой отчет----'
        self.assertEqual(generator.table_name(width), actual)

    def test_column_names(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        table = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)])]
        actual = '|        ПОЛ         |     СТОИМОСТЬ      |'
        self.assertEqual(generator.columns_names(table), actual)

        table = None
        actual = '|Ничего не найдено. Проверьте шаблон и данные|'
        self.assertEqual(generator.columns_names(table), actual)

    def test_table_width(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        table = [OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)]),
                 OrderedDict([('ПОЛ', 'м'), ('СТОИМОСТЬ', 20)])]
        actual = '|        ПОЛ         |     СТОИМОСТЬ      |'
        self.assertEqual(generator.table_width(table), len(actual))

        table = None
        actual = '|Ничего не найдено. Проверьте шаблон и данные|'
        self.assertEqual(generator.table_width(table), len(actual))

    def test_table_values(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        table = [OrderedDict([('ПОЛ', '         м          '),
                              ('СТОИМОСТЬ', '        20.0        ')])]
        actual = '-------------------------------------------\n' \
                 '|         м          |        20.0        |\n' \
                 '-------------------------------------------'
        self.assertEqual(generator.table_values(table), actual)

        table = None
        actual = '----------------------------------------------'
        self.assertEqual(generator.table_values(table), actual)

    def test_make_report(self):
        generator = TableReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name2,
            output_filename=self.output_name
        )
        actual = '---------------Годовой отчет---------------\n' \
                 '|        ПОЛ         |     СТОИМОСТЬ      |\n' \
                 '-------------------------------------------\n' \
                 '|         м          |        20.0        |\n' \
                 '-------------------------------------------'
        self.assertEqual(generator.generated_report, actual)

        table = None
        actual = '----------------Годовой отчет-----------------\n'\
                 '|Ничего не найдено. Проверьте шаблон и данные|\n'\
                 '----------------------------------------------'
        self.assertEqual(generator.make_report(table, self.output_name),
                         actual)


class TestReportGeneratorMethods(unittest.TestCase):

    def setUp(self):
        self.pattern_name = 'tests_/test_text_pattern.txt'
        self.data_name = 'tests_/test_text_data.txt'
        self.data_name2 = 'tests_/test_text_data2.txt'
        self.pattern_enc = 'utf-8'
        self.pattern_name2 = 'tests_/test_text_pattern2.txt'

    def test_read_pattern(self):
        generator = ReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name
        )
        actual = 'Report:\n{{name}}'
        self.assertEqual(generator.read_pattern(
            self.pattern_name, self.pattern_enc), actual)

    def test_declension(self):
        generator = ReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name
        )
        value = '11'
        word = 'рубль'
        actual = '11 рублей'
        self.assertEqual(f'11 {generator.declension(value, word)}', actual)

    def test_make_report_default_field(self):
        generator = ReportGenerator(
            p_filename=self.pattern_name,
            d_filename=self.data_name
        )
        actual = 'Report:\n        alex        '
        self.assertEqual(generator.generated_report, actual)

    def test_make_report_all_fields_types(self):
        generator = ReportGenerator(
            p_filename=self.pattern_name2,
            d_filename=self.data_name2
        )
        actual = '        alex        \n' \
                 '       Horhe        \n' \
                 '    Aleksandrii     \n' \
                 'home,                    \n' \
                 'sweet home               \n' \
                 '   UuU lights  '
        self.assertEqual(generator.generated_report, actual)


































