import sys
from os.path import join

WORKING_DIR = "/datacat/working-dir"    # Working directory

input_file_name = sys.argv[1]           # Input file to the experiment
output_file_name = sys.argv[2]          # Output file name

output_file = open(join(WORKING_DIR, output_file_name), 'w')

with open(join(WORKING_DIR, input_file_name)) as f:
    for line in f:
        output_file.write(line.lower())
output_file.close()
