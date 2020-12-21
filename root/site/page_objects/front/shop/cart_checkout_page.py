import re

from root.core import BaseElement
from root.site.page_objects import BaseFrontPage


class FrontShopCartCheckoutPage(BaseFrontPage):
    page_locator = "//div[@class='success']"

    locators = {
        'txbOrderTitle': "//div[@class='order-title']"
    }

    def get_order_number(self) -> str:
        """ Извлечение номера заказа """

        txb_order_number = BaseElement(self.locators["txbOrderTitle"]).text
        return re.search(r"(\d{6})", txb_order_number).group(0)
