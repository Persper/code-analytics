# References
# https://stackoverflow.com/questions/3318625/efficient-bidirectional-hash-table-in-python?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# https://stackoverflow.com/questions/19855156/whats-the-exact-usage-of-reduce-in-pickler?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# https://stackoverflow.com/questions/21144845/how-can-i-unpickle-a-subclass-of-dict-that-validates-with-setitem-in-pytho?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa


class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.items():
            self.inverse.setdefault(value, []).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super(bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value, []).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key], []).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)

    def __getstate__(self):
        return (self.inverse, dict(self))

    def __setstate__(self, state):
        self.inverse, data = state
        self.update(data)

    def __reduce__(self):
        return (bidict, (), self.__getstate__())
