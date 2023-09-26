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
POS Batch Handler
"""

from sqlalchemy import orm

from rattail.batch import BatchHandler
from rattail.db.model import POSBatch


class POSBatchHandler(BatchHandler):
    """
    Handler for POS batches
    """
    batch_model_class = POSBatch

    # TODO: should also filter this by terminal
    def get_current_batch(self, user, create=True, **kwargs):
        """
        Get the "current" POS batch for the given user, creating it as
        needed.
        """
        if not user:
            raise ValueError("must specify a user")

        model = self.model
        session = self.app.get_session(user)

        try:
            batch = session.query(model.POSBatch)\
                           .filter(model.POSBatch.created_by == user)\
                           .filter(model.POSBatch.executed == None)\
                           .one()
        except orm.exc.NoResultFound:
            if not create:
                return
            batch = self.make_batch(session, created_by=user)
            session.add(batch)
            session.flush()

        return batch

    # TODO: this should account for shoppers somehow too
    def set_customer(self, batch, customer, **kwargs):
        """
        Assign the customer account for POS transaction.
        """
        batch.customer = customer

    def process_entry(self, batch, entry, quantity=1, **kwargs):
        """
        Process an "entry" value direct from POS.  Most typically,
        this is effectively "ringing up an item" and hence we add a
        row to the batch and return the row.
        """
        session = self.app.get_session(batch)

        product = self.app.get_products_handler().locate_product_for_entry(session, entry)
        if product:

            # product located, so add item row
            row = self.make_row()
            # row.row_type = 'product' # TODO
            row.row_type = 'sell' # TODO
            row.item_entry = entry
            row.product = product
            row.description = str(product)
            row.quantity = quantity

            regprice = product.regular_price
            if regprice:
                row.reg_price = regprice.price

            txnprice = product.current_price or product.regular_price
            if txnprice:
                row.txn_price = txnprice.price

            if row.txn_price:
                row.sales_total = row.txn_price * row.quantity
                batch.sales_total = (batch.sales_total or 0) + row.sales_total

            # # TODO
            # row.tax1_total = None
            # row.tax2_total = None

            self.add_row(batch, row)
            session.flush()
            return row

    def refresh_row(self, row):
        # TODO (?)
        row.status_code = row.STATUS_OK
        row.status_text = None

    def void_batch(self, batch, user, **kwargs):
        batch.void = True
        batch.executed = self.app.make_utc()
        batch.executed_by = user

    # TODO: this is just for testing, should surely change
    def tender_and_execute(self, batch, user, tender, **kwargs):
        session = self.app.get_session(batch)
        row = self.make_row()
        row.row_type = 'tender'
        row.description = tender
        if batch.sales_total is not None:
            row.sales_total = -batch.sales_total
        self.add_row(batch, row)
        session.flush()

        return self.do_execute(batch, user, **kwargs)

    def execute(self, batch, progress=None, **kwargs):
        # TODO
        return True
