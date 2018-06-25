# -*- coding: utf-8 -*-

from odoo import fields, models, api
import time
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class AccountPartnerLedger(models.TransientModel):
    _inherit = 'account.report.partner.ledger'

    filter_type = fields.Selection([('partner_based', 'Based on partner'), ('salesmen_based', 'Based on sales person')])
    # corresponding_salesman = fields.Many2one('res.users', )
    partner_tags = fields.Many2many('res.partner', 'partner_ledger_partner_rel', 'id', 'partner_id', string='Partners')
    salesmen = fields.Many2many('res.users', string='Sales Person')

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency,
                             'partner_tags': self.partner_tags.ids, 'filter_type': self.filter_type, 'salesmen': self.salesmen.ids})
        return self.env['report'].get_action(self, 'account.report_partnerledger', data=data)


class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.account.report_partnerledger'

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        # sales_person = self.env[]
        print 'self=', self

        docs = self.env[self.model].browse(self.env.context.get('active_ids', [])).id
        print 'docs=',docs

        if not data.get('form'):
            raise UserError(("Form content is missing, this report cannot be printed."))

        data['computed'] = {}

        obj_partner = self.env['res.partner']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        print 'query_get_data=', query_get_data

        data['computed']['move_state'] = ['draft', 'posted']
        print 'data=', data

        if data['form'].get('target_move', 'all') == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = data['form'].get('result_selection', 'customer')
        print 'result_selection=', result_selection

        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['payable', 'receivable']

        self.env.cr.execute("""
            SELECT a.id
            FROM account_account a
            WHERE a.internal_type IN %s
            AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        print 'data=', data

        for (a,) in self.env.cr.fetchall():
            print 'a=', a
        print 'data[computed][account_ids]:=', data['computed']['account_ids']

        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        print 'params=', params
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        print 'reconcile_clause=', reconcile_clause

        if data['form']['filter_type'] == 'partner_based':
            query = """
                        SELECT DISTINCT "account_move_line".partner_id
                        FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                        WHERE "account_move_line".partner_id IS NOT NULL
                            AND "account_move_line".account_id = account.id
                            AND am.id = "account_move_line".move_id
                            AND am.state IN %s
                            AND "account_move_line".account_id IN %s
                            AND NOT account.deprecated
                            AND """ + query_get_data[1] + reconcile_clause
            print 'query partner based =', query
            self.env.cr.execute(query, tuple(params))
            # print_query = self.env.cr.execute(query, tuple(params))
            # print print_query

            if data['form']['partner_tags']:
                partner_ids = data['form']['partner_tags']
            else:
                partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
            partners = obj_partner.browse(partner_ids)
            partners = sorted(partners, key=lambda x: (x.ref, x.name))
        else:
            query2 = """
                        SELECT DISTINCT "account_invoice".user_id
                        FROM account_account AS account, account_move AS am, account_move_line inner join account_invoice
                        ON account_move_line.move_id = account_invoice.move_id
                        WHERE "account_move_line".partner_id IS NOT NULL
                            AND "account_move_line".account_id = account.id
                            AND account_move_line.move_id = account_invoice.move_id
                            AND am.id = "account_move_line".move_id
                            AND NOT account.deprecated
                            """ + reconcile_clause
            print 'query salesman based =', query2
            self.env.cr.execute(query2, tuple(params))
            # print_query = self.env.cr.execute(query2, tuple(params))
            # print print_query
            print "data['form']['salesmen']=", data['form']['salesmen']
            sales_person_ids = data['form']['salesmen']
            sales_person = self.env['res.users'].browse(sales_person_ids)
            sales_person = sorted(sales_person, key=lambda x: (x.ref, x.name))

        # print 'partners=', partners
        # print 'partners sorted=', partners

        if data['form']['filter_type'] == 'partner_based':
            docargs = {
                'doc_ids': partner_ids,
                'doc_model': self.env['res.partner'],
                'data': data,
                'docs': partners,
                'time': time,
                'lines': self._lines,
                'sum_partner': self._sum_partner,
            }
        else:
            docargs = {
                'doc_ids': sales_person_ids,
                'doc_model': self.env['res.users'],
                'data': data,
                'docs': sales_person,
                'time': time,
                'lines': self._lines,
                'sum_partner': self._sum_partner,
            }
        print 'docargs=', docargs
        return self.env['report'].render('account.report_partnerledger', docargs)


    def _lines(self, data, partner):
        print 'inside _lines in report->acc_partner_ledger'

        full_account = []
        currency = self.env['res.currency']
        query_get_data = self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()
        reconcile_clause = "" if data['form']['reconciled'] else ' AND "account_move_line".reconciled = false '
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        if data['form']['filter_type'] == 'partner_based':
            query = """
                SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
                FROM """ + query_get_data[0] + """
                LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
                LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
                LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
                LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
                WHERE "account_move_line".partner_id = %s
                    AND m.state IN %s
                    AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                    ORDER BY "account_move_line".date"""
            print 'query in _lines = ', query
        else:
            query = """
                    SELECT DISTINCT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id, c.symbol AS currency_code
                    FROM """ + query_get_data[0] + """
                    INNER JOIN account_invoice ON (account_move_line.move_id = account_invoice.move_id) 
                    LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
                    LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
                    LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
                    LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
                     WHERE "account_invoice".user_id = %s
                    AND m.state IN %s
                    AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                    ORDER BY "account_move_line".date"""
            print 'query_get_data[1]=', query_get_data[1]
            print 'else query in _lines of ', query
                    # WHERE "account_move_line".partner_id = %s
                    #     AND m.state IN %s
                    #     AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                    #     ORDER BY "account_move_line".date"""
            # query = """SELECT distinct "account_invoice".name
            #             FROM account_account AS account, account_move AS am, account_move_line inner join account_invoice
            #             ON account_move_line.move_id = account_invoice.move_id
            #             WHERE "account_move_line".account_id = account.id and user_id = 1"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        print 'in _lines() res=', res
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = datetime.strptime(r['date'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        return full_account



# class SalesmanFilter(models.AbstractModel):
#     _inherit = 'report.account.report_partnerledger'
#
#     def something(self):
#         self.env['account.invoice'].search()
