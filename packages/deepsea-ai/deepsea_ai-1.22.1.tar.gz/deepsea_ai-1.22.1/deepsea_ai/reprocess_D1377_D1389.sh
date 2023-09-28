#!/bin/bash
export AWS_PROFILE=902005-vaa-prod

# iterate through the dive array in bash
missing_dives=("1378" "1386"  "1387"  "1388"  "1389")

for dive in "${missing_dives[@]}"
do
    # the job name is the dive name
    job_name="D$dive"
    # dive is the input directory
    input_dir="/Volumes/M3/mezzanine/DocRicketts/2021/08/$dive/"
    echo "Processing dive: $dive $input_dir $job_name"
    deepsea-ai ecsprocess -u \
            --job "$job_name" \
            --cluster strongsort-yolov5-mbari315k  \
            --config 902005prod.ini \
            --conf-thres 0.2 \
            --iou-thres 0.2 \
      --check \
      --input $input_dir \
      --dry-run

done