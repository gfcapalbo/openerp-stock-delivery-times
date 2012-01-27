# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    stock_delivery_delays_advanced for OpenERP                                          #
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
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class stock_change_date_line(osv.TransientModel):
    _name = "stock.change.date.line"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True, ondelete='CASCADE'),
        'supplier_shortage': fields.date('Supplier Shortage'),
        'date_expected': fields.datetime('Scheduled Date', required=True, ondelete='CASCADE'),
        'move_id' : fields.many2one('stock.move', "Move", ondelete='CASCADE'),
        'wizard_id' : fields.many2one('stock.change.date', string="Wizard", ondelete='CASCADE'),
        'new_date_expected': fields.datetime('New Schedule Date'),
    }

class stock_change_date(osv.osv_memory):
    _name = "stock.change.date"
    _description = "Change Stock Date Wizard"

    _columns = {
        'move_ids' : fields.one2many('stock.change.date.line', 'wizard_id', 'Product Moves'),
        'picking_id': fields.many2one('stock.picking', 'Picking', required=True, ondelete='CASCADE'),
    }

    _defaults = {
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_change_date, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        if not picking_ids or (not context.get('active_model') == 'stock.picking') \
            or len(picking_ids) != 1:
            # change date may only be done for one picking at a time
            return res
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            moves = [self._change_date_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done','cancel')]
            res.update(move_ids=moves)
        return res

    def _change_date_for(self, cr, uid, move):
        supplier_id = move.address_id.partner_id.id
        supplier = move.address_id.partner_id
        for seller in move.product_id.product_tmpl_id.seller_ids:
            if seller.name == move.address_id.partner_id:
                supplier_shortage = seller.supplier_shortage
        change_date = {
            'product_id' : move.product_id.id,
            'date_expected' : move.date_expected,
            'supplier_shortage' : supplier_shortage,
            'move_id' : move.id,
        }
        return change_date

    def do_change(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'change date may only be done one at a time'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        change = self.browse(cr, uid, ids[0], context=context)
        picking_type = change.picking_id.type
        change_data = {}
        for move in change.move_ids:
            move_id = move.move_id.id
            if move.new_date_expected:
                move_id = stock_move.write(cr,uid, move_id, {
                                                        'date_expected' : move.new_date_expected,
                                                        },context=context)
                change_data['move%s' % (move_id)] = {
                    'product_id': move.product_id.id,
                    'date_expected' : move.new_date_expected,
                    }

        #stock_picking.do_change(cr, uid, [move.picking_id.id], change_data, context=context)
        return {'type': 'ir.actions.act_window_close'}


stock_change_date()
