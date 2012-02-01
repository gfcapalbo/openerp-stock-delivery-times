# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    stock_delivery_delays_manager for OpenERP                                          #
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
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class stock_picking(osv.osv):

    
    _inherit = "stock.picking"
    
    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_picking, self).get_min_max_date(cr, uid, ids, field_name, arg, context=context)
        for picking in self.browse(cr, uid, ids, context=context):
            if res[picking.id]['max_date'] and picking.original_date:
                date_max = datetime.strptime(res[picking.id]['max_date'], DEFAULT_SERVER_DATETIME_FORMAT)
                date_ori = datetime.strptime(picking.original_date, DEFAULT_SERVER_DATETIME_FORMAT)
                interval = int((date_max - date_ori).days)
                res[picking.id]['diff_days'] = interval
        return res

    _columns = {
        'original_date': fields.datetime('Original Expected Date', help= "Expected date planned at the creation of the picking, it doesn't change if the expected date change"),
        'diff_days':fields.function(get_min_max_date, string='Interval Days', type="integer", store=True, multi="min_max_date", help= "Days between the original expected date and the max expected date"),
        'to_order':fields.boolean('To Order')
    }

    _defaults = {
    }

    def action_confirm(self, cr, uid, ids, context=None):
        '''This method add the original date at the creation of the picking, this date will not be modified after'''
        res = super(stock_picking, self).action_confirm(cr, uid, ids, context=context)
        for picking in self.read(cr, uid, ids, ['min_date','original_date'], context=context):
            if not picking['original_date']:
                picking['original_date'] = picking['min_date']
                self.write(cr, uid, picking['id'], {'original_date' : picking['min_date']}, context=context)
        return res

    def run_to_order_scheduler(self, cr, uid, context=None):
        yesterday = (datetime.now()-timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        late_pickings = self.search(cr, uid, [('max_date', '<', yesterday),('state', '!=', 'done')], context=context)
        #TODO add parameter to choose when the picking is late 
        pickings_without_availability = []
        pickings_with_availability = []
        for late_picking in late_pickings:
            late_picking_info = self.browse(cr, uid, late_picking, context=context)
            picking_state = late_picking_info.to_order
            new_picking_state = False
            for line in late_picking_info.move_lines:
                if line.product_id.qty_available <= 0:
                    new_picking_state = True
                    break
            if picking_state != new_picking_state:
                if new_picking_state == True:
                    pickings_without_availability.append(late_picking)
                else: 
                    pickings_with_availability.append(late_picking)
        self.write(cr, uid, pickings_without_availability, {'to_order' : True}, context=context)
        self.write(cr, uid, pickings_with_availability, {'to_order' : False}, context=context)
        return True

stock_picking()

