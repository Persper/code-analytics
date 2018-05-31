import re


class PatchParser():

    def __init__(self):
        self.re_chunk_header = re.compile("""\@\@\s*
                                            \-(?P<old_start_line>\d+)(,(?P<old_num_lines>\d+))?\s*
                                            \+(?P<new_start_line>\d+)(,(?P<new_num_lines>\d+))?\s*
                                            \@\@
                                        """, re.VERBOSE)

    def clean(self):
        self.additions = []
        self.deletions = []
        self.in_add, self.in_del = False, False
        self.in_chunk = False

        self.add_start, self.del_start = None, None
        self.add_num_lines = None
        self.cur = None

    def start_add(self):
        self.in_add = True
        self.add_start = self.cur - 1
        self.add_num_lines = 1

    def start_del(self):
        self.in_del = True
        self.del_start = self.cur

    def finish_add(self):
        self.in_add = False
        self.additions.append([self.add_start, self.add_num_lines])

    def finish_del(self):
        self.in_del = False
        self.deletions.append([self.del_start, self.cur - 1])

    def parse(self, text):
        self.clean()
        for line in text.split('\n'):
            line = line.strip()
            if not self.in_chunk:
                if line.startswith('@@'):
                    self.in_chunk = True
                else:
                    continue

            if line.startswith('@@'):
                m = self.re_chunk_header.search(line)
                self.cur = max(int(m.groups()[0]), 1)
            elif line.startswith('-'):
                # print("in minus")
                if self.in_add:
                    self.finish_add()
                    self.start_del()
                elif self.in_del:
                    pass
                else:
                    self.start_del()
                self.cur += 1  # always increment in minus
            elif line.startswith('+'):
                # print("in plus")
                if self.in_add:
                    self.add_num_lines += 1
                elif self.in_del:
                    self.finish_del()
                    self.start_add()
                else:
                    self.start_add()
            else:
                # print("in blank")
                if self.in_add:
                    self.finish_add()
                elif self.in_del:
                    self.finish_del()
                else:
                    pass
                self.cur += 1  # always increment in blank

        if self.in_add:
            self.finish_add()
        elif self.in_del:
            self.finish_del()

        return self.additions, self.deletions
