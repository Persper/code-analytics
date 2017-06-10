#!/bin/bash

TEXTSUM=~/tensorflow-py2/models/bazel-bin/textsum/seq2seq_attention
DIR=data/

if [ $# -ne 1 ]; then
  echo "Usage: $0 DATA_SET_INDEX"
  exit
fi

files=($DIR/*.txt)
n=`wc -l ${files[$1]}`

$TEXTSUM --mode=decode \
  --article_key=article \
  --abstract_key=abstract \
  --data_path=$DIR/$1-eval-* \
  --vocab_path=$DIR/vocab \
  --log_root=log_root \
  --decode_dir=log_root/decode \
  --max_article_sentences=1 \
  --decode_batches_per_ckpt=$1 \
  --max_decode_steps=1 \
  --beam_size=1
