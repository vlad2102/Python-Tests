import pytest

from root.core.browser import BrowserFactory
from root.core.config import TEST_SITE

from root.site.page_objects import *


class TestsNew:

    def setup_class(cls):
        """ Предусловие для всего раздела """
        BrowserFactory.get_browser().get(f"{TEST_SITE['url']}/login")
        AdminLoginPage().login()
        AdminMainPage().open_item_by_name_in_main_menu("Пункт 1")
        # Предусловие
        BrowserFactory.close_browser()

    def setup_method(self):
        """ Предусловие для каждого теста """

        self.browser = BrowserFactory.get_browser()
        self.browser.maximize_window()

        self.browser.get(f"{TEST_SITE['url']}/login")
        AdminLoginPage().login()
        AdminMainPage().open_item_by_name_in_main_menu("Пункт 1")
        self.admin_shop_products_page = AdminShopProductsPage()
        self.admin_shop_products_page.open_site_by_link_in_header()
        self.browser.switch_to.tab("first")

    def teardown_method(self):
        """ Постусловие для каждого теста """

        BrowserFactory.close_browser()

    # @pytest.mark.skip()
    def test_001(self):
        """ Заказ без включенных методов оплаты и доставки """

        # Предусловие - шаг 1
        AdminShopProductsPage().open_product_by_name("product1")
        AdminShopProductPage().set_params(price=1000, count=1000)
        self.browser.switch_to.tab('last')

        # Тест - шаг 1
        FrontMainPage().open_item_by_name_in_main_menu("Пункт 1")
        FrontShopCatalogPage().open_product_by_name("product1")
        FrontShopProductPage().click_on_button_add_to_cart()
        FrontShopProductPage().open_shop_cart_in_main_menu()
        front_shop_cart_page = FrontShopCartPage()

        # ОР - пункт 1
        front_shop_cart_page.check(
            products=[{'name': "product1", 'price_per_product': 1000, 'quantity': 1, 'price_amount': 1000}],
            deliveries=[],
            prices={'amount_price': 1000}
        )

        # Тест - шаг 2
        front_shop_cart_page.form.fill_form([("Имя", "test1")])
        front_shop_cart_page.form.submit_form()

        # ОР - пункт 2
        order_number = FrontShopCartCheckoutPage().get_order_number()
        # ОР - пункт 3
        self.browser.switch_to.tab('first')
        self.admin_shop_products_page.open_item_by_names_in_left_menu("Продажи", "Заказы")
        admin_shop_orders_page = AdminShopOrdersPage()
        assert admin_shop_orders_page.is_order_number_exist(order_number), f"Заказа '{order_number}' нет"
        amount_price = admin_shop_orders_page.get_price_by_order_number(order_number)
        assert amount_price == 1000, "Неправильная сумма заказа '{order}': '{actual}'. Ожидалось: '{expected}'". \
            format(order=order_number, actual=amount_price, expected=1000)

    # @pytest.mark.skip()
    def test_003(self):
        """Заказ товара, которого нет в наличии"""

        # Предусловие - шаг 1
        self.admin_shop_products_page.open_product_by_name("product1")
        AdminShopProductPage().set_params(price=1000, count=1000)
        self.browser.switch_to.tab('last')

        # Тест - шаг 1
        FrontMainPage().open_item_by_name_in_main_menu("Пункт 1")
        FrontShopCatalogPage().open_product_by_name("product1")
        front_shop_product_page = FrontShopProductPage()

        # Тест - шаг 2
        front_shop_product_page.click_on_button_add_to_cart()

        # ОР - пункт 2
        assert front_shop_product_page.is_it_the_right_page(), "Это не страница товара"

        # Тест - шаг 3
        front_shop_product_page.open_shop_cart_in_main_menu()

        # ОР - пункт 3
        assert FrontShopCartPage().is_it_empty_shop_cart_page, "Должна быть пустая страница"
