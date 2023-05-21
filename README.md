#Video Lecture Notes Generator

This Python script automates the creation of lecture notes from video lectures and their associated subtitle files. For each video-subtitle pair, it generates a markdown file containing screenshots from the video, along with corresponding text from the subtitle file.

## Notes
* The script expects all video and subtitle files to be located somewhere within a single input directory. They can be nested within subdirectories.
* Video files should be named with a number at the beginning, followed by a space and a dash (e.g., 123 - some title.mp4).
* Subtitle files (.srt) should follow the same naming convention (e.g., 123 - some title.srt).
* The script matches video files with subtitle files based on the number at the beginning of the file name.
* The script expects subtitle files to be in .srt format, with the timecodes in the format 00:00:00,000 --> 00:00:05,000 and the subtitle text on the lines following the timecodes.
* The script creates an output directory containing an 'images' subdirectory for screenshots, a 'notes' subdirectory for markdown files, and an 'index.md' file in the root directory.

## Usage
You may (or may not?) need to install ffmpeg on your system first. The script uses a python module named ffmpeg-python.

Install the required Python packages:
`pip install -r requirements.txt`

Run the script from the command line, specifying the input and output directories:
`python create_notes.py --input /path/to/input --output /path/to/output --groupLinesBy n`

Replace /path/to/input with the path to your input directory, and /path/to/output with the path where you want the output files to be saved. The --groupLinesBy n parameter indicates how many lines from the subtitles file should be grouped together for each screenshot, where n is a positive integer.
