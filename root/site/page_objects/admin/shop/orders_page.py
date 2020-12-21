from selenium.common.exceptions import NoSuchElementException

from root.core import BaseElement
from root.site.page_objects import BaseAdminShopPage
from root.site.page_objects.front.shop.cart_page import convert_price_from_str_to_float


class AdminShopOrdersPage(BaseAdminShopPage):
    page_locator = "//div[@id='orders']"

    locators = {
        'txbOrderNumber': "//span[contains(text(), '{value}')]",
        'txbPriceByOrderNumber': "//span[contains(text(), '{value}')]/../../div[6]",
        'txbLastOrder': "//div[contains(@class, 'number')]",
    }

    def is_order_number_exist(self, order_number: str) -> bool:
        """ Проверка существования заказа с заданным номером """

        try:
            BaseElement(self.locators['txbOrderNumber'].format(value=order_number))
            return True
        except NoSuchElementException:
            return False

    def get_price_by_order_number(self, order_number: str) -> float:
        """ Получить сумму заказа по номеру заказа """

        txb_price = BaseElement(self.locators['txbPriceByOrderNumber'].format(value=order_number)).text
        return convert_price_from_str_to_float(txb_price)

    def open_last_order(self) -> None:
        """ Открыть последний заказ """
        self._browser.refresh()

        BaseElement(self.locators['txbLastOrder']).click()
