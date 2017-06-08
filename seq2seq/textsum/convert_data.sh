#!/bin/bash

PICKLE=../../notebooks/data/fs-patch.pickle
CONV=~/tensorflow-py2/models/textsum/data_convert_example.py
OUTPUT=data/

echo "Converting data..."
./convert_data.py -s fs -f $PICKLE -o $OUTPUT

for f in $OUTPUT/*.txt
do
  echo "Processing $f"
  base=`basename $f .txt`
  python $CONV --command text_to_binary --in_file $f --out_file $OUTPUT/$base'.data'
  python $CONV --command binary_to_text --in_file $OUTPUT/$base'.data' --out_file $OUTPUT/text_data
  diff $f $OUTPUT/text_data
done

rm -f $OUTPUT/text_data
