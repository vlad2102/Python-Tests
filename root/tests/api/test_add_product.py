from root.core import update_json_in_string
from root.site.api import ShopAPI
from root.site.db import get_session
from root.site.db import tables as st


class TestsAddProductToCart:
    """ Тесты на добавление товара в корзину """

    def setup_class(self):
        self.db_session = get_session('main')

        self.shop_id = self.db_session.query(st.Shop).first().id
        st.clear_tables(self.db_session)

        self.db_session.commit()

    def test_1(self):
        """ Отображение """
        self.db_session.add_all([
            st.Product(id=101, shop_id=self.shop_id, name="Product 1", visible=True),
            st.ProductSku(id=1001, product_id=101, price=0.63, amount=100),
        ])
        self.db_session.commit()

        shop_api = ShopAPI("http://site.loc/shop")
        shop_api.add_skus_to_cart([1001])

        cart_hash = shop_api.get_cart_hash_from_cookies()
        cart_id = self.db_session.query(st.Cart).filter(st.Cart.hash == cart_hash).first().id
        assert self.db_session.query(st.CartSku). \
                   filter(st.CartSku.cart_id == cart_id, st.CartSku.sku_id == 1001).count() == 1
        assert self.db_session.query(st.CartSku). \
                   filter(st.CartSku.cart_id == cart_id, st.CartSku.sku_id == 1001).first().quantity == 1
        assert self.db_session.query(st.CartSku).filter(st.CartSku.cart_id == cart_id).count() == 1

    def test_2(self):
        """ Отображать цену """
        self.db_session.add_all([
            st.Product(id=101, shop_id=self.shop_id, name="Product 1", visible=True),
            st.ProductSku(id=1001, product_id=101, price=0.63, amount=100),
        ])
        self.db_session.query(st.Settings).filter(st.Settings.shop_id == self.shop_id, st.Settings.key == "product"). \
            update({'value': update_json_in_string(st.Settings.default_values['product'], "hide_price", "true")})
        self.db_session.commit()

        shop_api = ShopAPI("http://site.loc/shop")
        shop_api.add_skus_to_cart([1001])

        cart_hash = shop_api.get_cart_hash_from_cookies()
        cart_id = self.db_session.query(st.Cart).filter(st.Cart.hash == cart_hash).first().id
        assert self.db_session.query(st.CartSku). \
                   filter(st.CartSku.cart_id == cart_id, st.CartSku.sku_id == 1001).count() == 1
        assert self.db_session.query(st.CartSku). \
                   filter(st.CartSku.cart_id == cart_id, st.CartSku.sku_id == 1001).first().quantity == 1
        assert self.db_session.query(st.CartSku).filter(st.CartSku.cart_id == cart_id).count() == 1
