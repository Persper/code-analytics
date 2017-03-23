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
            without_root = fname.split('/', 1)[1]
            output_path = os.path.join(output_dir, without_root) + ".xml"
            subprocess.call(
                'srcml {} --position -o {}'.format(fname, output_path), shell=True)
            
            counter += 1
    print("Tranformation completed, {} processed.".format(counter))

def transform_src_to_tree(source_code):
    root = None
    try:
        f = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        f.write(source_code)
        f.close()
    except UnicodeEncodeError:
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

