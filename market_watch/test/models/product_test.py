import unittest
from ...models import Product, ProductRef, Platform


class TestProduct(unittest.TestCase):
    def test_equality(self):
        product_ref_1 = ProductRef(Platform.AMAZON_JP, "ref1")
        product_ref_2 = ProductRef(Platform.AMAZON_JP, "ref2")
        product_ref_3 = ProductRef(Platform.AMAZON_JP, "ref1")

        self.assertEqual(product_ref_1 == product_ref_1, True)
        self.assertEqual(product_ref_1 == product_ref_2, False)
        self.assertEqual(product_ref_1 == product_ref_3, True)

        p1 = Product(product_ref_1)
        p2 = Product(product_ref_2)
        p3 = Product(product_ref_3)

        self.assertEqual(p1 == p1, True)
        self.assertEqual(p1 == p2, False)
        self.assertEqual(p1 == p3, True)
