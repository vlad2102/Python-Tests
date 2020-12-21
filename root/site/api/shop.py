import re
from typing import List, Tuple

import requests
import json

from root.core import BaseAPI
from root.site.page_objects.front.shop.cart_page import convert_price_from_str_to_float


def _get_items_id_from_list_of_items(items: list) -> list:
    return [item['id'] for item in items]


def _check_products_in_cart(products_in_response: list, products_for_check: list) -> None:
    """ Проверка продуктов в корзине """

    products_id_in_response: list = _get_items_id_from_list_of_items(products_in_response)
    products_id_for_check: list = _get_items_id_from_list_of_items(products_for_check)

    # Находим товары которые есть в одном списке, но нет в другом
    products_difference: list = list(set(products_id_for_check) ^ set(products_id_in_response))
    assert len(products_difference) == 0, f"В корзине нет '{products_difference}' товара/ов"

    def __get_product_index_by_id(product_id: int) -> int:
        return products_id_in_response.index(product_id)

    for product_for_check in products_for_check:
        product_in_response: dict = products_in_response[__get_product_index_by_id(product_for_check['id'])]
        for key in product_for_check:
            if key in ['price', 'cost', 'costDiscounted'] and product_in_response[key]:
                # В продукте из response переводим цены из str в float
                product_in_response[key]: float = convert_price_from_str_to_float(product_in_response[key])

            if key in product_in_response:
                assert product_for_check[key] == product_in_response[key], \
                    f"Неправильное значение '{key}' у sku '{product_for_check['id']}': '{product_in_response[key]}'. " \
                    f"Ожидалось: '{product_for_check[key]}'"
            else:
                raise Exception(f"Для проверки sku '{product_for_check['id']}' введен неизвестный параметр '{key}'")


def _check_delivery_in_cart(deliveries_in_response: list, delivery_for_check: dict) -> None:
    """ Проверка метода достовки в корзине """

    delivery_for_check['selected'] = True

    deliveries_id_in_response: list = _get_items_id_from_list_of_items(deliveries_in_response)
    assert delivery_for_check['id'] in deliveries_id_in_response, \
        f"В корзине нет метода доставки '{delivery_for_check['id']}'"

    delivery_index_in_response: int = deliveries_id_in_response.index(delivery_for_check['id'])

    for key in delivery_for_check:
        delivery_in_response: dict = deliveries_in_response[delivery_index_in_response]
        if key in ['price', 'priceDiscounted'] and delivery_in_response[key]:
            # В доставке из response переводим цены из str в float
            delivery_in_response[key]: float = convert_price_from_str_to_float(delivery_in_response[key])

        if key in delivery_in_response:
            assert delivery_for_check[key] == delivery_in_response[key], \
                f"Неправильное значение '{key}' " \
                f"у метода доставки '{delivery_for_check['id']}': '{delivery_in_response[key]}'. " \
                f"Ожидалось: '{delivery_for_check[key]}'"
        else:
            raise Exception(f"Для проверки метода оплаты '{delivery_for_check['id']}' "
                            f"введен неизвестный параметр '{key}'")


def _check_general_inf_in_cart(general_inf_in_response: dict, general_inf_for_check: dict) -> None:
    """ Проверка общей информации в корзине """

    for key in general_inf_for_check:
        if key in ['price', 'priceDiscounted'] and (
                general_inf_in_response[key] or general_inf_in_response[key] == 0):
            # Общие цены в response переводим из str в float
            general_inf_in_response[key] = convert_price_from_str_to_float(general_inf_in_response[key])

        assert general_inf_in_response[key] == general_inf_for_check[key], \
            f"Неправильное значение '{key}' в general: '{general_inf_in_response[key]}'. " \
            f"Ожидалось: '{general_inf_for_check[key]}'"


class ShopAPI(BaseAPI):
    def __init__(self,
                 shop_url: str,
                 ):

        super().__init__()
        self.shop_url = shop_url

    def get_cart_hash_from_cookies(self) -> str:
        cookie_cart_hash = self.get_cookie('cart')
        cart_hash = re.search(r"cart(.*)", cookie_cart_hash).group(0)

        return cart_hash

    @staticmethod
    def __basic_checks_of_response(response: requests.Response, extended_checks: dict = None) -> None:

        """ Базовые проверки ответа сервера """
        assert response.status_code == 200, f"'response.status_code': '{response.status_code}', ожидалось: '200'"
        assert len(response.text) > 0, f"Длина 'response.text' ожидалась > 0"

        response_value = json.loads(response.text)

        """ Расширенные проверки """
        for check in extended_checks:
            assert response_value[check] == extended_checks[check], \
                f"Неправильное значение '{check}' в response: '{response_value[check]}'. " \
                f"Ожидалось: '{extended_checks[check]}'"

    @staticmethod
    def __prepare_request_values(request_values: dict) -> dict:
        request_values_default = {
            'delivery': None,
            'payment': None,
            'promocode': None,
        }

        request_values, request_values_default = request_values_default, request_values
        request_values.update(request_values_default)

        request_data = {
            'deliveryMethodId': request_values['delivery'],
            'paymentMethodId': request_values['payment'],
            'promocode': request_values['promocode'],
        }

        return request_data

    def add_skus_to_cart(self,
                         skus: List[int],
                         ) -> None:
        """ Добавление товаров в корзину """

        first_level_checks_of_response = {
            'status': "success",
            'count': 0,
        }

        for sku in skus:
            response = self.session.get(f"{self.shop_url}/cart/{sku}/add")

            first_level_checks_of_response['count'] += 1
            self.__basic_checks_of_response(response, first_level_checks_of_response)

    def set_quantities_by_sku_in_cart(self,
                                      values: List[Tuple[int, int]],  # [(sku, quantity), (sku, quantity), ]
                                      ) -> None:
        """ Задать количество указанным товарам """

        first_level_checks_of_response = {
            'status': 200,
            'ok': True,
            'statusText': "ok",
            'data': None,
            'message': None,
        }

        for (sku, quantity) in values:
            response = self.session.put(
                url=f"{self.shop_url}/api/cart/{sku}",
                data={
                    'quantity': quantity,
                },
            )

            self.__basic_checks_of_response(response, first_level_checks_of_response)

    def check_cart(self,
                   request_values: dict,
                   check_data: dict,
                   ) -> None:
        """ Проверить корзину на валидность """

        first_level_checks_of_response = {
            'status': 200,
            'ok': True,
            'statusText': "ok",
        }

        request_data = self.__prepare_request_values(request_values)

        response = self.session.put(
            url=f"{self.shop_url}/api/check",
            data=request_data,
        )

        self.__basic_checks_of_response(response, first_level_checks_of_response)

        response_value = json.loads(response.text)

        if check_data['products']:
            _check_products_in_cart(products_in_response=response_value['data']['cart']['products'],
                                    products_for_check=check_data['products'])

        if check_data['delivery']:
            _check_delivery_in_cart(deliveries_in_response=response_value['data']['deliveryMethods'],
                                    delivery_for_check=check_data['delivery'])

        if check_data['general']:
            _check_general_inf_in_cart(
                general_inf_in_response={
                    'price': response_value['data']['price'],
                    'priceDiscounted': response_value['data']['priceDiscounted'],
                },
                general_inf_for_check=check_data['general'])

    def create_order(self,
                     values: dict,
                     fields: list,
                     ) -> None:

        first_level_checks_of_response = {
            'status': 200,
            'ok': True,
            'statusText': "ok",
            'data': None,
        }

        request_data = self.__prepare_request_values(values)

        for (field_id, field_value) in fields:
            request_data[f"fields[{field_id}]"] = field_value

        response = self.session.post(
            url=f"{self.shop_url}/api/check",
            data=request_data,
        )

        self.__basic_checks_of_response(response, first_level_checks_of_response)

        response_value = json.loads(response.text)

        assert f"{self.shop_url}/success" in response_value['message'], \
            f"При оформлении заказа значение 'message': {response_value['message']}. " \
            f"Ожидалось '/success'"
