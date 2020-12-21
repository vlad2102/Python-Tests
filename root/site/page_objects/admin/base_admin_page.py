from selenium.webdriver.support.ui import WebDriverWait

from root.core import BasePage, BaseElement


class BaseAdminPage(BasePage):
    base_admin_locators = {
        'txbSiteNameLink': "//a[contains(@class, 'link')]",
        'txbMenuItemByName': "//span[contains (text(), '{}')]/..",
    }

    main_menu = ["Пункт 1", "Пункт 2", "Пункт 3"]

    def open_site_by_link_in_header(self) -> None:
        """ Открытие главной страницы сайта по ссылке из шапки """

        tabs_in_browser = self._browser.window_handles
        txb_site_name_link = BaseElement(self.base_admin_locators['txbSiteNameLink'])
        txb_site_name_link.click()
        WebDriverWait(self._browser, 10).until(lambda browser: len(browser.window_handles) > len(tabs_in_browser))

    def open_item_by_name_in_main_menu(self, name: str) -> None:
        """ Открыть раздел сайта по имени в главном меню """

        assert name in self.main_menu, f"Нет пункта {name} в главном меню"

        txb_menu_item = BaseElement(self.base_admin_locators['txbMenuItemByName'].format(name))
        txb_menu_item.click()
