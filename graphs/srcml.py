#!/usr/bin/env python3

import argparse
import shutil
import os
import glob
import subprocess
import tempfile
from lxml import etree

def copy_dir(src, dst, *, follow_sym=True):
    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.isdir(src):
        shutil.copyfile(src, dst, follow_symlinks=follow_sym)
        shutil.copystat(src, dst, follow_symlinks=follow_sym)
    return dst

def transform_dir(input_dir='linux-kernel', output_dir='linux-kernel-xml', extensions=('.c', '.h')):    
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

def transform_src_to_tree(source_code):
    root = None
    try:
        f = tempfile.NamedTemporaryFile(mode='wb+', delete=False)
        f.write(source_code.encode('utf-8', 'replace'))
        f.close()
    except UnicodeEncodeError as e:
        print("UnicodeEncodeError in transform_src_to_tree!")
        if not f.closed:
            f.close()
        os.remove(f.name)
        return None

    # rename so that srcml can open it
    new_fname = f.name + ".c"
    os.rename(f.name, new_fname)
    xml_path = f.name + ".xml"
    subprocess.call('srcml {} --position -o {}'.format(new_fname, xml_path), shell=True)
    try:
        root = etree.parse(xml_path).getroot()
    except:
        print("Unable to parse xml file!")
    finally:
        if not f.closed:
            f.close()
        os.remove(new_fname)
        if os.path.exists(xml_path):
            os.remove(xml_path)

    return root

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('SOURCE', help='source dir', type=str)
    parser.add_argument('OUTPUT', help='output dir', type=str)
    args = parser.parse_args()
    transform_dir(args.SOURCE, args.OUTPUT)

if __name__ == '__main__':
    main()
