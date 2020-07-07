from .notfetched import NotFetched
from.path import Path

class ReJsonMixin:
    connection = None
    jsontype = ''
    pytype = None

    # def __init__(self, key, path='.', default=[]):
        # self.key = key
        # self.path = Path(path)
        # json_type = self.__class__.connection.jsontype(self.key, self.path)

        # #do not create a new array if one already exists
        # if json_type == self.__class__.jsontype:
        #     pass

        # #The array does not exist so create one
        # elif json_type is None:
        #     if not isinstance(default, self.__class__.pytype):
        #         raise TypeError(
        #             "default value is not an instance of '{}'".format(
        #                 self.__class__.pytype.__name__
        #             )
        #         )
            
        #     super().__init__(default)
        #     self.__class__.connection.jsonset(self.key, self.path, self)

        # else:
        #     raise TypeError(
        #         "Remote object is not of type '{}'".format(
        #             self.__class__.jsontype
        #         )
        #     )

    def expire(self, ttl):
        return self.__class__.connection.expire(self.key, ttl)

    def ttl(self):
        return self.__class__.connection.ttl(self.key)