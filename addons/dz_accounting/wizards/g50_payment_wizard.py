# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class G50Payment(models.TransientModel):
    _name = 'g50.payment.wizard'

    @api.model
    def default_get(self, fields):
        res = super(G50Payment, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'project.task' and active_ids:
            res['g50_ids'] = [(6, 0, active_ids)]

        return res

    amount = fields.Monetary(string='Montant', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.company.currency_id)
    g50_ids = fields.Many2many('declaration.g50', string='G50(s)', readonly=True)
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)

    tap = fields.Float('TAP')
    timbre = fields.Float('Droits de timbre')
    ibs = fields.Float('IBS')
    irg = fields.Float('IRG')
    tva = fields.Float('TVA à payer')


    def action_pay(self):
        posted_move = self.posted_move_id
        if not posted_move:
            raise ValidationError("La declaration G50 de ce mois n'exite pas !")
        if self.paying_move_id and self.paying_move_id.state == 'posted':
            raise ValidationError("Le réglement du G50 de ce mois a été déjà comptabilisé")
        self.paying_move_id.name = '/'
        self.paying_move_id.unlink()
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': fields.Date.today(),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'ref': self.name
        })
        lines = []
        # ********************** TAP *************************
        lines.append({
            'name': 'TAP',
            'move_id': move.id,
            'account_id': self.company_id.account_tap_credit_account_id.id,
            'debit': round(abs(self.tap), 2),
            'credit': 0,
        })

        # ********************** TVA *************************
        lines.append({
            'name': 'TVA',
            'move_id': move.id,
            'account_id': self.company_id.account_tva_credit_account_id.id,
            'debit': round(abs(self.tva), 2) if self.tva > 0 else 0,
            'credit': 0,
        })
        # ********************** IRG *************************

        # ********************** TIMBRE *************************
        timbre = self.timbre
        lines.append({
            'name': 'TIMBRE',
            'move_id': move.id,
            'account_id': self.company_id.account_droit_timbre_receivable_id.id,
            'debit': round(abs(timbre), 2),
            'credit': 0,
        })

        # ********************* Payment **************
        lines.append({
            'name': 'Règlement de la déclaration G50',
            'move_id': move.id,
            'account_id': self.paying_account_id.id,
            'debit': 0,
            'credit': self.amount_total,
        })

        move_lines = self.env['account.move.line'].create(lines)
        self.paying_move_id = move.id
        action_data = self.env.ref('account.action_move_journal_line').read()[0]
        action_data['res_id'] = move.id
        action_data['view_mode'] = 'form,tree,kanban'
        action_data['view_id'] = self.env.ref('account.view_move_form').id
        return {
            'name': _('Invoice created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
            'res_id': move.id,
        }

