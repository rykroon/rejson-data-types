from unittest import TestCase, main
import rejson
from rejsontypes import ReJsonArr
from rejsontypes.notpulled import NotPulled

client = rejson.Client(decode_responses=True)
ReJsonArr.connection = client


class ArrayTestCase(TestCase):
    def setUp(self):
        self.list = [100, 200, 300, 1.23, 4.56, 7.89, 'foo', 'bar', 'baz', True, False, None, [], {}]
        client.jsonset('array', '.', self.list)

    def tearDown(self):
        client.flushdb()


class ArrayInit(ArrayTestCase):
    def test_new_arr(self):
        arr = ReJsonArr('new_array')
        self.assertEqual(client.jsonget('new_array'), arr)

    def test_already_existing_arr(self):
        arr = ReJsonArr('array')
        self.assertEqual(len(arr), client.jsonarrlen('array'))

    def test_remote_object_is_not_an_array(self):
        client.jsonset('not_an_array', '.', {})
        self.assertRaises(TypeError, ReJsonArr, 'not_an_array')

    def test_default_value_is_not_a_list(self):
        self.assertRaises(TypeError, ReJsonArr, 'new_array', '.', {})


class ArrayGetItem(ArrayTestCase):
    def test_first(self):
        arr = ReJsonArr('array')
        self.assertEqual(arr[0], self.list[0])

    def test_last(self):
        arr = ReJsonArr('array')
        self.assertEqual(arr[-1], self.list[-1])

    def test_out_of_range(self):
        arr = ReJsonArr('array')
        self.assertRaises(IndexError, arr.__getitem__, len(arr))

    def test_out_of_range_neg(self):
        arr = ReJsonArr('array')
        out_of_range_index = len(arr) * -1 - 1 # out of range passed the 0th index
        self.assertRaises(IndexError, arr.__getitem__, out_of_range_index)

    def test_slice(self):
        pass


class ArraySetItem(ArrayTestCase):
    def test_first(self):
        arr = ReJsonArr('array')
        arr[0] = 'new value'
        self.assertEqual(arr[0], client.jsonget('array', '[0]'))

    def test_last(self):
        arr = ReJsonArr('array')
        arr[-1] = 'new value'
        self.assertEqual(arr[-1], client.jsonget('array', '[-1]'))

    def test_out_of_range(self):
        arr = ReJsonArr('array')
        self.assertRaises(IndexError, arr.__setitem__, len(arr), "new value")

    def test_out_of_range_neg(self):
        arr = ReJsonArr('array')
        out_of_range_index = len(arr) * -1 - 1 # out of range passed the 0th index
        self.assertRaises(IndexError, arr.__setitem__, out_of_range_index, "new value")

    def test_slice(self):
        pass


class ArrayDelItem(ArrayTestCase):
    def test_first(self):
        arr = ReJsonArr('array')
        del arr[0]
        self.assertEqual(arr[0], client.jsonget('array', '[0]'))
        self.assertEqual(len(arr), client.jsonarrlen('array'))

    def test_last(self):
        arr = ReJsonArr('array')
        del arr[-1]
        self.assertEqual(arr[-1], client.jsonget('array', '[-1]'))
        self.assertEqual(len(arr), client.jsonarrlen('array'))

    def test_out_of_range(self):
        arr = ReJsonArr('array')
        self.assertRaises(IndexError, arr.__delitem__, len(arr))

    def test_out_of_range_neg(self):
        arr = ReJsonArr('array')
        out_of_range_index = len(arr) * -1 - 1
        self.assertRaises(IndexError, arr.__delitem__, out_of_range_index)

    def test_slice(self):
        pass


class ArrayContains(ArrayTestCase):
    def test_contains(self):
        arr = ReJsonArr('array')
        self.assertEqual(100 in arr, 100 in self.list)
        self.assertEqual('nope' in arr, 'nope' in self.list)


class ArrayIter(ArrayTestCase):
    def test_iter(self):
        arr = ReJsonArr('array')
        for i in arr:
            self.assertNotEqual(i, NotPulled)

    def test_enumerate(self):
        arr = ReJsonArr('array')
        for _, value in enumerate(arr):
            self.assertNotEqual(value, NotPulled)


class ArrayAppend(ArrayTestCase):
    def test_append_to_new_array(self):
        pass

    def test_append_to_already_existing_array(self):
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


# !! test expire() and ttl() as well


if __name__ == '__main__':
    main()