import re

example_patch = \
r"""--- Portfile.orig        2011-07-25 18:52:12.000000000 -0700
+++ Portfile    2011-07-25 18:53:35.000000000 -0700
@@ -2,7 +2,7 @@
 PortSystem          1.0
 name                foo
 
-version             1.3.0
+version             1.4.0
 categories          net
 maintainers         nomaintainer
 description         A network monitoring daemon.
@@ -13,9 +13,9 @@
 
 homepage            http://rsug.itd.umich.edu/software/${name}
 
 master_sites        ${homepage}/files/
-checksums           rmd160 f0953b21cdb5eb327e40d4b215110b71
+checksums           rmd160 01532e67a596bfff6a54aa36face26ae
 extract.suffix      .tgz
 platforms           darwin"""

def parse_patch(text):
    """Parse the content of a patch string and return a list of modified intervals

    >>> parse_patch(example_patch)
    [[2, 8], [13, 21]]
    """
    re_chunk_header = re.compile("""\@\@\s*
                                    \-(?P<old_start_line>\d+),(?P<old_num_lines>\d+)\s*
                                    \+(?P<new_start_line>\d+),(?P<new_num_lines>\d+)\s*
                                    \@\@
                                """, re.VERBOSE)
    modified_intervals = []
    for m in re_chunk_header.finditer(text):
        old_start_line, old_num_lines, _, _ = m.groups()
        modified_intervals.append([int(old_start_line), int(old_start_line) + int(old_num_lines) - 1])
        
    return modified_intervals

if __name__ == "__main__":
    import doctest
    doctest.testmod()