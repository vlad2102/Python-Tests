import re
import time
from io import StringIO

from lxml import etree

from root.core import BaseElement
from root.site.page_objects import BaseFrontPage
from root.site.page_objects.front.shop.cart_page import convert_price_from_str_to_float


class FrontShopProductPage(BaseFrontPage):
    page_locator = "//div[@id='product-page']"

    locators = {
        'btnAddToCart': "//a/span",
        'btnOutOfStock': "//a/span",
        'locDescription': "//article",
        'txtName': "//h1",
        'txtVendorCode': "//span",
        'txtPrice': "//span",
        'txtPriceDiscount': "//span",
        'locParams': "//div",
        'locParamId': ".//select",
        'elmParamById': "//select",
        'txtParamSelected': ".//span",
        'locParamValues': ".//div/div",
        'elmValueByIdAndParamId': "//div[@data-value='{}']",
        'btnQuantityMinus': "//span",
        'inpQuantity': "//input",
        'btnQuantityPlus': "//span",
        'btnAdd': "//button",
        'btnPreOrder': "//button",
        'locCount': "//span",
        'errSku': "//div"
    }

    def __init__(self):
        super().__init__()
        self.page = self._parse_page()

    def _parse_page(self) -> dict:
        """ Распарсить страницу товара """

        elements = {}

        # Определение контекста, для парсинга информации на странице
        div_description = BaseElement(self.locators['locDescription'])
        div_description_html = etree.parse(StringIO(div_description.ge().get_property('outerHTML')),
                                           parser=etree.HTMLParser())

        # Название товара
        name = div_description_html.xpath(self.locators['txtName'])[0].text.strip()

        # Артикул
        vendor_code = None

        temp = div_description_html.xpath(self.locators['txtVendorCode'])
        if temp[0].text is not None:
            temp = temp[0].text.strip()
            if temp:
                vendor_code = {
                    'text': re.sub(r"\s+", " ", temp),
                    'code': re.search(r":\s*(.*)$", temp).group(1).rstrip()
                }

        # Цена и цена от..
        price = None
        price_from = None

        temp = div_description_html.xpath(self.locators['txtPrice'])
        if temp[0].text is not None:
            if "от" in temp[0].text or (temp[0].getparent().text is not None and "от" in temp[0].getparent().text):
                price_from = convert_price_from_str_to_float(temp[0].text.replace("\xa0", " "))
            else:
                price = convert_price_from_str_to_float(temp[0].text)

        # Цена со скидкой
        price_discount = None

        temp = div_description_html.xpath(self.locators['txtPriceDiscount'])
        if len(temp):
            temp = temp[0].text
            if temp:
                price_discount = convert_price_from_str_to_float(temp)

        # Параметры
        params = None

        div_params = div_description_html.xpath(self.locators['locParams'])
        if len(div_params):
            params = []

            for div_param in div_params:
                # id параметра
                param_id = int(div_param.xpath(self.locators['locParamId'])[0].attrib['name'])

                # выбранное значнеие
                selected = div_param.xpath(self.locators['txtParamSelected'])[0].text

                # Значения
                values = []

                div_values = div_param.xpath(self.locators['locParamValues'])
                for div_value in div_values:
                    # Проверяем отображение значения параметра
                    try:
                        disabled = True if div_value.attrib['disabled'] else False
                    except KeyError:
                        disabled = False

                    values.append({
                        'id': int(div_value.attrib['data-value']),  # id значения
                        'name': div_value.text,  # имя значения
                        'disabled': disabled,  # отображается ли он
                    })
                params.append({
                    'id': param_id,  # id параметра
                    'selected': selected,  # выбранное значение
                    'values': values,  # словарь значений
                })

        # Поле с количеством
        quantity = None

        temp = div_description_html.xpath(self.locators['inpQuantity'])
        if len(temp):
            quantity = int(temp[0].attrib['value'])  # количество

            elements['quantity_minus'] = BaseElement(self.locators['btnQuantityMinus'])
            elements['quantity'] = BaseElement(self.locators['inpQuantity'])
            elements['quantity_plus'] = BaseElement(self.locators['btnQuantityPlus'])

        # Кнопка
        button = None

        temp = div_description_html.xpath(self.locators['btnAdd'] + "/span")
        if len(temp):
            button_text = temp[0].text.strip()

            if "Заказать" in button_text:
                button_type = 'preOrder'
            else:
                button_type = 'addToCard'

            button = {
                'text': button_text,  # текст внутри
                'type': button_type,  # тип
            }

            # Элемент кнопка
            elements['button'] = BaseElement(self.locators['btnAdd'])
        else:
            temp = div_description_html.xpath(self.locators['btnPreOrder'] + "/span")
            if len(temp):
                button = {
                    'text': temp[0].text.strip(),  # текст внутри
                    'type': 'preOrder',  # тип
                }

                # Элемент кнопка
                elements['button'] = BaseElement(self.locators['btnPreOrder'])

        # Количестве товара
        count = None

        temp = div_description_html.xpath(self.locators['locCount'])
        if len(temp):
            text = temp[0].xpath("string()").strip()
            if text:
                text = re.sub(r"\s+", " ", text)

                count = {
                    'text': text,  # текст сообщения
                    'number': int(div_description_html.xpath(self.locators['locCount'] + "/span")[0].text),
                }

        result = {
            'name': name,  # название товара
            'vendor_code': vendor_code,  # артикул
            'price': price,  # цена
            'price_from': price_from,  # цена от..
            'price_discount': price_discount,  # цена со скидкой
            'params': params,  # словарь параметров
            'quantity': quantity,  # количество
            'button': button,  # словарь кнопки
            'count': count,  # словарь количества товара в наличии
            'elements': elements  # словарь элементов
        }

        return result

    def check(self, **kwargs) -> None:
        """ Проверка страницы на наличие параметров """

        for key, value in kwargs.items():
            if key == "name":
                assert value == self.page[key], \
                    f"Неправильное название товара: '{self.page[key]}'. Ожидалось: '{value}'"
            elif key == "vendor_code":
                pass
            elif key == "price":
                assert value == self.page[key], \
                    f"Неправильная цена товара: '{self.page[key]}'. Ожидалось: '{value}'"
            elif key == "price_min":
                assert value == self.page[key], \
                    f"Неправильная минимальная цена товара: '{self.page[key]}'. Ожидалось: '{value}'"
            elif key == "price_discount":
                assert value == self.page[key], \
                    f"Неправильная цена со скидкой: '{self.page[key]}'. Ожидалось: '{value}'"
            elif key == "button":
                if value is None:
                    assert value is self.page[key], \
                        f"Проблема с кнопкой товара: '{self.page[key]}'. Ожидалось: '{value}'"
                else:
                    for button_param in value:
                        if button_param == "type":
                            assert value[button_param] == self.page[key][button_param], \
                                f"Проблема с типом кнопкой товара: '{self.page[key][button_param]}'. " \
                                f"Ожидалось: '{value[button_param]}'"
                        else:
                            raise Exception(f"Не смог понять параметр '{button_param}' у кнопки товара")
            elif key == "error":
                pass

    def click_on_button_add_to_cart(self) -> None:
        """ Нажать на кнопку 'Добавить в корзину' """

        BaseElement(self.locators['btnAddToCart']).click()
        time.sleep(2.5)
