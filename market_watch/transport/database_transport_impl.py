import ssl
from typing import List, Optional
import pymongo
from .database_transport_base import DatabaseTransport
from ..models import Product, User, ProductRef, Platform


class DatabaseTransportImpl(DatabaseTransport):
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.__mongo_client = pymongo.MongoClient(
            uri,
            ssl_cert_reqs=ssl.CERT_NONE
        )

    def get_all_subscribed_products(self) -> List[Product]:
        default_product = Product(ProductRef(Platform.AMAZON_JP, ""))
        default_product_dict = default_product.to_dict()
        default_product_dict["_id"]["id"] = "$_id.id"
        default_product_dict["_id"]["platform"] = "$_id.platform"
        result = self.__mongo_client[self.db_name]["Users"].aggregate([
            # extract subscribed product refs from all users
            {"$unwind": "$subscribed"},
            # eliminate duplication
            {
                "$group": {
                    "_id": {
                        "platform": "$subscribed.platform",
                        "id": "$subscribed.id",
                    }
                }
            },
            # look up previous result in "Products"
            {
                "$lookup": {
                    "from": "Products",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "prev_records"
                }
            },
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [
                            default_product_dict,
                            {
                                "$arrayElemAt": ["$prev_records", 0]
                            }
                        ]
                    }
                }
            }
        ])

        return [Product.from_dict(d) for d in result]

    def get_products_by_refs(
        self,
        product_refs: List[ProductRef],
        return_default_if_not_found=False
    ) -> List[Product]:
        result = self.__mongo_client[self.db_name]["Products"].find(
            {
                "_id": {
                    "$in": [pr.to_dict() for pr in product_refs]
                }
            },
        )
        products = [Product.from_dict(d) for d in result]
        if not return_default_if_not_found:
            return products

        for pr in product_refs:
            if pr not in products:
                products.append(Product(pr))
        return products

    def save_products(self, products: List[Product]):
        for p in products:
            self.__mongo_client[self.db_name]["Products"].replace_one(
                {
                    "_id": p.product_ref.to_dict()
                },
                p.to_dict(),
                upsert=True
            )

    def get_user(self, chat_id: str) -> Optional[User]:
        doc = self.__mongo_client[self.db_name]["Users"].find_one({
            'chat_id': chat_id
        })
        if doc is not None:
            return User.from_dict(doc)
        return None

    def get_subscribed_users(
        self,
        product_refs: List[ProductRef]
    ) -> List[User]:
        user_dicts = self.__mongo_client[self.db_name]["Users"].find(
            {
                'subscribed': {
                    '$in': [pr.to_dict() for pr in product_refs]
                }
            },
        )
        return [User.from_dict(d) for d in user_dicts]

    def save_user(self, user: User):
        if user.doc_id is not None:
            self.__mongo_client[self.db_name]["Users"].replace_one(
                {'_id': user.doc_id},
                user.to_dict()
            )
        else:
            self.__mongo_client[self.db_name]["Users"].insert_one(
                user.to_dict()
            )
