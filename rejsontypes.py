

class Path(str):
    def __init__(self, *args, **kwargs):
        super().__init__()

    def __getitem__(self, key):
        path = str(self)
        if path.startswith('.'):
            path = path[1:]
        if isinstance(key, int):
            path = '{}[{}]'.format(path, key)
        elif isinstance(key, str):
            path = '{}.{}'.format(path, key)
        return self.__class__(path)


class NotPulledType:
    def __new__(cls):
        """
            There can only be at most ONE instance of NotPulledType
        """
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return '-'


NotPulled = NotPulledType()


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
        pass

    def ttl(self):
        pass


class ReJsonArr(list):
    connection = None

    def __init__(self, key, path='.', arr=[]):
        self.key = key
        self.path = Path(path)
        json_type = self.__class__.connection.jsontype(self.key, self.path)

        #do not create a new array if one already exists
        if json_type == 'array':
            length = self.__class__.connection.jsonarrlen(self.key, self.path)
            super().__init__([NotPulled] * length)

        #The array does not exist so create one
        elif json_type is None:
            super().__init__(arr)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError

    # def __iter__(self):
    #     self._pull(-1)
    #     return super().__iter__()
            
    # def __len__(self):
    #     if self.length is None:
    #         self.length = self.__class__.connection.jsonarrlen(self.key, self.path)
    #     return self.length
        
    def __getitem__(self, index):
        #add logic for slice
        value = super().__getitem__(index)
        if value is NotPulled:
            path = self.path[index]
            value = self.__class__.connection.jsonget(self.key, path)
            super().__setitem__(index, value)
        return value

    def __setitem__(self, index, value):
        #add logic for slice
        path = self.path[index]
        self.__class__.connection.jsonset(self.key, path, value)
        super().__setitem__(index, value)
        
    def __delitem__(self, index):
        # add logic for slice
        path = self.path[index]
        self.__class__.connection.jsondel(self.key, path)
        super().__delitem__(index)

    def append(self, obj):
        self.__class__.connection.jsonarrappend(self.key, self.path, obj)
        super().append(obj)
        
    def extend(self, iterable):
        self.__class__.connection.jsonarrappend(self.key, self.path, *iterable)
        super().extend(iterable)

    def index(self, value, start=0, stop=9223372036854775807):
        index = self.__class__.connection.jsonarrindex(self.key, self.path, value, start, stop)
        if index >= 0:
            super().__setitem__(index, value)
        else:
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


class ReJsonObj(dict):
    connection = None

    def __init__(self, key, path='.', obj={}):
        self.key = key
        self.path = Path(path)
        self.length = None

        json_type = self.__class__.connection.jsontype(self.key, self.path)

        #do not create a new object if one already exists
        if json_type == 'object':
            super().__init__([])

        #The object does not exist so create one
        elif json_type is None:
            super().__init__(obj)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError

    def __len__(self):
        return self.__class__.connection.jsonobjlen(self.key, self.path)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            pass

        path = self.path[key]
        value = self.__class__.connection.jsonget(self.key, path)
        
        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        super().__setitem__(key, value)
        return value

    def __setitem__(self, key, value):
        path = self.path[key]

        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        self.__class__.connection.jsonset(self.key, path, value)
        super().__setitem__(key, value)

    def __delitem__(self, key):
        path = self.path[key]
        self.__class__.connection.jsondel(self.key, path)
        super().__delitem__(key)

    def keys(self):
        return self.__class__.connection.jsonobjkeys(self.key)

    def values(self):
        pass

    def items(self):
        pass

    def update(self):
        pass
