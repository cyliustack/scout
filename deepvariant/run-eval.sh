#!/bin/bash
INPUT_DIR="${PWD}/quickstart-testdata"
DATA_HTTP_DIR="https://storage.googleapis.com/deepvariant/quickstart-testdata"
OUTPUT_DIR="${PWD}/quickstart-output"
mkdir -p "${OUTPUT_DIR}"
BIN_VERSION="0.8.0"
USE_GPU="--runtime=nvidia"

sudo docker pull pkrusche/hap.py
sudo docker run -it \
  -v "${INPUT_DIR}":"/input" \
  -v "${OUTPUT_DIR}:/output" \
  pkrusche/hap.py /opt/hap.py/bin/hap.py \
  /input/test_nist.b37_chr20_100kbp_at_10mb.vcf.gz \
  /output/output.vcf.gz \
  -f "/input/test_nist.b37_chr20_100kbp_at_10mb.bed" \
  -r "/input/ucsc.hg19.chr20.unittest.fasta" \
  -o "/output/happy.output" \
  --engine=vcfeval \
  -l chr20:10000000-10010000
