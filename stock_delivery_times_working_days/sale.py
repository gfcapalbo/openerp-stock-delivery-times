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

class sale_order(osv.osv):
    
    _inherit = "sale.order"
    

    _columns = {
    }

    _defaults = {
    }

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        '''This method overload the method _get_date_planned and use the method get_date to consider the working days'''
        start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        date_planned = self.pool.get('resource.calendar')._get_date(cr, uid, None, start_date, line.delay, context=context)
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        return date_planned  

sale_order()
