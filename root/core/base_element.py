from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.remote import webelement

# https://selenium.dev/selenium/docs/api/py/index.html

from root.core import BrowserFactory


class BaseElement(webelement):

    def __init__(self, locator: str, wait_seconds: int = 10, hidden: bool = False, context: object = None):
        self._locator = locator
        self._wait_seconds = wait_seconds

        self._context = context or BrowserFactory.get_browser()

        if not hidden:
            self.is_displayed = self.is_displayed(wait_seconds)
            assert self.is_displayed, f"Элемент {self._locator} не отображается или скрыт"
        else:
            self._get_element()

        self.ge = self._get_element

        self.text = self._get_text()

    def is_displayed(self, wait_seconds: int = 10) -> bool:
        """ Проверяем, отображается ли элемент. При необходимости ждем wait_seconds времени """

        try:
            WebDriverWait(self._context, wait_seconds).until(
                lambda context: context.find_element_by_xpath(self._locator).is_displayed())
            return True
        except TimeoutException:
            return False

    def _get_element(self, wait_seconds: int = None) -> webelement:
        """ Находим элемент. При необходимости ждем wait_seconds времени """

        wait_seconds = wait_seconds or self._wait_seconds

        try:
            return WebDriverWait(self._context, wait_seconds).until(
                lambda context: context.find_element_by_xpath(self._locator))
        except TimeoutException:
            raise Exception(f"Не могу найти элемент {self._locator}")

    def clear(self) -> None:
        """ Очистить содержимое элемента """

        self._get_element().clear()

    def set_text(self, text: str, clear: bool = True) -> None:
        """ Ввод значения в текстовое поле """

        element = self._get_element()
        if clear:
            self.clear()

        element.send_keys(text)

    def click(self) -> None:
        """ Кликнуть по текущему элементу """

        element = self._get_element()

        # Если _context = browser
        if self._context.__class__.__name__ == 'WebDriver':
            self._context.execute_script("arguments[0].scrollIntoView();", element)

        element.click()

    def _get_text(self, wait_seconds: int = 1) -> str:
        """ Получить текстовое содержимое элемента """

        try:
            text = self._get_element(wait_seconds).text
        except AssertionError:
            text = ""
        return text

    def check(self) -> None:
        """ Отметить чексбоксом текущий элемент """

        if not BaseElement(self._locator + "/preceding-sibling::input", hidden=True).ge().get_attribute("checked"):
            self.click()

    def uncheck(self) -> None:
        """ Снять чексбокс с текущего элемента """

        if BaseElement(self._locator + "/preceding-sibling::input", hidden=True).ge().get_attribute("checked"):
            self.click()
