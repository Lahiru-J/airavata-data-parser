import sys
import gaussian, gamess, molpro, newchem    # Scientific experiments

# Define constants for the experiments
EXP_GAUSSIAN = "gaussian"
EXP_GAMESS = "gamess"
EXP_MOLPRO = "molpro"
EXP_NEWCHEM = "newchem"

experiment_type = sys.argv[1]       # Extracting the experiment type (Gaussian, Gamess, Molpro, Newchem, etc.)
file_name = sys.argv[2]             # Input file to the experiment
output_file_name = sys.argv[3]      # Output file name which is going to be generated from the experiment

if experiment_type == EXP_GAUSSIAN:
    gaussian.parse(file_name, output_file_name)
elif experiment_type == EXP_GAMESS:
    gamess.parse(file_name, output_file_name)
elif experiment_type == EXP_MOLPRO:
    molpro.parse(file_name, output_file_name)
elif experiment_type == EXP_NEWCHEM:
    newchem.parse(file_name, output_file_name)