# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    delivery_delays for OpenERP                                          #
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

class product_template(osv.osv):

    _inherit = "product.template"
    
    _columns = {
        'sale_delay': fields.float('Shipping Time', help="This is the average delay in days between the confirmation of the customer order and the delivery of the finished products to the carrier. By adding the carrier delivery lead time to this delay, you obtain the delivery time to the customer."),
    }
