# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class ShopOptiqueStockMove(models.Model):
    _inherit = 'module.prescription'


    picking_count = fields.Integer(string="Count", copy=False)
    invoice_picking_id = fields.Many2one('stock.picking', string="Picking Id", copy=False)

    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type',
                                      compute='_get_stock_type_ids',
                                      help="This will determine picking type of incoming shipment")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('posted', 'Posted'),
        ('post', 'Post'),
        ('cancel', 'Cancelled'),
        ('done', 'Received'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)


    #@api.depends('service_id')
    def _get_stock_type_ids(self):
        self.picking_type_id = False
        for line in self:
            if line.service_id:
                line.picking_type_id = self.env['stock.picking.type'].search([('code','=','outgoing'),('default_location_src_id','=',line.service_id.entrepot.id)]).id


    def _get_status(self):
        for exam in self:
            #data =
            if exam.internal_status == 'pret' and exam.invoice_picking_id.state =='done' :
                exam.write({'internal_status':'delivered'})
            exam.status = exam.internal_status

            return super(ShopOptiqueStockMove, self)._get_status()

    def action_stock_move(self):
        if not self.picking_type_id:
            raise UserError(_(
                " Please select a picking type"))
        for order in self:
            if not self.invoice_picking_id:
                pick = {}
                if self.picking_type_id.code == 'outgoing':
                    pick = {
                        'picking_type_id': self.picking_type_id.id,
                        'partner_id': self.patient_id.partner_id.id,
                        'origin': "Shop Optique",
                        'location_dest_id': self.patient_id.partner_id.property_stock_customer.id,
                        'location_id': self.picking_type_id.default_location_src_id.id,
                        'move_type': 'direct'
                    }

                if self.picking_type_id.code == 'incoming':
                    pick = {
                        'picking_type_id': self.picking_type_id.id,
                        'partner_id': self.patient_id.partner_id.id,
                        'origin':  "Shop Optique",
                        'location_dest_id': self.picking_type_id.default_location_dest_id.id,
                        'location_id': self.patient_id.partner_id.property_stock_supplier.id,
                        'move_type': 'direct'
                    }

                picking = self.env['stock.picking'].create(pick)
                self.invoice_picking_id = picking.id
                self.picking_count = len(picking)
                moves = order.invoice_prd_ids.filtered(
                    lambda r: r.is_print == True)._create_stock_moves(picking)
                move_ids = moves._action_confirm()
                move_ids._action_assign()

    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        result['domain'] = [('id', '=', self.invoice_picking_id.id)]
        pick_ids = sum([self.invoice_picking_id.id])
        if pick_ids:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids or False
        return result


class PrescriptionInvoiceLine(models.Model):
    _inherit = 'module.lunette.details'

    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            price_unit = line.price_unit
            if picking.picking_type_id.code == 'outgoing':
                template = {
                    'name': "Shop Optique",
                    'product_id': line.product.id,
                    'product_uom': line.product.uom_id.id,
                    'location_id': picking.picking_type_id.default_location_src_id.id,
                    'location_dest_id': line.lunette_id.patient_id.partner_id.property_stock_customer.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'company_id': line.lunette_id.move_id.company_id.id,
                    'price_unit': line.product.list_price,
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            if picking.picking_type_id.code == 'incoming':
                template = {
                    'name': "Shop Optique",
                    'product_id': line.product.id,
                    'product_uom': line.product.uom_id.id,
                    'location_id': line.lunette_id.patient_id.partner_id.property_stock_supplier.id,
                    'location_dest_id': picking.picking_type_id.default_location_dest_id.id,
                    'picking_id': picking.id,
                    'state': 'draft',
                    'company_id': line.lunette_id.move_id.company_id.id,
                    'price_unit': line.product.list_price,
                    'picking_type_id': picking.picking_type_id.id,
                    'route_ids': 1 and [
                        (6, 0, [x.id for x in self.env['stock.location.route'].search([('id', 'in', (2, 3))])])] or [],
                    'warehouse_id': picking.picking_type_id.warehouse_id.id,
                }
            diff_quantity = line.quantity
            tmp = template.copy()
            tmp.update({
                'product_uom_qty': diff_quantity,
            })
            template['product_uom_qty'] = diff_quantity
            done += moves.create(template)
        return done
