import re
from persper.analytics.c import CGraphServer

class CPPGraphServer(CGraphServer):

    # CPPGraphServer only analyzes files with the following suffixes
    # http://gcc.gnu.org/onlinedocs/gcc-4.4.1/gcc/Overall-Options.html#index-file-name-suffix-71
    _suffix_regex = re.compile(r'.+\.(c|cc|cxx|cpp|CPP|c\+\+|C|h|hh|hpp|Hpp|h\+\+|H)$')
