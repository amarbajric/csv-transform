# csv-transform
A CSV parser that is able to do different transformations or modifications based on a given csv file.

Development of this software is maintained by:

| GithubID      | URL                             |
| ------------- |:-------------------------------:|
| @amarbajric   | (https://github.com/amarbajric) |


## Installation

The script is making use of multiple modules coming from the [Python Standard Library](https://docs.python.org/2/library/).
In this case, the only thing to worry about is a working python installation ;)

### Requirements
 - Python v2.7+ (preferrably Python v2.7+ should be used as this script was not tested with Python3 yet!)
   - Tested on the following Python version(s): 2.7.10


## Dependencies
As already mentioned before, the script is only making use of modules from the [Python Standard Library](https://docs.python.org/2/library/) that are the following:
 - csv
 - sys
 - argparse
 - datetime
 - re

 Hence, **NO** extra dependencies are given.


## Documentation

### Available arguments
```
  -h, --help            show this help message and exit
  -f inputfile, --file inputfile
                        The input file that should be processed. Needs to be a
                        comma separated file (i.e. csv file) with a header
  -o ofile, --output ofile
                        The name or path of/to the output file. The output
                        file will be saved in the same directory where the
                        script was executed from if no path is given
  -c count, --count count
                        number of lines the program should process. Always
                        starts from row zero to the specified count
  -cd column(s), --columndelete column(s)
                        Columns that should be deleted. Use the column names
                        of the header and separate multiple entries with a
                        comma (e.g. '-d ID,UnitID')
  -tt datetime, --timetransform datetime
                        Converts a datetime column into nanoseconds. Datetime
                        needs to have format 'YYYY-MMMM-DD HH:MM:SS.f' Use the
                        column name of the header (e.g. '-tt DateTime')
  -ct column(s), --columntransform column(s)
                        Swaps a columns value with another given value. Use
                        the column name of the header 
                        (e.g. '-ct BooleanValue:0->false,1->true;AnotherBooleanColumn:0->false,1->true')
  -ca column(s), --columnadd column(s)
                        Adds new columns with a given value to the file 
                        (e.g. '-ca ColumnName:ColumnValue,AnotherColumnName:AnotherColumnValue')
  -v, --version         show program's version number and exit
```


## Examples
TBD

## TODO
1. Allow the timestamp (i.e. `-tt`) parser to extract more than one column (support for multiple columns).
2. Allow the `-tt` flag to convert to a unix timestamp and vice versa. Use a source format and destination format for the time transformation.
2.1 Implement a `-tf` flag for time format which gets a format as input.
3. Add support for `-ct` to allow empty strings or nonetypes to transform to any given value.
5. BUG: FIX bug where no error is thrown if a column in header is NOT present which is given for deletion, transformation or timetransforming.
6. Add support for verbose output and quiet output (i.e. show how much lines have already been processed and how much are ahead etc).
7. Create an issue for every TODO
