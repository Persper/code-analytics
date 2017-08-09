#!/usr/bin/env python2

import argparse
import collections
import distutils.dir_util as dir_util
import nltk
import os.path as path
import pickle
import re

import sys
sys.path.append('../../lib')
import labeler

# Special tokens
PARAGRAPH_START = '<p>'
PARAGRAPH_END = '</p>'
SENTENCE_START = '<s>'
SENTENCE_END = '</s>'
UNKNOWN_TOKEN = '<UNK>'
PAD_TOKEN = '<PAD>'
DOCUMENT_START = '<d>'
DOCUMENT_END = '</d>'

def to_skip(token):
    return token in '={}<>()[]--' or '=' in token

def adjust(token):
    if token.isdigit():
        return '#'
    return token.lower()

def get_tokens(string, counter):
    string = string.encode('ASCII', errors='ignore').encode('UTF-8')
    tokens = [adjust(t) for t in nltk.word_tokenize(string) if not to_skip(t)]
    if not counter is None:
        counter.update(tokens)
    return tokens

def parse_patch(patch):
    label = FS_LABELER[patch['type']]
    lines = patch['message'].splitlines()
    assert patch['subject'] == lines[0].strip()
    return label, lines

def make_sentence(content, counter):
    s = SENTENCE_START + ' '
    s += ' '.join(get_tokens(content, counter)) + ' '
    return s + SENTENCE_END + ' '

def to_keep(line):
    return not re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
                         line)

def generate_line(abstract, sentences, counter=None):
    line = 'article='
    line += ' '.join([DOCUMENT_START, PARAGRAPH_START]) + ' '

    line += make_sentence(sentences[0], counter)
    if len(sentences) > 1: 
        content = [s for s in sentences[1:] if to_keep(s)]
        if len(content) > 0:
            line += make_sentence(' '.join(content), counter)
    line += ' '.join([PARAGRAPH_END, DOCUMENT_END])

    line += '\tabstract='
    line += ' '.join([DOCUMENT_START, PARAGRAPH_START, SENTENCE_START]) + ' '
    line += ' '.join(get_tokens(abstract, counter)) + ' '
    line += ' '.join([SENTENCE_END, PARAGRAPH_END, DOCUMENT_END])

    return line

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--data-set', required=True,
                        help='Data set: "fs" (filesystem patches)')
    parser.add_argument('-f', '--pickle-file', required=True,
                        help='Pickle file of data')
    parser.add_argument('-o', '--output-dir', required=True,
                        help='Dir for output data')
    args = parser.parse_args()

    dir_util.mkpath(args.output_dir)

    counter = collections.Counter()

    if args.data_set == 'fs':
        datasets = pickle.load(open(args.pickle_file, 'rb'))
        fss = ['ext3', 'ext4', 'btrfs', 'xfs', 'jfs', 'reiserfs']
        for fs in fss:
           with open(path.join(args.output_dir, fs + '.txt'), 'w') as data:
               for dp in datasets[fs]:
                   label, message = parse_patch(dp)
                   line = generate_line(label, message, counter)
                   data.write(line + '\n')

    with open(path.join(args.output_dir, 'vocab'), 'w') as vocab:
        for word, count in counter.most_common(20000 - 4):
            vocab.write(word + ' ' + str(count) + '\n') 
        vocab.write(SENTENCE_START + ' 1\n')
        vocab.write(SENTENCE_END + ' 1\n')
        vocab.write(UNKNOWN_TOKEN + ' 1\n')
        vocab.write(PAD_TOKEN + ' 1\n')

if __name__ == '__main__':
    main()

