import argparse
import csv
import datetime
import re
import sys


# Global variables
version = '0.3'
spec_cond = ['@timestamp']
spec_expr = ['@timestamp']
unix_mapping = {'millis': 1000, 'micros': 1000000, 'nanos': 1000000000}


def define_args():
    parser = argparse.ArgumentParser(description='Transform/Modify a given csv file')
    parser.add_argument('-f', '--file', metavar='<input_file_path>', required=True,
                        help='The input file that should be processed. Needs to be a comma separated file (i.e. csv file) with a header')
    parser.add_argument('-o', '--output', metavar='<output_file_path>', required=False,
                        help='The name or path of/to the output file. The output file will be saved in the same directory where the script was executed from if no path is given')
    parser.add_argument('-l', '--limit', metavar='<limit>', required=False,
                        help='number of lines the program should process. Always starts from row zero to the specified limit')
    parser.add_argument('-d', '--debug', action='store_true', required=False,
                        help='Prints each transformed row to the CLI instead of writing it to a new file. Can be combined with \'-l\' or \'--limit\' to limit results in the CLI')
    parser.add_argument('-cd', '--columndelete', metavar='[<column_name>[,<column_name>]]', required=False,
                        help='Columns that should be deleted. Use the column names of the header and separate multiple entries with a comma.')
    parser.add_argument('-ct', '--columntransform', metavar='[<column_name>:<column_value>-><column_value_transform>,[;<column_name>:<column_value>-><column_value_transform>]]',
                        required=False, help='''Converts a columns value into a specific value. Use the column name of the header.
                        Special expressions are supported. Check out the documentation for more information!''')
    parser.add_argument('-ca', '--columnadd', metavar='[<column_name>:<column_value>[,<column_name>:<column_value>]]', required=False,
                        help='''Adds new columns with a given value to the file
                        Special expressions are supported. Check out the documentation for more information!''')
    parser.add_argument('-v', '--version', action='version', version='{} v{}'.format(sys.argv[0].replace('.py',''), version))
    args = parser.parse_args()

    regex_spec_cond = re.compile(r'^\s*(\w*\d*)\s*:\s*(@\w*\{.*\}\s*->\s*@\w*\{.*\})\s*$')
    dict_cond_parser = lambda arg: dict([(m.group(1), [(x[0], x[1]) for x in (y.split('->') for y in m.group(2).split(','))]) for m in (re.match(regex_spec_cond, l) for l in arg.strip().split(';')) if m])

    if args.columndelete is not None:
        args.columndelete = args.columndelete.strip().replace(' ', '').split(',')
    if args.columntransform is not None:
        args.columntransform = dict_cond_parser(args.columntransform)
        if len(args.columntransform) < 1:
            exception_handler(Exception("ArgumentParseError: Could not parse argument for \'-ct\' \'--columntransform\' argument!"))
    if args.columnadd is not None:
        args.columnadd = [(m[0], m[1]) for m in (y.split(':', 1) for y in args.columnadd.strip().split(','))]
    if args.limit is not None:
        if type(int(args.limit)) is not int:
            exception_handler(Exception("ArgumentParseError: Could not parse argument for \'-l\' \'--limit\' argument!"))
    return args


def exception_handler(exception, args=None):
    print "\n"
    if type(exception) is IOError:
        print "File " + args[0].file + " does not exist!"
        print exception
        sys.exit(1)
    elif type(exception) is ValueError:
        print "DateTransformError: One of the provided timestamps does not match with the provided format!\nFormat should be \'YYYY-MMMM-DD HH:MM:SS.f\'"
        sys.exit(1)
    elif type(exception) is KeyError:
        print "KeyError: The provided column name " + str(exception) + " does not match any column name in the header of the file"
        wrong_key = str(exception).replace('\'', '').lower()
        suggestion = [m for m in args[1].keys() if m.lower() == wrong_key or
                      ((m.lower().startswith(wrong_key[:2]) or
                        m.lower().endswith(wrong_key[-2:]) or
                        wrong_key in m.lower()) and len(wrong_key) > 2)]
        if len(suggestion) > 0:
            print "Did you mean to use the column name '" + suggestion[0] + "' instead?"
        sys.exit(1)
    elif type(exception) is IndexError:
        print exception
    elif type(exception) is KeyboardInterrupt:
        print "Aborted by user. Exiting program..."
        sys.exit(0)
    elif type(exception) is Exception:
        print exception
        sys.exit(1)


def print_progress_bar(progress, total, cli_length=50):
    percent = "{0:.1f}".format(100 * (progress / float(total)))
    filled_length = int(cli_length * progress // total)
    bar = '#' * filled_length + '-' * (cli_length - filled_length)
    sys.stdout.write('\r%s [%s] %s%% %s' % ('Progress:', bar, percent, 'Complete'))
    sys.stdout.flush()


def convert_timestamp(dt, expressions):
    expr_split = [exp[1].replace('}', '') for exp in (tup.split('{') for tup in expressions)]
    try:
        if expr_split[0].startswith('unix') and expr_split[0][5:] in unix_mapping.keys():
            dt_source = datetime.datetime.utcfromtimestamp(float(dt) / unix_mapping[expr_split[0][5:]])
            if expr_split[1].startswith('unix') and expr_split[1][5:] in unix_mapping.keys():
                epoch = datetime.datetime.utcfromtimestamp(0)
                return int((dt_source - epoch).total_seconds() * unix_mapping[expr_split[1][5:]])
            else:
                return dt_source.strftime(expr_split[1])
        else:
            dt_source = datetime.datetime.strptime(dt, expr_split[0])
            if expr_split[1].startswith('unix') and expr_split[1][5:] in unix_mapping.keys():
                epoch = datetime.datetime.utcfromtimestamp(0)
                return int((dt_source - epoch).total_seconds() * unix_mapping[expr_split[1][5:]])
            else:
                return dt_source.strftime(expr_split[1])
    except ValueError as valerr:
        exception_handler(Exception("TimeStampConvertError: The expression \'{}\' for the timestamp \'{}\' is not valid!\n{}".format('->'.join(exp for exp in expressions), dt, valerr)))


def create_timestamp(expression):
    expr_split = expression.split('{')[1][:-1]
    dt = datetime.datetime
    if expr_split.startswith('unix') and expr_split[5:] in unix_mapping.keys():
        epoch = dt.utcfromtimestamp(0)
        return int((dt.now() - epoch).total_seconds() * unix_mapping[expr_split[5:]])
    elif expr_split:
        return dt.now().strftime(expr_split)
    else:
        exception_handler(Exception('TimeStampCreationError: The expression \'{}\' is not valid!\nYour expression is missing a (valid) format argument'.format(expression)))


def add_columns(columns, row, first_iteration=False):
    try:
        for column_tuple in columns:
            if first_iteration:
                row.append(column_tuple[0])
            else:
                if column_tuple[1].startswith('@') and column_tuple[1].split('{')[0] not in spec_expr:
                    raise Exception('ColumnAddError: The specified expression \'{}\' for the column \'{}\' is not valid!\nAvailable expressions are {}'.format(column_tuple[1], column_tuple[0], ', '.join(spec_expr)))
                elif column_tuple[1].startswith('@') and column_tuple[1].split('{')[0] in spec_expr:
                    row.append(str(create_timestamp(column_tuple[1])))
                else:
                    row.append(column_tuple[1])
        return row
    except KeyError as keyerr:
        raise keyerr


def delete_columns(columns, c_names, row):
    try:
        for i, column in enumerate(columns):
            del row[c_names[column][0] - i]
        return row
    except KeyError as keyerr:
        raise keyerr


def transform_columns(columns_dict, c_names, row):
    for key,arr_transforms in columns_dict.iteritems():
        for transform_tuple in arr_transforms:
            if str(transform_tuple[0]) == str(row[c_names[key][1]]):
                row[c_names[key][1]] = transform_tuple[1]
            elif (transform_tuple[0].startswith('@') and transform_tuple[0].split('{')[0] not in spec_expr) and (transform_tuple[0].startswith('@') and transform_tuple[0].split('{')[0] not in spec_expr):
                raise Exception('ColumnTransformError: The specified expressions \'{}\' and \'{}\' for the column \'{}\' are not valid!\nAvailable expressions are {}'.format(transform_tuple[0], transform_tuple[1], arr_transforms[key][0], ', '.join(spec_expr)))
            elif (transform_tuple[1].startswith('@') and transform_tuple[1].split('{')[0] in spec_expr) or (transform_tuple[1].startswith('@') and transform_tuple[1].split('{')[0] in spec_expr):
                row[c_names[key][1]] = convert_timestamp(row[c_names[key][1]], transform_tuple)
    return row


def remap_c_names(c_names, row):
    for i, column_name in enumerate(row):
        if column_name in c_names:
            c_names[column_name] = (c_names[column_name][0], i)
        else:
            c_names[column_name] = (None, i)
    return c_names


def check_input_file(csv_file):
    try:
        sniffer = csv.Sniffer()
        sniffer.has_header(csv_file.read(2048))
        csv_file.seek(0)
        row_count = sum(1 for _ in csv_file)
        csv_file.seek(0)
        return row_count
    except:
        exception_handler(Exception("The inputfile does not seem to be a valid csv file with a header!"))


def transform_csv():
    try:
        args = define_args()
        with open(args.file, mode='r') as csv_file_read:
            row_count = check_input_file(csv_file_read)
            csv_reader = csv.reader(csv_file_read, delimiter=',')
            if args.debug is False:
                if args.output is not None:
                    csv_file_write = open(args.output, mode='w')
                elif args.output is None:
                    csv_file_write = open(csv_file_read.name.replace('.csv', '.mod.csv'), mode='w')
                csv_writer = csv.writer(csv_file_write, delimiter=',')
            else:
                print "Program started in debug mode!\n{}".format('-' * 60)
                debug_output = []
            c_names = {}
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    c_names = dict(map(lambda (i,x): (x,(i, None)), enumerate(row)))
                    if args.columndelete is not None:
                        row = delete_columns(args.columndelete, c_names, row)
                    if args.columnadd is not None:
                        row = add_columns(args.columnadd, row, True)
                    c_names = remap_c_names(c_names, row)
                if args.limit is not None and int(args.limit) == line_count:
                    break
                if args.columndelete is not None and line_count > 0:
                    row = delete_columns(args.columndelete, c_names, row)
                if args.columnadd is not None and line_count > 0:
                    row = add_columns(args.columnadd, row)
                if args.columntransform is not None and line_count > 0:
                    row = transform_columns(args.columntransform, c_names, row)

                line_count += 1
                if args.debug is True:
                    print ', '.join(row)
                    debug_output.append(row)
                else:
                    csv_writer.writerow(row)
                    print_progress_bar(line_count, row_count)
            if args.debug is False:
                print "\nTransformed " + str(line_count) + " lines!"
                csv_file_read.close()
                csv_file_write.close()
            else:
                return debug_output
    except Exception as exception:
        exception_handler(exception, [args, c_names])


transform_csv()
