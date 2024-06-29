# -*- coding: utf-8 -*-
#############################################################################
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime
from odoo.exceptions import ValidationError

class BankReconciliationWizard(models.TransientModel):
    _name = 'bank.reconciliation.wizard'


    name = fields.Char(string='Référence')
    reference = fields.Char(string='Référence externe')
    date = fields.Date(required=True, default=fields.Date.context_today)
    balance_start = fields.Monetary(string='Solde initial',  compute='_compute_start_balance', store=True, readonly=False)
    balance_end_theory = fields.Monetary('Solde final théorique', compute='_compute_theoretical_end_balance')
    balance_end_real = fields.Monetary('Solde final', )
    journal_id = fields.Many2one('account.journal', required=True, string='Banque', domain="[('type', '=', 'bank')]", default=lambda self: self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    account_move_lines = fields.Many2many('account.move.line', string="Ecritures comptables", copy=True)

    @api.onchange('account_move_lines', 'balance_start')
    def onchange_account_move_lines(self):
        self._compute_theoretical_end_balance()

    @api.depends('journal_id')
    def _compute_start_balance(self):
        for record in self:
            last_bnk_stmt = self.env['account.bank.statement'].search([('journal_id', '=', record.journal_id.id)], limit=1) if record.journal_id else None
            if last_bnk_stmt:
                record.balance_start = last_bnk_stmt.balance_end
            record.balance_start = 0

    def _compute_theoretical_end_balance(self):
        for record in self:
            record.balance_end_theory = record.balance_start + sum(record.account_move_lines.mapped('debit')) - sum(record.account_move_lines.mapped('credit'))

    @api.onchange('date')
    def onchange_account_ids(self):
        if self.date:
            domain = {'account_move_lines': [('date', '<', self.date), ('move_id.state', '=', 'posted'), ('journal_id', '=', self.journal_id.id), ('account_id.account_type', '=', 'asset_cash')]}
            return {'domain': domain}


    def action_validate(self):
        if not len(self.account_move_lines):
            return

        if self.balance_end_real != self.balance_end_theory:
            raise ValidationError('le solde final théorique est different du sold final !')

        bank_statement = self.env['account.bank.statement'].create({
            'name': self.name,
            'balance_start': self.balance_start,
            'balance_end_real': self.balance_end_real,
            'date': self.date,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
        })

        for line in self.account_move_lines:
            data = {
                'amount': line.debit or -line.credit,
                'date': line.date,
                'name': line.name,
                'statement_id': bank_statement.id,
            }
            bank_statement_line = self.env['account.bank.statement.line'].create(data)
            line.statement_line_id = bank_statement_line.id
            line.statement_id = bank_statement.id
        view = self.env.ref('account.view_bank_statement_form')

        return {
            'name': 'Rapprochement bancaire',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': bank_statement.id,
            'context': self.env.context,
        }
