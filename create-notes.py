import os
import glob
import re
from tqdm import tqdm
import datetime
import argparse
from PIL import Image
import subprocess
import ffmpeg

summary = []

def get_mid_time(timestamps):
    start_time, end_time = [datetime.datetime.strptime(t, '%H:%M:%S,%f') for t in timestamps.split(" --> ")]
    mid_time = start_time + (end_time - start_time)/2
    return mid_time.hour*3600 + mid_time.minute*60 + mid_time.second + mid_time.microsecond/1E6

def create_screenshot(video_file, timestamp, output_path):
    # Create a screenshot using ffmpeg. Adjust parameters as necessary for your video files.
    subprocess.run(["ffmpeg", "-y", "-ss", str(timestamp), "-i", video_file, "-vframes", "1", "-s", "640x480", output_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def srt_timestamp_to_seconds(timestamp):
    hours, minutes, seconds_milliseconds = timestamp.split(':')
    seconds, milliseconds = seconds_milliseconds.split(',')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
    return total_seconds


def process_file(video_file, srt_file, output_dir, group_lines_by):
    title = video_file.split("/")[-1].replace('.mp4', '')
    notes_dir = os.path.join(output_dir, "notes")
    md_name = title + '.md'
    md_path = os.path.join(notes_dir, md_name)
    
    # Check if markdown file already exists
    if os.path.exists(md_path):
        return (2,f"File '{md_path}' already exists. Skipping.")
    try:
        with open(srt_file, 'r') as f:
            subtitles = f.readlines()
    except UnicodeDecodeError:
       return (1,f"Could not read SRT file ({srt_file})")
    
    # Parse into groups
    groups = []
    current_group = []
    for line in subtitles:
        current_group.append(line)
        if line.strip() == '':
            groups.append(current_group)
            current_group = []

    # If there was no trailing newline, make sure the last group gets added
    if current_group:
        groups.append(current_group)
    
    i = 0
    md_content = [f"\n\n# {title}\n"]
    md_content.append("<table>\n")

    for i in range(0, len(groups), group_lines_by):
        group = groups[i:i+group_lines_by]

        group_text = ""
        middle_timestamp = None
        for sub_group in group:
            if len(sub_group) >= 3:
                timestamps = sub_group[1].strip().split(' --> ')
                if len(timestamps) == 2:
                    start_time = srt_timestamp_to_seconds(timestamps[0])
                    end_time = srt_timestamp_to_seconds(timestamps[1])
                    middle_timestamp = (start_time + end_time) / 2
                group_text += f"{sub_group[2].strip()} "

        # Create screenshot
        if middle_timestamp is not None:
            img_name = f"{title}-{i//group_lines_by+1}.jpg"
            img_path = os.path.join(output_dir, 'images', img_name)
            create_screenshot(video_file, middle_timestamp, img_path)
            md_content.append(
                f"<tr><td width=\"320\"><a href=\"../images/{img_name}\"><img src=\"../images/{img_name}\" width=\"320\"></a></td><td>{group_text.strip()}</td></tr>\n"
            )



    md_content.append("</table>\n\n")
    md_name = title + '.md'
    with open(md_path, 'w') as f:
        f.writelines(md_content)
    
    return (0,"")



def main():
    summary = []
    skipped = 0
    processed = 0
    errors = 0

    parser = argparse.ArgumentParser(description="Process video and subtitle files to create markdown with screenshots and captions.")
    parser.add_argument('--input', required=True, help='Input directory containing video and subtitle files')
    parser.add_argument('--output', required=True, help='Output directory to save generated markdown files')
    parser.add_argument('--groupLinesBy', type=int, required=True)
    args = parser.parse_args()
    
    input_dir = args.input
    output_dir = args.output
    group_lines_by = args.groupLinesBy

    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'notes'), exist_ok=True)


    video_files = glob.glob(os.path.join(input_dir, '**/*.mp4'), recursive=True)
    srt_files = {f.split('/')[-1].split(' - ')[0]: f for f in glob.glob(os.path.join(input_dir, '**/*.srt'), recursive=True)}
    md_files = []
    for video_file in tqdm(video_files):
        number = video_file.split('/')[-1].split(' - ')[0]
        if number in srt_files:
            code,message = process_file(video_file, srt_files[number], output_dir, group_lines_by)
            if code:
                if code == 1:
                    errors += 1
                    summary.append(message)
                elif code == 2:
                    skipped += 1
                    md_files.append(video_file.split('/')[-1].replace('.mp4', '') + '.md')
            else:
                processed += 1
                md_files.append(video_file.split('/')[-1].replace('.mp4', '') + '.md')

    # Sort markdown files
    sorted_md_files = sorted(md_files, key=lambda x: int(x.split(' - ')[0]))


    # Add "previous" and "next" links to each markdown file
    for i, md_file in enumerate(sorted_md_files):
        prev_file = sorted_md_files[i-1] if i > 0 else None
        next_file = sorted_md_files[i+1] if i < len(sorted_md_files) - 1 else None
        md_path = os.path.join(output_dir, 'notes', md_file)

        with open(md_path, 'r+') as f:
            lines = f.readlines()

            # Check and remove existing pagination
            if "previous" in lines[0].lower() or "next" in lines[0].lower():
                del lines[0]
            if "previous" in lines[-1].lower() or "next" in lines[-1].lower():
                del lines[-1]
            f.seek(0, 0)
            f.write(f'Previous: [{prev_file if prev_file else "None"}](<{prev_file}>)  |  Next: [{next_file if next_file else "None"}](<{next_file}>)\n\n' + lines)
            f.write(f'\n\nPrevious: [{prev_file if prev_file else "None"}](<{prev_file}>)  |  Next: [{next_file if next_file else "None"}](<{next_file}>)')

    
    # Create index.md
    with open(os.path.join(output_dir, 'readme.md'), 'w') as f:
        for md_file in sorted_md_files:
            f.write(f"* [{md_file}](<./notes/{md_file}>)\n")

    
    print("\n")

    if len(summary):
        print("      !! ERRORS !!\n")
        for result in summary:
            print(f"|  {result}")

    print("\n")

    print(f"{processed} videos processed")
    print(f"{skipped} videos already existed")
    print(f"{errors} errors (listed above)")

if __name__ == "__main__":
    main()
