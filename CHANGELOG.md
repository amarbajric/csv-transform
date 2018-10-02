# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v0.3.0] - 2018-10-02
### Added
- ProgressBar in CLI to show the exact progress of the transformation
- Debug functionality added
  - With the argument `-d` or `--debug` every transformed row will be printed to the cli instead of
  being written into a new file. This allows for fast debugging and checking if the transformation meets
  the desired output. Can be combined with `-l` or `--limit`.
  - The `transform_csv()` function also returns an array of arrays (where each nested array represents one 
  transformed row) when debugging is enabled. Useful for testing and further debugging purposes.
- Initial directory `test` with and initial test file
  - Still empty test suite. Tests will be implemented in the next cycle (hopefully).
### Changed
- `-c` and `--count` changed to `-l` and `--limit` which makes a little bit more sense
- `@timestamp{}` and `@unix{}` have been merged into the expression `@timestamp`. See the "Remove" section or
documentation for usage explanation.
- After a successful transformation, the program prints `Transformed <int> lines!` instead of `Modified <int> lines!`
- Internal code changes
  - Errors are now handled by a separate function
  - Some error statements have been adapted
  - Some adaptations to functions and code blocks
### Removed
- Special expression `@unix{}` was removed. This expression was merged into the `@timestamp{}` expression.
  - Usage: `@timestamp{unix:millis|micros|nanos}`

## [v0.2.3] - 2018-09-05
### Added
### Changed
- Fixed bug where the csv sniffer would leave the file seeker (i.e. current position of pointer in file) at byte 2048 instead of
returning it to the beginning. Hence the csv file was not read correctly
  - Fixed by setting pointer to the beginning of the file after header check with `.seek(0)`
### Removed

## [v0.2.2] - 2018-09-02
### Added
### Changed
- Fixed bug where even valid csv files would be not recognized as such by the csv sniffer due to incorrect variable usage
  - Note: Need testing asap!
### Removed

## [v0.2.1] - 2018-08-31
### Added
- Added csv sniffer which checks for a valid header in the given inputfile
  - Error is raised if no header is found or if the csv file does not seem to be a valid csv file at all
### Changed
### Removed

## [v0.2] - 2018-08-31
### Added
- Added overall support of special expressions
- Added support for `-ca` (columnadd) to allow for special expressions like `@timestamp{%Y-%m-%d %H:%M:%S.f}` or `@unix{millis} to
insert the current date[time] in the given format or as unix timestamp`
- Added support for `-ct` (columntransform) where it now allows for special expressions This can be helpful to transform date[times] to other formats
  - Example: `-ct "DateTimeColumn:@timestamp{%Y-%m-%d %H:%M:%S.f}->@timestamp{%Y-%m-%d}"` or `-ct "DateTimeColumn:@timestamp{%Y-%m-%d %H:%M:%S.f}->@unix{millis}"`
- Added a subsection to the `Documentation` section in the README that explains the usage of special expressions
### Changed
- Changed `Documentation` section of the README
### Removed
- `-tt` (timetransform) is not longer available as the transformation of date[times] is now handled with the `-ct` (columntransformer)
  - Possible transformation of one date[time] to another is listed in the 'Added' section

## [v0.1] - 2018-08-30
### Added
- Added a CHANGELOG.md to communicate (breaking) changes
- Added support for transforming a csv file and its columns
- Added argument parser
- Added further functionality for:
  - deleting columns
  - adding new columns
  - transforming UTC datetime timestamps to unix nanoseconds
  - declaring an output file and path
  - setting a count argument that limits the number of lines being processed
### Changed
### Removed
