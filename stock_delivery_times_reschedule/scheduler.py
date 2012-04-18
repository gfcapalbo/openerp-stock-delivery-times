# -*- encoding: utf-8 -*-
################################################################################
#                                                                              #
#    stock_delivery_times_reschedule for OpenERP                              #
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
import netsvc
import tools
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pooler
from collections import defaultdict

class procurement_order(osv.osv):
    _inherit = "procurement.order"

    def _get_procurement_priority(self, cr, uid, ids, context=None):
        return 'priority, original_date_planned'

    def _reschedule_procurement(self, cr, uid, use_new_cursor=False, context=None):
        print "reschedule"
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        try:
            company_obj = self.pool.get('res.company')
            procurement_obj = self.pool.get('procurement.order')
            product_obj = self.pool.get('product.product')
            company_ids = company_obj.search(cr, uid, [], context=context)
            print "=====company ids===", company_ids
            for company in company_obj.browse(cr, uid, company_ids, context=context):
                maxdate = (datetime.today() + relativedelta(days=company.reschedule_range)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
                procurement_ids = procurement_obj.search(cr, uid, [['company_id', '=', company.id], ['not_enough_stock', '=', True], ['state', '=', 'exception'], ['date_planned', '<=', maxdate]])
                print 'procurement to recompute', procurement_ids
                date_to_product = defaultdict(list)
                product_and_date_to_qty = defaultdict(lambda : defaultdict(float))
                product_to_recompute = []
                for procurement in self.browse(cr, uid, procurement_ids, context=context):
                    product_id = procurement.product_id.id
                    date_to_product[procurement.date_planned].append(product_id)
                    product_and_date_to_qty[product_id][procurement.date_planned] += procurement.product_qty
                ctx = context.copy() #As the context will be use latter with the same function _product_available
                                     #it's better to not polluate the main context
                print date_to_product
                for date in date_to_product:
                    ctx.update({'to_date': date})
                    products_qty = product_obj._product_available(cr, uid, date_to_product[date], field_names=['virtual_available'], arg=False, context=ctx)
                    print products_qty, date
                    for product_id in products_qty:
                        print 'date, product_id, virtual_available', date, product_id, products_qty[product_id]['virtual_available']
                        #TODO fix me we should compare this qty with the qty of the procurement
                        if not product_id in product_to_recompute and products_qty[product_id]['virtual_available'] < product_and_date_to_qty[product_id][date]:
                            product_to_recompute.append(product_id)
                print 'recompute this product', product_to_recompute
                if product_to_recompute:
                    context['company_id'] = company.id
                    product_obj.reschedule_all_procurement(cr, uid, product_to_recompute, maxdate, context=context)

            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        ''' Runs through scheduler.
        @param use_new_cursor: False or the dbname
        '''
        super(procurement_order, self).run_scheduler(cr, uid, automatic=automatic, use_new_cursor=use_new_cursor, context=context)
        self._reschedule_procurement(cr, uid, use_new_cursor=use_new_cursor, context=context)
        return True
procurement_order()

