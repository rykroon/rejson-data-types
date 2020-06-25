import unittest
import rejson
from rejsontypes import ReJsonArr

client = rejson.Client(decode_responses=True)
ReJsonArr.connection = client


class TestArrayInit(unittest.TestCase):
    def setUp(self):
        pass

    def test_new_arr(self):
        pass

    def test_already_existing_arr(self):
        pass

    def test_remote_object_is_not_an_array(self):
        pass

    def test_default_value_is_not_a_list(self):
        pass


class TestArrayGetItem(unittest.TestCase):
    def setUp(self):
        pass

    def test_first(self):
        pass

    def test_last(self):
        pass

    def test_out_of_range(self):
        pass

    def test_out_of_range_neg(self):
        pass

    def test_slice(self):
        pass


class TestArraySetItem(unittest.TestCase):
    def setUp(self):
        pass

    def test_first(self):
        pass

    def test_last(self):
        pass

    def test_out_of_range(self):
        pass

    def test_out_of_range_neg(self):
        pass

    def test_slice(self):
        pass


class TestArrayDelItem(unittest.TestCase):
    def setUp(self):
        pass

    def test_first(self):
        pass

    def test_last(self):
        pass

    def test_out_of_range(self):
        pass

    def test_out_of_range_neg(self):
        pass

    def test_slice(self):
        pass


class TestReJsonArr(unittest.TestCase):    

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


if __name__ == '__main__':
    unittest.main()