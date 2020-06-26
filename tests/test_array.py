from unittest import TestCase, main
import rejson
from rejsontypes import ReJsonArr

client = rejson.Client(decode_responses=True)
ReJsonArr.connection = client


class ArrayInit(TestCase):
    def test_new_arr(self):
        arr = ReJsonArr('new_array')
        self.assertEqual(client.jsonget('new_array'), [])

    def test_already_existing_arr(self):
        arr = ReJsonArr('array')
        self.assertEqual(len(arr), client.jsonarrlen('array'))

    def test_remote_object_is_not_an_array(self):
        self.assertRaises(TypeError, ReJsonArr, 'not_an_array')

    def test_default_value_is_not_a_list(self):
        self.assertRaises(TypeError, ReJsonArr, 'new_array', '.', {})

    @classmethod
    def setUpClass(cls):
        arr = [1, 2, 3, 'a', 'b', 'c', True, False, None, [], {}]
        client.jsonset('array', '.', arr)
        client.jsonset('not_an_array', '.', {})

    @classmethod
    def tearDownClass(cls):
        client.flushdb()


class ArrayGetItem(TestCase):
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


class ArraySetItem(TestCase):
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


class ArrayDelItem(TestCase):
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


class ArrayAppend(TestCase):
    pass


class ArrayClear(TestCase):
    pass


class ArrayCopy(TestCase):
    pass


class ArrayCount(TestCase):
    pass


class ArrayExtend(TestCase):
    pass


class ArrayIndex(TestCase):
    pass


class ArrayInsert(TestCase):
    pass


class ArrayPop(TestCase):
    pass


class ArrayRemove(TestCase):
    pass


class ArrayReverse(TestCase):
    pass


class ArraySort(TestCase):
    pass


if __name__ == '__main__':
    main()