#!/usr/bin/env python3

import argparse
import shutil
import os
import glob
import subprocess
import tempfile
from lxml import etree

# Create our custom xml parser to handle very deep documents
xml_parser = etree.XMLParser(huge_tree=True)


def copy_dir(src, dst, *, follow_sym=True):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.isdir(src):
        shutil.copyfile(src, dst, follow_symlinks=follow_sym)
        shutil.copystat(src, dst, follow_symlinks=follow_sym)
    return dst


def transform_dir(input_dir, output_dir, extensions=('.c', '.h')):
    """Run srcML recursively under a directory

    First copy directory structure from input_dir to output_dir,
    then for every source file that ends with ext in extentions,
    run srcML and output to corresponding directory under output_dir.
    """
    # copy directory structure
    input_dir = os.path.expanduser(input_dir)
    output_dir = os.path.expanduser(output_dir)
    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    shutil.copytree(input_dir, output_dir, copy_function=copy_dir)

    print("Transforming source code to xml...")
    counter = 0
    for ext in extensions:
        for fname in glob.iglob(input_dir + '/**/*' + ext, recursive=True):
            if counter % 100 == 0:
                print('Processed {}'.format(counter))
            # linux-kernel/arch/alpha/boot/bootp.c -> arch/alpha/boot/bootp.c
            pre = os.path.commonprefix((input_dir, fname))
            rel = os.path.relpath(fname, pre)
            output_path = os.path.join(output_dir, rel) + ".xml"

            cmd = 'srcml {} --position -o {}'.format(fname, output_path)
            subprocess.call(cmd, shell=True)

            counter += 1
    print("Tranformation completed, {} processed.".format(counter))


def src_to_tree(filename, src):
    """
    Assume src is UTF-8 encoded.
    the temp file needs to have the right ext so that srcml can open it
    """
    _, ext = os.path.splitext(filename)
    if ext == '':
        print("ERROR: src_to_tree can't extract file extension.")
        return None

    try:
        f = tempfile.NamedTemporaryFile(mode='wb+', suffix=ext, delete=False)
        f.write(src.encode('utf-8', 'replace'))
        f.close()
    except UnicodeEncodeError as e:
        print("ERROR: src_to_tree encounters UnicodeEncodeError.")
        if not f.closed:
            f.close()
        os.remove(f.name)
        return None

    cmd = ['srcml', f.name, '--position']
    xml_str = subprocess.run(cmd, stdout=subprocess.PIPE).stdout

    try:
        root = etree.fromstring(xml_str)
    except BaseException as ex:
        print("ERROR: src_to_tree unable to parse xml file: {}".format(ex))
        return None

    return root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('SOURCE', help='source dir', type=str)
    parser.add_argument('OUTPUT', help='output dir', type=str)
    args = parser.parse_args()
    transform_dir(args.SOURCE, args.OUTPUT)


if __name__ == '__main__':
    main()
