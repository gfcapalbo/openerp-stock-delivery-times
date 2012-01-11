# -*- encoding: utf-8 -*-
################################################################################
#                                                                              #
#    stock_delivery_delays_reschedule for OpenERP                              #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                              #
#    This program is free software: you can redistribute it and/or modify      #
#    it under the terms of the GNU Affero General Public License as            #
#    published by the Free Software Foundation, either version 3 of the        #
#    License, or (at your option) any later version.                           #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU Affero General Public License for more details.                       #
#                                                                              #
#    You should have received a copy of the GNU Affero General Public License  #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                              #
################################################################################

from osv import osv, fields
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from collections import defaultdict

class product_product(osv.osv):
    
    _inherit = "product.product"


    def get_incomming_qty(self, cr, uid, ids, product_to_procurement, company_id, context=None):
        """
        return a dictionnary of value that represent for each product the incomming stock planned by date
        """
        warehouse_obj = self.pool.get('stock.warehouse')
        move_obj = self.pool.get('stock.move')

        location_ids = []
        warehouse_ids = warehouse_obj.search(cr, uid, [['company_id', '=', company_id]], context=None)
        for warehouse in warehouse_obj.browse(cr, uid, warehouse_ids, context=context):
            location_ids.append(warehouse.lot_stock_id.id)

        incomming_move_ids = move_obj.search(cr, uid, [
                                ['state', 'in', ['wating', 'confirmed', 'assigned']],
                                ['location_id', 'not in', location_ids],
                                ['location_dest_id', 'in', location_ids],
                                ['product_id', 'in', ids]
                            ], context=context)

        #TODO it will be great to test this module using uom and uos to check if everything work correctly
        incomming_move = move_obj.read(cr, uid, incomming_move_ids, ['product_qty', 'product_id', 'date_expected'], context=context)

        product_to_qty_dict = defaultdict(lambda : defaultdict(float))
        for move in incomming_move:
            product_to_qty_dict[move['product_id'][0]][move['date_expected']] += move['product_qty']
        
        product_to_qty_list = {}
        for product_id in product_to_qty_dict:
            product_to_qty_list[product_id] = product_to_qty_dict[product_id].items()
            product_to_qty_list[product_id].sort()
        return product_to_qty_list


    def get_reschedule_date(self, cr, uid, ids, product_to_procurement, company_id, context=None):
        move_obj = self.pool.get('stock.move')
        product_qty_available = self._product_available(cr, uid, ids, field_names=['qty_available'], arg=False, context=context)
        for id in product_qty_available:
            product_qty_available[id] = product_qty_available[id]['qty_available']

        product_to_qty = self.get_incomming_qty(cr, uid, ids, product_to_procurement, company_id, context=context)

        procurement_ids = [procurement_id for product_id in product_to_procurement for procurement_id in product_to_procurement[product_id]]
        procurement_to_qty = {}
        for procurement in self.pool.get('procurement.order').read(cr, uid, procurement_ids, ['product_qty'], context=context):
            procurement_to_qty[procurement['id']] = procurement['product_qty']
        
        procurement_id_to_date = {}
        for id in ids:
            date, incomming_qty = product_to_qty[id].pop()
            qty_available = product_qty_available[id] + incomming_qty
            procurement_id = product_to_procurement[id].pop()
            qty_needed = procurement_to_qty[procurement_id]
            while True:
                if qty_available >= qty_needed:
                    procurement_id_to_date[procurement_id] = date
                    if not product_to_procurement[id]:
                        #there is not more procurement to compute for this product => let's do the next product
                        break
                    procurement_id = product_to_procurement[id].pop()
                    #attention le product_to_procurement peu etre vide
                    qty_needed += procurement_to_qty[procurement_id]
                else:
                    if not product_to_qty[id]:
                        #there is no more incomming product, the next procurement can not be re-scheduled
                        break
                    date, incomming_qty = product_to_qty[id].pop()
                    qty_available += incomming_qty

        return procurement_id_to_date

    def get_related_procurement(self, cr, uid, ids, maxdate, company_id, context=None):
        result = {}
        procurement_obj = self.pool.get('procurement.order')
        #TODO be carefull with the procurement order, maybe it will be great to add a field 'orignal date'
        procurement_ids = procurement_obj.search(cr, uid, [['company_id', '=', company_id], ['state', '=', 'exception'], ['date_planned', '<=', maxdate], ['product_id', 'in', ids]], context=context)
        for procurement in procurement_obj.read(cr, uid, procurement_ids, ['product_id'], context=context):
             if result.get(procurement['product_id']):
                result[procurement['product_id'][0]].append(procurement['id'])
             else:
                result[procurement['product_id'][0]] = [procurement['id']]
        return result


    def reschedule_all_procurement(self, cr, uid, ids, maxdate, context=None):
        if not context:
            context={}
        company_id = context.get('company_id')
        if not company_id:
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            company_id = user.company_id.id
        product_to_procurement = self.get_related_procurement(cr, uid, ids, maxdate, company_id, context=context)
        procurement_recomputed_date = self.get_reschedule_date(cr, uid, ids, product_to_procurement, company_id, context=context)
        procurement_obj = self.pool.get('procurement.order')
        for procurement_id in procurement_recomputed_date:
            ctx = context.copy()
            ctx['do_not_trigger'] = True
            procurement_obj.write(cr, uid, procurement_id, {'date_planned': procurement_recomputed_date[procurement_id]}, context=ctx)
        return True

product_product()
