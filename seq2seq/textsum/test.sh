#!/bin/bash

# Example commands (in the current dir):
# $ for i in `seq 0 5`; do ./test.sh $i; done
# $ ./test.sh

TEXTSUM=~/tensorflow-python2.7/models/bazel-bin/textsum/seq2seq_attention
INPUT=data/
OUTPUT=log_root/

files=($INPUT/*.txt)

if [ $# -eq 1 ]; then
  l=(`wc -l ${files[$1]}`)
  $TEXTSUM --mode=decode \
    --article_key=article \
    --abstract_key=abstract \
    --data_path=$INPUT/$1-eval-* \
    --vocab_path=$INPUT/vocab \
    --log_root=$OUTPUT \
    --decode_dir=$OUTPUT/decode \
    --max_article_sentences=2 \
    --truncate_input \
    --decode_batches_per_ckpt=$l \
    --max_decode_steps=1 \
    --beam_size=4
else
  refs=($OUTPUT/decode/ref*)
  preds=($OUTPUT/decode/decode*)
  n=${#refs[@]}
  if [ $n -ne ${#preds[@]} ]; then
    echo "Ref and decode files do not match!"
    exit 1
  fi
  for i in `seq 0 $((n-1))`; do
    ./stats_output.py -r ${refs[$i]} -p ${preds[$i]}
  done
fi
