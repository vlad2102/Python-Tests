DB: dict = {
    'user': "user",
    'password': "password",
    'host': "localhost:3000",
    'names': {
        'main': "main",
    },
}

""" Данные тестового сайта """
TEST_SITE = {
    'url': "https://site.loc",
    'login_name': "test",
    'login_password': "test",
}


class Browsers:
    """ Задаем webdrivers и их расположение """

    """ Браузер по умолчанию для запуска тестов
        Используются: firefox, chrome, safari """
    DEFAULT = "chrome"

    """ Все webdrivers располагаются в папке _folder """
    FOLDER = "root/core/browsers"

    FIREFOX_DRIVER_NAME_WINDOWS = "geckodriver.exe"
    FIREFOX_DRIVER_NAME_LINUX = "geckodriver-v0.26.0-linux64"
    FIREFOX_DRIVER_NAME_MAC = "geckodriver-v0.26.0-macos"

    CHROME_DRIVER_NAME_WINDOWS = "chromedriver.exe"
    CHROME_DRIVER_NAME_LINUX = "chromedriver_linux64"
    CHROME_DRIVER_NAME_MAC = "chromedriver_mac64"


""" Папка для сохранения исходных скриншотов, которе сравнивались """
FOLDER_SCREENSHOTS_SOURCES = "images/sources"
""" Папка для сохранения результата сравнения двух скриншотов """
FOLDER_SCREENSHOTS_COMPARED = "images"
