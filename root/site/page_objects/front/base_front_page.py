from root.core.base_page import BasePage
from root.core.base_element import BaseElement
from root.core.config import TEST_SITE


class BaseFrontPage(BasePage):
    base_front_locators = {
        'txbMenuItem': "//nav//li[contains(@class, 'menu-item')]/a[@data-name='{}']",
        'btnShopCartInMenu': "//nav//a[@data-id='widget']",
    }

    main_menu = [
        {'name': "МАГАЗИН", 'link': f"{TEST_SITE['url']}/shop"},
    ]

    def open_item_by_name_in_main_menu(self, name: str) -> None:
        """ Открыть страницу по ссылке в меню"""

        assert name in [item['name'] for item in self.main_menu], f"Нет пункта {name} в меню"

        BaseElement(self.base_front_locators['txbMenuItem'].format(name)).click()

    def open_shop_cart_in_main_menu(self) -> None:
        """ Открыть страницу корзины по значку в меню """

        BaseElement(self.base_front_locators['btnShopCartInMenu']).click()
