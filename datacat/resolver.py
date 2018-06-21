import sys
from datacat.newchem import newchem
from datacat.molpro import molpro
from datacat.gamess import gamess
from datacat.gaussian import gaussian

# Define constants for the experiments
EXP_GAUSSIAN = "gaussian"
EXP_GAMESS = "gamess"
EXP_MOLPRO = "molpro"
EXP_NEWCHEM = "newchem"

experiment_type = sys.argv[1]       # Extracting the experiment type (Gaussian, Gamess, Molpro, Newchem, etc.)
file_name = sys.argv[2]             # Input file to the experiment
local_directory = sys.argv[3]       # Local path of the working directory
output_file_name = sys.argv[4]      # Output file name which is going to be generated from the experiment

if experiment_type == EXP_GAUSSIAN:
    gaussian.parse(file_name, local_directory, output_file_name)
elif experiment_type == EXP_GAMESS:
    gamess.parse(file_name, output_file_name)
elif experiment_type == EXP_MOLPRO:
    molpro.parse(file_name, output_file_name)
elif experiment_type == EXP_NEWCHEM:
    newchem.parse(file_name, output_file_name)