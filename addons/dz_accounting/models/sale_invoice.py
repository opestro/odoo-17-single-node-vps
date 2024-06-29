# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#


from contextlib import ExitStack, contextmanager
from odoo import fields, models, api,_
from odoo.tools.misc import formatLang
from odoo.tools import format_amount
import logging
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)



class PurchaseOrderr(models.Model):
    _inherit = "purchase.order"

    apply_timbre = fields.Boolean('Appliquer les droits de timbre?')

    @api.depends('apply_timbre', 'amount_total')
    def _amount_timbre(self):
        for order in self:
            amount_timbre = order.amount_total
            if order.apply_timbre:
                timbre = self.env['config.timbre']._timbre(order.amount_total)
                order.timbre = timbre['timbre']
                amount_timbre = timbre['amount_timbre']
            order.amount_timbre = amount_timbre
            order.amount_total = order.amount_timbre

    timbre = fields.Monetary(string='Timbre', store=True, readonly=True,
                             compute='_amount_timbre', track_visibility='onchange')
    amount_timbre = fields.Monetary(string='Total avec Timbre', store=True,
                                    readonly=True, compute='_amount_timbre', track_visibility='onchange')

    @api.depends('order_line.taxes_id', 'order_line.price_subtotal', 'amount_total', 'amount_untaxed', 'apply_timbre')
    def _compute_tax_totals(self):
        super(PurchaseOrderr, self)._compute_tax_totals()
        for record in self:
            record.tax_totals['timbre'] = abs(record.timbre)
            record.tax_totals['amount_total_timbre'] = abs(record.tax_totals['amount_total'] + abs(record.timbre))
            format_amount = formatLang(self.env, abs(record.tax_totals['amount_total'] + abs(record.timbre)),
                                       currency_obj=record.currency_id),
            record.tax_totals['formatted_amount_total_timbre'] = format_amount

    def _prepare_invoice(self, ):
        invoice_vals = super(PurchaseOrderr, self)._prepare_invoice()
        invoice_vals.update({
            'apply_timbre': self.apply_timbre,
        })
        return invoice_vals


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    apply_timbre = fields.Boolean('Appliquer les droits de timbre?')

    @api.depends('apply_timbre', 'amount_total')
    def _amount_timbre(self):
        for order in self:
            amount_timbre = order.amount_total
            if order.apply_timbre:
                timbre = self.env['config.timbre']._timbre(order.amount_total)
                order.timbre = timbre['timbre']
                amount_timbre = timbre['amount_timbre']
            order.amount_timbre = amount_timbre
            order.amount_total = order.amount_timbre

    timbre = fields.Monetary(string='Timbre', store=True, readonly=True,
                             compute='_amount_timbre', track_visibility='onchange')
    amount_timbre = fields.Monetary(string='Total avec Timbre', store=True,
                                    readonly=True, compute='_amount_timbre')

    @api.depends('order_line.price_total','apply_timbre')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        lang_env = self.with_context(lang=self.partner_id.lang).env
        for order in self:
            amount_untaxed = amount_tax = amount_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_discount += (line.product_uom_qty * line.price_unit * line.discount) / 100
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_discount': amount_discount,
                'amount_total': amount_untaxed + amount_tax,
            })


    def _prepare_invoice(self, ):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'apply_timbre': self.apply_timbre,
        })
        return invoice_vals

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id', 'apply_timbre')
    def _compute_tax_totals(self):
        super(SaleOrder, self)._compute_tax_totals()
        for record in self:
            record.tax_totals['timbre'] = abs(record.timbre)
            record.tax_totals['amount_total_timbre'] = abs(record.tax_totals['amount_total'] + abs(record.timbre))
            format_amount = formatLang(self.env, abs(record.tax_totals['amount_total'] + abs(record.timbre)), currency_obj=record.currency_id),
            record.tax_totals['formatted_amount_total_timbre'] = format_amount


class AccountMove(models.Model):
    _inherit = "account.move"

    apply_timbre = fields.Boolean('Appliquer les droits de timbre?')
    timbre = fields.Monetary(string='Timbre', compute="_compute_amount", store=True, readonly=True, track_visibility='onchange')

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'apply_timbre',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        super(AccountMove, self)._compute_amount()

        def _compute_timbre(self,total_balance ):
            today_date = fields.Date.context_today(self)
            amount_timbre = abs(total_balance)
            if self.apply_timbre:
                timbre = self.env['config.timbre']._timbre(amount_timbre)
                amount_timbre = timbre['timbre']
                amount_timbre_total = timbre['amount_timbre']
            return (today_date, amount_timbre_total, amount_timbre)

        for record in self:
            if record.apply_timbre:
                date_now, total, timbre = _compute_timbre(record, record.amount_total_signed)
                sign = record.direction_sign * -1
                record.timbre = timbre * sign
                record.amount_total = record.amount_total + timbre
                record.amount_total_signed = record.amount_total_signed + record.timbre
                record.amount_total_in_currency_signed = abs(record.amount_total) if record.move_type == 'entry' else (sign * record.amount_total)
            else:
                record.timbre = 0

    def _recompute_timber_lines(self):
        def _get_timbre_account(self):
            ''' Get the account from timbre configuration pannel.
            :param self:                    The current account.move record.
            :return:                        An account.account record.
            '''

            # Search new account.
            domain = [
                ('name', '=', 'Calcul Timbre'),
            ]
            timbre_account = self.env['config.timbre'].search(domain).account_id
            timbre_account_purchase = self.env['config.timbre'].search(domain).account_id_purchase
            if self.move_type in ('in_invoice', 'in_refund'):
                timbre_account = timbre_account_purchase

            if not timbre_account and self.apply_timbre:
                raise ValidationError(
                    "Compte De Droit d’enregistrement n'est pas paramétré. \n Allez dans Facturation/Configuration/Configuration Timbre")
            return timbre_account
        for record in self:
            if not record.line_ids or not record._origin.id:
                continue
            timbre_line = record.line_ids.filtered(lambda line: line.istimbre is True)
            existing_terms_lines = record.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))
            if existing_terms_lines:
                existing_terms_lines = existing_terms_lines[0]
            else:
                continue
            if record.apply_timbre:
                if abs(record.timbre) > 0:
                    existing_terms_lines.with_context(check_move_validity=False).write({'balance': record.amount_total if existing_terms_lines.balance > 0 else - record.amount_total})
                    if timbre_line:
                        timbre_line.with_context(check_move_validity=False).write({'balance': abs(record.timbre) if existing_terms_lines.balance < 0 else -abs(record.timbre)})
                    else:
                        line_vals = {
                            'display_type': 'timbre',
                            'name': 'Timbre',
                            'move_id': record._origin.id,
                            'account_id': _get_timbre_account(record).id,
                            'balance': abs(record.timbre) if existing_terms_lines.balance < 0 else -abs(record.timbre),
                            'istimbre': True,
                            'date_maturity': False,
                            'partner_id': record.partner_id.id,
                            'company_id': record.company_id.id,
                            'currency_id': record.currency_id.id,
                            'company_currency_id': record.company_id.currency_id.id,
                        }
                        timbre_line = self.env['account.move.line'].with_context(check_move_validity=False).create(line_vals)


            if timbre_line and record.timbre == 0:
                existing_terms_lines.with_context(check_move_validity=False).write({'balance': record.amount_total if existing_terms_lines.balance > 0 else - record.amount_total})
                timbre_line.with_context(check_move_validity=False).unlink()

    @api.depends(
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'apply_timbre',
        'currency_id',
    )
    def _compute_tax_totals(self):
        def _compute_timbre(self, total_balance):
            today_date = fields.Date.context_today(self)
            amount_timbre = abs(total_balance)
            if self.apply_timbre:
                timbre = self.env['config.timbre']._timbre(amount_timbre)
                amount_timbre = timbre['timbre']
                amount_timbre_total = timbre['amount_timbre']
            return (today_date, amount_timbre_total, amount_timbre)

        super(AccountMove, self)._compute_tax_totals()
        for record in self:
            if record.apply_timbre:
                date_now, total, timbre = _compute_timbre(record, record.tax_totals['amount_total'])
                sign = record.direction_sign * -1
                record.timbre = timbre * sign
            if record.tax_totals:
                record.tax_totals['timbre'] = abs(record.timbre)
                record.tax_totals['amount_total_timbre'] = abs(record.tax_totals['amount_total'] + abs(record.timbre))
                format_amount = formatLang(self.env, abs(record.tax_totals['amount_total'] + abs(record.timbre)), currency_obj=record.currency_id),
                record.tax_totals['formatted_amount_total_timbre'] = format_amount

    @contextmanager
    def _sync_rounding_lines(self, container):
        yield
        for invoice in container['records']:
            invoice._recompute_cash_rounding_lines()
            invoice._recompute_timber_lines()

    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        if unbalanced_moves:
            error_msg = _("An error has occurred.")
            for move_id, sum_debit, sum_credit in unbalanced_moves:
                move = self.browse(move_id)
                if move.timbre or move.apply_timbre:
                    continue
                error_msg += _(
                    "\n\n"
                    "The move (%s) is not balanced.\n"
                    "The total of debits equals %s and the total of credits equals %s.\n"
                    "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
                    move.display_name,
                    format_amount(self.env, sum_debit, move.company_id.currency_id),
                    format_amount(self.env, sum_credit, move.company_id.currency_id),
                    move.journal_id.name)
            if '\n' in error_msg:
                raise UserError(error_msg)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    _order = "date desc, move_name desc, id"

    istimbre = fields.Boolean()
    display_type = fields.Selection(
        selection_add=[
            ('timbre', "Timbre"),
        ], ondelete={'timbre': 'cascade'})
