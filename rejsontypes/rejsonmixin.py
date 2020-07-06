class ReJsonMixin:
    connection = None

    def expire(self, ttl):
        return self.__class__.connection.expire(self.key, ttl)

    def ttl(self):
        return self.__class__.connection.ttl(self.key)