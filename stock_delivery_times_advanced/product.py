# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_advanced for OpenERP
#    Copyright (C) 2011-2014 Akretion
#    Author: Benoît Guillot <benoit.guillot@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp.osv import orm, fields
from datetime import date


class product_supplierinfo(orm.Model):
    _inherit = "product.supplierinfo"

    _columns = {
        'supplier_shortage': fields.date('Supplier Shortage'),
    }

    def run_supplier_shortage_scheduler(self, cr, uid, context=None):
        """Cron task to delete the supplier shortage attribute when the date
            has passed.
        """
        old_shortage_ids = self.search(
            cr, uid, [('supplier_shortage', '<=', date.today())],
            context=context)
        self.write(cr, uid, old_shortage_ids,
                   {'supplier_shortage': False},
                   context=context)
        return True
