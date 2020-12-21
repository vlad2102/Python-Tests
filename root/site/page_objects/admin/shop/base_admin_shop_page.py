import time

from root.core import BaseElement
from root.site.page_objects import BaseAdminPage


class BaseAdminShopPage(BaseAdminPage):
    base_admin_shop_locators = {
        'txbMenu': "//nav//a[contains(@class, 'menu') and text()='{}']",
        'txbSubMenu': "//nav//a[text()='{}']",
        'btnSubmit': "//input[@type='submit']",
    }

    def open_item_by_names_in_left_menu(self, menu_item: str, sub_menu_item: str) -> None:
        """ Открыть раздел сайта по имени раздела и пункта в левом меню """

        menu_item_parent_element = BaseElement(
            self.base_admin_shop_locators['txbMenu'].format(menu_item) + "/..")

        if 'is-open' not in menu_item_parent_element.ge().get_attribute('class'):
            # Если родительская категория не раскрыта, раскрываю
            BaseElement(self.base_admin_shop_locators['txbMenu'].format(menu_item)).click()

        # Открываю подменю
        BaseElement(self.base_admin_shop_locators['txbSubMenu'].format(sub_menu_item)).click()

    def click_on_button_save(self):
        """ Стандартная кнопка сохранения для магазина """

        BaseElement(self.base_admin_shop_locators['btnSubmit']).click()

        time.sleep(1)
