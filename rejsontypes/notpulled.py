class NotPulledType:
    """
        A Singleton class
    """
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return '\u21e3' #downward dashed arrow
        #return '-'


NotPulled = NotPulledType()