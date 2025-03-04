
import os
import time
import datetime
import re

def run(task, tools):
    archive_dir = "/home/velinxs/Alice-Blogs/blog_archive"
    files = [f for f in os.listdir(archive_dir) if os.path.isfile(os.path.join(archive_dir, f))]
    if not files:
        return "No files found in the archive directory."

    # Parse dates from filenames
    dated_files = []
    for filename in files:
        # Try YYYY-MM-DD format
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if match:
            try:
                date = datetime.datetime.strptime(match.group(1), '%Y-%m-%d').date()
                dated_files.append((filename, date))
                continue
            except ValueError:
                pass

        # Try archive_YYYYMMDD_HHMMSS.txt format
        match = re.match(r'archive_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2}).txt', filename)
        if match:
            try:
                year = int(match.group(1))
                month = int(match.group(2))
                day = int(match.group(3))
                hour = int(match.group(4))
                minute = int(match.group(5))
                second = int(match.group(6))
                dt = datetime.datetime(year, month, day, hour, minute, second)
                dated_files.append((filename, dt))
                continue
            except ValueError:
                pass
        print(f"Skipping file due to invalid filename format: {filename}")


    if not dated_files:
        return "No validly named files found in the archive directory."

    # Find the most recent file
    most_recent_file, most_recent_date = max(dated_files, key=lambda item: item[1])
    filepath = os.path.join(archive_dir, most_recent_file)

    # Read the file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"

    # Summarize (take the first 200 words)
    words = content.split()
    summary = " ".join(words[:200])
    if not summary:
        summary = "File is empty."
    return f"Most recent file: {most_recent_file}\nSummary: {summary}"
