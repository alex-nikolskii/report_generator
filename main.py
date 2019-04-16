from table_report_generator import TableReportGenerator
from report_generator import ReportGenerator
import entering_data as ed


def main():
    input_data = ed.input_data()
    for i in range(len(input_data.data_name)):
        if input_data.input_format == 'table':
            generator = TableReportGenerator(
                p_filename=input_data.pattern_name,
                p_enc=input_data.pattern_enc,
                d_filename=input_data.data_name[i],
                d_enc=input_data.data_enc,
                output_filename=f'{i + 1}_{input_data.output_filename}',
                default_field_width=input_data.default_field_width
            )
            # print(generator.generated_report)
        else:
            generator = ReportGenerator(
                p_filename=input_data.pattern_name,
                p_enc=input_data.pattern_enc,
                d_filename=input_data.data_name[i],
                d_enc=input_data.data_enc,
                default_field_width=input_data.default_field_width,
                output_filename=f'{i + 1}_{input_data.output_filename}'
            )
            # print(generator.generated_report)


if __name__ == '__main__':
    main()
