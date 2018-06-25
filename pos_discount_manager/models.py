# _*_ coding:utf-8 _*_

from odoo import models, fields


class DisableDiscount(models.Model):
    _inherit = 'pos.config'

    disable_discount = fields.Boolean(string='Disable Discounts in POS')
