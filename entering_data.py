import argparse


class EnteredData:
    def __init__(self, namespace):
        self.pattern_name = namespace.pattern
        self.pattern_enc = namespace.pattern_encoding
        self.data_name = namespace.data
        self.data_enc = namespace.data_encoding
        self.default_field_width = namespace.default_field_width
        self.output_filename = namespace.output_filename
        self.input_format = namespace.input_format


def create_argument_parser():
    description = 'This program is for automation of creating reports'
    epilog = ('\n\nExit code "0" - Successfully ended.\nExit code "1" - '
              'Exception during the working with the file. Check filename\'s '
              '\n\nMarch 2019, Ural Federal University')
    pattern_help = 'Pattern is needed for substitution of your data'
    data_help = ('Input data will be substituted to the pattern.\n'
                 'You can add a few files with data.\n'
                 'It will be looks like \'-d f1.txt f2.txt\'')
    data_enc_help = ('Helps you solve problems '
                     'with text\'s readability of data.\n'
                     'Default encoding is cp1251.')
    field_width_help = 'Defines the number of positions for the key'
    pattern_enc_help = ('Helps you solve problems '
                        'with text\'s readability of the pattern.\n'
                        'Default encoding is cp1251.')
    input_format_help = 'Chooses a form to read data from table or from text\n'

    parser = argparse.ArgumentParser(
        prog='ReportsGenerator',
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--pattern', '-p',
        metavar='PATTERN',
        type=str,
        help=pattern_help,
        required=True
    )
    parser.add_argument(
        '--data', '-d',
        metavar='DATA',
        nargs='+',
        type=str,
        help=data_help,
        required=True
    )
    parser.add_argument(
        '--data_encoding', '-de',
        metavar='DATA_ENCODING',
        type=str,
        help=data_enc_help,
        default='utf-8'
    )
    parser.add_argument(
        '--pattern_encoding', '-pe',
        metavar='PATTERN_ENCODING',
        type=str,
        help=pattern_enc_help,
        default='utf-8'
    )
    parser.add_argument(
        '--input_format', '-in',
        metavar='IN_FORMAT',
        type=str,
        choices=['table', 'text'],
        help=input_format_help,
        required=True
    )
    parser.add_argument(
        '--default-field-width', '-l',
        metavar='WIDTH',
        type=int,
        help=field_width_help,
        default=20
    )
    parser.add_argument(
        '--output-filename', '-out',
        metavar='OUTPUT',
        type=str,
        default='generated_report.txt'
    )
    return parser


def input_data():
    parser = create_argument_parser()
    namespace = parser.parse_args()

    return EnteredData(namespace)








