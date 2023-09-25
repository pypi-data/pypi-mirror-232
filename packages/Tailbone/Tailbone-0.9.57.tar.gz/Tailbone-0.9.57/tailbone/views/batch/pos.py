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
Views for POS batches
"""

from rattail.db.model import POSBatch, POSBatchRow

from tailbone.views.batch import BatchMasterView


class POSBatchView(BatchMasterView):
    """
    Master view for POS batches
    """
    model_class = POSBatch
    model_row_class = POSBatchRow
    default_handler_spec = 'rattail.batch.pos:POSBatchHandler'
    route_prefix = 'batch.pos'
    url_prefix = '/batch/pos'
    creatable = False

    grid_columns = [
        'id',
        'customer',
        'created',
        'created_by',
        'rowcount',
        'sales_total',
        'void',
        'status_code',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'id',
        'customer',
        'params',
        'rowcount',
        'sales_total',
        'tax1_total',
        'tax2_total',
        'status_code',
        'created',
        'created_by',
        'executed',
        'executed_by',
    ]

    row_grid_columns = [
        'sequence',
        'row_type',
        'product',
        'description',
        'reg_price',
        'txn_price',
        'quantity',
        'sales_total',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'row_type',
        'item_entry',
        'product',
        'description',
        'reg_price',
        'txn_price',
        'quantity',
        'sales_total',
        'tax1_total',
        'tax2_total',
        'status_code',
    ]

    def configure_grid(self, g):
        super().configure_grid(g)

        g.set_link('customer')

        g.set_link('created')
        g.set_link('created_by')

        g.set_type('sales_total', 'currency')
        g.set_type('tax1_total', 'currency')
        g.set_type('tax2_total', 'currency')

    def grid_extra_class(self, batch, i):
        if batch.void:
            return 'warning'

    def configure_form(self, f):
        super().configure_form(f)

        f.set_renderer('customer', self.render_customer)

        f.set_type('sales_total', 'currency')
        f.set_type('tax1_total', 'currency')
        f.set_type('tax2_total', 'currency')

    def configure_row_grid(self, g):
        super().configure_row_grid(g)

        g.set_type('quantity', 'quantity')
        g.set_type('reg_price', 'currency')
        g.set_type('txn_price', 'currency')
        g.set_type('sales_total', 'currency')

        g.set_link('product')
        g.set_link('description')

    def configure_row_form(self, f):
        super().configure_row_form(f)

        f.set_type('quantity', 'quantity')
        f.set_type('reg_price', 'currency')
        f.set_type('txn_price', 'currency')
        f.set_type('sales_total', 'currency')
        f.set_renderer('product', self.render_product)


def defaults(config, **kwargs):
    base = globals()

    POSBatchView = kwargs.get('POSBatchView', base['POSBatchView'])
    POSBatchView.defaults(config)


def includeme(config):
    defaults(config)
