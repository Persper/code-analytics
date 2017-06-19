#!/bin/bash

TEXTSUM=~/tensorflow-py2/models/bazel-bin/textsum/seq2seq_attention
INPUT=data/
OUTPUT=log_root/

if [ $# -eq 1 ]; then
  $TEXTSUM --mode=train \
    --article_key=article \
    --abstract_key=abstract \
    --data_path=$INPUT/$1-train-* \
    --vocab_path=$INPUT/vocab \
    --log_root=$OUTPUT \
    --train_dir=$OUTPUT/train \
    --max_article_sentences=2 \
    --truncate_input
else
  files=($INPUT/*.data)
  n=${#files[@]}
  for i in `seq 0 1 $((n-1))`; do
    if [ $i -gt 0 ]; then
      for j in `seq 0 1 $((i-1))`; do
        ln -fs `basename ${files[j]}` $INPUT/$i-train-$j
      done
    fi
    ln -fs `basename ${files[i]}` $INPUT/$i-eval-$i
    if [ $i -lt $((n-1)) ]; then
      for j in `seq $((i+1)) 1 $((n-1))`; do
        ln -fs `basename ${files[j]}` $INPUT/$i-train-$j
      done
    fi
  done
fi
