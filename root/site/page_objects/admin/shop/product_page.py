import time

from root.site.page_objects import BaseAdminShopPage
from root.core.base_element import BaseElement


class AdminShopProductPage(BaseAdminShopPage):
    page_locator = "//label[@for='product']"

    locators = {
        'inpPrice': "//input[@name='price']",
        'inpDiscount': "//input[@name='discount']",
        'inpCount': "//input[@name='amount']",
    }

    def set_params(
            self,
            price: int = None,  # Цена
            discount: int = None,  # Цена со скидкой
            count: int = None  # Количество
    ) -> None:
        """ Задать параметры продукту """

        # Цена
        if price is not None:
            BaseElement(self.locators['inpPrice']).set_text(str(price))

        # Цена со скидкой
        if discount is not None:
            BaseElement(self.locators['inpDiscount']).set_text(str(discount))

        # Количество
        if count is not None:
            BaseElement(self.locators['inpCount']).set_text(str(count))

        self.click_on_button_save()
        time.sleep(2)
