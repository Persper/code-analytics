import os
import re


def translate(pat):
    """
    Translate a shell PATTERN to a regular expression.
    There is no way to quote meta-characters.
    This version can handle **/ pattern properly, compared with fnmatch.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            if i < n and pat[i] == '*':
                res = res + '.*?'
                i = i + 1
                if i < n and pat[i] == os.sep:
                    i = i + 1
            else:
                res = res + r'[^\\/]+'
        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j + 1
            if j < n and pat[j] == ']':
                j = j + 1
            while j < n and pat[j] != ']':
                j = j + 1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return '(?ms)' + res + '$'
