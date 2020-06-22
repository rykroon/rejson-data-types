

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
    pass


class ReJsonArr(list):
    connection = None

    def __init__(self, key, path='.', arr=[]):
        self.key = key
        self.path = Path(path)
        self.length = None
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

    # def __iter__(self):
    #     self._pull(-1)
    #     return super().__iter__()
            
    def __len__(self):
        if self.length is None:
            self.length = self.__class__.connection.jsonarrlen(self.key, self.path)
        return self.length
        
    def __getitem__(self, index):
        self._pull(index)
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        self._pull(index)
        path = self.path[index]

        if isinstance(value, dict):
            value = ReJsonObj(self.key, path, value)

        elif isinstance(value, list):
            value = ReJsonArr(self.key, path, value)

        self.__class__.connection.jsonset(self.key, path, value)
        super().__setitem__(index, value)
        

    def __delitem__(self, index):
        self._pull(index)
        path = self.path[index]
        self.__class__.connection.jsondel(self.key, path)
        self.length = None
        super().__delitem__(index)

    def __repr__(self):
        result = super().__repr__()
        if len(self) > super().__len__():
            if super().__len__() == 0:
                return '[...]'
            result = result[:-1]
            result += ', ...]'
        return result

    def _convert_neg_index(self, index):
        if index < 0:
            return index + len(self)
        return index

    def _round_index(self, index, exclusive=False):
        """
            if the index is out of range... 
                set to 0 if below range
                set to last index or last index +1 if above range
            
            :param index: The index to round
            :type index: int or slice
            :param exclusive: Whether or not the index should be treated as inclusive or exclusive
            :type exclusive: bool
        """
        #convert slice into an int
        if type(index) == slice:
            index = index.stop or len(self)

        #convert negative index
        index = self._convert_neg_index(index)

        # set minimum index to 0
        index = max(index, 0)

        #set maximum index to the length of the list
        max_index = len(self)
        #if not exclusive, subtract 1
        if not exclusive:
            max_index -= 1
        index = min(index, max_index)
        return index

    def _pull(self, index):
        """
            Pull elements from redis up to a certain index
        """
        start_index = super().__len__()
        index = self._round_index(index)    
        if start_index > index:
            return

        paths = [self.path[i] for i in range(start_index, index + 1)]

        if len(paths) == 1:
            value = self.__class__.connection.jsonget(self.key, paths[0])
            super().append(value)
        elif len(paths) > 1:
            #this will probably only work properly for versions of Python that have ordered dictionaries
            result = self.__class__.connection.jsonget(self.key, *paths)
            values = list(result.values())
            super().extend(values)

    def append(self, obj):
        self._pull(-1)
        self.length = self.__class__.connection.jsonarrappend(self.key, self.path, obj)
        super().append(obj)
        
    def extend(self, iterable):
        self._pull(-1)
        self.length = self.__class__.connection.jsonarrappend(self.key, self.path, *iterable)
        super().extend(iterable)

    def insert(self, index, obj):
        self._pull(index)
        index = self._round_index(index, exclusive=True)
        self.length = self.__class__.connection.jsonarrinsert(self.key, self.path, index, obj)
        super().insert(index, obj)

    def pop(self, index=-1):
        result = self.__class__.connection.jsonarrpop(self.key, self.path, index)
        self.length = None

        index = self._convert_neg_index(index)
        if index < super().__len__():
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
