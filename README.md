# csv-transform
A CSV parser that is able to do different transformations or modifications on a given csv file.

Development of this software is maintained by:

| GithubID      | URL                             |
| ------------- |:-------------------------------:|
| @amarbajric   | (https://github.com/amarbajric) |


## Installation

The script is making use of multiple modules coming from the [Python Standard Library](https://docs.python.org/2/library/).
In this case, the only thing to worry about is a working python installation ;)

### Requirements
 - `Python v2.7+` (preferrably Python v2.7+ should be used as this script was not tested with Python3 yet!)
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
  -c count, --count count
                        number of lines the program should process. Always
                        starts from row zero to the specified count
  -cd column(s), --columndelete column(s)
                        Columns that should be deleted. Use the column names
                        of the header and separate multiple entries with a
                        comma (e.g. '-d ID,UnitID')
  -ct column(s), --columntransform column(s)
                        Converts a columns value into a specific value. Use
                        the column name of the header (e.g. '-ct
                        IsEventData:0->f,1->t;ValueStatus:0->f,1->t') Special
                        expressions are supported. Check out the documentation
                        for more information!
  -ca column(s), --columnadd column(s)
                        Adds new columns with a given value to the file (e.g.
                        '-ca ColumnName:ColumnValue,AnotherColumnName:AnotherC
                        olumnValue') Special expressions are supported. Check
                        out the documentation for more information!
  -v, --version         show program's version number and exit
```

### Arugments Overview
The following table describes every argument in more detail and its usage

| Argument            | Description                                              | Examples                                | Optional | Support for [Special Expressions](#Special-Expressions) |
| --------------------|:---------------------------------------------------------|:--------------------------------------- |:--------:|:-------------------------------:
| `-h`, `--help`      | Shows the help message which is shown in the section [Available arguments](#Available-arguments) | | NO | NO |
| `-f <inputfile>`,<br>`--file <inputfile>` | Speciy the input file (i.e. csv file) that should be transformed. The header in the csv file is **mandatory** | `-f /myFiles/mycsvfile.csv`<br>`--file mycsvfile.csv` | YES | NO |
| `-o <ofile>`,<br>`--output <ofile>` | Specifies the output file and path. If no path is given, the output file will be saved in the same directory where the script was executed.<br>**Info:** If no output file is specified, the script will automatically generate a new csv file with the ending `.mod` in the same directory as the input file | `-o /myFiles/myoutputfile.csv`<br>`--output myoutputfile.csv` | NO | NO |
| `-c <count>`,<br>`--count <count>` | The number of lines the script should process from the input csv file. Always starts from the first row. Can be used for debugging and testing purposes or if the file should only be transformed partially. | `-c 100`<br>`--count 250` | NO | NO |
| `-cd <column,[...]>`,<br>`--columndelete <column,[...]>` | Specifies the columns that should be deleted by using the column names given in the header of the file. Multiple columns can be seperated by using a comma | `-cd DateTime`<br>`--columndelete id,name,date` | NO | NO |
| `-ct <column:val->newVal,[...]>`,<br>`--columntransform <column:val->newVal,[...]>` | Specifies the columns that should be transformed by using the column names given in the header of the file. Each column can receive multiple tansformations that are separated with a colon. Each transformation expression defines the value that should be matched and the value that should be replace the old value. This is denoted with the following syntax: `oldValueToMatch->newValueToReplaceWith`. Multiple transformation expressions for one column can be separated with a comma. Multiple columns can be separated by using a semicolon. | `-ct id:100->50,99->25;name:foo->co,bar->ol`<br>`--columntransform boolean:0->false;1->true` | NO | YES |
| `-ca <column,[...]>`,<br>`--columnadd <column,[...]>` | Specifies columns and its values that should be added to the transformed csv file. Multiple columns can be separated by using a comma. | `-ca ColumnName:ColumnValue,BooleanVal:true`<br>`--columnadd tag:sensor9` | NO | YES | 
| `-v`,<br>`--version` | Shows the program's version number and exits | | NO | NO |

### Special Expressions
Besides transforming values of one or specified columns (i.e. with `--columntransform`) or adding new columns with a given static value (i.e. `--columnadd`), special expressions allow for transforming and inserting dynamic values.
Currently the only special expressions available are the following listed in the table below:

| Special Expression  | Description                                              | Examples                                |
| --------------------|:---------------------------------------------------------|:--------------------------------------- |
| `@timestamp{FORMAT}` | The `timestamp` expression allows for transforming or creating timestamps like dates or datetimes. The `FORMAT` placeholder should be replaced with a valid timestamp format like `%Y-%m-%d %H:%M:%S.f` or other combinations. Check out the [documentation](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) of the python `datetime` module where all directives are described. If using the timestamp expression with the `--columntransform` argument, the part on the left of the `->` sign defines that the given column in the original file has a timestamp with the given `FORMAT`. The right part of the `->` sign defines the desired timestamp and `FORMAT` | `-ca dateColumn:@timestamp{%Y-%m-%d}`<br>`-ct dateColumn:@timestamp{%Y-%m-%d}->@timestamp{%Y-%m-%d %H:%M:%S.f}` |
| `@unix{FORMAT}` | The `unix` expression allows for transforming or creating timestamps to the the unix representation. The `FORMAT` placeholder should be replaced with one of the following options: `millis, micros, nanos`. (`millis`=Milliseconds, `micros`=Microseconds, `nanos`=Nanoseconds) | `-ca unixColumn:@unix{millis}`<br>`-ct unixColumn:@unix{millis}->@unix{nanos}` |

#### Further Usage
When using special expressions with the `--columntransform` argument, it is also possible to transform a date, datetime or other formats of timestamps to a unix timestamp and vice versa.
When doing so, the source format has to be correct and also a desired output format has to be declared.<br>
**Example1:** `-ct dateTime:@timestamp{%Y-%m-%d %H:%M:%S.f}->@unix{millis}`<br>
**Example2:** `-ct dateTime:@unix{millis}->@timestamp{%Y-%m-%d %H:%M:%S.f}`<br>
In Example1, a transformation is done on the timestamps in the dateTime column. In this case, the original timestamps have to be in the given format and the output format will be in milliseconds.
In Example2, the column dateTime holds unix timestamps in milliseconds that should be transformed to a datetime timestamp with the given format.
