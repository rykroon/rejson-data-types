
from .path import Path
from .notpulled import NotPulled


class ReJsonModel():
    connection = None

    def __new__(cls, key, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__dict__ = ReJsonObj(key)
        return instance

    def __getattr__(self, attr):
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

    def __delattr__(self, attr):
        del self.__dict__[attr]


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
            length = self.__class__.connection.jsonarrlen(self.key, self.path)
            super().__init__([NotPulled] * length)

        #The array does not exist so create one
        elif json_type is None:
            if not isinstance(default, list):
                raise TypeError("default value is not an instance of 'list'")
            
            super().__init__(default)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError("Remote object is not of type 'array'")

    # def __iter__(self):
    #     self._pull(-1)
    #     return super().__iter__()
        
    def __getitem__(self, index):
        #add logic for slice
        value = super().__getitem__(index)
        if value is NotPulled:
            value = self.__class__.connection.jsonget(self.key, self.path[index])
            super().__setitem__(index, value)
        return value

    def __setitem__(self, index, value):
        #add logic for slice
        self.__class__.connection.jsonset(self.key, self.path[index], value)
        super().__setitem__(index, value)
        
    def __delitem__(self, index):
        # add logic for slice
        self.__class__.connection.jsondel(self.key, self.path[index])
        super().__delitem__(index)

    def append(self, obj):
        self.__class__.connection.jsonarrappend(self.key, self.path, obj)
        super().append(obj)

    def clear(self):
        self.__class__.connection.jsonset(self.key, self.path, [])
        super().clear()

    def count(self, value):
        raise NotImplementedError
        
    def extend(self, iterable):
        self.__class__.connection.jsonarrappend(self.key, self.path, *iterable)
        super().extend(iterable)

    def index(self, value, start=0, stop=9223372036854775807):
        index = self.__class__.connection.jsonarrindex(self.key, self.path, value, start, stop)
        if index < 0:
            raise ValueError("{} is not in list".format(value))
        return index

    def insert(self, index, obj):
        #round index
        if index < 0:
            index += len(self)
        index = max(index, 0)
        index = min(index, len(self))

        self.__class__.connection.jsonarrinsert(self.key, self.path, index, obj)
        super().insert(index, obj)

    def pop(self, index=-1):
        result = self.__class__.connection.jsonarrpop(self.key, self.path, index)
        super().pop(index)
        return result

    def remove(self, value):
        index = self.__class__.connection.jsonarrindex(self.key, self.path, value)
        if index >= 0:
            self.__class__.connection.jsondel(self.key, self.path[index])        
        super().remove(value)

    def reverse(self):
        raise NotImplementedError

    def sort(self):
        raise NotImplementedError


class ReJsonObj(ReJsonMixin, dict):

    def __init__(self, key, path='.', obj={}):
        self.key = key
        self.path = Path(path)
        self.length = None

        json_type = self.__class__.connection.jsontype(self.key, self.path)

        #do not create a new object if one already exists
        if json_type == 'object':
            keys = self.__class__.connection.jsonobjkeys(self.key)
            super().__init__(dict.fromkeys(keys, NotPulled))

        #The object does not exist so create one
        elif json_type is None:
            super().__init__(obj)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if value is NotPulled:
            value = self.__class__.connection.jsonget(self.key, self.path[key])
            super().__setitem__(key, value)
        return value

    def __setitem__(self, key, value):
        #add logic for slice
        self.__class__.connection.jsonset(self.key, self.path[key], value)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.__class__.connection.jsondel(self.key, self.path[key])
        super().__delitem__(key)

    def clear(self):
        self.__class__.connection.jsonset(self.key, self.path, {})
        super().clear()

    # def copy(self):
    #     pass

    def get(self, key, default=None):
        value = super().get(key, default)
        if value is NotPulled:
            value = self.__class__.connection.jsonget(self.key, self.path[key])
            super().__setitem__(key, value)
        return value

    def items(self):
        pass   

    def pop(self, key, *args):
        value = super().pop(key, *args)
        if value is NotPulled:
            value = self.__class__.connection.jsonget(self.key, self.path[key])
        self.__class__.connection.jsondel(self.path, self.path[key])
        return value

    def popitem(self):
        key, value = super().popitem()
        if value is NotPulled:
            value = self.__class__.connection.jsonget(self.key, self.path[key])
        self.__class__.connection.jsondel(self.key, self.path[key])
        return (key, value)

    def setdefault(self, key, default=None):
        """
            Insert key with a value of default if key is not in the dictionary.

            Return the value for key if key is in the dictionary, else default.
        """
        value = super().setdefault(key, default)
        if value is NotPulled:
            value = self.__class__.connection.jsonget(self.key, self.path[key])
            super().__setitem__(key, value)
            return value

        if value == default:
            self.__class__.connection.jsonset(self.key, self.path[key], default, nx=True)

        return value

    def update(self):
        raise NotImplementedError

    def values(self):
        raise NotImplementedError
