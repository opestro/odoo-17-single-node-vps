# -*- coding: utf-8 -*-
#############################################################################
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import timedelta
from odoo.exceptions import ValidationError

class BankReconciliation(models.Model):
    _name = 'bank.releve'


    name = fields.Char(string='Référence')
    reference = fields.Char(string='Référence externe')
    date_from = fields.Date(string='Date du', required=True, default=fields.Date.today().replace(day=1))
    date = fields.Date(string='Date au', required=True, default=fields.Date.context_today)
    balance_start = fields.Monetary(string='Solde du compte 512',  compute='_compute_start_balance', store=True, readonly=False)
    balance_end = fields.Monetary('Solde final du compte 512')
    bank_balance_start = fields.Monetary(string='Solde de la banque')
    bank_balance_end = fields.Monetary('Solde final de la banque', )
    journal_id = fields.Many2one('account.journal', required=True, string='Banque', domain="[('type', '=', 'bank')]", default=lambda self: self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    account_move_lines = fields.Many2many('account.move.line', string="Ecritures comptables")
    bank_lines = fields.One2many('bank.releve.line', 'releve_id' ,string="Lignes du relevé")
    state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'), ('done', 'Validé')], string='État', default='draft',
    )

    @api.depends('journal_id')
    def _compute_start_balance(self):
        for record in self:
            record.balance_start = record.journal_id._get_journal_bank_account_balance()[0] if record.journal_id else 0

    @api.onchange('date_from', 'date', 'journal_id')
    def onchange_account_ids(self):
        if self.date_from and self.journal_id:
            dom = [('date', '<=', self.date), ('date', '>=', self.date_from), ('move_id.state', '=', 'posted'), ('journal_id', '=', self.journal_id.id), ('account_id.account_type', '=', 'asset_cash')]
            lines = self.env['account.move.line'].search(dom)
            self.account_move_lines = lines
            dom = [('date', '>=', self.date_from), ('move_id.state', '=', 'posted'), ('journal_id', '=', self.journal_id.id), ('account_id.account_type', '=', 'asset_cash')]
            domain = {'account_move_lines': dom}
            return {'domain': domain}

    @api.onchange('balance_start', 'bank_lines')
    def onchange_balance_start(self):
        debit = sum(self.bank_lines.mapped('debit'))
        credit = sum(self.bank_lines.mapped('credit'))
        self.balance_end = self.balance_start + credit - debit

    @api.onchange('bank_balance_start', 'account_move_lines')
    def onchange_bank_balance_start(self):
        debit = sum(self.account_move_lines.mapped('debit'))
        credit = sum(self.account_move_lines.mapped('credit'))
        self.bank_balance_end = self.bank_balance_start - credit + debit

    def action_validate(self):
        self.state = 'done'

class BankReconciliationLine(models.Model):
    _name = 'bank.releve.line'


    name = fields.Char(string='libellé')
    account_id = fields.Many2one('account.account', string="Account",)
    debit = fields.Monetary(string='Debit')
    credit = fields.Monetary(string='Credit')
    partner_id = fields.Many2one('res.partner', 'Partner')
    releve_id = fields.Many2one('bank.releve', 'Relevé')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    date = fields.Date(required=True, default=fields.Date.context_today)