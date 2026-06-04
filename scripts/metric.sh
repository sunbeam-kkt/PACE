#!/bin/bash

ROOT_DIR='.'
ANALYSIS_LIST="eval"
PATH_TYPE_LIST="full easy hard"

CUDA_VISIBLE_DEVICES=0 python3 ./utils/metric.py \
    --root_dir $ROOT_DIR \
    --analysis_list $ANALYSIS_LIST \
    --path_type_list $PATH_TYPE_LIST
