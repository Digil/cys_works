# _*_ coding: UTF-8 _*_
from openerp import models, fields


class SaleLink(models.Model):
    _inherit = 'sale.order'

    project = fields.Char(string='Project', help='Project details')
    contract_no = fields.Char(string='Contract No')
    inh = fields.One2many('purchase.order', 'rel_sale_order')


class PurchaseLink(models.Model):
    _inherit = 'purchase.order'

    rel_sale_order = fields.Many2one('sale.order', string='Related Sales Order', required=True)
    contract_num = fields.Char(string='Contract number', related='rel_sale_order.contract_no')
