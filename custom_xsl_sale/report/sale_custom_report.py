from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ReportXlsxSale(ReportXlsx):

    def generate_xlsx_report(self, workbook, data, lines):

        sheet = workbook.add_worksheet()
        # order_no = self.env['sale.order'].search([])
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#F3F3F3', 'bold': True})
        format2 = workbook.add_format({'bold': True})
        format5 = workbook.add_format({'font_size': 10, 'bg_color': '#FFFFFF'})
        sheet.merge_range('A1:B1', lines.company_id.name, format5)
        sheet.merge_range('A2:B2', lines.company_id.street, format5)
        sheet.write('A3', lines.company_id.city, format5)
        sheet.write('B3', lines.company_id.zip, format5)
        sheet.merge_range('A4:B4', lines.company_id.state_id.name, format5)
        sheet.merge_range('A5:B5', lines.company_id.country_id.name, format5)
        sheet.merge_range('K1:L1', lines.company_id.rml_header1, format5)
        sheet.merge_range(5, 0, 6, 1, 'Quotation', format1)
        sheet.merge_range(5, 2, 6, 3, lines.name, format1)

        sheet.write('A9', 'Customer', format2)
        sheet.write('B9', lines.partner_id.name)
        sheet.write('A11', 'Project', format2)
        # sheet.write('B12', lines.project.name)
        sheet.merge_range('A12:B12', 'Contract No', format2)
        sheet.write('C12', lines.contract_no)

        sheet.merge_range('H9:I9', 'Date', format2)
        sheet.write('J9', lines.date_order)
        sheet.merge_range('H10:I10', 'Reference/Description', format2)
        sheet.write('J10', lines.client_order_ref)
        sheet.merge_range('H12:I12', 'Warehouse', format2)
        sheet.write('J12', lines.warehouse_id.name)
        sheet.merge_range('H13:I13', 'Pricelist', format2)
        sheet.write('J13', lines.pricelist_id.name)

        sheet.merge_range(13, 0, 14, 11, 'Order Lines', format1)

        sheet.merge_range('A16:B16', 'Product', format2)
        sheet.merge_range('C16:D16', 'Description', format2)
        sheet.merge_range('E16:F16', 'Quantity', format2)
        sheet.merge_range('G16:H16', 'Unit Price', format2)
        sheet.merge_range('I16:J16', 'Taxes', format2)
        sheet.merge_range('K16:L16', 'Sub-total', format2)

        irow = 16
        icol = 0
        for order in lines.order_line:
            print order.product_id.name

            sheet.merge_range(irow, icol, irow, icol+1, order.product_id.name)
            sheet.merge_range(irow, icol+2, irow, icol+3, order.product_id.name)
            sheet.merge_range(irow, icol+4, irow, icol+5, order.product_uom_qty)
            sheet.merge_range(irow, icol+6, irow, icol+7, order.price_unit)
            sheet.merge_range(irow, icol+8, irow, icol+9, order.tax_id.name)
            sheet.merge_range(irow, icol+10, irow, icol+11, order.price_subtotal)
            irow+= 1
            icol = 0

        sheet.merge_range('J21:K21', 'Untaxed Amount', format2)
        sheet.write('L21', lines.amount_untaxed)
        sheet.merge_range('J22:K22', 'Taxes', format2)
        sheet.write('L22', lines.amount_tax)
        sheet.merge_range('J23:K23', 'Total', format2)
        sheet.write('L23', lines.amount_total)


ReportXlsxSale('report.custom_xsl_sale.sale_custom_report', 'sale.order')
