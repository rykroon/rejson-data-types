import unittest
import rejson
from rejsontypes import ReJsonArr, ReJsonObj

client = rejson.Client(decode_responses=True)
ReJsonArr.connection = client
ReJsonObj.connection = client


class TestReJsonArr(unittest.TestCase):

    def test_init(self):
        pass
    
    def test_getitem(self):
        pass

    def test_setitem(self):
        pass

    def test_delitem(self):
        pass

    def test_append(self):
        pass

    def test_clear(self):
        pass

    def test_copy(self):
        pass

    def test_count(self):
        pass

    def test_extend(self):
        pass

    def test_index(self):
        pass

    def test_insert(self):
        pass

    def test_pop(self):
        pass

    def test_remove(self):
        pass

    def test_reverse(self):
        pass

    def test_sort(self):
        pass


class TestReJSonObj(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()