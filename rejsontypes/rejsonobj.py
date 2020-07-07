from redis.exceptions import ResponseError
from .path import Path
from .notfetched import NotFetched
from .rejsonmixin import ReJsonMixin

# used to differentiate between a default value and 'None'
DEFAULT = object()


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
        super().__setitem__(key, value)
        self._jsonset(key, value)
        
    def __delitem__(self, key):
        super().__delitem__(key)
        self._jsondel(key)

    def _jsonget(self, key):
        value = self.__class__.connection.jsonget(self.key, self.path[key])
        super().__setitem__(key, value)
        return value

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

    def pop(self, key, default=DEFAULT):
        if default is DEFAULT:
            value = super().pop(key)
        else:
            value = super().pop(key, default)

        if value is NotFetched:
            value = self._jsonget(key)
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

    def update(self, iterable={}, **kwargs):
        super().update(iterable, **kwargs)
        p = self.__class__.connection.pipeline()
        if iterable:
            if hasattr(iterable, 'keys'):
                for k in iterable:
                    p.jsonset(self.key, self.path[k], iterable[k])
                    
            else:
                for k, v in iterable:
                    p.jsonset(self.key, self.path[k], v)
        
        for k in kwargs:
            p.jsonset(self.key, self.path[k], kwargs[k])

        p.execute()

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