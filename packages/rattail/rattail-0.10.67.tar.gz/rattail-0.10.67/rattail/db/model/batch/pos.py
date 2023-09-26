# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Models for POS transaction batch
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.model import Base, BatchMixin, BatchRowMixin


class POSBatch(BatchMixin, Base):
    """
    Hopefully generic batch used for entering new purchases into the system, etc.?
    """
    batch_key = 'pos'
    __tablename__ = 'batch_pos'
    __batchrow_class__ = 'POSBatchRow'
    model_title = "POS Batch"
    model_title_plural = "POS Batches"

    @declared_attr
    def __table_args__(cls):
        return cls.__batch_table_args__() + (
            sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'],
                                    name=f'{cls.__tablename__}_fk_store'),
            sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'],
                                    name=f'{cls.__tablename__}_fk_customer'),
        )

    STATUS_OK                           = 1

    STATUS = {
        STATUS_OK                       : "ok",
    }

    store_id = sa.Column(sa.String(length=10), nullable=True, doc="""
    ID of the store where the transaction occurred.
    """)

    store_uuid = sa.Column(sa.String(length=32), nullable=True)
    store = orm.relationship(
        'Store',
        doc="""
        Reference to the store where the transaction ocurred.
        """)

    # terminal_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Terminal ID from which the transaction originated, if known.
    # """)

    # receipt_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Receipt number for the transaction, if known.
    # """)

    # cashier_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    # ID of the cashier who rang the transaction.
    # """)

    # cashier_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the cashier who rang the transaction.
    # """)

    start_time = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp when the transaction began.
    """)

    # customer_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    # ID of the customer account for the transaction.
    # """)

    # customer_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Number of the customer account for the transaction.
    # """)

    # customer_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the Customer account for the transaction.
    # """)

    customer_uuid = sa.Column(sa.String(length=32), nullable=True)
    customer = orm.relationship(
        'Customer',
        doc="""
        Reference to the customer account for the transaction.
        """)

    # shopper_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Number of the shopper account for the transaction, if applicable.
    # """)

    # shopper_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the shopper account for the transaction, if applicable.
    # """)

    # shopper_uuid = sa.Column(sa.String(length=32), nullable=True)
    # shopper = orm.relationship(
    #     'CustomerShopper',
    #     doc="""
    #     Reference to the shopper account for the transaction.
    #     """)

    sales_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Sales total for the transaction.
    """)

    tax1_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tax 1 total for the transaction.
    """)

    tax2_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tax 2 total for the transaction.
    """)

    void = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating if the transaction was voided.
    """)


class POSBatchRow(BatchRowMixin, Base):
    """
    Row of data within a POS batch.
    """
    __tablename__ = 'batch_pos_row'
    __batch_class__ = POSBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__batchrow_table_args__() + (
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name=f'{cls.__tablename__}_fk_item'),
        )

    STATUS_OK                           = 1

    STATUS = {
        STATUS_OK                       : "ok",
    }

    row_type = sa.Column(sa.String(length=32), nullable=True, doc="""
    Type of item represented by this row, e.g. "item" or "return" or
    "tender" etc.

    .. todo::
       need to figure out how to manage/track POSBatchRow.row_type
    """)

    item_entry = sa.Column(sa.String(length=32), nullable=True, doc="""
    Raw/original entry value for the item, if applicable.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)
    product = orm.relationship(
        'Product',
        doc="""
        Reference to the associated product, if applicable.
        """)

    description = sa.Column(sa.String(length=60), nullable=True, doc="""
    Description for the line item.
    """)

    quantity = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Quantity for the item.
    """)

    reg_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Regular price for the item.
    """)

    txn_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Actual price paid for the item.
    """)

    sales_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Sales total for the item.
    """)

    tax1_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tax 1 total for the item.
    """)

    tax2_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tax 2 total for the item.
    """)
