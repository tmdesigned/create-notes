# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.6.0] - 2023-05-27

### Added

- A progress bar indicating the percentage completion based on the number of video files.

## [0.5.0] - 2023-05-25

### Added

- Script now accepts command line arguments for the input directory, output directory, and number of subtitle lines to group by per screenshot.
- Resiliency features: The script checks if the output file already exists and skips processing if true, allowing the process to be resumed if interrupted.

## [0.4.0] - 2023-05-24

### Added

- Conversion of markdown images to HTML images for better compatibility.
- Images in markdown are clickable and open in full resolution.

## [0.3.0] - 2023-05-23

### Added

- Markdown output changed to table format with screenshots on the left and corresponding text on the right.

## [0.2.0] - 2023-05-22

### Added

- An index.md file is created in the output directory containing links to all the generated markdown files.
- Grouping of images and corresponding text by 4 in the markdown file.

## [0.1.0] - 2023-05-21

### Added

- Basic functionality to match video files with subtitle files based on filenames and create corresponding markdown files with screenshots from the videos and text from the subtitle files.
