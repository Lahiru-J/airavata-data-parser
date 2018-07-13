import sys
import csv
from os.path import join

input_file_name = sys.argv[1]   # Input file to the experiment
working_dir = sys.argv[2]       # Working directory
output_file_name = sys.argv[3]  # Output file name

with open(join(working_dir, input_file_name), 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line.split(",") for line in stripped if line)
    with open(join(working_dir, output_file_name), 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerows(lines)
