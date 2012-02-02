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
from datetime import date
from datetime import timedelta, datetime
from tools.translate import _
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class stock_change_date_line(osv.TransientModel):
    _name = "stock.change.date.line"
    _rec_name = 'product_id'
    _columns = {
        'product_id' : fields.many2one('product.product', string="Product", required=True, readonly=True),
        'supplier_shortage': fields.date('Supplier Shortage'),
        'date_expected': fields.datetime('Scheduled Date', required=True, readonly=True),
        'move_id' : fields.many2one('stock.move', "Move"),
        'wizard_id' : fields.many2one('stock.change.date', string="Wizard"),
        'new_date_expected': fields.datetime('New Schedule Date'),
        'change_supplier_shortage':fields.boolean('Change Shortage'),
        'original_date_expected':fields.datetime('Original Scheduled Date', readonly=True),
    }

    def on_change_supplier_shortage(self, cr, uid, ids, supplier_shortage, context=None):
        return {'value' : {'change_supplier_shortage' : True}}


stock_change_date_line()

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
        change_date = {
            'product_id' : move.product_id.id,
            'date_expected' : move.date_expected,
            'supplier_shortage' : move.supplier_shortage,
            'original_date_expected': move.original_date_expected,
            'move_id' : move.id,
        }
        return change_date

    def do_change(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'change date may only be done one at a time'
        stock_picking = self.pool.get('stock.picking')
        stock_move = self.pool.get('stock.move')
        product_supplierinfo = self.pool.get('product.supplierinfo')
        change = self.browse(cr, uid, ids[0], context=context)
        picking_type = change.picking_id.type
        change_data = {}
        for move in change.move_ids:
            move_id = move.move_id.id
            if move.new_date_expected:
                move_id = stock_move.write(cr,uid, move_id, {
                                                        'date_expected' : move.new_date_expected,
                                                        },context=context)
            if move.change_supplier_shortage:
                supplierinfo_id = product_supplierinfo.search(cr, uid, [
                                                                    ('product_id', '=', move.product_id.id),
                                                                    ('name', '=', change.picking_id.partner_id.id)
                                                                    ], context=context)
                if not supplierinfo_id:
                    raise osv.except_osv(_('Error !'), _('You need to define a supplierinfo for this product !'))
                else:
                    supplierinfo = product_supplierinfo.browse(cr, uid, supplierinfo_id[0], context=context)
                    product_id = product_supplierinfo.write(cr, uid, supplierinfo_id, {
                                                                                'supplier_shortage': move.supplier_shortage,
                                                                                }, context=context)
                    start_date = datetime.strptime(move.supplier_shortage, DEFAULT_SERVER_DATE_FORMAT)
                    date_expected = self.pool.get('resource.calendar')._get_date(cr, uid, None, start_date, supplierinfo.delay, context=context)
                    move_lines = stock_move.search(cr, uid, [
                                                        ('product_id', '=', move.product_id.id),
                                                        ('date_expected', '<', date_expected.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                                        ('picking_id.original_date', '>', change.picking_id.original_date)
                                                        ], context=context)
                    if move_id not in move_lines:
                        move_lines.append(move_id)
                    stock_move.write(cr, uid, move_lines, {
                                                    'date_expected' : date_expected,
                                                    'supplier_shortage' : move.supplier_shortage,
                                                    }, context=context)

            change_data['move%s' % (move_id)] = {
                'product_id': move.product_id.id,
                'date_expected' : move.new_date_expected,
                }

        #stock_picking.do_change(cr, uid, [move.picking_id.id], change_data, context=context)
        return {'type': 'ir.actions.act_window_close'}


stock_change_date()
