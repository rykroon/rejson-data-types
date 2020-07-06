
from redis.exceptions import ResponseError
from .path import Path
from .notfetched import NotFetched
from .rejsonmixin import ReJsonMixin

"""
    to keep things simple, avoid overwriting methods that...
        - require iteration 
        - require all values to be fetched from redis
"""


class ReJsonArr(ReJsonMixin, list):

    def __init__(self, key, path='.', default=[]):
        self.key = key
        self.path = Path(path)
        json_type = self.__class__.connection.jsontype(self.key, self.path)

        #do not create a new array if one already exists
        if json_type == 'array':
            length = self._jsonarrlen()
            super().__init__([NotFetched] * length)

        #The array does not exist so create one
        elif json_type is None:
            if not isinstance(default, list):
                raise TypeError("default value is not an instance of 'list'")
            
            super().__init__(default)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError("Remote object is not of type 'array'")

    def __contains__(self, value):
        raise NotImplementedError

    def __iter__(self):
        return ReJsonArrayIterator(self)
        
    def __getitem__(self, index):
        #add logic for slice
        value = super().__getitem__(index)
        if value is NotFetched:
            value = self._jsonget(index)
        return value

    def __setitem__(self, index, value):
        #add logic for slice
        try:
            self._jsonset(self.path[index], value)
        except ResponseError:
            raise IndexError('list assignment index out of range')
        super().__setitem__(index, value)
        
    def __delitem__(self, index):
        # add logic for slice
        self._jsondel(index)
        super().__delitem__(index)

    def _jsonget(self, *indices):
        if len(indices) == 1:
            idx = indices[0]
            val = self.__class__.connection.jsonget(self.key, self.path[idx])
            super().__setitem__(idx, val) #cache the value
            return val

        elif len(indices) > 1:
            paths = [self.path[idx] for idx in indices]
            result = self.__class__.connection.jsonget(self.key, *paths)
            for idx, val in result.items():
                super().__setitem__(idx, val)
            return list(result.values())
        
        raise ValueError("must pass at least one index")

    def _jsonset(self, index, value):
        return self.__class__.connection.jsonset(self.key, self.path[index], value)

    def _jsondel(self, index):
        return self.__class__.connection.jsondel(self.key, self.path[index])

    def _jsonarrappend(self, *values):
        return self.__class__.connection.jsonarrappend(self.key, self.path, *values)

    def _jsonarrinsert(self, index, *values):
        return self.__class__.connection.jsonarrinsert(self.key, self.path, index, *values)

    def _jsonarrlen(self):
        return self.__class__.connection.jsonarrlen(self.key, self.path)

    def _jsonarrpop(self, index):
        return self.__class__.connection.jsonarrpop(self.key, self.path[index])

    def append(self, obj):
        self._jsonarrappend(obj)
        super().append(obj)

    def clear(self):
        self.__class__.connection.jsonset(self.key, self.path, [])
        super().clear()

    def count(self, value):
        raise NotImplementedError
        
    def extend(self, iterable):
        self._jsonarrappend(*iterable)
        super().extend(iterable)

    def index(self, value, start=None, stop=None):
        raise NotImplementedError

    def insert(self, index, obj):
        #round index
        if index < 0:
            index += len(self)
        index = max(index, 0)
        index = min(index, len(self))

        self._jsonarrinsert(index, obj)
        super().insert(index, obj)

    def pop(self, index=-1):
        result = self._jsonarrpop(index)
        super().pop(index)
        return result

    def remove(self, value):
        raise NotImplementedError

    def reverse(self):
        raise NotImplementedError

    def sort(self):
        raise NotImplementedError


class ReJsonArrayIterator:
    def __init__(self, array):
        self._array = array
        self._iterator = list.__iter__(self._array)
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        value = next(self._iterator)
        if value is NotFetched:
            value = self._array._jsonget(self._index)
        self._index += 1
        return value
