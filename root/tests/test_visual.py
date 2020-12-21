import pytest
import time

from root.core import element_screenshot, compare_images, save_images, BrowserFactory
from root.core.visual_functions import _full_screenshot_old


class TestsBasedOnCompareScreenshots:
    """ Визуальные тесты основанные на сравнении скриншотов """

    # @pytest.mark.skip()
    def test_1(self):
        """ Ручной тест
            Запуск с флагом -s """

        site_1 = "http://site.loc"
        site_2 = "http://history.loc"

        landing = [
            "/",
            "/page-1",
            "/page-2",
        ]

        blog = [
            "/post-1",
            "/post-2",
        ]

        shop = [
            "/product-1",
            "/product-2",
        ]

        pages_for_test = landing + blog + shop

        browsers = []

        browser_names = ["chrome-max", "chrome-tab", "chrome-mob"]
        for browser_name in browser_names:
            browser = BrowserFactory.get_browser()

            if browser_name == "chrome-max":
                browser.maximize_window()
            elif browser_name == "chrome-tab":
                browser.set_window_size(1024, 720)
            else:
                browser.set_window_size(560, 720)

            browser.open_new_tab()

            browsers.append(browser)

        while True:
            for page in pages_for_test:
                screenshot = True

                if type(page) is tuple:
                    if len(page) == 2:
                        page_1, page_2 = page
                    elif len(page) == 3:
                        page_1, page_2 = page[:2]

                        if page[2] == "dont_do_screenshot":
                            screenshot = False
                else:
                    page_1 = page_2 = page

                for i, browser in enumerate(browsers):
                    browser.switch_to.tab("first")
                    browser.get(site_1 + page_1)
                    if screenshot:
                        time.sleep(3)
                        image_1 = element_screenshot(browser)
                        # image_1 = _full_screenshot_old(browser)

                    browser.switch_to.tab("last")
                    browser.get(site_2 + page_2)
                    if screenshot:
                        time.sleep(3)
                        image_2 = element_screenshot(browser)
                        # image_2 = _full_screenshot_old(browser)

                    images_compared = compare_images(image_1, image_2)

                    save_images(sources=[image_1, image_2], compared=images_compared, page=page_1, browser=browser_names[i])
            input("\nЖдемс...")
