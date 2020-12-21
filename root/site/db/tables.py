from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import Table, MetaData

from root.site.db import get_engine

_Base = declarative_base()
_metadata = MetaData(bind=get_engine('main'))


class Cart(_Base):
    __table__ = Table('table_1', _metadata, autoload=True)


class CartSku(_Base):
    __table__ = Table('table_2', _metadata,
                      Column('cart_id', primary_key=True),
                      Column('product_sku_id', primary_key=True),
                      extend_existing=True, autoload=True)


class Product(_Base):
    __table__ = Table('table_3', _metadata,
                      Column('title', default=""),
                      Column('description', default=""),
                      extend_existing=True, autoload=True)


class ProductSku(_Base):
    __table__ = Table('table_4', _metadata,
                      Column('params', default=""),
                      Column('url', default=""),
                      extend_existing=True, autoload=True)


class Settings(_Base):
    __table__ = Table('table_5', _metadata,
                      Column('shop_id', primary_key=True),
                      Column('key', primary_key=True),
                      extend_existing=True, autoload=True)

    default_values: dict = {
        'mail': "{'test': True}",
        'product': "{'test': True}",
        'shop': "{'test': True}",
    }


class Shop(_Base):
    __table__ = Table('table_6', _metadata, autoload=True)


def clear_tables(session: Session) -> None:
    def _set_default_values_in_settings_table() -> None:
        for key, value in Settings.default_values.items():
            session.query(Settings).filter(Settings.shop_id == shop_id, Settings.key == key). \
                update({'value': value})

    not_clear_this_tables = [
        'message',
    ]

    shop_id = session.query(Shop).first().id
    shop_tables = _metadata.sorted_tables
    tables_for_cleaning = [table for table in shop_tables if table.name not in not_clear_this_tables]

    for table in reversed(tables_for_cleaning):
        session.execute(table.delete())

    _set_default_values_in_settings_table()
