# csv-transform
A CSV parser that is able to do different transformations or modifications on a given csv file.

Development of this software is maintained by:

| GithubID      | URL                             |
| ------------- |:-------------------------------:|
| @amarbajric   | (https://github.com/amarbajric) |


## Installation

The script is making use of multiple modules coming from the [Python Standard Library](https://docs.python.org/2/library/).
In this case, the only thing to worry about is a working python installation :)

### Requirements
 - `Python v2.7+` (preferably Python v2.7+ should be used as this script was written for Python 2.7+ only!)
   - Tested on the following Python version: `2.7.10`


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
The currently supported arguments are the following:
```
  -h, --help            show this help message and exit
  -f inputfile, --file inputfile
                        The input file that should be processed. Needs to be a
                        comma separated file (i.e. csv file) with a header
  -o ofile, --output ofile
                        The name or path of/to the output file. The output
                        file will be saved in the same directory where the
                        script was executed from if no path is given
  -l limit, --limit limit
                        number of lines the program should process. Always
                        starts from row zero to the specified limit
  -d, --debug           Prints each transformed row to the CLI instead of
                        writing it to a new file. Can be combined with '-l' or
                        '--limit' to limit results in the CLI
  -cd column(s), --columndelete column(s)
                        Columns that should be deleted. Use the column names
                        of the header and separate multiple entries with a
                        comma.
  -ct column(s), --columntransform column(s)
                        Converts a columns value into a specific value. Use
                        the column name of the header. Special expressions are
                        supported. Check out the documentation for more
                        information!
  -ca column(s), --columnadd column(s)
                        Adds new columns with a given value to the file
                        Special expressions are supported. Check out the
                        documentation for more information!
  -v, --version         show program's version number and exit
```

### Arugments Overview
The following table describes every argument in more detail and its usage

| Argument            | Description                                              | Examples                               |
| --------------------|:---------------------------------------------------------|:---------------------------------------|
| `-h`, `--help`      | Shows the help message which is shown in the section [Available arguments](#available-arguments) |
| `-f <inputfile>`,<br>`--file <inputfile>` | Speciy the input file (i.e. csv file) that should be transformed. The header in the csv file is **mandatory** | `-f /myFiles/mycsvfile.csv`<br>`--file mycsvfile.csv` |
| `-o <ofile>`,<br>`--output <ofile>` | Specifies the output file and path. If no path is given, the output file will be saved in the same directory where the script was executed.<br>**Info:** If no output file is specified, the script will automatically generate a new csv file with the ending `.mod` in the same directory as the input file | `-o /myFiles/myoutputfile.csv`<br>`--output myoutputfile.csv` |
| `-c <count>`,<br>`--count <count>` | The number of lines the script should process from the input csv file. Always starts from the first row. Can be used for debugging and testing purposes or if the file should only be transformed partially. | `-c 100`<br>`--count 250` |
| `-cd <column,[...]>`,<br>`--columndelete <column,[...]>` | Specifies the columns that should be deleted by using the column names given in the header of the file. Multiple columns can be seperated by using a comma | `-cd DateTime`<br>`--columndelete id,name,date` |
| `-ct <column:val->newVal,[...]>`,<br>`--columntransform <column:val->newVal,[...]>` | Specifies the columns that should be transformed by using the column names given in the header of the file. Each column can receive multiple tansformations that are separated with a colon. Each transformation expression defines the value that should be matched and the value that should be replace the old value. This is denoted with the following syntax: `oldValueToMatch->newValueToReplaceWith`. Multiple transformation expressions for one column can be separated with a comma. Multiple columns can be separated by using a semicolon. | `-ct id:100->50,99->25;name:foo->co,bar->ol`<br>`--columntransform boolean:0->false,1->true` |
| `-ca <column,[...]>`,<br>`--columnadd <column,[...]>` | Specifies columns and its values that should be added to the transformed csv file. Multiple columns can be separated by using a comma. | `-ca ColumnName:ColumnValue,BooleanVal:true`<br>`--columnadd tag:sensor9` |
| `-v`,<br>`--version` | Shows the program's version number and exits | |

### Special Expressions
Besides transforming values of one or specified columns (i.e. with `--columntransform`) or adding new columns with a given static value (i.e. `--columnadd`), special expressions allow for transforming and inserting dynamic values.
Currently the only special expressions available are the following listed in the table below:

| Special Expression  | Description                                              | Examples                                |
| --------------------|:---------------------------------------------------------|:--------------------------------------- |
| `@timestamp{FORMAT}` | The `timestamp` expression allows for transforming or creating timestamps like dates or datetimes. The `FORMAT` placeholder should be either replaced by using the keyword `unix:` and followed by a precision keyword like `millis, micros` or `nanos`. (`millis`=Milliseconds, `micros`=Microseconds, `nanos`=Nanoseconds) or with a valid timestamp format like `%Y-%m-%d %H:%M:%S.%f`. Check out the [documentation](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) of the python `datetime` module where all directives are described. If using the timestamp expression with the `--columntransform` argument, the part on the left of the `->` sign defines that the given column in the original file has a timestamp with the given `FORMAT`. The right part of the `->` sign defines the desired timestamp and `FORMAT` | `-ca dateColumn:@timestamp{unix:millis}`<br>`-ct dateColumn:@timestamp{%Y-%m-%d}->@timestamp{%Y-%m-%d %H:%M:%S.%f}` |
