# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Ship(models.Model):
        _name = 'ship.ship'
        _rec_name = 'vessel_name'

        sql_constraints = [('imo_unique', 'unique(imo)', "IMO can't made duplicate")]
        imo = fields.Integer(string='IMO Number', required=True, select=1,
                             help='International Maritime Organization Number')
        hull_number = fields.Integer(string='Hull Number', help='Hull number of this ship')
        engine_number = fields.Integer(string="Engine Number", required=True)
        vessel_name = fields.Char(string='Vessel Name', required=True)
        build_year = fields.Date(string='Build Year', required=True)
        ship_yard = fields.Many2one('res.partner', string='Shipyard')
        ship_owner = fields.Many2one('res.partner', string='Ship Owner')
        ship_management = fields.Many2one('res.partner', string='Ship Management')
        engine_builder = fields.Many2one('res.partner', string='Engine Builder')


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'
    sale_ship = fields.Many2one('ship.ship', string="Ship", help='Ship that allot for this order..!')

    @api.one
    def update_order_lines(self):
        ship_order_line_obj = self.order_line
        for line in ship_order_line_obj:
            line.ship_line = self.sale_ship.id


class SaleOrderlineInherited(models.Model):
    _inherit = 'sale.order.line'
    ship_line = fields.Many2one('ship.ship', string="Ship")
