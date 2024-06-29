# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import xlwt
import io
import base64

class BankBookWizard(models.TransientModel):
    _name = 'account.livre.tiers'

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date' )
    date_to = fields.Date(string='End Date')
    file = fields.Binary('File', attachment=False)
    filename = fields.Char('File Name')

    @api.onchange('exercice_id')
    def onchange_exercice_id(self):
        if self.exercice_id:
            self.date_from = self.exercice_id.date_from
            self.date_to = self.exercice_id.date_to

    def get_balance_all_accounts(self):
        livre = []
        accounts = self.env['account.account'].search([])

        for account in accounts:
            lines = self.env['account.move.line'].search([
                    ('move_id.state', '=', 'posted'),
                    ('date','<=',self.date_to),('date','>=',self.date_from),
                    ('account_id', '=', account.id)])
            lines_at_start = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),('date', '<', self.date_from), ('account_id', '=', account.id)])
            if len(lines_at_start) or len(lines):
                livre.append({'name': account.name,
                          'code':account.code,
                          'credit_start': sum(lines_at_start.mapped('credit')),
                          'debit_start': sum(lines_at_start.mapped('debit')),
                          'solde_start': sum(lines_at_start.mapped('debit')) - sum(lines_at_start.mapped('credit')),
                          'credit': sum(lines.mapped('credit')),
                          'debit': sum(lines.mapped('debit')),
                          'solde': sum(lines.mapped('debit')) - sum(lines.mapped('credit')),

                          })

        return livre

    def get_tier_lines(self):
        partners = self.env['res.partner'].search([])
        livre = []
        accounts = self.env['account.account'].search(['|',('account_type','=','asset_receivable'),('account_type','=','liability_payable')])

        for account in accounts:
            partners_list = []
            for partner in partners:
                items = [{
                    'date':line.date,
                    'journal_id':line.journal_id.code,
                    'partner_id':line.partner_id.name,
                    'name':line.name,
                    'ref':line.ref,
                    'debit':line.debit,
                    'credit':line.credit,
                    'solde':line.debit - line.credit,
                    'reconcile_id':line.matching_number if line.matching_number else ''
                }
                         for line in self.env['account.move.line'].search([
                    ('move_id.state', '=', 'posted'),('move_id.is_closing', '!=', True),
                    ('date','<=',self.date_to),('date','>=',self.date_from),
                    ('account_id', '=', account.id),
                    ('partner_id','=',partner.id)])]
                if len(items):
                    lines_at_start = self.env['account.move.line'].search([
                        ('move_id.state', '=', 'posted'), ('move_id.is_closing', '!=', True),
                        ('date', '<', self.date_from),('account_id', '=', account.id),('partner_id', '=', partner.id)])
                    partners_list.append({'name':partner.name, 'items': items,
                                          'credit_start': sum(lines_at_start.mapped('credit')),
                                          'debit_start': sum(lines_at_start.mapped('debit')),
                                          'solde_start': sum(lines_at_start.mapped('debit')) - sum(lines_at_start.mapped('credit')),
                                          'exercice_credit_cumule': sum([l['credit'] for l in items]),
                                          'exercice_debit_cumule': sum([l['debit'] for l in items]),
                                          'exercice_solde_cumule': sum([l['debit'] for l in items]) - sum([l['credit'] for l in items]),

                                          })
            if len(partners_list):
                livre.append({'name': account.name, 'code':account.code, 'partners': partners_list})

        return livre

    def check_report(self):
        self.ensure_one()
        data = {'livres':self.get_tier_lines(),
                'currency_id': self.company_id.currency_id,
                'nif': self.company_id.vat,
                'company': self.company_id.name,
                'address': self.company_id.street,
                'activity': self.company_id.activite,
                'current_year': self.date_from.year,
                'previous_year': self.date_from.year - 1,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'consolidate': False
                }
        return self.env.ref('dz_accounting.livre_des_tiers_action').report_action(self, data=data)

    def check_report_balance(self):
        self.ensure_one()
        data = {'balance':self.get_balance_all_accounts(),
                'currency_id': self.company_id.currency_id,
                'nif': self.company_id.vat,
                'company': self.company_id.name,
                'address': self.company_id.street,
                'activity': self.company_id.activite,
                'current_year': self.date_from.year,
                'previous_year': self.date_from.year - 1,
                'date_from': self.date_from.strftime('%d/%m/%Y'),
                'date_to': self.date_to.strftime('%d/%m/%Y'),
                'consolidate': False
                }
        return self.env.ref('dz_accounting.balance_report_action').report_action(self, data=data)

    def check_report_xls(self):
        self.ensure_one()
        livres = self.get_tier_lines()
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("LIVRE DES TIERS")
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
        worksheet.write_merge(7, 7, 2, 6, 'LIVRE DES TIERS : ' + self.date_from.strftime('%d/%m/%Y') + ' à ' + self.date_to.strftime('%d/%m/%Y'), font_bold)
        worksheet.row(7).height = 500

        row = 9
        worksheet.row(row).height = 340
        for livre in livres:
            row += 1
            worksheet.write_merge(row, row, 0, 8, livre['code'] + '-' + livre['name'], header_bold)
            worksheet.row(row).height = 340
            for partner in livre['partners']:
                row += 1
                worksheet.row(row).height = 340
                worksheet.write(row, 0, 'Date', header_bold)
                worksheet.write(row, 1, 'Journal', header_bold)
                worksheet.write(row, 2, 'Partenaire', header_bold)
                worksheet.write(row, 3, 'écriture', header_bold)
                worksheet.write(row, 4, 'Référence', header_bold)
                worksheet.write(row, 5, 'Débit', header_bold)
                worksheet.write(row, 6, 'Crédit', header_bold)
                worksheet.write(row, 7, 'Solde', header_bold)
                worksheet.write(row, 8, 'let.', header_bold)
                for line in partner['items']:
                    row += 1
                    worksheet.row(row).height = 340
                    worksheet.write(row, 0, line['date'], amount_border)
                    worksheet.write(row, 1, line['journal_id'], amount_border)
                    worksheet.write(row, 2, line['partner_id'], amount_border)
                    worksheet.write(row, 3, line['name'], amount_border)
                    worksheet.write(row, 4, line['ref'], amount_border)
                    worksheet.write(row, 5, line['debit'], amount_border)
                    worksheet.write(row, 6, line['credit'], amount_border)
                    worksheet.write(row, 7, line['solde'], amount_border)
                    worksheet.write(row, 8, line['reconcile_id'], amount_border)

                row += 1
                worksheet.row(row).height = 340
                worksheet.write_merge(row, row, 0, 4, 'Total des mouvements', amount_bold)
                worksheet.write(row, 5, partner['exercice_debit_cumule'], amount_bold)
                worksheet.write(row, 6, partner['exercice_credit_cumule'], amount_bold)
                worksheet.write(row, 7, partner['exercice_solde_cumule'], amount_bold)

                row += 1
                worksheet.row(row).height = 340
                worksheet.write_merge(row, row, 0, 4, 'Total au debut de la periode', amount_bold)
                worksheet.write(row, 5, partner['debit_start'], amount_bold)
                worksheet.write(row, 6, partner['credit_start'], amount_bold)
                worksheet.write(row, 7, partner['solde_start'], amount_bold)

                row += 1
                worksheet.row(row).height = 340
                worksheet.write_merge(row, row, 0, 4, 'Solde à la fin de la periode', amount_bold)
                worksheet.write(row, 5, partner['debit_start'] + partner['exercice_debit_cumule'], amount_bold)
                worksheet.write(row, 6, partner['credit_start'] + partner['exercice_credit_cumule'], amount_bold)
                worksheet.write(row, 7, partner['solde_start'] + partner['exercice_solde_cumule'], amount_bold)
                row += 2

        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodebytes(fp.getvalue())
        self.file = excel_file
        self.filename = 'LIVRE DES TIERS.xls'
        fp.close()
        action = {
            'name': self.filename,
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=account.livre.tiers&id=" + str(
                self.id) + "&filename_field=filename&field=file&download=true&filename=" + self.filename,
            'target': 'self',
        }
        return action


    def balance_xls(self):
        workbook = xlwt.Workbook()
        font_bold = xlwt.easyxf("font: bold on;font:height 300;align: horiz centre;align: vert centre")
        header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour light_green;align: horiz centre;align: vert centre;borders: left thin, right thin, top thin, bottom thin;")
        header_info = xlwt.easyxf("font: bold on;align: horiz left;align: vert centre;pattern: pattern solid, fore_colour lime;")
        amount_border = xlwt.easyxf("borders: left thin, right thin, top thin, bottom thin;align: vert centre;")
        amount_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour white;align: vert centre;align: horiz right;borders: left thin, right thin, top thin, bottom thin;")
        worksheet = workbook.add_sheet("BALANCE")
        worksheet.col(0).width = 2500
        worksheet.col(1).width = 13500
        worksheet.col(2).width = 4500
        worksheet.col(3).width = 4500
        worksheet.col(4).width = 4500
        worksheet.col(5).width = 4500
        worksheet.col(6).width = 4500
        worksheet.col(7).width = 4500
        worksheet.col(8).width = 4500
        worksheet.col(9).width = 4500
        worksheet.col(10).width = 4500
        worksheet.row(2).height = 340
        worksheet.row(3).height = 340
        worksheet.row(4).height = 340
        worksheet.row(5).height = 340
        worksheet.write_merge(2, 2, 0, 3, 'Désignation de l’entreprise : ' + self.company_id.name, header_info)
        worksheet.write_merge(3, 3, 0, 3, 'Activité : ' + (self.company_id.activite or ''), header_info)
        worksheet.write_merge(4, 4, 0, 3, 'Adresse : ' + (self.company_id.street or ''), header_info)
        worksheet.write_merge(5, 5, 0, 3, 'NIF : ' + (self.company_id.vat or ''), header_info)
        worksheet.write_merge(7, 7, 1, 6, 'BALANCE GENERALE: ' + self.date_from.strftime('%d/%m/%Y') + ' à ' + self.date_to.strftime('%d/%m/%Y'), font_bold)
        worksheet.row(7).height = 500

        row = 9
        worksheet.row(row).height = 340
        balances = self.get_balance_all_accounts()
        worksheet.write_merge(row, row + 1, 0, 0, 'Code', header_bold)
        worksheet.write_merge(row, row + 1, 1, 1, 'Compte', header_bold)
        worksheet.write_merge(row, row, 2, 4, 'Solde au ' + self.date_from.strftime('%d/%m/%Y'), header_bold)
        worksheet.write(row + 1, 2, 'Débit ', header_bold)
        worksheet.write(row + 1, 3, 'Credit ', header_bold)
        worksheet.write(row + 1, 4, 'Solde ', header_bold)
        worksheet.write(row + 1, 5, 'Débit', header_bold)
        worksheet.write(row + 1, 6, 'Crédit', header_bold)
        worksheet.write(row + 1, 7, 'Solde ', header_bold)
        worksheet.write(row + 1, 8, 'Débit', header_bold)
        worksheet.write(row + 1, 9, 'Crédit', header_bold)
        worksheet.write(row + 1, 10, 'Solde', header_bold)
        worksheet.write_merge(row, row, 5, 7, 'MVM DU: ' + self.date_from.strftime('%d/%m/%Y') + ' AU: ' + self.date_to.strftime('%d/%m/%Y'), header_bold)
        worksheet.write_merge(row, row, 8, 10, 'Solde au ' + self.date_to.strftime('%d/%m/%Y') , header_bold)
        row += 1
        worksheet.row(row).height = 340
        for item in balances:
            row += 1
            worksheet.row(row).height = 340
            worksheet.write(row, 0, item['code'], amount_border)
            worksheet.write(row, 1, item['name'], amount_border)
            worksheet.write(row, 2, item['debit_start'], amount_border)
            worksheet.write(row, 3, item['credit_start'], amount_border)
            worksheet.write(row, 4, item['solde_start'], amount_border)
            worksheet.write(row, 5, item['debit'], amount_border)
            worksheet.write(row, 6, item['credit'], amount_border)
            worksheet.write(row, 7, item['solde'], amount_border)
            worksheet.write(row, 8, item['debit'] + item['solde_start'], amount_border)
            worksheet.write(row, 9, item['credit'] + item['solde_start'], amount_border)
            worksheet.write(row, 10, item['solde'] + item['solde_start'], amount_border)

        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodebytes(fp.getvalue())
        self.file = excel_file
        self.filename = 'BALANCE.xls'
        fp.close()
        action = {
            'name': self.filename,
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=account.livre.tiers&id=" + str(
                self.id) + "&filename_field=filename&field=file&download=true&filename=" + self.filename,
            'target': 'self',
        }
        return action