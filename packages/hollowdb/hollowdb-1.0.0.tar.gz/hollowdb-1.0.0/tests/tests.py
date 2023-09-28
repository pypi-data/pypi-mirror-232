import unittest
from src import HollowClient


class TestHollowClient(unittest.TestCase):
    def setUp(self):
        self.api_key = ''  # replace with your API key
        self.db = ''  # replace with your database name
        self.hc = HollowClient(api_key=self.api_key, db=self.db)

    def test_get(self):
        # Assuming you have a key 'test' with value 'value'
        key = 'test'
        val = 'value'
        self.hc.put(key, val)
        value = self.hc.get(key)
        self.assertEqual(value, 'value')

    def test_get_multi(self):
        # Assuming you have keys 'test1' with value 'value1' and 'test2' with value 'value2'
        keys = ['test1', 'test2']
        self.hc.put("test1", "value1")
        self.hc.put("test2", "value2")
        values = self.hc.get_multi(keys)
        self.assertEqual(values, ['value1', 'value2'])

    def test_put(self):
        key = 'test_put'
        self.hc.put(key, 'value_put')
        value = self.hc.get(key)
        self.assertEqual(value, 'value_put')

    def test_put_multi(self):
        self.hc.put_multi([{"key": "key_put_1", "value": "value_put_1"},
                           {"key": "key_put_2", "value": "value_put_2"}])

        value = self.hc.get("key_put_1")
        self.assertEqual(value, 'value_put_1')
        value = self.hc.get("key_put_2")
        self.assertEqual(value, 'value_put_2')

    def test_update(self):
        key = 'test_update'
        self.hc.put(key, 'value_update_1')
        self.hc.update(key, 'value_update_2')
        value = self.hc.get(key)
        self.assertEqual(value, 'value_update_2')

    def test_update_multi(self):
        self.hc.put_multi([{"key": "key_update_1", "value": "value_put_1"},
                           {"key": "key_uptade_2", "value": "value_put_2"}])

        self.hc.update_multi([{"key": "key_update_1", "value": "value_updated_1"},
                              {"key": "key_uptade_2", "value": "value_updated_2"}])

        value = self.hc.get("key_update_1")
        self.assertEqual(value, 'value_updated_1')
        value = self.hc.get("key_uptade_2")
        self.assertEqual(value, 'value_updated_2')

    def test_remove(self):
        key = 'test_remove'
        self.hc.put(key, 'value_remove')
        self.hc.remove(key)
        self.assertEqual(self.hc.get(key), None)

    def test_remove_multi(self):
        self.hc.put_multi([{"key": "key_remove_1", "value": "value_put_1"},
                           {"key": "key_remove_2", "value": "value_put_2"}])

        self.hc.remove_multi([{"key": "key_remove_1"},
                              {"key": "key_remove_2"}])

        value = self.hc.get("key_remove_1")
        self.assertEqual(value, None)
        value = self.hc.get("key_remove_2")
        self.assertEqual(value, None)


if __name__ == '__main__':
    unittest.main()
