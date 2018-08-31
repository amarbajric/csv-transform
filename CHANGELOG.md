# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

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