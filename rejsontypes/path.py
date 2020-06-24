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