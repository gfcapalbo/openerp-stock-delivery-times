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

class stock_picking(osv.osv):

    
    _inherit = "stock.picking"
    

    _columns = {
        'original_date': fields.datetime('Original Expected Date', help= "Expected date planned at the creation of the picking, it doesn't change if the expected date change"),
    }

    _defaults = {
    }

    def action_confirm(self, cr, uid, ids, context=None):
        '''This method add the original date at the creation of the picking, this date will not be modified after'''
        res = super(stock_picking, self).action_confirm(cr, uid, ids, context=context)
        for picking in self.read(cr, uid, ids, ['max_date','original_date'], context=context):
            if not picking['original_date']:
                picking['original_date'] = picking['max_date']
                self.write(cr, uid, picking['id'], {'original_date' : picking['max_date']}, context=context)
        return res

stock_picking()

