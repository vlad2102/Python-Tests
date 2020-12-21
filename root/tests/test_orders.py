import copy

import pytest

from root.site.api import ShopAPI
from root.site.page_objects import AdminShopOrdersPage, AdminShopOrderPage

""" Дефолтная информация о товарах """
_PRODUCTS: dict = {
    '1-1': {  # Название товара для тестов
        'id': 1011,
        'name': "Product 1",
        'vendorCode': "1011",
        'price': 0.63,
        'quantity': 1,
        'cost': 0.63,
        'costDiscounted': None,
    },
    '1-2': {
        'id': 1012,
        'name': "Product 1",
        'vendorCode': "1012",
        'price': 0,
        'quantity': 1,
        'cost': 0,
        'costDiscounted': None,
    },
    '1-3': {
        'id': 1013,
        'name': "Product 1",
        'vendorCode': "1013",
        'price': 19949.90,
        'quantity': 1,
        'cost': 19949.90,
        'costDiscounted': None,
    },
    '2-1': {
        'id': 1021,
        'name': "Product 2",
        'vendorCode': "1021",
        'price': 499.37,
        'quantity': 1,
        'cost': 499.37,
        'costDiscounted': None,
    },
    '2-2': {
        'id': 1022,
        'name': "Product 2",
        'vendorCode': "1022",
        'price': 101.01,
        'quantity': 1,
        'cost': 101.01,
        'costDiscounted': None,
    },
    '3': {
        'id': 1031,
        'name': "Product 3",
        'vendorCode': "1031",
        'price': 99.99,
        'quantity': 1,
        'cost': 99.99,
        'costDiscounted': None,
    },
    '4-1': {
        'id': 1041,
        'name': "Product 4",
        'vendorCode': "1041",
        'price': 1,
        'quantity': 1,
        'cost': 1,
        'costDiscounted': None,
    },
    '4-2': {
        'id': 1042,
        'name': "Product 4",
        'vendorCode': "1042",
        'price': 0.01,
        'quantity': 1,
        'cost': 0.01,
        'costDiscounted': None,
    },
    '5': {
        'id': 1051,
        'name': "Product 5",
        'vendorCode': "1051",
        'price': 0,
        'quantity': 1,
        'cost': 0,
        'costDiscounted': None,
    },
    '6': {
        'id': 1061,
        'name': "Product 6",
        'vendorCode': "1061",
        'price': 1,
        'quantity': 1,
        'cost': 1,
        'costDiscounted': None,
    },
    '7': {
        'id': 1071,
        'name': "Prodcut 7",
        'vendorCode': "1071",
        'price': 101.01,
        'quantity': 1,
        'cost': 101.01,
        'costDiscounted': None,
    },
    '8': {
        'id': 1081,
        'name': "Product 8",
        'vendorCode': "1081",
        'price': 10,
        'quantity': 1,
        'cost': 10,
        'costDiscounted': None,
    },
}


def _get_prepared_products_in_sets() -> list:
    """ Изменяем дефолтную информацию о товарах в зависимости от набора товаров """

    prepared_products = [copy.deepcopy(_PRODUCTS) for i in range(6)]

    prepared_products[1]['1-1'].update({'quantity': 12, 'cost': 7.56})

    prepared_products[2]['1-1'].update({'quantity': 2, 'cost': 1.26})
    prepared_products[2]['2-1'].update({'quantity': 2, 'cost': 998.74})

    prepared_products[3]['1-1'].update({'quantity': 6, 'cost': 3.78})
    prepared_products[3]['1-2'].update({'quantity': 2})
    prepared_products[3]['1-3'].update({'quantity': 4, 'cost': 79799.60})

    prepared_products[4]['1-1'].update({'quantity': 2, 'cost': 1.26})
    prepared_products[4]['2-1'].update({'quantity': 8, 'cost': 3994.96})
    prepared_products[4]['4-1'].update({'quantity': 999, 'cost': 999})

    prepared_products[5]['1-1'].update({'quantity': 7, 'cost': 4.41})
    prepared_products[5]['1-2'].update({'quantity': 1999})
    prepared_products[5]['2-2'].update({'quantity': 3, 'cost': 303.03})
    prepared_products[5]['4-2'].update({'quantity': 1949, 'cost': 19.49})
    prepared_products[5]['5'].update({'quantity': 11})
    prepared_products[5]['6'].update({'quantity': 24, 'cost': 24})

    return prepared_products


_prepared_products_sets = _get_prepared_products_in_sets()

""" Дефолтная информация о наборах товаров """
PRODUCTS_SET: dict = {
    '0': {  # Название набора товаров для тестов
        'names': ['1-1'],  # Название товаров с параметрами
        'products': _prepared_products_sets[0],
    },
    '1': {
        'names': ['1-1'],
        'products': _prepared_products_sets[1],
    },
    '2': {
        'names': ['1-1', '2-1'],
        'products': _prepared_products_sets[2],
    },
    '3': {
        'names': ['1-1', '1-2', '1-3'],
        'products': _prepared_products_sets[3],
    },
    '4': {
        'names': ['1-1', '2-1', '3', '4-1'],
        'products': _prepared_products_sets[4],
    },
    '5': {
        'names': ['1-1', '1-2', '2-1', '2-2', '3', '4-2', '5', '6', '7', '8'],
        'products': _prepared_products_sets[5],
    },
}

""" Дефолтная информация о методах доставки """
DELIVERIES: dict = {
    '1': {  # Название метода доставки
        'id': 101,
        'name': "Доставка 1",
        'price': 0,
        'priceDiscounted': None,
    },
    '2': {
        'id': 102,
        'name': "Доставка 2",
        'price': 0,
        'priceDiscounted': None,
    },
    '3': {
        'id': 103,
        'name': "Доставка 3",
        'price': 0,
        'priceDiscounted': None,
    },
    '4': {
        'id': 104,
        'name': "Доставка 4",
        'price': 0,
        'priceDiscounted': None,
    },
    '5': {
        'id': 105,
        'name': "Доставка 5",
        'price': 0,
        'priceDiscounted': None,
    },
    '6': {
        'id': 106,
        'name': "Доставка 6",
        'price': 0,
        'priceDiscounted': None,
    },
    '7': {
        'id': 107,
        'name': "Доставка 7",
        'price': 0,
        'priceDiscounted': None,
    },
    '8': {
        'id': 108,
        'name': "Доставка 8",
        'price': 0,
        'priceDiscounted': None,
    },
}

""" Дефолтная информация о методах оплаты """
PAYMENTS: dict = {
    '1': {  # Название метода оплаты
        'id': 201,
        'name': "Мой вид оплаты 1",
        'price': None,
    },
    '2': {
        'id': 202,
        'name': "Мой вид оплаты 2",
        'price': None,
    },
}

""" Дефолтная информация для полей в форме заказа в корзине """
FIELDS: dict = {
    303: {  # Номер поля в форме заказа
        'id': 303,
        'value': "mat@ga.com",
    },
}


class TestsNew:

    @staticmethod
    def base_test(data: dict):
        shop_api = ShopAPI("http://site.loc")
        shop_api.add_skus_to_cart([item['id'] for item in data['products']])
        shop_api.set_quantity_by_sku(
            [(item['id'], item['quantity']) for item in data['products'] if item['quantity'] > 1])

        shop_api.check_cart(
            values={
                'delivery': data['delivery']['id'],
                'payment': data['payment']['id'] if data['payment'] else "",
                'promocode': data['promocode']['code'],
            },
            check_data=data,
        )

        shop_api.create_order(
            values={
                'delivery': data['delivery']['id'],
                'payment': data['payment']['id'] if data['payment'] else "",
                'promocode': data['promocode']['code'],
            },
            fields=[(item['id'], item['value']) for item in data['fields']],
        )

        AdminShopOrdersPage().open_last_order()

        products = []
        for item in data['products']:
            products.append({
                'name': f"{item['name']}|{item['vendorCode']}",
                'price_per_product': item['price'],
                'quantity': item['quantity'],
                'price_amount': item['cost'],
            })

        AdminShopOrderPage().check({
            'type': "Заказ",
            'delivery': data['delivery']['name'],
            'payment': data['payment']['name'] if data['payment'] else "Нет",
            'promocode': data['promocode']['code'] if data['promocode']['success'] else "Нет",
            'form': [item['value'] for item in data['fields']],
            'products': products,
            'delivery_tax':
                data['delivery']['priceDiscounted'] if data['delivery']['priceDiscounted'] is not None else
                data['delivery']['price'],
            'discount': data['discount'],
            'markup': data['payment']['price'] if data['payment'] and data['payment']['price'] is not None else 0,
            'total_amount':
                data['general']['priceDiscounted'] if data['general']['priceDiscounted'] is not None else
                data['general']['price'],
        })

    def test_1(self):
        products = copy.deepcopy(PRODUCTS_SET['0']['products'])

        delivery = copy.deepcopy(DELIVERIES['4'])

        fields = copy.deepcopy(FIELDS)
        fields[303].update({'value': "test_1@tail.poc"})

        data = {
            'products': [products[name] for name in PRODUCTS_SET['0']['names']],
            'delivery': delivery,
            'payment': None,
            'fields': [fields[303]],
            'promocode': {
                'code': "1",
                'success': True,
            },
            'general': {
                'price': 0.63,
                'priceDiscounted': 0,
            },
            'discount': 0.63,
        }

        self.base_test(data)

    def test_2(self):
        products = copy.deepcopy(PRODUCTS_SET['0']['products'])

        delivery = copy.deepcopy(DELIVERIES['3'])

        payment = copy.deepcopy(PAYMENTS['1'])

        fields = copy.deepcopy(FIELDS)
        fields[303].update({'value': "test_2@tail.poc"})

        data = {
            'products': [products[name] for name in PRODUCTS_SET['0']['names']],
            'delivery': delivery,
            'payment': payment,
            'fields': [fields[303]],
            'promocode': {
                'code': "2",
                'success': False,
            },
            'general': {
                'price': 0.63,
                'priceDiscounted': None,
            },
            'discount': 0,
        }

        self.base_test(data)
