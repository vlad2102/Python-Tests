import re
from io import StringIO

from lxml import etree

from root.core import BaseElement
from root.site.page_objects import BaseAdminShopPage
from root.site.page_objects.front.shop.cart_page import convert_price_from_str_to_float


class AdminShopOrderPage(BaseAdminShopPage):
    page_locator = "//div[@class='order']"

    locators = {
        'locOrderData': "//div[@class='order']",
        'locOrderDataFields': ".//div",
        'btnOrderDataField': ".//button",
        'inpOrderDataFields': "./input",
        'locOrderTable': "//table[@class='order-table']/tbody",

        'inpDeliveryTax': "//input[@name='delivery_tax']",
        'inpDiscount': "//input[@name='discount']",
        'inpMarkup': "//input[@name='markup']",
        'txbTotalAmount': "//td[@id='total]",
    }

    def __init__(self):
        super().__init__()

        self.order = self._get_order()

    def _get_order(self) -> dict:
        order = {}

        div_order_data = BaseElement(self.locators['locOrderData'])
        html = etree.parse(StringIO(div_order_data.ge().get_property('outerHTML')), parser=etree.HTMLParser())
        div_fields = html.xpath(self.locators['locOrderDataFields'])

        temp = div_fields[0].text
        order['number'] = re.search(r"(\d{6})", temp).group(0)

        temp = div_fields[1].text
        order['date'] = re.search(r"Дата:\s*(.*)$", temp).group(1)

        temp = div_fields[2].text
        order['type'] = re.search(r"Тип:\s*(.*)$", temp).group(1)

        order['status'] = div_fields[3].xpath(self.locators['btnOrderDataField'])[0].attrib['title']
        order['delivery'] = div_fields[4].xpath(self.locators['btnOrderDataField'])[0].attrib['title']
        order['payment'] = div_fields[5].xpath(self.locators['btnOrderDataField'])[0].attrib['title']

        order['promocode'] = div_fields[-1].xpath(self.locators['btnOrderDataField'])[0].attrib['title']
        if len(order['promocode']) != 3:
            order['promocode'] = re.search(r"^(.*)\s-\s.*$", order['promocode']).group(1)

        order['form'] = []
        # for div_field in div_fields[6:-1]:
        #     order['form'].append(div_field.xpath(self.locators['inpOrderDataFields'])[0].attrib['value'])

        order['products'] = []
        order_table = BaseElement(self.locators['locOrderTable'])
        html = etree.parse(StringIO(order_table.ge().get_property('outerHTML')), parser=etree.HTMLParser())
        tr_elements = html.xpath(".//tr")[:-5]
        for tr_element in tr_elements:
            vendor_code = tr_element.xpath(".//span[@class='vendor-code']")[0].text
            order['products'].append({
                'name': tr_element.xpath(".//td[@class='sku']")[0].text + "|" + vendor_code,
                'price_per_product':
                    convert_price_from_str_to_float(tr_element.xpath(".//td[@class='sku-price']")[0].attrib['value']),
                'quantity': int(tr_element.xpath(".//td[@class='sku-quantit']")[0].attrib['value']),
                'price_amount': convert_price_from_str_to_float(tr_element.xpath(".//td[@class='total-cost']")[0].text),
            })

        order['delivery_tax'] = convert_price_from_str_to_float(
            html.xpath(self.locators['inpDeliveryTax'])[0].attrib['value'])
        order['discount'] = convert_price_from_str_to_float(html.xpath(self.locators['inpDiscount'])[0].attrib['value'])
        order['markup'] = convert_price_from_str_to_float(html.xpath(self.locators['inpMarkup'])[0].attrib['value'])
        order['total_amount'] = convert_price_from_str_to_float(html.xpath(self.locators['txbTotalAmount'])[0].text)

        return order

    def check(self, order: dict) -> None:
        for key in order.keys():
            if key == 'products':
                self._check_products(order[key])
            elif key in self.order.keys():
                assert order[key] == self.order[key], \
                    f"Неправильное старое значение заказа '{key}': '{self.order[key]}'. Ожидалось: '{order[key]}'"
            else:
                raise Exception(f"Для проверки заказа введен неизвестный параметр '{key}'")

    def _check_products(self, products: list) -> None:
        """ Проверка продуктов в заказе """

        self_products: dict = self.order['products']
        products_name = [item['name'] for item in products]
        self._is_products_in_order_by_names(products_name)

        for product in products:
            index = self._get_index_by_name(product['name'])
            for key in product.keys():
                if key in self_products[index].keys():
                    assert product[key] == self_products[index][key], \
                        f"Неправильное старое значение '{key}' для продукта '{product['name']}': '{product['key']}'. " \
                        f"Ожидалось: '{self_products[index][key]}'"
                else:
                    raise Exception(f"Для проверки продукта '{product['name']}' в заказе "
                                    f"введен неизвестный параметр '{key}'")

    def _is_products_in_order_by_names(self, products_name: list, mode: str = 'hard') -> None:
        """ Проверка, есть ли в заказе переданные товары
            - mode=light : в корзине есть товары products_name
            - mode=hard : в корзине есть ТОЛЬКО товары products_name """

        products = [item['name'] for item in self.order['products']]
        result = list(set(products_name) ^ set(products))
        assert len(result) == 0, f"В заказе нет {result} товара/ов"

        if mode == 'hard':
            result = list(set(products) - set(products_name))
            assert len(result) == 0, f"В заказе есть дополнительные {result} товар/ы"

    def _get_index_by_name(self, product_name: str) -> int:
        """ Получить индекс товара по его названию """

        return [item['name'] for item in self.order['products']].index(product_name)
