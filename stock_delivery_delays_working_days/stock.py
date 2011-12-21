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

class resource_calendar(osv.osv):

    _inherit = "resource.calendar"

    _columns = {
    }

    _defautls = {
    }

    def _get_date(self, cr, uid, id, start_date, delay, resource=False, context=None):
        if not id:
            company_id = self.pool.get('res.users').get_current_company(cr, uid)[0][0]
            calendar_id = self.pool.get('res.company').read(cr, uid, company_id, ['calendar_id'], context=context)['calendar_id'][0]
            id = calendar_id
        dt_leave = self._get_leaves(cr, uid, id, resource)
        calendar_info = self.browse(cr, uid, id, context=context)
        worked_days = [day['dayofweek'] for day in calendar_info.attendance_ids]
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        while datetime.strftime(start_date, "%Y-%m-%d") in dt_leave or str(start_date.weekday()) not in worked_days:
            start_date = start_date + timedelta(days=1)
        date = start_date
        while delay:
            date = date + timedelta(days=1)
            if datetime.strftime(date, "%Y-%m-%d") not in dt_leave and str(date.weekday()) in worked_days:
                delay -= 1
        return date

resource_calendar()

class sale_order(osv.osv):
    
    _inherit = "sale.order"
    

    _columns = {
    }

    _defaults = {
    }

    def _get_date_planned(self, cr, uid, order, line, start_date, *args):
        date_planned = self.pool.get('resource.calendar')._get_date(cr, uid, None, start_date, line.delay)
        date_planned = (date_planned - timedelta(days=order.company_id.security_lead)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        return date_planned  

sale_order()

