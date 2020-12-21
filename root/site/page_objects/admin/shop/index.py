from root.core import BaseElement
from root.site.page_objects import BaseAdminShopPage


class AdminShopProductsPage(BaseAdminShopPage):
    page_locator = "//a[@id='product']"

    locators = {
        'productName': "//a[.='{}']",
    }

    def open_product_by_name(self, product_name: str) -> None:
        """ Открыть продукт по имени """

        BaseElement(self.locators['productName'].format(product_name)).click()
