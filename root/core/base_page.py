from root.core import BaseElement, BrowserFactory


class BasePage:
    page_locator: str

    def __init__(self):
        self._browser = BrowserFactory.get_browser()

        assert self.is_it_the_right_page(), f"Не удалось открыть страницу '{self.__class__.__name__}'. " \
                                            f"На странице нет элемента '{self.page_locator}'"

    def is_it_the_right_page(self) -> bool:
        """ Определяем что текущая страница правильная, если на ней есть элемент page_locator """

        try:
            BaseElement(self.page_locator, wait_seconds=20)
            return True
        except AssertionError:
            return False
