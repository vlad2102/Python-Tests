import os
from platform import system
from types import MethodType
from typing import Union
from selenium import webdriver

from root.core import Browsers


class BrowserFactory:
    instance = None

    @classmethod
    def get_browser(cls, browser_name: str = Browsers.DEFAULT):
        if cls.instance is None:
            cls.instance = BrowserFactory(browser_name)
        return cls.instance.browser

    @classmethod
    def close_browser(cls):
        if cls.instance:
            cls.instance.browser.quit()
        cls.instance = None

    def __init__(self, browser_name: str):
        if 'browser' not in self.__dict__:
            self.browser = self._get_browser_for_current_os(browser_name)

        # Расширение экземпляра браузера пользовательскими методами
        self.browser.open_new_tab = MethodType(self._open_new_tab, self.browser)
        self.browser.switch_to.tab = MethodType(self._switch_to_tab, self.browser)

    @staticmethod
    def _get_browser_for_current_os(browser_name: str) -> webdriver:
        """ Определяем версию операционной системы и возвращаем соостветсвующий webdriver """

        _browsers_folder = os.path.join(os.getcwd(), *Browsers.FOLDER.split('/'))

        if system() == 'Windows':
            _browsers_folder += '\\'
            if browser_name == 'firefox':
                return webdriver.Firefox(executable_path=_browsers_folder + Browsers.FIREFOX_DRIVER_NAME_WINDOWS)
            elif browser_name == 'chrome':
                return webdriver.Chrome(executable_path=_browsers_folder + Browsers.CHROME_DRIVER_NAME_WINDOWS)
        elif system() == 'Linux':
            _browsers_folder += '/'
            if browser_name == 'firefox':
                return webdriver.Firefox(executable_path=_browsers_folder + Browsers.FIREFOX_DRIVER_NAME_LINUX)
            elif browser_name == 'chrome':
                return webdriver.Chrome(executable_path=_browsers_folder + Browsers.CHROME_DRIVER_NAME_LINUX)
        elif system() == 'Darwin':
            _browsers_folder += '/'
            if browser_name == 'firefox':
                return webdriver.Firefox(executable_path=_browsers_folder + Browsers.FIREFOX_DRIVER_NAME_MAC)
            elif browser_name == 'chrome':
                return webdriver.Chrome(executable_path=_browsers_folder + Browsers.CHROME_DRIVER_NAME_MAC)
            elif browser_name == 'safari':
                return webdriver.Safari()

        raise Exception(f"Не получается запустить браузер {browser_name} на ОС {system()}")

    @staticmethod
    def _open_new_tab(self) -> None:
        """ Открыть новую вкладку в браузере """

        self.execute_script("window.open('', 'new_window')")

    @staticmethod
    def _switch_to_tab(self, tab: Union[int, str]) -> None:
        """ Переключиться на вкладку в браузере: первую, последнюю или по номеру """

        if type(tab) is int:
            pass
        elif tab == 'first':
            tab = 0
        elif tab == 'last':
            tab = -1
        else:
            raise Exception(f"Неизвестный формат вкладки [tab]: '{tab}'")

        self.switch_to.window(self.window_handles[tab])
