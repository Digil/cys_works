# _*_ coding: UTF-8 _*_
from openerp import fields, models, api


class SaleCommission(models.Model):
    _inherit = 'sale.order'

    commission_tab = fields.One2many('related.commission', 'rel_comm_tab')

    state = fields.Selection([('draft', 'Draft Quotation'),
                              ('to_check', 'To Check'),
                              ('checked', 'Checked'),
                              ('approve', 'Approve'),
                              ('manual', 'Sale Order'),
                              ('progress', 'Sale Order'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')],  string='Status', readonly=True, select=True)

    def action_check_order(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'to_check'}, context=context)

    def action_checked(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'checked'}, context=context)

    def action_approved(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'approve'}, context=context)

    def action_button_confirm(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'manual'}, context=context)


class RelatedCommission(models.Model):
    _name = 'related.commission'

    rel_comm_tab = fields.Many2one('sale.order', readonly=True)

    user_select = fields.Many2one('res.users', string="User")
    sales_value = fields.Float(string="Sales Value", compute='get_total')
    sale_percent = fields.Float(string='Percent')
    sale_commission = fields.Float(string='Commission', compute='get_commission')

    @api.depends('user_select')
    def get_total(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            new_item = self.pool.get('sale.order').browse(cr, uid, record.rel_comm_tab.id)
            record['sales_value'] = new_item.amount_total
            obj = {
                'value': {
                    'sales_value': new_item.amount_total
                }
            }
            return obj

    @api.depends('sales_value', 'sale_percent')
    def get_commission(self, cr, uid, ids, context=None):
        rec = {}
        for record in self.browse(cr, uid, ids, context=context):
            record['sale_commission'] = (record.sales_value * record.sale_percent)/100
            return rec
