import unittest
from parameterized import parameterized
from ...models import ProductStatus


class TestProductStatus(unittest.TestCase):
    @parameterized.expand([
        [ProductStatus.AVAILABLE,   "AvAilAble",                True],
        [ProductStatus.AVAILABLE,   ProductStatus.AVAILABLE,    True],
        [ProductStatus.UNAVAILABLE, "UNAvailAble",              True],
        [ProductStatus.UNAVAILABLE, ProductStatus.UNAVAILABLE,  True],
        [ProductStatus.NOT_FOUND,   "nOt_FouNd",                True],
        [ProductStatus.NOT_FOUND,   ProductStatus.NOT_FOUND,    True],
        [ProductStatus.UNKNOWN,     "UnkNoWn",                  True],
        [ProductStatus.AVAILABLE,   ProductStatus.UNAVAILABLE,  False],
        [ProductStatus.AVAILABLE,   ProductStatus.NOT_FOUND,    False],
        [ProductStatus.UNKNOWN,     ProductStatus.NOT_FOUND,    False],
        [ProductStatus.UNAVAILABLE, ProductStatus.NOT_FOUND,    False],
    ])
    def test_equality(self, s1, s2, should_equal: bool):
        self.assertEqual((s1 == s2), should_equal)
