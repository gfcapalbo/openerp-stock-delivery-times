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

class stock_picking(osv.osv):

    _inherit = "stock.picking"
    
    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_picking, self).get_min_max_date(cr, uid, ids, field_name, arg, context=context)
        for picking in self.browse(cr, uid, ids, context=context):
            delivery_date = False
            if picking.carrier_id and res[picking.id]['max_date']:
                start_date = datetime.strptime(res[picking.id]['max_date'], DEFAULT_SERVER_DATETIME_FORMAT)
                delivery_date = (self.pool.get('resource.calendar')._get_date(cr, uid, picking.carrier_id.calendar_id.id, start_date, picking.carrier_id.delivery_lead_time, context=context)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            elif not picking.carrier_id and res[picking.id]['max_date']:
                delivery_date = res[picking.id]['max_date']
            if delivery_date:            
                #path to fix fields.function bug indeed with a multi field the value is not updated 
                #https://bugs.launchpad.net/openobject-server/+bug/912189
                cr.execute('update stock_picking set delivery_date = %s where id=%s', (delivery_date, picking.id))
        return res

    def _set_maximum_date(self, cr, uid, ids, name, value, arg, context=None):
        return super(stock_picking, self)._set_maximum_date(cr, uid, ids, name, value, arg, context=context)

    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        return super(stock_picking, self)._set_minimum_date(cr, uid, ids, name, value, arg, context=context)

    def _get_picking_from_delivery_carrier(self, cr, uid, ids, context=None):
        res = self.pool.get('stock.picking').search(cr, uid, [('carrier_id', '=', ids[0]), ('state', '!=', 'done')], context=context)
        return res

    def _get_delivery_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            if not picking.max_date:
                res[picking.id] = False
            elif not picking.carrier_id:
                res[picking.id] = picking.max_date
            else:
                start_date = datetime.strptime(picking.max_date, DEFAULT_SERVER_DATETIME_FORMAT)
                res[picking.id] = (self.pool.get('resource.calendar')._get_date(cr, uid, picking.carrier_id.calendar_id.id, start_date, picking.carrier_id.delivery_lead_time, context=context)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return res

    _columns = {
        'delivery_date': fields.function(_get_delivery_date, string='Delivery Date', type="datetime", help="Date of delivery to the customer", 
                                            store= {
                                'delivery.carrier':(_get_picking_from_delivery_carrier, ['delivery_lead_time'], 10),
                                'stock.picking':(lambda self, cr, uid, ids, c=None: ids, ['carrier_id','max_date'], 10),

        }
        ),
        'min_date': fields.function(get_min_max_date, fnct_inv=_set_minimum_date, multi="min_max_date",
                 store=True, type='datetime', string='Expected Date', select=1, help="Expected date for the picking to be processed"),
        'max_date': fields.function(get_min_max_date, fnct_inv=_set_maximum_date, multi="min_max_date",
                 store=True, type='datetime', string='Max. Expected Date', select=2),
    }

    _defautls = {
    }


