# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class BankBookWizard(models.TransientModel):
    _name = 'account.amo.report'

    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 default=lambda self: self.env.user.company_id)
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    date_from = fields.Date(string='Start Date', related="exercice_id.date_from")
    date_to = fields.Date(string='End Date', related="exercice_id.date_to")


    def get_amortissment_lines(self, date_from, date_to):
        depreciation_lines = self.env['account.asset.depreciation.line'].search([('depreciation_date','<=',self.date_to),('depreciation_date','>=',self.date_from),('asset_id.state', '=', 'open')])
        account_amo = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_depreciation_id')
        account_dotation = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_depreciation_expense_id')
        account_actif = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_asset_id')
        accounts = []
        for account in account_amo:
            lines = depreciation_lines.filtered(lambda l: l.asset_id.category_id.account_depreciation_id.id == account.id)
            accounts.append({
                'name': account.display_name,
                'items': [{
                    'code': l.asset_id.code,
                    'name': l.asset_id.name,
                    'date': l.asset_id.date,
                    'brute': l.asset_id.value,
                    'amo_debut': l.depreciated_value - l.amount,
                    'dotation': l.amount,
                    'amo_fin': l.depreciated_value,
                    'net': l.asset_id.value - l.depreciated_value,

                } for l in lines],
                'total_brute': sum(lines.mapped('asset_id').mapped('value')),
                'total_amo_debut': sum(lines.mapped('depreciated_value')) - sum(lines.mapped('amount')),
                'total_dotation': sum(lines.mapped('amount')),
                'total_amo_fin': sum(lines.mapped('depreciated_value')),
                'total_net': sum(lines.mapped('asset_id').mapped('value')) - sum(lines.mapped('depreciated_value')),
            })

        return {
            'comptes':accounts,
            'total_brute': sum([l['total_brute'] for l in accounts]),
            'total_amo_debut': sum([l['total_amo_debut'] for l in accounts]),
            'total_dotation': sum([l['total_dotation'] for l in accounts]),
            'total_amo_fin': sum([l['total_amo_fin'] for l in accounts]),
            'total_net': sum([l['total_net'] for l in accounts]),
        }

    def get_invesstissement_lines(self, date_from, date_to):
        depreciation_lines = self.env['account.asset.depreciation.line'].search([('depreciation_date','<=',self.date_to),('depreciation_date','>=',self.date_from),('asset_id.state', '=', 'open')])
        asset_ids = self.env['account.asset.asset'].search([('state', '=', 'open')])
        account_amo = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_depreciation_id')
        account_dotation = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_depreciation_expense_id')
        account_actif = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_asset_id')
        accounts = []
        for account in account_actif:
            lines = depreciation_lines.filtered(lambda l: l.asset_id.category_id.account_asset_id.id == account.id)
            account_assets = asset_ids.filtered(lambda a: a.category_id.account_asset_id.id == account.id and a.id not in lines.mapped('asset_id').mapped('id'))
            old_assets = [{'code': l.code,
                    'name': l.name,
                    'date': l.date,
                    'brute': l.value,
                    'amo_debut': l.value - l.salvage_value,
                    'dotation': 0,
                    'amo_fin': l.value - l.salvage_value,
                    'net': l.salvage_value} for l in account_assets]
            total_brute = sum(account_assets.mapped('value'))
            total_net = sum(account_assets.mapped('salvage_value'))
            total_amo_debut = total_brute - total_net
            accounts.append({
                'name': account.display_name,
                'items': [{
                    'code': l.asset_id.code,
                    'name': l.asset_id.name,
                    'date': l.asset_id.date,
                    'brute': l.asset_id.value,
                    'amo_debut': l.depreciated_value - l.amount,
                    'dotation': l.amount,
                    'amo_fin': l.depreciated_value,
                    'net': l.asset_id.value - l.depreciated_value,

                } for l in lines] + old_assets,
                'total_brute': sum(lines.mapped('asset_id').mapped('value')) + total_brute,
                'total_amo_debut': sum(lines.mapped('depreciated_value')) - sum(lines.mapped('amount')) + total_amo_debut,
                'total_dotation': sum(lines.mapped('amount')),
                'total_amo_fin': sum(lines.mapped('depreciated_value')) + total_amo_debut,
                'total_net': sum(lines.mapped('asset_id').mapped('value')) - sum(lines.mapped('depreciated_value')) + total_net,
            })

        return {
            'comptes':accounts,
            'total_brute': sum([l['total_brute'] for l in accounts]),
            'total_amo_debut': sum([l['total_amo_debut'] for l in accounts]),
            'total_dotation': sum([l['total_dotation'] for l in accounts]),
            'total_amo_fin': sum([l['total_amo_fin'] for l in accounts]),
            'total_net': sum([l['total_net'] for l in accounts]),
        }

    def get_dotation_lines(self, date_from, date_to):
        depreciation_lines = self.env['account.asset.depreciation.line'].search([('depreciation_date','<=',self.date_to),('depreciation_date','>=',self.date_from),('asset_id.state', '=', 'open')])
        account_amo = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_depreciation_id')
        account_dotation = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_depreciation_expense_id')
        account_actif = depreciation_lines.mapped('asset_id').mapped('category_id').mapped('account_asset_id')
        accounts = []
        for account in account_dotation:
            lines = depreciation_lines.filtered(lambda l: l.asset_id.category_id.account_depreciation_expense_id.id == account.id)
            accounts.append({
                'name': account.display_name,
                'items': [{
                    'code': l.asset_id.code,
                    'name': l.asset_id.name,
                    'date': l.asset_id.date,
                    'brute': l.asset_id.value,
                    'amo_debut': l.depreciated_value - l.amount,
                    'dotation': l.amount,
                    'amo_fin': l.depreciated_value,
                    'net': l.asset_id.value - l.depreciated_value,

                } for l in lines],
                'total_brute': sum(lines.mapped('asset_id').mapped('value')),
                'total_amo_debut': sum(lines.mapped('depreciated_value')) - sum(lines.mapped('amount')),
                'total_dotation': sum(lines.mapped('amount')),
                'total_amo_fin': sum(lines.mapped('depreciated_value')),
                'total_net': sum(lines.mapped('asset_id').mapped('value')) - sum(lines.mapped('depreciated_value')),
            })

        return {
            'comptes':accounts,
            'total_brute': sum([l['total_brute'] for l in accounts]),
            'total_amo_debut': sum([l['total_amo_debut'] for l in accounts]),
            'total_dotation': sum([l['total_dotation'] for l in accounts]),
            'total_amo_fin': sum([l['total_amo_fin'] for l in accounts]),
            'total_net': sum([l['total_net'] for l in accounts]),
        }

    def check_report(self):
        self.ensure_one()
        data = {
            'currency_id': self.company_id.currency_id,
            'nif': list(self.company_id.vat) if self.company_id.vat else [],
            'company': self.company_id.name,
            'address': self.company_id.street,
            'activity': self.company_id.activite,
            'current_year': self.date_from.year,
            'previous_year': self.date_from.year - 1,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'consolidate': True
                }
        tft = self.get_amortissment_lines(self.date_from, self.date_to)
        data.update(tft)
        return self.env.ref('dz_accounting.tableau_amortissements_report_action').report_action(self, data=data)

    def check_report_investissement(self):
        self.ensure_one()
        data = {
            'currency_id': self.company_id.currency_id,
            'nif': list(self.company_id.vat) if self.company_id.vat else [],
            'company': self.company_id.name,
            'address': self.company_id.street,
            'activity': self.company_id.activite,
            'current_year': self.date_from.year,
            'previous_year': self.date_from.year - 1,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'consolidate': True
                }
        tft = self.get_invesstissement_lines(self.date_from, self.date_to)
        data.update(tft)
        return self.env.ref('dz_accounting.tableau_investissments_report_action').report_action(self, data=data)

    def check_report_dotation(self):
        self.ensure_one()
        data = {
            'currency_id': self.company_id.currency_id,
            'nif': list(self.company_id.vat) if self.company_id.vat else [],
            'company': self.company_id.name,
            'address': self.company_id.street,
            'activity': self.company_id.activite,
            'current_year': self.date_from.year,
            'previous_year': self.date_from.year - 1,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'consolidate': True
                }
        tft = self.get_dotation_lines(self.date_from, self.date_to)
        data.update(tft)
        return self.env.ref('dz_accounting.tableau_dotations_report_action').report_action(self, data=data)