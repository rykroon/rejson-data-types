

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


class ReJsonArr(list):
    connection = None

    def __init__(self, key, path='.', arr=[]):
        self.key = key
        self.path = path
        json_type = self.__class__.connection.jsontype(self.key, self.path)

        #do not create a new array if one already exists
        if json_type == 'array':
            super().__init__([])

        #The array does not exist so create one
        elif json_type is None:
            super().__init__(arr)
            self.__class__.connection.jsonset(self.key, self.path, self)

        else:
            raise TypeError
            

    def __len__(self):
        return self.__class__.connection.jsonarrlen(self.key, self.path)
        
    def __getitem__(self, index):
        try:
            return super().__getitem__(index)
        except IndexError:
            print("Get from Redis")
            self._pull(index)
            return super().__getitem__(index)

    def __setitem__(self, index, value):
        path = '{}[{}]'.format(self.path, index)
        if path.startswith('.'):
            path = path[1:]

        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        super().__setitem__(index, value)
        self.__class__.connection.jsonset(self.key, path, value)

    def __delitem__(self, index):
        path = '{}[{}]'.format(self.path, index)
        if path.startswith('.'):
            path = path[1:]

        super().__delitem__(index)
        self.__class__.connection.jsondel(self.key, path)        

    def __repr__(self):
        result = super().__repr__()
        if len(self) > super().__len__():
            if super().__len__() == 0:
                return '[...]'
            result = result[:-1]
            result += ', ...]'
        return result

    def _normalize_index(self, index):
        remote_length = len(self)
        if index < 0:
            index = remote_length + index
        index = max(index, 0)
        index = min(index, remote_length-1)
        return index

    def _pull(self, index):
        """
            Pull elements from redis up to a certain index
        """
        start_index = super().__len__()
        end_index = self._normalize_index(index)
        if start_index >= end_index:
            return
        
        #remove the '.'
        path = self.path
        if path.startswith('.'):
            path = path[1:]

        paths = ['{}[{}]'.format(path, i) for i in range(start_index, end_index + 1)]

        if len(paths) == 1:
            value = self.__class__.connection.jsonget(self.key, paths[0])
            super().append(value)
        else:
            #this will probably only work properly for versions of Python that have ordered dictionaries
            result = self.__class__.connection.jsonget(self.key, *paths)
            values = list(result.values())
            super().extend(values)

    def append(self, obj):
        self._pull(-1)
        super().append(obj)
        self.__class__.connection.jsonarrappend(self.key, self.path, obj)

    def extend(self, iterable):
        #ReJson does not have this capability
        raise NotImplementedError

    def insert(self, index, obj):
        # found a bug 
        # python will interpret an index out of range as the first or last index (depending on which direction it is out of bounds)
        # redis will interpret an index out of range as.. well.. an index out of range
        index = self._normalize_index(index)
        self._pull(index)
        super().insert(index, obj)
        self.__class__.connection.jsonarrinsert(self.key, self.path, index, obj)

    def pop(self, index=-1):
        self._pull(index)
        super().pop(index)
        self.__class__.connection.jsonarrpop(self.key, self.path, index)


class ReJsonObj(dict):
    connection = None

    def __init__(self, key, path='.', obj={}):
        self.key = key
        self.path = path

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

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            pass

        path = '{}["{}"]'.format(self.path, key)
        if path.startswith('.'):
            path = path[1:]
        value = self.__class__.connection.jsonget(self.key, path)
        
        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        super().__setitem__(key, value)
        return value

    def __setitem__(self, key, value):
        path = '{}["{}"]'.format(self.path, key)
        if path.startswith('.'):
            path = path[1:]

        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        super().__setitem__(key, value)
        self.__class__.connection.jsonset(self.key, path, value)

    def __delitem__(self, key):
        path = '{}["{}"]'.format(self.path, key)
        if path.startswith('.'):
            path = path[1:]

        super().__delitem__(key)
        self.__class__.connection.jsondel(self.key, path)

    def keys(self):
        return self.__class__.connection.jsonobjkeys(self.key)

    def values(self):
        pass

    def items(self):
        pass

    def update(self):
        pass
