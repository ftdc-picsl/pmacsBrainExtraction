#!/bin/bash

module load miniconda/3-22.11
module load singularity/3.8.3

scriptPath=$(readlink -f "$0")
scriptDir=$(dirname "${scriptPath}")
# Repo base dir under which we find bin/ and containers/
repoDir=${scriptDir%/bin}

function usage() {
  echo "Usage:
  $0 [-h] [-a (synthstrip|hdbet)] image_list

  This is a wrapper script to submit images for processing. It assumes input from the BIDS dataset

  /project/ftdc_volumetric/fw_bids

  The image_list should be one per line, and relative to the BIDS dataset, eg

  sub-123456/ses-19970829x0214/anat/sub-123456_ses-19970829x0214_T1w.nii.gz

  Output will be under

  /project/ftdc_pipeline/data/synthstripT1w
  /project/ftdc_pipeline/data/hdbetT1w

  The default algorithm is synthstrip

"
}

if [[ $# -eq 0 ]]; then
  usage
  exit 1
fi

algorithm="synthstrip"

while getopts "a:d:i:o:h" opt; do
  case $opt in
    a) algorithm=$OPTARG;;
    h) usage; exit 1;;
    \?) echo "Unknown option $OPTARG"; exit 2;;
    :) echo "Option $OPTARG requires an argument"; exit 2;;
  esac
done

shift $((OPTIND-1))

imageList=$1

inputBIDS="/project/ftdc_volumetric/fw_bids"

date=`date +%Y%m%d`

if [[ $algorithm == "synthstrip" ]]; then
    bsub -cwd . -o "/project/ftdc_pipeline/data/synthstripT1w/logs/synthstrip_${date}_%J.txt" conda run -n base ${repoDir}/scripts/run_synthstrip.py \
      --container ${repoDir}/containers/synthstrip-1.4.sif \
      --input-dataset $inputBIDS \
      --output-dataset /project/ftdc_pipeline/data/synthstripT1w \
      --anatomical-images $imageList
elif [[ $algorithm == "hdbet" ]]; then
    bsub -cwd . -o "/project/ftdc_pipeline/data/hdbetT1w/logs/hdbet_${date}_%J.txt"\
      -gpu "num=1:mode=shared:mps=no:j_exclusive=no" \
      conda run -n base ${repoDir}/scripts/run_hdbet.py \
      --container ${repoDir}/containers/hdbet-latest.sif \
      --input-dataset $inputBIDS \
      --output-dataset /project/ftdc_pipeline/data/hdbetT1w \
      --anatomical-images $imageList
else
    echo "Unrecognized algorithm $algorithm"
    exit 1
fi


