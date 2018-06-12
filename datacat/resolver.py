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
    print("Gaussian")
elif experiment_type == EXP_GAMESS:
    print("Gamess")
elif experiment_type == EXP_MOLPRO:
    print("Molpro")
elif experiment_type == EXP_NEWCHEM:
    print("New Chem")