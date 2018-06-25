from odoo import models, fields, api


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    use_product = fields.Many2one('product.template', related='user_id.company_id.commission_product')
    commission = fields.Char(string='Total Commission', compute='calculate_total_commission')

    @api.depends('order_line.commission_line')
    def calculate_total_commission(self):
        for order in self:
            commission_total = 0.0
            for line in order.order_line:
                commission_total += line.commission_line
            order.update({'commission': commission_total})

    @api.multi
    def pay_commission(self):
        journal = self.env['account.invoice']._default_journal().id
        print journal
        supplier_line = {
            'product_id': self.use_product.id,
            'name': self.use_product.name,
            'quantity': 1,
            'account_id': journal,
            'price_unit': self.commission,
            'type': 'in_invoice',
        }
        record_line = {
            'partner_id': self.user_id.id,
            'type': 'in_invoice',
            'invoice_line_ids': [(0, 0, supplier_line)],
        }
        record = self.env['account.invoice'].create(record_line)
        self.env['account.invoice'].action_invoice_open()
        return record


class ProductCommission(models.Model):
    _inherit = 'product.template'

    commission_percentage = fields.Float(string='Commission Percent')


class CommissionProduct(models.Model):
    _inherit = 'res.company'

    commission_product = fields.Many2one('product.template', string='Commission Product')


class SaleOrderlineInherited(models.Model):
    _inherit = 'sale.order.line'
    commission_line_percentage = fields.Float(related='product_id.product_tmpl_id.commission_percentage')
    commission_line = fields.Float(string='Commission', compute='get_commission')

    @api.depends('commission_line_percentage')
    def get_commission(self):
        for record in self:
            record['commission_line'] = (record.price_subtotal * record.commission_line_percentage) / 100
        return None
