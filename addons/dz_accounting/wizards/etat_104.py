# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlwt
import io
import base64

class BankBookWizard(models.TransientModel):
    _name = 'account.etat.client'

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    file = fields.Binary('File', attachment=False)
    filename = fields.Char('File Name')

    @api.onchange('exercice_id')
    def onchange_exercice_id(self):
        if self.exercice_id:
            self.date_from = self.exercice_id.date_from
            self.date_to = self.exercice_id.date_to

    def check_report(self):
        self.ensure_one()
        partners = self.env['res.partner'].search([])
        clients = []
        total = 0
        tva = 0
        for partner in partners:
            all_invoices = partner.invoice_ids.filtered(lambda x: x.state == 'posted' and (not x.invoice_date or x.invoice_date >= self.date_from))
            invoices = all_invoices.filtered(lambda x: x.move_type == 'out_invoice')
            refunds = all_invoices.filtered(lambda x: x.move_type == 'out_refund')
            if len(invoices) > 0 or len(refunds) > 0:
                clients.append({
                    'ai': partner.ai,
                    'rc': partner.company_registry,
                    'nif': partner.vat,
                    'name': partner.name,
                    'address': (partner.street or "") + (partner.state_id.name or "") + (partner.country_id.name or ""),
                    'amount_ht': sum(invoices.mapped('amount_untaxed')) - sum(refunds.mapped('amount_untaxed')),
                    'tva': sum(invoices.mapped('amount_tax')) - sum(refunds.mapped('amount_tax')),
                })
                total += (sum(invoices.mapped('amount_untaxed')) - sum(refunds.mapped('amount_untaxed')))
                tva += (sum(invoices.mapped('amount_tax')) - sum(refunds.mapped('amount_tax')))
        data = {
            'clients': clients,
            'total_amount': total,
            'total_tva': tva,
            'nif': self.company_id.vat,
            'company': self.company_id.name,
            'address': self.company_id.street,
            'activity': self.company_id.activite,
            'current_year': self.date_from.year,
            'previous_year': self.date_from.year - 1,
            'date_from': self.date_from.strftime('%d/%m/%Y'),
            'date_to': self.date_to.strftime('%d/%m/%Y'),
        }

        return self.env.ref(
            'dz_accounting.etat_104_report_action').report_action(self, data)

    def check_report_xls(self):
        self.ensure_one()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("État 104")
        font_bold = xlwt.easyxf("font: bold on;font:height 300;align: horiz centre;align: vert centre")
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour light_green;align: horiz centre;align: vert centre;borders: left thin, right thin, top thin, bottom thin;")
        header_info = xlwt.easyxf("font: bold on;align: horiz left;align: vert centre;pattern: pattern solid, fore_colour lime;")
        amount_border = xlwt.easyxf("borders: left thin, right thin, top thin, bottom thin;align: vert centre;")
        amount_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour white;align: vert centre;align: horiz right;borders: left thin, right thin, top thin, bottom thin;")

        worksheet.col(0).width = 4500
        worksheet.col(1).width = 4500
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 5500
        worksheet.col(4).width = 9500
        worksheet.row(2).height = 340
        worksheet.row(3).height = 340
        worksheet.row(4).height = 340
        worksheet.row(5).height = 340
        worksheet.write_merge(2, 2, 0, 3, 'Désignation de l’entreprise : ' + self.company_id.name, header_info)
        worksheet.write_merge(3, 3, 0, 3, 'Activité : ' + (self.company_id.activite or ''), header_info)
        worksheet.write_merge(4, 4, 0, 3, 'Adresse : ' + (self.company_id.street or ''), header_info)
        worksheet.write_merge(5, 5, 0, 3, 'NIF : ' + (self.company_id.vat or ''), header_info)
        worksheet.write_merge(7, 7, 2, 6, 'État 104: ' + self.date_from.strftime('%d/%m/%Y') + ' à ' + self.date_to.strftime('%d/%m/%Y'), font_bold)
        worksheet.row(7).height = 500
        row = 9
        worksheet.write(row, 0, 'AI', header_bold)
        worksheet.write(row, 1, 'RC', header_bold)
        worksheet.write(row, 2, 'NIF', header_bold)
        worksheet.write(row, 3, 'Nom et prénom', header_bold)
        worksheet.write(row, 4, 'Adresse', header_bold)
        worksheet.write(row, 5, 'Montant HT', header_bold)
        worksheet.write(row, 6, 'TVA', header_bold)

        partners = self.env['res.partner'].search([])
        total = 0
        tva = 0
        worksheet.row(row).height = 340
        for partner in partners:
            all_invoices = partner.invoice_ids.filtered(lambda x: x.state == 'posted' and (not x.invoice_date or x.invoice_date >= self.date_from))
            invoices = all_invoices.filtered(lambda x: x.move_type == 'out_invoice')
            refunds = all_invoices.filtered(lambda x: x.move_type == 'out_refund')
            if len(invoices) > 0 or len(refunds) > 0:
                row += 1
                worksheet.row(row).height = 340
                worksheet.write(row, 0, partner.ai, amount_border)
                worksheet.write(row, 1, partner.company_registry, amount_border)
                worksheet.write(row, 2, partner.vat, amount_border)
                worksheet.write(row, 3, partner.name, amount_border)
                worksheet.write(row, 4, (partner.street or "") + (partner.state_id.name or "") + (partner.country_id.name or ""), amount_border)
                worksheet.write(row, 5, sum(invoices.mapped('amount_untaxed')) - sum(refunds.mapped('amount_untaxed')), amount_border)
                worksheet.write(row, 6, sum(invoices.mapped('amount_tax')) - sum(refunds.mapped('amount_tax')), amount_border)
                total += (sum(invoices.mapped('amount_untaxed')) - sum(refunds.mapped('amount_untaxed')))
                tva += (sum(invoices.mapped('amount_tax')) - sum(refunds.mapped('amount_tax')))
        row += 1
        worksheet.row(row).height = 340
        worksheet.write_merge(row, row, 0, 4, 'TOTAL', amount_bold)
        worksheet.write(row, 5, total, amount_bold)
        worksheet.write(row, 6, tva, amount_bold)

        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodebytes(fp.getvalue())
        self.file = excel_file
        self.filename = 'État 104.xls'
        fp.close()
        action = {
            'name': self.filename,
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=account.etat.client&id=" + str(
                self.id) + "&filename_field=filename&field=file&download=true&filename=" + self.filename,
            'target': 'self',
        }
        return action