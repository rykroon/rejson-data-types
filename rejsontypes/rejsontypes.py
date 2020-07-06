
import logging
from redis.exceptions import ResponseError
from .path import Path
from .notfetched import NotFetched

log = logging.getLogger(__name__)

"""
    to keep things simple, avoid overwriting methods that...
        - require iteration 
        - require all values to be fetched from redis
"""


class ReJsonMixin:
    connection = None

    def expire(self, ttl):
        return self.__class__.connection.expire(self.key, ttl)

    def ttl(self):
        return self.__class__.connection.ttl(self.key)


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


class ReJsonObj(ReJsonMixin, dict):

    def __init__(self, key, path='.', obj={}):
        self.key = key
        self.path = Path(path)
        self.length = None

        json_type = self.__class__.connection.jsontype(self.key, self.path)

        #do not create a new object if one already exists
        if json_type == 'object':
            keys = self._jsonobjkeys()
            super().__init__(dict.fromkeys(keys, NotFetched))

        #The object does not exist so create one
        elif json_type is None:
            super().__init__(obj)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if value is NotFetched:
            value = self._jsonget(key)
        return value

    def __setitem__(self, key, value):
        #add logic for slice
        self._jsonset(key, value)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self._jsondel(key)
        super().__delitem__(key)

    def _jsonget(self, *keys):
        if len(keys) == 1:
            key = keys[0]
            value = self.__class__.connection.jsonget(self.key, self.path[key])
            super().__setitem__(key, value)
            return value

        if len(keys) > 1:
            pass

    def _jsonset(self, key, value, nx=False, xx=False):
        return self.__class__.connection.jsonset(self.key, self.path[key], value, nx=nx, xx=xx)

    def _jsondel(self, key):
        return self.__class__.connection.jsondel(self.key, self.path[key])

    def _jsonobjkeys(self):
        return self.__class__.connection.jsonobjkeys(self.key)

    def clear(self):
        self.__class__.connection.jsonset(self.key, self.path, {})
        super().clear()

    def copy(self):
        raise NotImplementedError

    def get(self, key, default=None):
        value = super().get(key, default)
        if value is NotFetched:
            value = self._jsonget(key)
        return value

    def items(self):
        raise NotImplementedError 

    def pop(self, key, *args):
        value = super().pop(key, *args)
        if value is NotFetched:
            value = self.__class__.connection.jsonget(self.key, self.path[key])
        self._jsondel(key)
        return value

    def popitem(self):
        raise NotImplementedError

    def setdefault(self, key, default=None):
        """
            Insert key with a value of default if key is not in the dictionary.

            Return the value for key if key is in the dictionary, else default.
        """
        value = super().setdefault(key, default)
        if value is NotFetched:
            return self._jsonget(key)

        if value == default:
            self._jsonset(key, default, nx=True)

        return value

    def update(self):
        #add logic later. probably best to use a pipeline
        raise NotImplementedError

    def values(self):
        raise NotImplementedError


class ReJsonObjItemIterator:
    def __init__(self, obj):
        self._obj = obj
        self._key_iterator = iter(self._obj)

    def __iter__(self):
        return self

    def __next__(self):
        key = next(self._key_iterator)
        return (key, self._obj[key])


class ReJsonObjValueIterator:
    def __init__(self, obj):
        self._obj = obj
        self._key_iterator = iter(self._obj)

    def __iter__(self):
        return self

    def __next__(self):
        key = next(self._key_iterator)
        return self._obj[key]


