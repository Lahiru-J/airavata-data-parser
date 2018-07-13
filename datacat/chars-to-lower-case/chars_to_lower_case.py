import sys
from os.path import join

input_file_name = sys.argv[1]       # Input file to the experiment
working_dir = sys.argv[2]           # Working directory
output_file_name = sys.argv[3]      # Output file name

output_file = open(join(working_dir, output_file_name), 'w')

with open(join(working_dir, input_file_name)) as f:
    for line in f:
        output_file.write(line.lower())
output_file.close()
