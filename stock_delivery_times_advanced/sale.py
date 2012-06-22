# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    stock_delivery_times_working_days for OpenERP                                          #
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
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class sale_order_line(osv.osv):
    
    _inherit = "sale.order.line"
    

    _columns = {
        'supplier_shortage':fields.date('Supplier Shortage'),
    }

    _defaults = {
    }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
        uom=False, qty_uos=0, uos=False, name='', partner_id=False,
        lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None, order_lines=False):
        '''This method determine if there is enough stock for a sale order and calculate the corresponding delay''' 
        res= super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
        uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context=context)
        product_obj = self.pool.get('product.product')
        if order_lines != False and product:
            total_qty = 0
            for line_product in order_lines:
                if line_product[2] and line_product[2]['product_id'] == product:
                    total_qty += line_product[2]['product_uom_qty']
            total_qty = total_qty + qty
            info_product = product_obj.browse(cr, uid, product, context=context)
            delay, supplier_shortage = product_obj._get_delays(cr, uid, info_product, qty=total_qty, context=context)
            res['value']['delay'] = delay
            res['value']['supplier_shortage'] = supplier_shortage
        return res

sale_order_line()

class sale_order(osv.osv):
    
    _inherit = "sale.order"
    

    _columns = {
    }

    _defaults = {
    }

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        '''This method overload the method _get_date_planned and use the method get_date to consider the working days, and change the start date in function of the supplier_shortage'''
        if line.supplier_shortage:
            start_date = line.supplier_shortage
        return super(sale_order, self)._get_date_planned(cr, uid, order, line, start_date, context=context)

sale_order()

