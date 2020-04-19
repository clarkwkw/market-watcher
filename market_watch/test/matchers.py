from ..models import User, Product


class UserMatcher:
    def __init__(self, ref_user: User):
        self.ref_user = ref_user

    def __eq__(self, other):
        return self.ref_user.chat_id == other.chat_id and\
            self.ref_user.doc_id == other.doc_id and\
            self.ref_user.subscribed == other.subscribed


class ProductMatcher:
    def __init__(self, ref_product: Product):
        self.ref_product = ref_product

    def __eq__(self, other):
        return self.ref_product.product_ref == other.product_ref and\
            self.ref_product.name == other.name and\
            self.ref_product.status == other.status
