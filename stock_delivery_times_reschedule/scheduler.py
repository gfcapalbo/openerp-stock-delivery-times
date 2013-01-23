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
        if not context: context={}
        print "reschedule"
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        try:
            company_obj = self.pool.get('res.company')
            product_obj = self.pool.get('product.product')
            company_ids = company_obj.search(cr, uid, [], context=context)
            print "=====company ids===", company_ids
            for company in company_obj.browse(cr, uid, company_ids, context=context):
                maxdate = (datetime.today() + relativedelta(days=company.reschedule_range)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)

                product_ids_to_recompute = product_obj._get_product_ids_to_recompute(cr, uid, maxdate, company, context=context)
                print 'recompute this product', product_ids_to_recompute
                if product_ids_to_recompute:
                    context['company_id'] = company.id
                    product_obj.reschedule_all_procurement(cr, uid, product_ids_to_recompute, maxdate, context=context)

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

