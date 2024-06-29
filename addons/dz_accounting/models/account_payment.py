# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields
from datetime import timedelta
import logging
logger = logging.getLogger(__name__)




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    g50_ids = fields.One2many('declaration.g50', 'payment_id', string="G50s")
    tva_percent = fields.Float('TVA(%)')
    tva_amount = fields.Float('TVA')
    ca = fields.Float('ca')
    tap_percent = fields.Float('TAP(%)')
    tap_amount = fields.Float('TAP')


    @api.onchange('tva_percent')
    def onchange_percentage_tva(self):
        self.tva_amount = self.amount - self.amount / ( 1 + 0.01 * self.tva_percent)
        self.onchange_tva_tap()

    @api.onchange('tap_percent')
    def onchange_percentage_tap(self):
        self.tap_amount = self.amount - self.amount / ( 1 + 0.01 * self.tap_percent)
        self.onchange_tva_tap()

    @api.onchange('tva_amount', 'tap_amount')
    def onchange_tva_tap(self):
        g50 = self.env['declaration.g50'].search([('year', '=', self.date.year)])
        g50 = g50.filtered(lambda l: self._origin.id in l.received_payment_ids.ids or self._origin.id in l.sent_payment_ids.ids)
        self.env['account.payment'].search([('id', '=', int(self._origin.id))]).write({'tap_amount': self.tap_amount, 'tva_amount': self.tva_amount})
        logger.info(g50)
        for record in g50:
            record.onchange_payement_lines()


    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
        if self.env.context.get('g50_id', False):
            g50_id = self.env.context.get('g50_id')
            g50 = self.env['declaration.g50'].browse(g50_id)
            rec.update({
                'currency_id': g50.currency_id.id,
                'amount': abs(g50.amount_total),
                'payment_type': 'outbound',
            })
        logger.info(rec)
        return rec

    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        if self.env.context.get('g50_id', False):
            return self.amount
        res = super(AccountPayment, self)._compute_payment_amount(invoices, currency, journal, date)
        return res

    def action_post(self):
        if self.env.context.get('g50_id', False):
            g50_id = self.env.context.get('g50_id')
            g50 = self.env['declaration.g50'].browse(g50_id)
            g50.payment_id = self.id
            res = super(AccountPayment, self).action_post()
            move = self.move_id
            move.button_draft()
            move.line_ids.with_context(force_delete=True).unlink()
            lines = []
            name = "G-50 " + str(g50.month) + "/" + str(g50.year)
            liquidity_line_account = self.payment_method_line_id.payment_account_id or self.journal_id.default_account_id
            # ********************** TAP *************************
            tap = g50.tap
            lines.append({
                'name': name + ' TAP',
                'move_id': move.id,
                'account_id': self.company_id.account_tap_credit_account_id.id,
                'debit': round(abs(tap), 2),
                'credit': 0,
                'payment_id': self.id,
            })
            # ********************** IRG *************************
            if g50.irg:
                lines.append({
                'name': name + ' TIMBRE',
                'move_id': move.id,
                'account_id': self.company_id.account_irg_debit_account_id.id,
                'debit': round(abs(g50.irg), 2),
                'credit': 0,
                'payment_id': self.id,
            })
            # ********************** D.Timbre *************************
            timbre = g50.timbre
            if timbre:
                timbre_account = self.env['config.timbre'].search([('name', '=', 'Calcul Timbre')]).account_id.id
                lines.append({
                'name': name + ' TIMBRE',
                'move_id': move.id,
                'account_id': timbre_account,
                'debit': round(abs(timbre), 2),
                'credit': 0,
                'payment_id': self.id,
            })

            # ********************** TVA à decaisser *************************
            if g50.tva:
                lines.append({
                'name': name + ' TVA à décaisser',
                'move_id': move.id,
                'account_id': self.company_id.account_tva_credit_account_id.id,
                'debit': abs(g50.tva),
                'credit': 0,
                'payment_id': self.id,
            })
            # ***************** IBS *************
            if g50.ibs:
                lines.append({
                    'name': name + 'IBS',
                    'move_id': move.id,
                    'account_id': self.company_id.account_ibs_credit_account_id.id,
                    'debit': g50.ibs,
                    'credit': 0,
                    'payment_id': self.id,
                })

            # *****************Paiement / Règlement
            lines.append({
                'name': name + ' Paiement',
                'move_id': move.id,
                'account_id': liquidity_line_account.id,
                'debit': 0,
                'credit': g50.amount_total,
                'payment_id': self.id,
            })
            move_lines = self.env['account.move.line'].with_context(skip_account_move_synchronization=True).create(lines)
            move._post()
            g50.write({'state': 'paid'})
            g50.write({'paying_move_id': move.id})
        else:
            res = super(AccountPayment, self).action_post()

        return res
