# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class ProductCategory(models.Model):
    _inherit = 'sale.order.line'
    product_categ_id = fields.Selection(related='product_id.product_tmpl_id.type',
                                        string='Category')

    def category_checker(self,product_categ_id):
        print 'test'
        loc = self.env['sale.order.line'].search([('id', '=', self.id)])
        print 'test here'
        print 'product_categ_id', loc.product_categ_id.id


class CustomSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    show_separate_invoice = fields.Boolean('separate_invoice', help='Show separate invoice based on product type', store=True)
    journal_to_invoice = fields.Many2one('account.journal', string='journal', store=True)

    @api.model
    def get_default_show_separate_invoice(self, fields):
        irconfigparam = self.env['ir.config_parameter']
        return{
            'show_separate_invoice': irconfigparam.get_param('show_separate_invoice', False)
        }

    @api.multi
    def set_default_show_separate_invoice(self):
        self.ensure_one()
        irconfigparam = self.env['ir.config_parameter']
        irconfigparam.set_param('show_separate_invoice', self.show_separate_invoice)

    @api.multi
    def set_default_journal_to_invoice(self):
        return self.env['ir.values'].sudo().set_default('sale.config.settings', 'journal_to_invoice', self.journal_to_invoice.id)


class CustomSaleOrderFunction(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        print 'came here action_invoice_create'
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        inv_data = {}
        for order in self:
            print 'inside for order in self'
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.product_id.product_tmpl_id.type):
                print '\ninside line in order.order_line'
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                print 'group_key', group_key
                if group_key not in invoices:
                    if line.product_id.product_tmpl_id.type == 'service':
                        print 'service product'

                        print 'before order._prepare_service_invoice()'
                        inv_data = order._prepare_service_invoice()
                        print 'inv_data', inv_data
                        invoice = inv_obj.create(inv_data)
                        print 'invoice ', invoice
                        references[invoice] = order
                        print 'references', references
                        invoices[group_key] = invoice
                        print 'invoices', invoices
                    else:
                        print 'before _prepare_invoice()'
                        inv_data = order._prepare_invoice()
                        print 'inv_data', inv_data
                        invoice = inv_obj.create(inv_data)
                        print 'invoice ', invoice
                        references[invoice] = order
                        print 'references', references
                        invoices[group_key] = invoice
                        print 'invoices', invoices
                elif group_key in invoices:
                    print 'inside elif'
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref

                    if line.product_id.product_tmpl_id.type == 'service' and inv_data['journal_id'] != 8:
                        print 'service product but customer journal. Calling _prepare_service_invoice again'
                        inv_data = order._prepare_service_invoice()
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice
                    elif line.product_id.product_tmpl_id.type != 'service' and inv_data['journal_id'] == 8:
                        print 'Consumable or stockable product but service jrnl. Calling _prepare_invoice again'
                        inv_data = order._prepare_invoice()
                        invoice = inv_obj.create(inv_data)
                        references[invoice] = order
                        invoices[group_key] = invoice

                    invoices[group_key].write(vals)
                    print 'invoices after if', invoices
                if line.qty_to_invoice > 0:
                    print 'inside line.qty_to_invoice> 0'
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    print 'inside line.qty_to_invoice < 0 and final'
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    print 'inside order not in references'
                    references[invoice] = references[invoice] | order
                    print 'references=', references[invoice]

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            print 'before compute taxes'
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        print '\nReturned value :',   [inv.id for inv in invoices.values()]
        return [inv.id for inv in invoices.values()]

    @api.multi
    def _prepare_service_invoice(self):

        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        print "here _prepare_service_invoice"
        self.ensure_one()

        field_value = self.env['ir.config_parameter'].get_param('show_separate_invoice', '')
        if field_value:
            print 'field_value', field_value
            journal_id = self.env['ir.values'].get_default('sale.config.settings', 'journal_to_invoice')
            print 'journal_id', journal_id
        else:
            journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
            print 'journal_id', journal_id
        # ir_values = self.env['ir.values']
        # field_value = self.env['ir.config_parameter'].get_param('show_separate_invoice', '')
        # if field_value:
        #     print 'field_value', field_value
        #     journal_id = ir_values.get_default('sale.config.settings', 'journal_to_invoice')
        #     print 'journal_id', journal_id
        # else:
        #     journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']

        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals