import calendar
import json
import sys
from collections import OrderedDict
from datetime import datetime
from os import listdir
from os.path import isfile, join
from subprocess import Popen, PIPE, STDOUT

import pybel
from cclib.parser import ccopen

from datacat.ccdbt.MetaFile import metafile
from datacat.ccdbt.ParserLoader import ParserPyramid

WORKING_DIR = "../working-dir"


def parse(file_name, local_directory, output_file_name):
    result = OrderedDict()
    identifiers = OrderedDict()
    calculation = OrderedDict()
    molecule = OrderedDict()
    calculated_properties = OrderedDict()
    execution_environment = OrderedDict()
    molecule_structural_formats = OrderedDict()
    files_dict = OrderedDict()

    # extracting fields from open-babel
    mol = pybel.readfile('g98', file_name).next()
    identifiers['InChI'] = mol.write('inchi').strip()
    identifiers['InChIKey'] = mol.write('inchikey').strip()
    identifiers['SMILES'] = mol.write('smiles').split('\t')[0]
    identifiers['CanonicalSMILES'] = mol.write('can').split('\t')[0]

    molecule_structural_formats['PDB'] = mol.write('pdb').split('\t')[0]
    molecule_structural_formats['SDF'] = mol.write('sdf').split('\t')[0]

    # extracting fields from ccdbt
    parser_pyramid = ParserPyramid()
    meta_f = metafile(file_name)
    if meta_f.parse(parser_pyramid):
        if 'CodeVersion' in meta_f.record:
            calculation['Package'] = meta_f.record['CodeVersion']
        if 'CalcType' in meta_f.record:
            calculation['CalcType'] = meta_f.record['CalcType']
        if 'Methods' in meta_f.record:
            calculation['Methods'] = meta_f.record['Methods']
        if 'Basis' in meta_f.record:
            calculation['Basis'] = __extract(meta_f.record['Basis'])
        if 'Keywords' in meta_f.record:
            calculation['Keywords'] = meta_f.record['Keywords']
        if 'JobStatus' in meta_f.record:
            calculation['JobStatus'] = __extract(meta_f.record['JobStatus'])

        if 'Formula' in meta_f.record:
            molecule['Formula'] = meta_f.record['Formula']
        if 'OrbSym' in meta_f.record:
            molecule['OrbSym'] = meta_f.record['OrbSym']
        if 'Multiplicity' in meta_f.record:
            molecule['Multiplicity'] = meta_f.record['Multiplicity']
        if 'Charge' in meta_f.record:
            molecule['Charge'] = meta_f.record['Charge']
        if 'ElecSym' in meta_f.record:
            molecule['ElecSym'] = meta_f.record['ElecSym']

        if 'Energy' in meta_f.record:
            calculated_properties['Energy'] = meta_f.record['Energy']
        if 'Dipole' in meta_f.record:
            calculated_properties['Dipole'] = meta_f.record['Dipole']
        if 'HF' in meta_f.record:
            calculated_properties['HF'] = meta_f.record['HF']

        # Calling the jar to get distribution values
        process = Popen(['java', '-jar', './gaussian-helper.jar', '--arg=' + file_name], stdout=PIPE, stderr=STDOUT)
        for line in process.stdout:
            value = line.split(':')
            if value[0] == 'Iterations':
                calculated_properties['Iterations'] = value[1]
            elif value[0] == 'MaximumGradientDistribution':
                calculated_properties['MaximumGradientDistribution'] = value[1]
            elif value[0] == 'RMSGradientDistribution':
                calculated_properties['RMSGradientDistribution'] = value[1]
            elif value[0] == 'EnergyDistribution':
                calculated_properties['EnergyDistribution'] = value[1]

        if 'CalcMachine' in meta_f.record:
            tmp = str(meta_f.record['CalcMachine'])
            if ';' in tmp:
                line = tmp.split(';')[0]
                bits = line.split('-')
                if len(bits) == 4:
                    execution_environment['CalcMachine'] = bits[1]
                else:
                    execution_environment['CalcMachine'] = line

            else:
                bits = tmp.split('-')
                if len(bits) == 4:
                    execution_environment['CalcMachine'] = bits[1]
                else:
                    execution_environment['CalcMachine'] = tmp

        if 'FinTime' in meta_f.record:
            execution_environment['FinTime'] = __extract(meta_f.record['FinTime'])
            fin_date = datetime.strptime(execution_environment['FinTime'], '%d %b %y')
            execution_environment['FinTimeStamp'] = datetime.utcfromtimestamp(calendar.timegm(fin_date.timetuple()))

        if 'CalcBy' in meta_f.record:
            execution_environment['CalcBy'] = __extract(meta_f.record['CalcBy'])

        for f in listdir(WORKING_DIR):
            if isfile(join(WORKING_DIR, f)):  # Check this in docker container
                if f.endswith('.out') or f.endswith('.log'):
                    files_dict['GaussianOutputFile'] = join(local_directory, f)  # If exists include the absolute path
                elif f.endswith('.com') or f.endswith('.in'):
                    files_dict['GaussianInputFile'] = join(local_directory, f)
                elif f.endswith('.chk'):
                    files_dict['GaussianCheckpointFile'] = join(local_directory, f)
                elif f.endswith('.fchk'):
                    files_dict['GaussianFCheckpointFile'] = join(local_directory, f)

        with open(join(WORKING_DIR, 'structure.sdf'), 'w') as output:
            output.write(str(molecule_structural_formats['SDF']))
        files_dict['SDFStructureFile'] = join(local_directory, 'structure.sdf')  # Local directory path as the key

        with open(join(WORKING_DIR, 'structure.pdb'), 'w') as output:
            output.write(str(molecule_structural_formats['PDB']))
        files_dict['PDBStructureFile'] = join(local_directory, 'structure.pdb')

        with open(join(WORKING_DIR, 'inchi.txt'), 'w') as output:
            output.write(str(identifiers['InChI']))
        files_dict['InChIFile'] = join(local_directory, 'inchi.txt')

        with open(join(WORKING_DIR, 'smiles.txt'), 'w') as output:
            output.write(str(identifiers['SMILES']))
        files_dict['SMILESFile'] = join(local_directory, 'smiles.txt')

        # Open Gaussian output file
        # Extracting some fields which cannot be extracted from existing parsers
        #   * Stoichiometry
        #   * Job cpu time
        #   * %mem
        #   * %nprocshare

        with open(file_name) as f:
            content = f.readlines()

        if content is not None and len(content) > 0:
            for line in content:
                if line.lower().startswith(' stoichiometry'):
                    formula = line.replace('Stoichiometry', '').strip()
                    molecule['Formula'] = formula
                elif ' job cpu time' in line.lower():
                    time = line.split(':')[1].strip()
                    time.replace('days', '')
                    time.replace('hours', '')
                    time.replace('minutes', '')
                    time.replace('seconds', '')
                    time.replace(' +', '')

                    time_arr = time.split(' ')
                    time_in_seconds = 0.0
                    time_in_seconds += float(time_arr[0]) * 86400
                    time_in_seconds += float(time_arr[1]) * 3600
                    time_in_seconds += float(time_arr[2]) * 60
                    time_in_seconds += float(time_arr[3])

                    execution_environment['JobCPURunTime'] = time_in_seconds

                elif line.lower().startswith(' %mem'):
                    memory = line.split('=')[1].strip().lower()
                    # default memory is 256 MB
                    memory_int = 256
                    if memory.endswith('gw'):
                        memory_int = int(memory[:-2]) * 1000 * 8
                    elif memory.endswith('gb'):
                        memory_int = int(memory[:-2]) * 1000
                    elif memory.endswith('mw'):
                        memory_int = int(memory[:-2]) * 8
                    elif memory.endswith('mb'):
                        memory_int = int(memory[:-2])

                    execution_environment['Memory'] = memory_int

                elif line.lower().startswith(' %nproc'):
                    nproc = line.split('=')[1].strip()
                    execution_environment['NProcShared'] = nproc

        # Rest of the key value pairs are not updated by the seagrid-data
        if 'ParsedBy' in meta_f.record:
            result['ParsedBy'] = meta_f.record['ParsedBy']
        if 'NumBasis' in meta_f.record:
            result['NumBasis'] = meta_f.record['NumBasis']
        if 'NumFC' in meta_f.record:
            result['NumFC'] = meta_f.record['NumFC']
        if 'NumVirt' in meta_f.record:
            result['NumVirt'] = meta_f.record['NumVirt']
        if 'InitGeom' in meta_f.record:
            result['InitGeom'] = meta_f.record['InitGeom']
        if 'FinalGeom' in meta_f.record:
            result['FinalGeom'] = meta_f.record['FinalGeom']
        if 'PG' in meta_f.record:
            result['PG'] = meta_f.record['PG']
        if 'NImag' in meta_f.record:
            result['NImag'] = meta_f.record['NImag']
        if 'EnergyKcal' in meta_f.record:
            result['EnergyKcal'] = meta_f.record['EnergyKcal']
        if 'ZPE' in meta_f.record:
            result['ZPE'] = meta_f.record['ZPE']
        if 'ZPEKcal' in meta_f.record:
            result['ZPEKcal'] = meta_f.record['ZPEKcal']
        if 'HFKcal' in meta_f.record:
            result['HFKcal'] = meta_f.record['HFKcal']
        if 'Thermal' in meta_f.record:
            result['Thermal'] = meta_f.record['Thermal']
        if 'ThermalKcal' in meta_f.record:
            result['ThermalKcal'] = meta_f.record['ThermalKcal']
        if 'Enthalpy' in meta_f.record:
            result['Enthalpy'] = meta_f.record['Enthalpy']
        if 'EnthalpyKcal' in meta_f.record:
            result['EnthalpyKcal'] = meta_f.record['EnthalpyKcal']
        if 'Entropy' in meta_f.record:
            result['Entropy'] = meta_f.record['Entropy']
        if 'EntropyKcal' in meta_f.record:
            result['EntropyKcal'] = meta_f.record['EntropyKcal']
        if 'Gibbs' in meta_f.record:
            result['Gibbs'] = meta_f.record['Gibbs']
        if 'GibbsKcal' in meta_f.record:
            result['GibbsKcal'] = meta_f.record['GibbsKcal']
        if 'Freq' in meta_f.record:
            result['Freq'] = meta_f.record['Freq']
        if 'AtomWeigh' in meta_f.record:
            result['AtomWeigh'] = meta_f.record['AtomWeigh']
        if 'Conditions' in meta_f.record:
            result['Conditions'] = meta_f.record['Conditions']
        if 'ReacGeom' in meta_f.record:
            result['ReacGeom'] = meta_f.record['ReacGeom']
        if 'ProdGeom' in meta_f.record:
            result['ProdGeom'] = meta_f.record['ProdGeom']
        if 'MulCharge' in meta_f.record:
            result['MulCharge'] = meta_f.record['MulCharge']
        if 'NatCharge' in meta_f.record:
            result['NatCharge'] = meta_f.record['NatCharge']
        if 'S2' in meta_f.record:
            result['S2'] = meta_f.record['S2']
        if 'MemCost' in meta_f.record:
            result['MemCost'] = meta_f.record['MemCost']
        if 'TimeCost' in meta_f.record:
            result['TimeCost'] = meta_f.record['TimeCost']
        if 'CPUTime' in meta_f.record:
            result['CPUTime'] = meta_f.record['CPUTime']
        if 'Convergence' in meta_f.record:
            result['Convergenece'] = meta_f.record['Convergence']
        if 'FullPath' in meta_f.record:
            result['FullPath'] = meta_f.record['FullPath']
        if 'InputButGeom' in meta_f.record:
            result['InputButGeom'] = meta_f.record['InputButGeom']
        if 'Otherinfo' in meta_f.record:
            result['Otherinfo'] = meta_f.record['Otherinfo']
        if 'Comments' in meta_f.record:
            result['Comments'] = meta_f.record['Comments']

    # extracting fields from cclib
    my_file = ccopen(file_name)
    try:
        data = my_file.parse()
        data.listify()
        if hasattr(data, 'natom'):
            molecule['NAtom'] = data.natom
        if hasattr(data, 'homos'):
            calculated_properties['Homos'] = data.homos
        if hasattr(data, 'scfenergies'):                    # Not updated by the seagrid-data
            result['ScfEnergies'] = data.scfenergies
        if hasattr(data, 'coreelectrons'):                  # Not updated by the seagrid-data
            result['CoreElectrons'] = data.coreelectrons
        if hasattr(data, 'moenergies'):
            calculation['MoEnergies'] = data.moenergies
        if hasattr(data, 'atomcoords'):                     # Not updated by the seagrid-data
            result['AtomCoords'] = data.atomcoords
        if hasattr(data, 'scftargets'):                     # Not updated by the seagrid-data
            result['ScfTargets'] = data.scftargets
        if hasattr(data, 'nmo'):
            calculation['Nmo'] = data.nmo
        if hasattr(data, 'nbasis'):
            calculation['NBasis'] = data.nbasis
        if hasattr(data, 'atomnos'):                        # Not updated by the seagrid-data
            result['AtomNos'] = data.atomnos
    except:
        sys.stderr.write('cclib parsing failed!')

    # Drawing the molecule
    # mol.draw(show=False, filename=molecule_image_file)

    result['Identifiers'] = identifiers
    result['Calculation'] = calculation
    result['Molecule'] = molecule
    result['CalculatedProperties'] = calculated_properties
    result['ExecutionEnvironment'] = execution_environment
    result['FinalMoleculeStructuralFormats'] = molecule_structural_formats
    result['Files'] = files_dict

    result = json.dumps(result, separators=(',', ':'), sort_keys=False, indent=4)
    output_file = open(output_file_name, 'w')
    for row in result:
        output_file.write(row)
    output_file.close()


def __extract(meta_record_value):
    temp = str(meta_record_value)
    if ';' in temp:
        return temp.split(';')[0]
    else:
        return temp
