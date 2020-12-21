from root.core import BaseElement
from root.site.page_objects import BaseFrontPage


class FrontShopCatalogPage(BaseFrontPage):
    page_locator = "//div[@class='products']"

    locators = {
        'txbProductName': "//div[text()='{name}']"
    }

    def open_product_by_name(self, product_name: str) -> None:
        """ Открыть продукт по имени """

        BaseElement(self.locators['txbProductName'].format(name=product_name)).click()
