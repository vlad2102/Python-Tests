from root.core import BasePage, BaseElement, TEST_SITE


class AdminLoginPage(BasePage):
    page_locator = "//a[@class='login']"

    locators = {
        'inpLogin': "//input[@id='login']",
        'inpPassword': "//input[@id='pass']",
        'btnLogin': "//input[@type='submit']"
    }

    def login(self, name: str = None, password: str = None) -> None:
        """ Метод логина в админку сайта """

        inp_login = BaseElement(self.locators['inpLogin'])
        name = name or TEST_SITE['login_name']
        inp_login.set_text(name)

        inp_password = BaseElement(self.locators['inpPassword'])
        password = password or TEST_SITE['login_password']
        inp_password.set_text(password)

        btn_login = BaseElement(self.locators['btnLogin'])
        btn_login.click()
