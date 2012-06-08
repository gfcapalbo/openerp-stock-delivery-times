# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    stock_delivery_times_advanced for OpenERP                                          #
#    Copyright (C) 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc
import time
from datetime import date
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

class product_supplierinfo(osv.osv):
    
    _inherit = "product.supplierinfo"
    

    _columns = {
        'supplier_shortage': fields.date('Supplier Shortage'),

    }

    _defaults = {

    }

    def run_supplier_shortage_scheduler(self, cr, uid, context=None):
        '''Cron task to delete the supplier shortage attribute when the date has passed'''
        old_shortage_id = self.search(cr, uid, [('supplier_shortage', '<=', date.today())], context=context)
        self.write(cr, uid, old_shortage_id, {'supplier_shortage' : False}, context=context)
        return True

product_supplierinfo()

class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_delays(self, cr, uid, product, qty=1, context=None):
        '''Compute the delay information for a product'''
        supplier_shortage = False
        #TODO this should be parametable using immediately_usable_qty or virtual_qty think about it
        if (product.immediately_usable_qty - qty) >= 0: #TODO check is there is an incomming shipment for the product
            delay = product.sale_delay
        elif product.seller_info_id.supplier_shortage:
            #TODO use a different calendar for the supplier delay than the company calendar
            delay = product.sale_delay + (product.seller_info_id.delay or 0.0) 
            supplier_shortage = product.seller_info_id['supplier_shortage']
        else:
            delay = (product.seller_info_id.delay or 0.0) + product.sale_delay
        return delay, supplier_shortage







