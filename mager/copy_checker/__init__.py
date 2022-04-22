from collections.abc import MutableSequence, MutableSet, MutableMapping, Container

codes = {
    0: 'same ref',
    1: 'shallow',
    2: 'deep',
    3: 'unidentifiable'
}


def is_mutable(obj):
    return isinstance(obj, (MutableSequence, MutableSet, MutableMapping))


def is_container(obj):
    return isinstance(obj, Container)


def get_type(i, j):
    return 1 if i is j else 2


class CopyChecker:
    def __init__(self, iter1, iter2):
        assert iter1 == iter2, 'Two iterables should have the same value'
        self._iter1 = iter1
        self._iter2 = iter2
        self.iter = iter1
        self.stop_at = None
        self.has_mutable = False

    def check_copy(self, recursive=False, is_first=True):
        if is_first and (self._iter1 is self._iter2):
            return 0
        elif isinstance(self._iter1, dict):
            return self._recursive(self._iter1.values(),
                                   self._iter2.values(), recursive)
        return self._recursive(self._iter1, self._iter2, recursive)

    def _recursive(self, iter1, iter2, recursive):
        if recursive:
            for i, j in zip(iter1, iter2):
                if is_mutable(i):
                    self.has_mutable = True
                    self.stop_at = i
                    return self._get_type(i, j)
                if is_container(i):
                    self._iter1, self._iter2 = i, j
                    return self.check_copy(True, False)
        return self._get_type(iter1, iter2)

    def _get_type(self, iter1, iter2):
        if self.has_mutable:
            return get_type(iter1, iter2)
        for i, j in zip(iter1, iter2):
            if is_mutable(i):
                self.stop_at = i
                return get_type(i, j)
        return 3
