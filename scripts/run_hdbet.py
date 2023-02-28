#!/usr/bin/env python

import argparse
import json
import os
import re
from shutil import which
import subprocess


parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                 prog="HD-BET brain extraction", add_help = False, description='''
Wrapper for brain extraction using synthstrip. The input and output data are in BIDS format. Because
there might be multiple T1w images and other anatomical images in a session, the input is a list of
anatomical images to process. The output is written to another BIDS dataset with the sidecar
referring to the source data.

Requires:
  singularity

''')
required = parser.add_argument_group('Required arguments')
required.add_argument("--container", help="Path to the container to run", type=str, required=True)
required.add_argument("--input-dataset", help="Input BIDS dataset dir, containing the source images", type=str, required=True)
required.add_argument("--output-dataset", help="Output BIDS dataset dir", type=str, required=True)
required.add_argument("--anatomical-images", help="List of anatomical images relative to the input data set", type=str, required=True)
optional = parser.add_argument_group('Optional arguments')
optional.add_argument("-h", "--help", action="help", help="show this help message and exit")
args = parser.parse_args()

script_dir = os.path.dirname(os.path.realpath(__file__))

input_dataset_dir = args.input_dataset
output_dataset_dir = args.output_dataset

singularity_env = os.environ.copy()
singularity_env['SINGULARITYENV_OMP_NUM_THREADS'] = "1"

if which('singularity') is None:
    raise RuntimeError('singularity executable not found')

with open(args.anatomical_images, 'r') as file_in:
    anatomical_images = file_in.readlines()

anatomical_images = [ line.rstrip() for line in anatomical_images ]

print(f"Processing {len(anatomical_images)} images")

# Get BIDS dataset name
with open(f"{input_dataset_dir}/dataset_description.json", 'r') as file_in:
    input_dataset_json = json.load(file_in)

input_dataset_name = input_dataset_json['Name']

# Check if output bids dir exists, and if not, create it
if not os.path.isdir(output_dataset_dir):
    os.mkdir(output_dataset_dir)

container = args.container

# Now process input data
for input_anatomical in anatomical_images:

    input_anatomical_full_path = os.path.join(input_dataset_dir, input_anatomical)

    if not os.path.isfile(input_anatomical_full_path):
        print(f"Anatomical input file not found: {input_anatomical}")
        continue

    print(f"Processing {input_anatomical}")

    match = re.match('(.*)_(\w+)\.nii\.gz$', input_anatomical)

    anatomical_prefix = match.group(1)
    anatomical_suffix = match.group(2)

    # Output image path relative to output data set
    # hdbet always outputs both the image and mask. We'll delete the image to save space
    output_image = f"{anatomical_prefix}_space-{anatomical_suffix}_desc-brain.nii.gz"

    output_mask = f"{anatomical_prefix}_space-{anatomical_suffix}_desc-brain_mask.nii.gz"

    # Full path on local file system
    output_mask_full_path = os.path.join(output_dataset_dir, output_mask)

    # Check for existing mask
    if os.path.exists(output_mask_full_path):
        print(f"Mask already exists: {output_mask}")
        continue

    output_mask_dir = os.path.dirname(output_mask_full_path)

    if not os.path.isdir(output_mask_dir):
        os.makedirs(output_mask_dir)

    # Now call synthstrip
    subprocess.run(['singularity', 'run', '--cleanenv', '--nv', '-B',
                    f"{os.path.realpath(input_dataset_dir)}:/input,{os.path.realpath(output_dataset_dir)}:/output",
                    container, '-i', f"/input/{input_anatomical}", "-o", f"/output/{output_image}"], env = singularity_env)

    subprocess.run(['rm', os.path.join(output_dataset_dir, output_image)])

    sidecar_json = {'Sources': [f"bids:{input_dataset_name}:{input_anatomical}"]}
    output_sidecar_full_path = re.sub('\.nii\.gz$', '.json', output_mask_full_path)
    with open(output_sidecar_full_path, 'w') as sidecar_out:
        json.dump(sidecar_json, sidecar_out, indent=2, sort_keys=True)
