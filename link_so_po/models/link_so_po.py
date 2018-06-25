# -*- coding: utf-8 -*-
from openerp import models, fields, api


class AddProject(models.Model):
    _inherit = 'sale.order'
    _description = 'Project and Contract Details '

    project = fields.Char(string='Project')
    contract_no = fields.Char(string='Contract No')
    purchase_orders = fields.One2many('purchase.order', 'ref_sale_order', string="Purchase orders", copy=True)
    sales_commissions = fields.One2many('sales.commission', 'orders_id', string="Sales Commission")
    state = fields.Selection([('draft', 'Draft Quotation'), ('to_check', 'To Check'), ('checked', 'Checked'),
                              ('approved', 'Approved'), ('manual', 'Sale Order'), ('progress', 'Sale Order'),
                              ('done', 'Done'), ('cancel', 'Cancelled')], string='Status',
                             readonly=True, copy=False, select=True)

    def action_check_order(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'to_check'}, context=context)

    def action_checked_order(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'checked'}, context=context)

    def action_approved_order(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'approved'}, context=context)

    def action_button_confirm(self,cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'manual'}, context=context)


class LinkSoPo(models.Model):
    _inherit = 'purchase.order'
    _description = 'Link sale and purchase order'

    ref_sale_order = fields.Many2one('sale.order', string='Related Sale Order', required=True)
    contracts_no = fields.Char(string='Contract No')
   
    def onchange_sale_order(self, cr, uid, ids, sale_id, context=None):
        value = {}
        contract_val = self.pool('sale.order').browse(cr, uid, sale_id,)
        contract_no = contract_val['contract_no']
        contract = {'contracts_no': contract_no}
        return {'value': contract}


class SalesmenCommission(models.Model):
    _name = 'sales.commission'
    _description = 'Salesmen commission'
    _order = 'orders_id desc '

    @api.depends('user')
    def get_total(self, cr, uid, ids, context=None):
        obj = {}
        for record in self.browse(cr, uid, ids, context=context):
            print 'total'
            new_item = self.pool.get('sale.order').browse(cr, uid, record.orders_id.id)
            record['sales_value'] = new_item .amount_total
        return obj

    @api.depends('percentage', 'sales_value')
    def get_commission(self, cr, uid, ids, context):
        obj = {}
        for record in self.browse(cr, uid, ids, context=context):
            print 'commission'
            record['commission'] = (record.sales_value * record.percentage) / 100
        return obj

    orders_id = fields.Many2one('sale.order', string='Sale order', required=True, ondelete='cascade', index=True)
    user = fields.Many2one('res.users', string='Users')
    sales_value = fields.Float(compute='get_total', string='Sales Value')
    percentage = fields.Float(string='percentage')
    commission = fields.Float(compute='get_commission', string='Commission')

