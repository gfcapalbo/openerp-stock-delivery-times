# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    stock_delivery_delays_working_days for OpenERP                                          #
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

class purchase_order_line(osv.osv):

    _inherit = 'purchase.order.line'
    
    _columns = {
    }

    _defaults = {
    }

    def _get_date_planned(self, cr, uid, seller, start_date, context=None):
        """Return the datetime value to use as Schedule Date (``date_planned``) for the
           Purchase Order Lines created in the purchase order considering the working time.

           :param int seller_delay: the delivery delay of the supplier of the product.
           :rtype: datetime
           :return: the desired Schedule Date for the PO lines
        """
        if seller:
            seller_delay = seller.delay
        else:
            seller_delay = 0
        start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        date_planned = self.pool.get('resource.calendar')._get_date(cr, uid, None, start_date, seller_delay, context=context)
        return date_planned

class procurement_order(osv.osv):

    _inherit = 'procurement.order'

    _columns = {
    }

    _defaults = {
    }

    def _get_schedule_date(self, cr, uid, procurement, company, context=None): 
        '''This method overload the method _get_schedule_date in order to have a good calculation of the date'''
        delay = -procurement.sale_order_line_id.product_id.sale_delay
        date_planned = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = self.pool.get('resource.calendar')._get_date(cr, uid, None, date_planned, delay, context=context)
        schedule_date = (schedule_date - relativedelta(days=company.po_lead))
        return schedule_date

    def _get_order_dates(self, cr, uid, schedule_date, seller_delay, context=None):
        '''This method overload the method _get_order_dates in order to have a good calculation of the date'''
        delay = -seller_delay
        order_dates = self.pool.get('resource.calendar')._get_date(cr, uid, None, schedule_date, delay, context=context)
        return order_dates

procurement_order()
