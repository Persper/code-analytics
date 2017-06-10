#!/bin/bash

TEXTSUM=~/tensorflow-py2/models/bazel-bin/textsum/seq2seq_attention
DIR=data/

if [ $# -eq 1 ]; then
  $TEXTSUM --mode=train \
    --article_key=article \
    --abstract_key=abstract \
    --data_path=$DIR/$1-train-* \
    --vocab_path=$DIR/vocab \
    --log_root=log_root \
    --train_dir=log_root/train \
    --max_article_sentences=1
else
  files=($DIR/*.data)
  n=${#files[@]}
  for i in `seq 0 1 $((n-1))`; do
    if [ $i -gt 0 ]; then
      for j in `seq 0 1 $((i-1))`; do
        ln -fs `basename ${files[j]}` $DIR/$i-train-$j
      done
    fi
    ln -fs `basename ${files[i]}` $DIR/$i-eval-$i
    if [ $i -lt $((n-1)) ]; then
      for j in `seq $((i+1)) 1 $((n-1))`; do
        ln -fs `basename ${files[j]}` $DIR/$i-train-$j
      done
    fi
  done
fi
