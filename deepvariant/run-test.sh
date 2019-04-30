#!/bin/bash
INPUT_DIR="${PWD}/quickstart-testdata"
DATA_HTTP_DIR="https://storage.googleapis.com/deepvariant/quickstart-testdata"
OUTPUT_DIR="${PWD}/quickstart-output"
mkdir -p "${OUTPUT_DIR}"
BIN_VERSION="0.8.0"
USE_GPU="--runtime=nvidia"
docker pull gcr.io/deepvariant-docker/deepvariant:"${BIN_VERSION}"
docker run ${USE_GPU}\
  -v "${INPUT_DIR}":"/input" \
  -v "${OUTPUT_DIR}:/output" \
  gcr.io/deepvariant-docker/deepvariant:"${BIN_VERSION}" \
  /opt/deepvariant/bin/run_deepvariant \
  --model_type=WGS \
  --ref=/input/ucsc.hg19.chr20.unittest.fasta \
  --reads=/input/NA12878_S1.chr20.10_10p1mb.bam \
  --regions "chr20:10,000,000-10,010,000" \
  --output_vcf=/output/output.vcf.gz \
  --output_gvcf=/output/output.g.vcf.gz \
  --num_shards=4 

