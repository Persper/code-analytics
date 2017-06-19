#!/usr/bin/env python2

import argparse
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-r', '--ref-file', required=True,
                      help='file path storing ground truth')
  parser.add_argument('-p', '--pred-file', required=True,
                      help='file path storing predictions')
  args = parser.parse_args()

  with open(args.ref_file) as ref_file, open(args.pred_file) as pred_file:
    refs = [line.split('=')[1].strip() for line in ref_file.readlines()]
    preds = [line.split('=')[1].strip() for line in pred_file.readlines()]
    assert len(refs) == len(preds)
    print(classification_report(refs, preds, digits=3))
    print('Accuracy: %.3f' % accuracy_score(refs, preds))

if __name__ == '__main__':
  main()
