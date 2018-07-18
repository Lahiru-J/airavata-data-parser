import sys
import csv
from os.path import join

WORKING_DIR = "/datacat/working-dir"    # Working directory

input_file_name = sys.argv[1]           # Input file to the experiment
output_file_name = sys.argv[2]          # Output file name

with open(join(WORKING_DIR, input_file_name), 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line.split(",") for line in stripped if line)
    with open(join(WORKING_DIR, output_file_name), 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerows(lines)
