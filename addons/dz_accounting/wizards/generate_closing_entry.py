# -*- coding: utf-8 -*-
#############################################################################
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime
from odoo.exceptions import UserError, ValidationError

class AccountClosingEntry(models.TransientModel):
    _name = 'account.close.entry'

    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type', '=', 'general')]",  default=lambda self: self.env['account.journal'].search([('type', '=', 'general')], limit=1).id)
    account_id = fields.Many2one('account.account', 'Compte comptable de cloture', required=True,
                                 default=lambda self: self.env.user.company_id.get_unaffected_earnings_account())
    def execute(self):
        move = self.env['account.move'].search([('is_closing', '=', True),
                                                ('date', '>=', self.exercice_id.date_from),
                                                ('date', '<=', self.exercice_id.date_to)])
        if move:
            if move.state == 'draft':
                move.name = '/'
                move.unlink()
                move = False
            elif move.state == 'posted':
                raise ValidationError("La pièce comptable de clôture de l'année: " + self.exercice_id.date_to.strftime('%Y') + " existe déjà")
        if not move :
            expense = ['expense', 'expense_depreciation', 'expense_direct_cost']
            income = ['income', 'income_other']
            income_accounts = []
            for account in self.env['account.account'].search([('account_type', 'in', income)]):
                income_accounts.append(account.id)
            expense_accounts = []
            for account in self.env['account.account'].search([('account_type', 'in', expense)]):
                expense_accounts.append(account.id)
            income_lines = self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('account_id', 'in', income_accounts),
                                                                 ('date', '>=', self.exercice_id.date_from),
                                                                 ('date', '<=', self.exercice_id.date_to)])
            income_debit = 0
            income_credit = 0
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'date': self.exercice_id.date_to,
                'is_closing': True,
                'journal_id': self.journal_id.id
            })

            lines = []
            for income_line in income_lines:
                lines.append({
                    'name': income_line.name,
                    'move_id': move.id,
                    'account_id': income_line.account_id.id,
                    'debit': income_line.credit,
                    'credit': income_line.debit,
                })
                income_credit += income_line.debit
                income_debit += income_line.credit

            expense_lines = self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('account_id','in',expense_accounts),
                                                                  ('date', '>=', self.exercice_id.date_from),
                                                                  ('date', '<=', self.exercice_id.date_to)])
            expense_debit = 0
            expense_credit = 0
            for expense_line in expense_lines:
                lines.append({
                    'name': expense_line.name,
                    'move_id': move.id,
                    'account_id': expense_line.account_id.id,
                    'debit': expense_line.credit,
                    'credit': expense_line.debit,
                })
                expense_credit += expense_line.debit
                expense_debit += expense_line.credit
            credit = income_credit + expense_credit
            debit = income_debit + expense_debit
            lines.append(
                {
                    'name': 'Result',
                    'move_id': move.id,
                    'account_id': self.account_id.id,
                    'credit': (debit - credit) if debit > credit else 0,
                    'debit': (credit - debit )if credit > debit else 0
                }
            )
            move_lines = self.env['account.move.line'].create(lines)
        return self.env.ref('account.action_move_journal_line').read()[0]

