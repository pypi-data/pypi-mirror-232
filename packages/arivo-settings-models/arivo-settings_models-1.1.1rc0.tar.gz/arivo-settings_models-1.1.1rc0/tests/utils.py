import unittest

import orjson

from settings_models.serialization import dump_setting


class TestCase(unittest.TestCase):
    def remove_nones(self, d):
        if isinstance(d, dict):
            for k, v in list(d.items()):
                if isinstance(v, dict):
                    self.remove_nones(v)
                elif v is None:
                    del d[k]
        return d

    @staticmethod
    def load_if_json(obj):
        if not isinstance(obj, (str, bytes)):
            obj = dump_setting(obj)
        return orjson.loads(obj)

    def assert_result(self, res, gt):
        res = self.remove_nones(self.load_if_json(res))
        gt = self.remove_nones(self.load_if_json(gt))
        if isinstance(res, dict):
            self.assertDictEqual(res, gt)
        elif isinstance(res, list):
            self.assertCountEqual(res, gt)
        else:
            self.assertEqual(res, gt)

    def assert_not_result(self, res, gt):
        res = self.remove_nones(self.load_if_json(res))
        gt = self.remove_nones(self.load_if_json(gt))
        self.assertNotEqual(res, gt)
