import csv
import sys
import datetime
import argparse
import re

version = '0.2.2'
special_expressions = ['@timestamp', '@unix']
unix_mapping = {'millis': 1000, 'micros': 1000000, 'nanos': 1000000000}

def define_args():
    parser = argparse.ArgumentParser(description='Transform/Modify a given csv file')
    parser.add_argument('-f','--file', metavar='inputfile', required=True,
                        help='The input file that should be processed. Needs to be a comma separated file (i.e. csv file) with a header')
    parser.add_argument('-o','--output', metavar='ofile', required=False,
                        help='The name or path of/to the output file. The output file will be saved in the same directory where the script was executed from if no path is given')
    parser.add_argument('-c','--count', metavar='count', required=False,
                        help='number of lines the program should process. Always starts from row zero to the specified count')
    parser.add_argument('-cd','--columndelete', metavar='column(s)', required=False,
                        help='Columns that should be deleted. Use the column names of the header and separate multiple entries with a comma.')
    parser.add_argument('-ct','--columntransform', metavar='column(s)', required=False,
                        help='''Converts a columns value into a specific value. Use the column name of the header.
                        Special expressions are supported. Check out the documentation for more information!''')
    parser.add_argument('-ca','--columnadd', metavar='column(s)', required=False,
                        help='''Adds new columns with a given value to the file
                        Special expressions are supported. Check out the documentation for more information!''')
    parser.add_argument('-v', '--version', action='version', version='{} v{}'.format(sys.argv[0].replace('.py',''), version))
    args = parser.parse_args()
    
    try:
        if args.columndelete != None:
            args.columndelete = args.columndelete.strip().replace(' ', '').split(',')
        if args.columntransform != None:
            regex = re.compile(r'^\s*(\w*\d*)\s*:\s*(.*)$')
            args.columntransform = dict([(m.group(1), [(x[0], x[1]) for x in (y.split('->') for y in m.group(2).split(','))]) for m in (re.match(regex, l) for l in args.columntransform.strip().split(';')) if m])
        if args.columnadd != None:
            args.columnadd = [(m[0], m[1]) for m in (y.split(':', 1) for y in args.columnadd.strip().split(','))]
        return args
    except:
        print "Arguments could not be parsed. Check out the help section with \'-h\' to get an overview on how values have to be passed exactly!"
        sys.exit(1)

def convert_timestamp(dt, expressions):
    expr_split = [(exp[0], exp[1].replace('}', '')) for exp in (tup.split('{') for tup in expressions)]
    try:
        if expr_split[0][0] == '@timestamp':
            dt_source = datetime.datetime.strptime(dt, expr_split[0][1])
            if expr_split[1][0] == '@timestamp':
                return dt_source.strftime(expr_split[1][1])
            elif expr_split[1][0] == '@unix':
                epoch = datetime.datetime.utcfromtimestamp(0)
                return int((dt_source - epoch).total_seconds() * unix_mapping[expr_split[1][1]])
        elif expr_split[0][0] == '@unix':
            dt_source = datetime.datetime.utcfromtimestamp(float(dt) / unix_mapping[expr_split[0][1]])
            if expr_split[1][0] == '@timestamp':
                return dt_source.strftime(expr_split[1][1])
            elif expr_split[1][0] == '@unix':
                epoch = datetime.datetime.utcfromtimestamp(0)
                return int((dt_source - epoch).total_seconds() * unix_mapping[expr_split[1][1]])
    except ValueError as valerr:
        raise Exception("TimeStampConvertError: The expression \'{}\' for the timestamp \'{}\' is not valid!\nWhat went wrong: {}".format('->'.join(exp for exp in expressions), dt, valerr))

def create_timestamp(expression):
    expr_split = [exp.replace('}', '') for exp in expression.split('{')]
    dt = datetime.datetime

    try:
        if expr_split[0] == '@timestamp' and len(expr_split[1]) > 0:
            return dt.now().strftime(expr_split[1])
        elif expr_split[0] == '@unix' and expr_split[1] in unix_mapping.keys():
            epoch = dt.utcfromtimestamp(0)
            return int((dt.now() - epoch).total_seconds() * unix_mapping[expr_split[1]])
        else:
            raise Exception('TimeStampCreationError: The expression \'{}\' is not valid!\nYour expression is missing a (valid) format argument'.format(expression))
    except IndexError as ixerr:
        raise Exception('TimeStampCreationError: The expression \'{}\' does not contain any format argument!'.format(expression))

def add_columns(columns, c_names, row, first_iteration=False):
    try:
        for column_tuple in columns:
            if first_iteration:
                row.append(column_tuple[0])
            else:
                if column_tuple[1].startswith('@') and column_tuple[1].split('{')[0] not in special_expressions:
                    raise Exception('ColumnAddError: The specified expression \'{}\' for the column \'{}\' is not valid!\nAvailable expressions are {}'.format(column_tuple[1], column_tuple[0], ', '.join(special_expressions)))
                elif column_tuple[1].startswith('@') and column_tuple[1].split('{')[0] in special_expressions:
                    row.append(str(create_timestamp(column_tuple[1])))
                else:
                    print column_tuple[1]
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
            elif (transform_tuple[0].startswith('@') and transform_tuple[0].split('{')[0] not in special_expressions) and (transform_tuple[0].startswith('@') and transform_tuple[0].split('{')[0] not in special_expressions):
                raise Exception('ColumnTransformError: The specified expressions \'{}\' and \'{}\' for the column \'{}\' are not valid!\nAvailable expressions are {}'.format(transform_tuple[0], transform_tuple[1], arr_transforms[key][0], ', '.join(special_expressions)))
            elif (transform_tuple[1].startswith('@') and transform_tuple[1].split('{')[0] in special_expressions) or (transform_tuple[1].startswith('@') and transform_tuple[1].split('{')[0] in special_expressions):
                row[c_names[key][1]] = convert_timestamp(row[c_names[key][1]], transform_tuple)
    return row

def remap_c_names(c_names, row):
    for i,column_name in enumerate(row):
        if column_name in c_names:
            c_names[column_name] = (c_names[column_name][0], i)
        else:
            c_names[column_name] = (None, i)
    return c_names

def check_for_header(csv_file):
    try:
        sniffer = csv.Sniffer()
        has_header = sniffer.has_header(csv_file.read(2048))
    except:
        raise Exception("The inputfile does not seem to be a valid csv file with a header!")

def readCsv():
    try:
        args = define_args()
        with open(args.file, mode='r') as csv_file_read:
            check_for_header(csv_file_read)
            csv_reader = csv.reader(csv_file_read, delimiter=',')
            if args.output != None:
                csv_file_write = open(args.output, mode='w')
            else:
                csv_file_write = open(csv_file_read.name.replace('.csv', '.mod.csv'), mode='w')
            csv_writer = csv.writer(csv_file_write, delimiter=',')
            line_count = 0
            c_names = {}
            for row in csv_reader:
                if line_count == 0:
                    c_names = dict(map(lambda (i,x): (x,(i, None)) , enumerate(row)))
                    if args.columndelete != None:
                        row = delete_columns(args.columndelete, c_names, row)
                    if args.columnadd != None:
                        row = add_columns(args.columnadd, c_names, row, True)
                    c_names = remap_c_names(c_names, row)
                if args.count != None and int(args.count) == line_count:
                    break
                if args.columndelete != None and line_count > 0:
                    row = delete_columns(args.columndelete,c_names, row)
                if args.columnadd != None and line_count > 0:
                    row = add_columns(args.columnadd, c_names, row)
                if args.columntransform != None and line_count > 0:
                    row = transform_columns(args.columntransform, c_names, row)
                    
                csv_writer.writerow(row)
                line_count += 1
            print "Modified " + str(line_count) + " lines!"
            csv_file_read.close()
            csv_file_write.close()        
    except IOError as ioerr:
        print "File " + args.file + " does not exist!"
        print err
        sys.exit(1)
    except ValueError as valerr:
        print "DateTransformError: One of the provided timestamps does not match with the provided format!\nFormat should be \'YYYY-MMMM-DD HH:MM:SS.f\'"
        sys.exit(1)
    except KeyError as keyerr:
        print "KeyError: The provided column name " + str(keyerr) + " does not match any column name in the header of the file"
        wrong_key = str(keyerr).replace('\'', '').lower()
        suggestion = [m for m in c_names.keys() if m.lower() == wrong_key or ((m.lower().startswith(wrong_key[:2]) or m.lower().endswith(wrong_key[-2:]) or 
        wrong_key in m.lower()) and len(wrong_key) > 2)]
        if len(suggestion) > 0:
            print "Did you mean to use the colum name '" + suggestion[0] + "' instead?"
        sys.exit(1)
    except IndexError as ixerr:
        print ixerr
    except KeyboardInterrupt as userr:
        print "Aborted by user. Exiting program..."
        sys.exit(0)
    except Exception as exerr:
        print exerr
        sys.exit(1)


readCsv()