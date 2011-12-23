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

class stock_picking(osv.osv):

    _inherit = "stock.picking"

    def _get_delivery_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for picking_id in ids:
            picking = self.browse(cr, uid, picking_id, context=context)
            res[picking_id] = self.pool.get('resource.calendar')._get_date(cr, uid, picking.carrier_id.calendar_id.id, picking.max_date.split()[0], picking.carrier_id.delivery_lead_time, context=context)
        return res

    _columns = {
        'delivery_date': fields.function(_get_delivery_date, string='Delivery Date', help="Date of delivery to the customer"), #TODO store=True
    }

    _defautls = {
    }



stock_picking()
