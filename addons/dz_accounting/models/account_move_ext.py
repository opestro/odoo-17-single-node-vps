# -*- coding: utf-8 -*-
#############################################################################
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_closing = fields.Boolean('is Closing')
    contain_tft_accounts = fields.Boolean('Contains TFT Account', compute="compute_contain_tft_accounts")

    payment_date = fields.Date(string='Date de paiement',store=True, readonly=True, compute='_compute_payment_date')


    def is_sale_document_g50(self, include_receipts=False):
        return (self.is_sale_document(include_receipts) or self.move_type in ['in_refund']) and self.move_type not in ['out_refund']


    @api.depends('payment_state')
    def _compute_payment_date(self):
        for invoice in self:
            in_draft_mode = invoice != invoice._origin
            invoice.payment_date = None
            if invoice.is_invoice():
                if not in_draft_mode and invoice.amount_total > 0 and invoice.id:
                    if invoice.payment_state == 'paid':
                        payment = self.env['account.payment'].sudo().search([('partner_id', '=', invoice.partner_id.id)], order='date desc').filtered(lambda x: invoice.id in x.reconciled_invoice_ids.ids or invoice.id in x.reconciled_bill_ids.ids)
                        if payment:
                            invoice.payment_date = payment[0].date
                    else:
                        invoice.payment_date = None

    def compute_contain_tft_accounts(self):
        for move in self:
            move.contain_tft_accounts = False
            for record in move.line_ids:
                if move.contain_tft_accounts is True:
                    continue
                for code in ["51", "52", "53", "54", "58"]:
                    if str(record.account_id.code).startswith(code):
                        move.contain_tft_accounts = True

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_droit_timbre = fields.Boolean('écriture de droit de timbre')
    payment_date = fields.Date(string='Date de paiment', related="move_id.payment_date")
