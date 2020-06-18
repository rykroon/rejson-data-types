class ReJsonModel(BaseModel):
    connection = redis0

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
    connection = redis0

    def __init__(self, key, path='.', arr=[]):
        super().__init__(arr)
        self.key = key
        self.path = path
        if self.key not in self.__class__.connection:
            self.__class__.connection.jsonset(self.key, self.path, self)

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            pass

        path = '{}[{}]'.format(self.path, key)
        if path.startswith('.'):
            path = path[1:]
        value = self.__class__.connection.jsonget(self.key, path)
        
        if isinstance(value, dict):
            value = ReJsonObj(value, self.key, path)

        elif isinstance(value, list):
            value = ReJsonArr(value, self.key, path)

        super().__setitem__(key, value)
        return value

    def __setitem__(self, key, value):
        path = '{}[{}]'.format(self.path, key)
        if path.startswith('.'):
            path = path[1:]

        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        super().__setitem__(key, value)
        self.__class__.connection.jsonset(self.key, path, value)

    def __delitem__(self, key):
        path = '{}[{}]'.format(self.path, key)
        if path.startswith('.'):
            path = path[1:]

        super().__delitem__(key)
        self.__class__.connection.jsondel(self.key, path)

    def append(self, obj):
        super().append(obj)
        self.__class__.connection.jsonarrappend(self.key, self.path, obj)

    def insert(self, index, obj):
        super().insert(index, obj)
        self.__class__.connection.jsonarrinsert(self.key, self.path, index, obj)

    def pop(self, index=-1):
        super().pop(index)
        self.__class__.connection.jsonarrpop(self.key, self.path, index)


class ReJsonObj(dict):
    connection = redis0

    def __init__(self, key, path='.', obj={}):
        super().__init__(obj)
        self.key = key
        self.path = path
        if self.key not in self.__class__.connection:
            self.__class__.connection.jsonset(self.key, self.path, self)

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
