"""Taller evaluable"""
"""Taller evaluable"""

# pylint: disable=broad-exception-raised

import fileinput
import glob
import os
import os.path
import re
import shutil
import time
from itertools import groupby


def copy_raw_files_to_input_folder(n):
    """Generate n copies of the raw files in the input folder.

    For each iteration this copies all files from `files/raw/` into
    `files/input/` so running with `n=1000` creates 1000 copies of each
    raw file (i.e. 4000 files if there are 4 raw files).
    """
    src_pattern = os.path.join("files", "raw", "*.txt")
    raw_files = sorted(glob.glob(src_pattern))
    dest_dir = os.path.join("files", "input")

    # recreate input directory
    if os.path.exists(dest_dir):
        for f in glob.glob(os.path.join(dest_dir, "*")):
            try:
                os.remove(f)
            except Exception:
                shutil.rmtree(f, ignore_errors=True)
    else:
        os.makedirs(dest_dir, exist_ok=True)

    for i in range(n):
        for src in raw_files:
            basename = os.path.basename(src)
            dest = os.path.join(dest_dir, f"{i:06d}_{basename}")
            shutil.copyfile(src, dest)


def load_input(input_directory):
    """Yield lines from all files in `input_directory`."""
    files = sorted(glob.glob(os.path.join(input_directory, "*")))
    for line in fileinput.input(files=files, openhook=fileinput.hook_encoded("utf-8")):
        yield line


def preprocess_line(x):
    """Lowercase the line and remove non-alphanumeric characters."""
    if x is None:
        return ""
    # Normalize to lowercase and remove punctuation
    text = x.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text


def map_line(x):
    """Map a line into (word, 1) pairs."""
    line = preprocess_line(x)
    words = [w for w in line.split() if w]
    for w in words:
        yield (w, 1)


def mapper(sequence):
    """Mapper: flatten sequence of lines into (key, 1) tuples."""
    for line in sequence:
        for pair in map_line(line):
            yield pair


def shuffle_and_sort(sequence):
    """Group values by key (shuffle and sort).

    Accepts an iterable of (key, value) and yields (key, list(values)).
    """
    # materialize and sort by key to make groupby work
    items = sorted(sequence, key=lambda kv: kv[0])
    for key, group in groupby(items, key=lambda kv: kv[0]):
        values = [v for (_, v) in group]
        yield (key, values)


def compute_sum_by_group(group):
    """Given (key, values) return (key, sum(values))."""
    key, values = group
    return (key, sum(values))


def reducer(sequence):
    """Reducer: compute sum for each group and yield (key, total)."""
    for group in sequence:
        yield compute_sum_by_group(group)


def create_directory(directory):
    """Create or recreate output directory (empty)."""
    if os.path.exists(directory):
        for f in glob.glob(os.path.join(directory, "*")):
            try:
                os.remove(f)
            except Exception:
                shutil.rmtree(f, ignore_errors=True)
    else:
        os.makedirs(directory, exist_ok=True)


def save_output(output_directory, sequence):
    """Save reduced (key, total) pairs to `part-00000` in the output directory."""
    out_path = os.path.join(output_directory, "part-00000")
    # ensure a concrete list so it can be sorted deterministically
    items = list(sequence)
    items.sort(key=lambda kv: kv[0])
    with open(out_path, "w", encoding="utf-8") as f:
        for key, value in items:
            f.write(f"{key}\t{value}\n")


def create_marker(output_directory):
    """Create a _SUCCESS marker file in the output directory."""
    marker = os.path.join(output_directory, "_SUCCESS")
    open(marker, "w", encoding="utf-8").close()


def run_job(input_directory, output_directory):
    """Job"""
    sequence = load_input(input_directory)
    sequence = mapper(sequence)
    sequence = shuffle_and_sort(sequence)
    sequence = reducer(sequence)
    create_directory(output_directory)
    save_output(output_directory, sequence)
    create_marker(output_directory)


if __name__ == "__main__":

    copy_raw_files_to_input_folder(n=1000)

    start_time = time.time()

    run_job(
        "files/input",
        "files/output",
    )

    end_time = time.time()
    print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
