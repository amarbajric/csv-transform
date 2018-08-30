import csv
import sys
import datetime
import argparse
import re

version = '0.1'

def define_args():
    parser = argparse.ArgumentParser(description='Transform/Modify a given csv file')
    parser.add_argument('-f','--file', metavar='inputfile', required=True,
                        help='The input file that should be processed. Needs to be a comma separated file (i.e. csv file) with a header')
    parser.add_argument('-o','--output', metavar='ofile', required=False,
                        help='The name or path of/to the output file. The output file will be saved in the same directory where the script was executed from if no path is given')
    parser.add_argument('-c','--count', metavar='count', required=False,
                        help='number of lines the program should process. Always starts from row zero to the specified count')
    parser.add_argument('-cd','--columndelete', metavar='column(s)', required=False,
                        help='Columns that should be deleted. Use the column names of the header and separate multiple entries with a comma (e.g. \'-d ID,UnitID\')')
    parser.add_argument('-tt','--timetransform', metavar='datetime', required=False,
                        help='Converts a datetime column into nanoseconds. Datetime needs to have format \'YYYY-MMMM-DD HH:MM:SS.f\'\nUse the column name of the header (e.g. \'-tt DateTime\')')
    parser.add_argument('-ct','--columntransform', metavar='column(s)', required=False,
                        help='Converts a columns value into a specific value. Use the column name of the header (e.g. \'-ct IsEventData:0->f,1->t;ValueStatus:0->f,1->t\')')
    parser.add_argument('-ca','--columnadd', metavar='column(s)', required=False,
                        help='Adds new columns with a given value to the file (e.g. \'-ca ColumnName:ColumnValue,AnotherColumnName:AnotherColumnValue\')')
    parser.add_argument('-v', '--version', action='version', version='{} v{}'.format(sys.argv[0].replace('.py',''), version))
    args = parser.parse_args()
    
    try:
        if args.columndelete != None:
            args.columndelete = args.columndelete.strip().replace(' ', '').split(',')
        if args.columntransform != None:
            regex = re.compile(r'^\s*(\w*\d*)\s*:\s*(.*)$')
            args.columntransform = dict([(m.group(1), [(x[0], x[1]) for x in (y.split('->') for y in m.group(2).split(','))]) for m in (re.match(regex, l) for l in args.columntransform.strip().replace(' ', '').split(';')) if m])
        if args.columnadd != None:
            args.columnadd = [(m[0], m[1]) for m in (y.split(':') for y in args.columnadd.strip().replace(' ', '').split(','))]
        return args
    except:
        print "Arguments could not be parsed. Check out the help section with \'-h\' to get an overview on how values have to be passed exactly!"
        sys.exit(1)

def unix_time_to_nano(dt):
    try:
        dt_transformed = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M:%S.%f")
        epoch = datetime.datetime.utcfromtimestamp(0)
        return (dt_transformed - epoch).total_seconds() * 1000000000
    except ValueError as valerr:
        raise valerr

def add_columns(columns, c_names, row, first_iteration=False):
    try:
        for column_tuple in columns:
            if first_iteration:
                row.append(column_tuple[0])
            else:
                if column_tuple[1] == 'time':
                    row.append(str(datetime.datetime.now()))
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
    return row

def remap_c_names(c_names, row):
    for i,column_name in enumerate(row):
        if column_name in c_names:
            c_names[column_name] = (c_names[column_name][0], i)
        else:
            c_names[column_name] = (None, i)
    return c_names


def readCsv():
    try:
        args = define_args()
        with open(args.file, mode='r') as csv_file_read:
            csv_reader = csv.reader(csv_file_read, delimiter=',')
            if args.output != None:
                csv_file_write = open(args.output, mode='w')
            else:
                csv_file_write = open(csv_file_read.name.replace('.csv', '.mod.csv'), mode='w')
            csv_writer = csv.writer(csv_file_write, delimiter=',')
            line_count = 0
            c_names = {} #column names extracted from header of original file
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
                if args.timetransform != None and line_count > 0:
                    row[c_names[args.timetransform][1]] = int(unix_time_to_nano(row[c_names[args.timetransform][1]]))
                if args.columntransform != None and line_count > 0:
                    row = transform_columns(args.columntransform, c_names, row)
                    
                csv_writer.writerow(row)
                line_count += 1
            print "Modified " + str(line_count) + " lines!"
            csv_file_read.close()
            csv_file_write.close()        
    except IOError as ioerr:
        print "File " + sys.argv[1] + " does not exist!"
        print err
        sys.exit(1)
    except ValueError as valerr:
        print "The provided datetime does not have the right format for transformation!\nFormat should be \'YYYY-MMMM-DD HH:MM:SS.f\'"
        sys.exit(1)
    except KeyError as keyerr:
        print "KeyError: The provided column name " + str(keyerr) + " does not match any column name in the header of the file"
        wrong_key = str(keyerr).replace('\'', '').lower()
        suggestion = [m for m in c_names.keys() if m.lower() == wrong_key or ((m.lower().startswith(wrong_key[:2]) or m.lower().endswith(wrong_key[-2:]) or 
        wrong_key in m.lower()) and len(wrong_key) > 2)]
        if len(suggestion) > 0:
            print "Did you mean to use the colum name '" + suggestion[0] + "' instead?"
        sys.exit(1)
    except KeyboardInterrupt as userr:
        print "Aborted by user. Exiting program..."
        sys.exit(0)


readCsv()