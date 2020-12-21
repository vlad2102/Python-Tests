import re
import time
from io import StringIO
from typing import Any

from lxml import etree
# https://lxml.de/1.3/tutorial.html
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.support.wait import WebDriverWait

from root.core import BaseElement
from root.site.page_objects import BaseFrontPage


def convert_price_from_str_to_float(price: str) -> float:
    """ Приведение цены к вещественному числу """

    # Находим построку состоящую из: чисел, пробелов и точек
    price = re.search(r"([\d\s.]+)", price).group(0)

    price = price.replace(" ", "")

    return float(price)


class FrontShopCartPage(BaseFrontPage):
    page_locator = "//div[@id='cart-page']"

    locators = {
        'divCartLoaded': f"{page_locator}/div",
        'divEmptyShopCartPage': "//div[@class='shopcart-empty']",
        'locLoader': "//*[name()='svg' and contains(@class, 'loader')]",
        'txbMinOrderMessage': "//span[contains(@class, 'min-price-error')]",
    }

    def __init__(self, is_wait: bool = False):
        super().__init__()
        self._wait_while_cart_loading()
        self.is_it_empty_shop_cart_page = self.is_it_empty_shop_cart_page()
        if not self.is_it_empty_shop_cart_page:
            self._wait_while_cart_recalculate()
            if not is_wait:
                self.products = self.Products(self._browser)
                self.deliveries = self.Deliveries(self._browser)
                self.payments = self.Payments(self._browser)
                self.promocode = self.Promocode()
                self.form = self.Form(self._browser)
                self.prices = self.Prices()
                self.errors = self.products.errors + self.promocode.errors + self.form.errors

                self._error_min_order_message()

    def _wait_while_cart_loading(self) -> None:
        """ Ждем пока сформируется корзина """

        WebDriverWait(self._browser, 10).until(
            lambda browser: browser.find_element_by_xpath(self.locators['divCartLoaded']))

    def is_it_empty_shop_cart_page(self) -> bool:
        """ Проверяем что открыта пустая корзина """

        try:
            BaseElement(self.locators['divEmptyShopCartPage'], 1)
            return True
        except AssertionError:
            return False

    def _wait_while_cart_recalculate(self) -> None:
        """ Ждем пересчета корзины """

        time.sleep(0.5)
        WebDriverWait(self._browser, 10).until_not(
            lambda browser: browser.find_element_by_xpath(self.locators['locLoader']).is_displayed())
        time.sleep(0.3)

    def _error_min_order_message(self) -> None:
        try:
            self.errors.append(('min_order_message', BaseElement(self.locators['txbMinOrderMessage'], 0).text))
        except AssertionError:
            pass

    def check(self, products: list = None, deliveries: list = None,
              payments: list = None, prices: dict = None, errors: dict = None) -> None:
        """ Проверка страницы на наличие параметров """

        if products:
            products_name = [item['name'] for item in products]
            self.Products.is_in_cart_by_names(self.products, products_name)

            for product in products:
                for key in product:
                    temp = self.Products.get_property_by_name(self.products, product['name'], key)
                    assert product[key] == temp, \
                        f"Неправильное значение '{key}' у товара '{product['name']}': '{temp}'. " \
                        f"Ожидалось: '{product[key]}'"

        if deliveries:
            deliveries_name = [item['name'] for item in deliveries]
            self.Deliveries.is_in_cart_by_names(self.deliveries, deliveries_name)

            for delivery in deliveries:
                for key in delivery:
                    temp = self.Deliveries.get_property_by_name(self.deliveries, delivery['name'], key)
                    assert delivery[key] == temp, \
                        f"Неправильное значение '{key}' у метода доставки '{delivery['name']}': '{temp}'. " \
                        f"Ожидалось: '{delivery[key]}'"

        if payments:
            payments_name = [item['name'] for item in payments]
            self.Payments.is_in_cart_by_names(self.payments, payments_name=payments_name)

            for payment in payments:
                for key in payment:
                    temp = self.Payments.get_property_by_name(self.payments, payment['name'], key)
                    assert payment[key] == temp, \
                        f"Неправильное значение '{key}' у метода оплаты '{payment['name']}': '{temp}'. " \
                        f"Ожидалось: '{payment['price']}'"

        if prices:
            for key in prices:
                assert prices[key] == self.prices.prices[key], \
                    f"Неправильное значение '{key}': '{self.prices.prices[key]}'. Ожидалось: '{prices[key]}'"

        if errors:
            for key in errors:
                error_names = [item[0] for item in self.errors]
                if key == 'form_fields_not_red':
                    result = list(set(errors[key]) ^ set(self.errors[error_names.index(key)][1]))
                    assert len(result) == 0, f"В корзине не подсвечены {result} поля"
                elif key in error_names:
                    assert errors[key] == self.errors[error_names.index(key)][1], \
                        f"Неправильное значение '{key}' в ошибке : '{self.errors[error_names.index(key)][1]}'. " \
                        f"Ожидалось: '{errors[key]}'"
                else:
                    raise Exception(f"В ошибках нет параметра '{key}'")

    class Products:
        locators = {
            'divProducts': "//div[@class='cart-products']/div",
            'txbName': ".//span[contains(@class, 'title')]",
            'txbParams': ".//span[contains(@class, 'title')]/span",
            'txbPricePerProduct': ".//div[contains(@class, 'price')]",
            'inpQuantity': ".//input[contains(@class, 'quantity')]",
            'txbPriceAmount': ".//div[contains(@class, 'amount')]/span[last()]",
            'txbPriceAmountOld': ".//div[contains(@class, 'amount')]/span[@id='old']",
            'btnDelete': ".//a[contains(@class, 'delete-product')]",
            'txbProductCount': ".//div[contains(@class, 'box') and contains(@class, 'count')]",
            'btnConfirmDelete': "//button[contains(@class, 'confirm')]",
        }

        def __init__(self, browser: webdriver):
            self._browser = browser

            self.products = []
            self.errors = []

            div_products = self._browser.find_elements_by_xpath(self.locators['divProducts'])
            for div_product in div_products:
                html = etree.parse(StringIO(div_product.get_property('outerHTML')), parser=etree.HTMLParser())

                # Название товара
                name_element = BaseElement(self.locators['txbName'], context=div_product)

                # Цена за единицу продукта
                price_per_product = html.xpath(self.locators['txbPricePerProduct'])[0].text

                # Поле с количеством
                quantity_element = BaseElement(self.locators['inpQuantity'], context=div_product)

                # Итогова цена за товар
                price_amount = convert_price_from_str_to_float(html.xpath(self.locators['txbPriceAmount'])[0].text)
                try:
                    # Итоговая цена без скидки
                    price_amount_old = convert_price_from_str_to_float(
                        html.xpath(self.locators['txbPriceAmountOld'])[0].text)
                except IndexError:
                    price_amount_old = None

                # Элемент удаления товара из корзины
                delete_element = BaseElement(self.locators['btnDelete'], context=div_product)

                # Сообщение о количестве товара в магазине
                try:
                    count_message = html.xpath(self.locators['txbProductCount'])[0].text
                except IndexError:
                    count_message = None

                self.products.append({
                    'name': name_element.text + self._get_params(html),  # название товара
                    'price_per_product': convert_price_from_str_to_float(price_per_product),  # цена за единицу продукта
                    'quantity': int(quantity_element.ge().get_property('value')),  # количество товара
                    'price_amount': price_amount,  # итогова цена за товар
                    'price_amount_old': price_amount_old,  # итоговая цена без скидки
                    'count_message': count_message,  # сообщение о количеством товара в магазине
                    'elements': {
                        'name': name_element,  # элемент название товара
                        'quantity': quantity_element,  # элемент количество товара
                        'delete': delete_element  # элемент удаления товара из корзины
                    }
                })

                self._error_in_quantity(self.products[-1]['name'], quantity_element, count_message)

        def _get_params(self, html: etree) -> str:
            """ Определяем параметры товара """

            params = ""
            span_params = html.xpath(self.locators['txbParams'])
            for span_param in span_params:
                params += "|" + span_param.text.strip()

            return params

        def is_in_cart_by_names(self, products_name: list, mode: str = 'hard') -> None:
            """ Проверка, есть ли в корзине переданные товары
                - mode=light : в корзине есть товары products_name
                - mode=hard : в корзине есть ТОЛЬКО товары products_name """

            products = [item['name'] for item in self.products]
            result = list(set(products_name) ^ set(products))
            assert len(result) == 0, f"В корзине нет {result} товара/ов"

            if mode == 'hard':
                result = list(set(products) - set(products_name))
                assert len(result) == 0, f"В корзине есть дополнительные {result} товар/ы"

        def get_property_by_name(self, product_name: str, property: str) -> Any:
            """ Получить свойство товара по названию товара и названию свойства """

            return self.products[self._get_index_by_name(product_name)][property]

        def set_quantity_by_name(self, product_name: str, quantity: int) -> None:
            """ Задать количество указанному товару """

            for i in range(10):
                try:
                    element = self.products[self._get_index_by_name(product_name)]['elements']['quantity']
                    # Два символа backspace
                    # add_text = "\ue003\ue003"
                    element.set_text(f"\ue003\ue003\ue003\ue003{quantity}", clear=False)
                    break
                except ElementNotInteractableException:
                    time.sleep(1)
            FrontShopCartPage(is_wait=True)

        def delete_by_name(self, product_name: str) -> None:
            """ Удалить указанный товар """

            time.sleep(1)
            self.products[self._get_index_by_name(product_name)]['elements']['delete'].click()
            time.sleep(2)
            # Подтверждения удаления товара
            BaseElement(self.locators['btnConfirmDelete']).click()
            FrontShopCartPage(is_wait=True)

        def _get_index_by_name(self, product_name: str) -> int:
            """ Получить индекс товара по его названию """

            return [item['name'] for item in self.products].index(product_name)

        def _error_in_quantity(self, product_name: str, inp_quantity: BaseElement, count_message: str) -> None:
            """ Поле количество указанного товара """

            error = 0

            if "isError__" in inp_quantity.ge().get_attribute('class'):
                error += 1

            if count_message:
                error += 1

            if error == 2:
                self.errors.append(('product_quantity', product_name))

    class Deliveries:
        locators = {
            'divDeliveries': "//div[@class='_delivery']/div[contains(@class, 'item')]",
            'txbName': ".//div[contains(@class, 'title')]",
            'txbPrice': ".//div[contains(@class, 'price')]/span[last()]",
            'txbPriceOld': ".//div[contains(@class, 'price')]/span[@id='old']",
        }

        def __init__(self, browser: webdriver):
            self._browser = browser

            self.deliveries = []

            div_deliveries = self._browser.find_elements_by_xpath(self.locators['divDeliveries'])
            for div_delivery in div_deliveries:
                html = etree.parse(StringIO(div_delivery.get_property('outerHTML')), parser=etree.HTMLParser())

                # Название метода
                name_element = BaseElement(self.locators['txbName'], context=div_delivery)

                # Стоимость доставки
                price = convert_price_from_str_to_float(html.xpath(self.locators['txbPrice'])[0].text)

                # Стоимость доставки без скидки
                try:
                    old_price = convert_price_from_str_to_float(html.xpath(self.locators['txbPriceOld'])[0].text)
                except IndexError:
                    old_price = None

                self.deliveries.append({
                    'name': name_element.text,  # название метода
                    'price': price,  # стоимость
                    'old_price': old_price,  # стоимость без скидки
                    'elements': {
                        'name': name_element  # элемент названия метода
                    }
                })

        def choose_by_name(self, delivery_name: str) -> None:
            """ Выбрать метод доставки по имени """

            # Определение id метода доставки по имени
            index = [item['name'] for item in self.deliveries].index(delivery_name)

            self.deliveries[index]['elements']['name'].click()
            FrontShopCartPage(is_wait=True)

        def is_in_cart_by_names(self, deliveries_name: list, mode: str = 'light') -> None:
            """ Проверка, есть ли в корзине переданные методы доставки
                - mode=light : в корзине есть товары deliveries_name
                - mode=hard : в корзине есть ТОЛЬКО товары deliveries_name """

            deliveries = [item['name'] for item in self.deliveries]
            result = list(set(deliveries_name) ^ set(deliveries))
            assert len(result) == 0, f"В корзине нет {result} метода/ов доставки"

            if mode != 'light':
                result = list(set(deliveries) - set(deliveries_name))
                assert len(result) == 0, f"В корзине есть дополнительные {result} метод/ы доставки"

        def get_property_by_name(self, delivery_name: str, property: str):
            """ Вернуть свойство метода по названию метода и названию метода доставки """

            return self.deliveries[self._get_index_by_name(delivery_name)][property]

        def _get_index_by_name(self, delivery_name: str) -> int:
            """ Определение id метода доставки по имени """

            return [item['name'] for item in self.deliveries].index(delivery_name)

    class Payments:
        locators = {
            'divPayments': "//div[@class='payment']/div[contains(@class, 'item')]",
            'txbName': ".//div[contains(@class, 'description')]",
            'txbDescription': ".//span[contains(@class, 'description')]",
            'txbPrice': ".//div[contains(@class, 'price')]",
        }

        def __init__(self, browser: webdriver):
            self._browser = browser

            self.payments = []

            div_payments = self._browser.find_elements_by_xpath(self.locators['divPayments'])
            for div_payment in div_payments:
                if not div_payment.is_displayed:
                    # Метод оплаты не отображается
                    continue

                html = etree.parse(StringIO(div_payment.get_property('outerHTML')), parser=etree.HTMLParser())

                # Описание
                try:
                    description = html.xpath(self.locators['txbDescription'])[0].text
                except IndexError:
                    description = None

                # Название метода
                name_element = BaseElement(self.locators['txbName'], context=div_payment)

                if description:
                    name = re.search(r"(.+)\n", name_element.text).group(1)
                else:
                    name = name_element.text

                # Комиссия
                price = html.xpath(self.locators['txbPrice'])[0].text

                if price:
                    price = convert_price_from_str_to_float(price)
                else:
                    price = None

                self.payments.append({
                    'name': name,  # название метода
                    'description': description,  # описание
                    'price': price,  # комиссия
                    'elements': {
                        'name': name_element  # элемент названия метода
                    }
                })

        def choose_by_name(self, payment_name: str) -> None:
            """ Выбрать метод оплаты по имени """

            self.payments[self._get_index_by_name(payment_name)]['elements']['name'].click()
            FrontShopCartPage(is_wait=True)

        def is_in_cart_by_names(self, payments_name: list, mode: str = 'light') -> None:
            """ Проверка, есть ли в корзине переданные методы оплаты
                - mode=light : в корзине есть товары payments_name
                - mode=hard : в корзине есть ТОЛЬКО товары payments_name """

            payments = [item['name'] for item in self.payments]
            result = list(set(payments_name) ^ set(payments))
            assert len(result) == 0, f"В корзине нет {result} метода/ов оплаты"

            if mode != 'light':
                result = list(set(payments) - set(payments_name))
                assert len(result) == 0, f"В корзине есть дополнительные {result} метод/ы оплаты"

        def get_property_by_name(self, payment_name: str, property: str):
            """ Вернуть свойство метода по названию метода и названию метода оплаты """

            return self.payments[self._get_index_by_name(payment_name)][property]

        def _get_index_by_name(self, payment_name: str) -> int:
            """ Определение id метода оплаты по имени """

            return [item['name'] for item in self.payments].index(payment_name)

    class Promocode:
        locators = {
            'txbLink': "//a",
            'inpField': "//input",
            'txbApply': "//a",
            'txbMessage': "//span",
            'txbError': "//span",
        }

        def __init__(self):
            self.errors = []

            self.is_applied = self.is_applied()
            self._error_check_message()

        def is_applied(self) -> bool:
            """ Проверяем, что промокод применен """

            try:
                BaseElement(self.locators['txbMessage'], 1)
                return True
            except AssertionError:
                return False

        def activate(self, promo_code: str) -> None:
            """ Активировать промокод """

            # Проверяем, что в корзине нет активированного промокода
            applied_promo_code = self.get_applied_name()
            assert not applied_promo_code, f"В корзине уже активирован промокод '{applied_promo_code}'"

            # Если отображается текст, активируем поле ввода промокода
            try:
                BaseElement(self.locators['txbLink'], 1).click()
            except AssertionError:
                pass

            # Вводим промокод
            BaseElement(self.locators['inpField']).set_text(promo_code)

            # Нажимаем применить промокод
            BaseElement(self.locators['txbApply']).click()

            FrontShopCartPage(is_wait=True)

        def get_applied_name(self) -> str:
            """ Получить имя примененного промокода """

            try:
                return BaseElement(self.locators['inpField'], 2, True).ge().get_attribute('value')
            except Exception:
                return ""

        def _error_check_message(self) -> None:
            """ Проверка промокода на наличие ошибок """

            try:
                message = BaseElement(self.locators['txbError'], 0).text
                if message == "Can not apply.":
                    self.errors.append(('promocode_cant_apply', True))
                elif message == "123":
                    self.errors.append(('promocode_not_exist', True))
                else:
                    self.errors.append(('promocode', message))
            except AssertionError:
                pass

    class Form:
        default_fields = [("Имя", "Test"), ("Фамилия", "Test"), ("Email", "test@test.com")]

        locators = {
            'inpField': "//input[@name='{value}']",
            'inpFieldRed': "//input[@name='{value} and contains(@class, 'error')]",
            'btnSubmit': "//button[@type='submit']",
            'txbErrors': "//div[@id='errors']/span",
        }

        def __init__(self, browser: webdriver):
            self._browser = browser

            self.errors = []

            self._error_check_under_form()
            self._error_form_fields_are_red()

        def fill_form(self, fields: list) -> None:
            """ Заполняем форму заказа
                fields: [(name, value), (name, value), ...] """

            names_without_check = []

            names = [field[0] for field in fields]

            for default_field in self.default_fields:
                if default_field[0] not in names:
                    fields.append(default_field)
                    names_without_check.append(default_field[0])

            for field in fields:
                try:
                    BaseElement(self.locators['inpField'].format(value=field[0]), 0).set_text(field[1])
                except AssertionError:
                    assert field[0] not in names_without_check, f"Не удалось найти поле '{field[0]}' в форме"

        def submit_form(self) -> bool:
            """ Оформляем заказ """

            FrontShopCartPage(is_wait=True)

            try:
                BaseElement(self.locators['btnSubmit'], 2).click()
                return True
            except ElementClickInterceptedException:
                return False

        def _error_form_fields_are_red(self, names: list = None) -> None:
            """ Незаполненные формы должны подсветиться красным """
            error_field_names = []

            if not names:
                names = [item[0] for item in self.default_fields]

            for name in names:
                try:
                    BaseElement(self.locators['inpFieldRed'].format(value=name), 0)
                except AssertionError:
                    error_field_names.append(name)

            if error_field_names:
                self.errors.append(('form_fields_not_red', error_field_names))

        def _error_check_under_form(self) -> None:
            """ Проверка формы на наличие ошибок """

            try:
                BaseElement(self.locators['txbErrors'], 0)

                errors = self._browser.find_elements_by_xpath(self.locators['txbErrors'])
                for error in errors:
                    if error.text == "Стоимость изенилась":
                        self.errors.append(('amount_price_change', True))
                    elif error.text == "Такой доставки нет":
                        self.errors.append(('delivery_method_unavailable', True))
                    elif error.text == "Такой платежки нет":
                        self.errors.append(('payment_method_unavailable', True))
                    else:
                        self.errors.append(('under_form', error.text))
            except AssertionError:
                pass

    class Prices:
        locators = {
            'txbTotalPrice': "//span[@id='total-price']",
            'txbTotalPriceOld': "//span[@id='old-price']",
            'txbAmountPrice': "//span[@id='amount-price')]",
            'txbAmountPriceOld': "//span[@id='old-amount-price')]",
        }

        def __init__(self):
            total_price = convert_price_from_str_to_float(BaseElement(self.locators['txbTotalPrice'], 3).text)

            try:
                total_price_old = convert_price_from_str_to_float(
                    BaseElement(self.locators['txbTotalPriceOld'], 0).text)
            except AssertionError:
                total_price_old = None

            amount_price = convert_price_from_str_to_float(BaseElement(self.locators['txbAmountPrice'], 3).text)

            try:
                amount_price_old = convert_price_from_str_to_float(
                    BaseElement(self.locators['txbAmountPriceOld'], 0).text)
            except AssertionError:
                amount_price_old = None

            self.prices = {
                'total_price': total_price,
                'total_price_old': total_price_old,
                'amount_price': amount_price,
                'amount_price_old': amount_price_old,
            }
