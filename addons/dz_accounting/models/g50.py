# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime,timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger(__name__)

MONTH_SELECTION = [
    ('01', 'Janvier'),
    ('02', 'Février'),
    ('03', 'Mars'),
    ('04', 'Avril'),
    ('05', 'Mai'),
    ('06', 'Juin'),
    ('07', 'Juillet'),
    ('08', 'Aout'),
    ('09', 'Septembre'),
    ('10', 'Octobre'),
    ('11', 'Novembre'),
    ('12', 'Decembre'),
]

class G50(models.Model):
    _name = "declaration.g50"
    _order = 'year desc,month desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nom')
    tap = fields.Float('TAP', track_visibility='always',)
    timbre = fields.Float('Droits de timbre', track_visibility='always',)
    ibs = fields.Float('IBS', track_visibility='always',)
    irg = fields.Float('IRG', track_visibility='always',)
    last_g50_tva = fields.Float('Précompte mois précédent')
    tva = fields.Float('TVA à payer', track_visibility='always',)
    tva_sale = fields.Float('TVA collectée', track_visibility='always',)
    tva_purchase = fields.Float('TVA déductible', track_visibility='always',)
    ca_imposable = fields.Float('C.A Imposable', track_visibility='always',)
    amount_total = fields.Float('Total à payer', track_visibility='always',)
    month = fields.Selection(MONTH_SELECTION, default=MONTH_SELECTION[date.today().month-1][0], required=True, string="Mois", track_visibility='always')
    year = fields.Char('Année', compute='compute_year', required=True, store=True)
    declaration_date = fields.Date("Date de déclaration", default=date.today())
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    exercice_id = fields.Many2one('account.exercice', 'Exercice comptable', track_visibility='always', required=True)
    posted_move_id = fields.Many2one('account.move', 'Pièce de déclaration G50', readonly=True, copy=False)
    paying_move_id = fields.Many2one('account.move', 'Pièce du paiement G50', readonly=True, copy=False)
    paying_account_id = fields.Many2one('account.account', 'Compte banque', readonly=False, copy=False)
    tva_line_ids = fields.Many2many('account.move.line', 'account_move_line_g50_tva', string='TVA Items', readonly=True)
    tap_line_ids = fields.Many2many('account.move.line', 'account_move_line_g50_tap', string='TAP Items', readonly=True)
    timbre_line_ids = fields.Many2many('account.move.line', 'account_move_line_g50_timbre', string='timbre Items', readonly=True)
    received_payment_ids = fields.Many2many('account.payment', 'account_payment_g50_recu', string='Paiements encaissés', readonly=False)
    sent_payment_ids = fields.Many2many('account.payment', 'account_payment_g50_send', string='Réglements effectués', readonly=False)
    payment_id = fields.Many2one('account.payment', string='Paiement')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('posted', 'Confirmé'),
        ('paid', 'Payé'),
        ('canceled', 'Annulé'),
    ], string="State", default='draft', track_visibility='always', compute="_compute_state", store=True, readonly=False)

    @api.constrains('exercice_id', 'month')
    def _check_month_unique(self):
        for record in self:
            records = self.env['declaration.g50'].search([('id', '!=', record.id), ('exercice_id', '=', record.exercice_id.id), ('month', '=', record.month)])
            if len(records):
                raise ValidationError("Le G50 de ce mois existe déja")


    @api.depends('exercice_id')
    def compute_year(self):
        for record in self:
            record.year = record.exercice_id.year

    @api.depends('posted_move_id.state')
    def _compute_state(self):
        for record in self:
            if record.posted_move_id and record.posted_move_id.state == 'posted':
                record.state = 'posted'
            else:
                record.state = record.state

    def get_account_balance(self, accounts,date_from=None,date_to=None,etat = None):
        if date_from:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),
                                                         ('date','<=',date_to),('date','>=',date_from),
                                                         ('account_id', 'in', accounts.mapped('id'))])
        else:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('date', '<=', date_to),
                                                             ('account_id', 'in', accounts.mapped('id'))])
        if str(etat) == 'C':
            return sum(line_ids.mapped('credit'))
        if str(etat) == 'D':
            return sum(line_ids.mapped('debit'))
        return sum(line_ids.mapped('balance'))

    def action_post(self):
        if self.posted_move_id and self.posted_move_id.state == 'posted':
            raise ValidationError("La declaration G50 de ce mois a été déjà comptabilisée")
        self.posted_move_id.name = '/'
        self.posted_move_id.unlink()
        name = "G50 " + str(self.month) + "/" + str(self.year)
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': fields.Date.today(),
            'journal_id': self.env['account.journal'].search([('type', '=', 'general')], limit=1).id,
            'ref': name
        })
        date_from = date.today().replace(day=1, month=int(self.month), year=int(self.year))
        last_g50_month = (date_from + timedelta(days=-1)).month
        last50_year = (date_from + timedelta(days=-1)).year
        last_g50 = self.env['declaration.g50'].search([('month', '=', MONTH_SELECTION[last_g50_month - 1][0]), ('year', '=', str(last50_year))])
        lines = []
        # ********************** TAP *************************
        tap = self.tap
        if tap:
            lines.append({
                'name': 'TAP ' + str(name),
                'move_id': move.id,
                'account_id': self.company_id.account_tap_debit_account_id.id,
                'debit': round(abs(tap), 2),
                'credit': 0,
                        })
            lines.append({
                'name': 'TAP ' + name,
                'move_id': move.id,
                'account_id': self.company_id.account_tap_credit_account_id.id,
                'debit': 0,
                'credit': round(abs(tap), 2),
            })
        # ********************* TVA **********************
        previous_precompte = abs(last_g50.tva) if last_g50 and last_g50.tva < 0 else 0

        #           **************** TVA Collectées ****************
        tva_collected_account = self.company_id.account_sale_tax_id.invoice_repartition_line_ids.mapped('account_id')
        if self.tva_sale >0:
            lines.append({
                'name': 'TVA Collectées ' + name,
                'move_id': move.id,
                'account_id': tva_collected_account.id,
                'debit': self.tva_sale,
                'credit': 0,
            })

#                    ********************* TVA déductibles *****************
        tva_paid_account = self.company_id.account_purchase_tax_id.invoice_repartition_line_ids.mapped('account_id')
        if self.tva_purchase > 0:
            lines.append({
                'name': 'TVA déductibles ' + name,
                'move_id': move.id,
                'account_id': tva_paid_account.id,
                'debit': 0,
                'credit': self.tva_purchase,
            })

        # ********************* TVA Précompte mois précédent **************
        if previous_precompte:
            lines.append({
                'name': 'Précompte mois précédent ' + name,
                'move_id': move.id,
                'account_id': self.company_id.account_tva_debit_account_id.id,
                'debit': 0,
                'credit': previous_precompte,
            })

        # ********************* Precompte ou TVA à payer **************
        lines.append({
            'name': ('Crédit de TVA' if self.tva < 0 else 'TVA à décaisser') + ' ' + name,
            'move_id': move.id,
            'account_id': self.company_id.account_tva_debit_account_id.id if self.tva < 0 else self.company_id.account_tva_credit_account_id.id,
            'debit': abs(self.tva) if self.tva < 0 else 0,
            'credit': self.tva if self.tva > 0 else 0,
        })

        # ********************* Precompte ou TVA à payer **************
        if self.ibs:
            lines.append({
                'name': 'IBS ' + name,
                'move_id': move.id,
                'account_id': self.company_id.account_ibs_credit_account_id.id,
                'debit': 0,
                'credit': self.ibs,
            })
            lines.append({
                'name': 'IBS ' + name,
                'move_id': move.id,
                'account_id': self.company_id.account_ibs_debit_account_id.id,
                'debit': self.ibs,
                'credit': 0,
            })

        move_lines = self.env['account.move.line'].create(lines)
        self.posted_move_id = move.id
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

    def action_register_payment(self):
        ctx = dict(self.env.context, g50_id=self.id, default_amount=self.amount_total, default_payment_type='outbound', default_journal_id=False, default_partner_type='supplier')

        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'context': ctx,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_draft(self):
        self.posted_move_id.filtered(lambda move: move.state == 'posted').button_draft()
        self.posted_move_id.with_context(force_delete=True).unlink()
        self.write({'state': 'draft'})

    def action_cancel(self):
        pass

    def action_calculate(self, imprimer=False):
        date_from = date.today().replace(day=1, month=int(self.month), year=int(self.year))
        date_to = (datetime.now().replace(day=1, month=int(self.month), year=int(self.year)) + relativedelta(months=+1, day=1, days=-1)).date()
        last_g50_month = (date_from + timedelta(days=-1)).month
        last50_year = (date_from + timedelta(days=-1)).year
        last_g50 = self.env['declaration.g50'].search([('month', '=', MONTH_SELECTION[last_g50_month - 1][0]), ('year' ,'=', str(last50_year))])
        first_g50 = self.env['declaration.g50'].search([], order="year,month asc", limit=1)
        if self.company_id.fait_generateur == 'paiement':
            return self.action_calculate_payments()
            fait_date = 'payment_date'
        else:
            fait_date = 'invoice_date'

        if len(last_g50) == 0 and self.id != first_g50.id:
            raise ValidationError(_('La déclaration du mois précédent est manquante !'))

        # ******************** TVA ********************
        tva_purchase = sum(self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and not move.is_sale_document_g50()).mapped('amount_tax'))
        tva_sale = sum(self.env['account.move'].search([('state', '=', 'posted'),  (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.is_sale_document_g50()).mapped('amount_tax'))
        ca_imposable = sum(self.env['account.move'].search([('state', '=', 'posted'),  (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.is_sale_document_g50()).mapped('amount_untaxed'))
        tva_purchase_excluded = sum(self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and not move.is_sale_document_g50() and move.timbre > 0 and move.amount_total > 100000).mapped('amount_tax'))
        tva_purchase = tva_purchase - tva_purchase_excluded
        last_g50_tva = 0 if last_g50.tva > 0 else abs(last_g50.tva)
        tva = tva_sale - tva_purchase - last_g50_tva

        # ******************** TAP ********************
        ca = sum(self.env['account.move'].search([('state', '=', 'posted'),  (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.is_sale_document_g50() and move.move_type != 'in_refund').mapped('amount_untaxed'))
        tap = ca * self.company_id.tap_percentage * 0.01 - (ca * self.company_id.tap_percentage * 0.01 * self.company_id.tap_refaction * 0.01)

        # # ******************** TIMBRE ********************
        timbre = sum(self.env['account.move'].search([('state', '=', 'posted'),  (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.is_sale_document_g50()).mapped('timbre'))

        # # ******************** IBS ********************
        ibs = 0
        if self.month in ['02', '05', '10']:
            if self.exercice_id.is_first:
                capital = self.company_id.capital
                ibs = capital * 0.30 * self.company_id.account_percentage_ibs * 0.01 * 0.05
            else:
                previous_exercice = self.exercice_id.previous_exercice_id
                second_previous_exercice = previous_exercice.previous_exercice_id if previous_exercice else False
                if previous_exercice.state == 'closed':
                    ibs = previous_exercice.resultat_impot * 0.30 * self.company_id.account_percentage_ibs * 0.01
                    ibs = 3000 if ibs < 0 else ibs
                elif second_previous_exercice:
                    ibs = second_previous_exercice.resultat_impot * 0.30 * self.company_id.account_percentage_ibs * 0.01
                    ibs = 3000 if ibs < 0 else ibs
                elif not second_previous_exercice:
                    capital = self.company_id.capital
                    ibs = capital * 0.30 * self.company_id.account_percentage_ibs * 0.01 * 0.05

        # # ******************** IRG ********************
        irg = 0
        irg_account = self.company_id.account_irg_debit_account_id.id or False
        line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),
                                                         ('date', '<=', date_to), ('date', '>=', date_from),
                                                         ('account_id', '=', irg_account)])
        irg = sum(line_ids.mapped('balance'))

        # TOTAL A PAYER
        amount_total = tap + timbre + ibs + irg + (tva if tva > 0 else 0)


        self.tva_purchase = tva_purchase
        self.tva_sale = tva_sale
        self.tap = tap
        self.ibs = ibs
        self.timbre = timbre
        self.irg = irg
        self.tva = tva
        self.amount_total = amount_total
        self.ca_imposable = ca_imposable
        self.last_g50_tva = -last_g50_tva

        tva_purchase_lines = self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and not move.is_sale_document_g50()).mapped('line_ids').filtered(lambda line: line.tax_base_amount > 0).mapped('id')
        tva_sale_lines = self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.is_sale_document_g50()).mapped('line_ids').filtered(lambda line: line.tax_base_amount > 0).mapped('id')
        tva_purchase_excluded_lines = self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and not move.is_sale_document_g50() and move.timbre > 0 and move.amount_total > 100000).mapped('line_ids').filtered(lambda line: line.tax_base_amount > 0).mapped('id')
        tap_sale_lines = self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.move_type != 'out_refund' and move.is_sale_document()).mapped('line_ids').filtered(lambda line:  line.display_type == 'product').mapped('id')
        tva_purchase_lines = [id for id in tva_purchase_lines if id not in tva_purchase_excluded_lines]
        timbre_lines = self.env['account.move'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from)]).filtered(lambda move: move.is_invoice() and move.is_sale_document_g50()).mapped('line_ids').filtered(lambda line: line.istimbre).mapped('id')

        self.tva_line_ids = [(6, 0, tva_purchase_lines + tva_sale_lines)]
        self.tap_line_ids = [(6, 0, tap_sale_lines)]
        self.timbre_line_ids = [(6, 0, timbre_lines)]

        return True

    def action_calculate_payments(self, imprimer=False):
        date_from = date.today().replace(day=1, month=int(self.month), year=int(self.year))
        date_to = (datetime.now().replace(day=1, month=int(self.month), year=int(self.year)) + relativedelta(months=+1, day=1, days=-1)).date()
        last_g50_month = (date_from + timedelta(days=-1)).month
        last50_year = (date_from + timedelta(days=-1)).year
        last_g50 = self.env['declaration.g50'].search([('month', '=', MONTH_SELECTION[last_g50_month - 1][0]), ('year' ,'=', str(last50_year))])
        first_g50 = self.env['declaration.g50'].search([], order="year,month asc", limit=1)
        if self.company_id.fait_generateur == 'paiement':
            fait_date = 'date'
        else:
            return

        if len(last_g50) == 0 and self.id != first_g50.id:
            raise ValidationError(_('La déclaration du mois précédent est manquante !'))

        # ******************** TVA ********************
        received_payments = self.env['account.payment'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from), ('partner_type', '=', 'customer'), ('is_internal_transfer', '=', False)])
        sent_payments = self.env['account.payment'].search([('state', '=', 'posted'), (fait_date, '<=', date_to), (fait_date, '>=', date_from),('partner_type', '=', 'supplier'), ('is_internal_transfer', '=', False)])
        sent_payments = sent_payments.filtered(lambda l: len(l.g50_ids) == 0)
        for record in received_payments + sent_payments:
            record.tva_percent = self.company_id.account_sale_tax_id.amount if self.company_id.account_sale_tax_id else 19
            record.tva_amount = record.amount * record.tva_percent * 0.01
            record.ca = record.amount - record.tva_amount
            record.tap_percent = self.company_id.tap_percentage if self.company_id.tap_percentage else 0
            record.tap_amount = record.amount * record.tap_percent * 0.01

        self.received_payment_ids = [(6, 0, received_payments.mapped('id'))]
        self.sent_payment_ids = [(6, 0, sent_payments.mapped('id'))]
        self.onchange_payement_lines()
        return True

    def onchange_payement_lines(self):
        date_from = date.today().replace(day=1, month=int(self.month), year=int(self.year))
        date_to = (datetime.now().replace(day=1, month=int(self.month), year=int(self.year)) + relativedelta(months=+1,
                                                                                                             day=1,
                                                                                                             days=-1)).date()
        last_g50_month = (date_from + timedelta(days=-1)).month
        last50_year = (date_from + timedelta(days=-1)).year
        last_g50 = self.env['declaration.g50'].search(
            [('month', '=', MONTH_SELECTION[last_g50_month - 1][0]), ('year', '=', str(last50_year))])
        first_g50 = self.env['declaration.g50'].search([], order="year,month asc", limit=1)
        tva_purchase = sum(self.sent_payment_ids.mapped('tva_amount'))
        tva_sale = sum(self.received_payment_ids.mapped('tva_amount'))
        ca_imposable = sum(self.received_payment_ids.mapped('amount')) - sum(
            self.received_payment_ids.mapped('tva_amount'))
        tva_purchase_excluded = 0
        tva_purchase = tva_purchase - tva_purchase_excluded
        last_g50_tva = 0 if last_g50.tva > 0 else abs(last_g50.tva)
        tva = tva_sale - tva_purchase - last_g50_tva

        # ******************** TAP ********************
        ca = ca_imposable
        tap = sum(self.received_payment_ids.mapped('tap_amount'))

        # # ******************** TIMBRE ********************
        timbre = 0

        # # ******************** IBS ********************
        ibs = 0
        if self.month in ['02', '05', '10']:
            if self.exercice_id.is_first:
                capital = self.company_id.capital
                ibs = capital * 0.30 * self.company_id.account_percentage_ibs * 0.01 * 0.05
            else:
                previous_exercice = self.exercice_id.previous_exercice_id
                second_previous_exercice = previous_exercice.previous_exercice_id if previous_exercice else False
                if previous_exercice.state == 'closed':
                    ibs = previous_exercice.resultat_impot * 0.30 * self.company_id.account_percentage_ibs * 0.01
                    ibs = 3000 if ibs < 0 else ibs
                elif second_previous_exercice:
                    ibs = second_previous_exercice.resultat_impot * 0.30 * self.company_id.account_percentage_ibs * 0.01
                    ibs = 3000 if ibs < 0 else ibs
                elif not second_previous_exercice:
                    capital = self.company_id.capital
                    ibs = capital * 0.30 * self.company_id.account_percentage_ibs * 0.01 * 0.05

        # # ******************** IRG ********************
        irg_account = self.company_id.account_irg_debit_account_id.id or False
        line_ids = self.env['account.move.line'].search(
            [('move_id.state', '=', 'posted'), ('date', '<=', date_to), ('date', '>=', date_from),
             ('account_id', '=', irg_account)])
        irg = sum(line_ids.mapped('balance'))

        # TOTAL A PAYER
        amount_total = tap + timbre + ibs + irg + (tva if tva > 0 else 0)

        self.tva_purchase = tva_purchase
        self.tva_sale = tva_sale
        self.tap = tap
        self.ibs = ibs
        self.timbre = timbre
        self.irg = irg
        self.tva = tva
        self.amount_total = amount_total
        self.ca_imposable = ca_imposable
        self.last_g50_tva = -last_g50_tva

        return True

    def name_get(self):
        result = []
        for record in self:
            name = "G-50 " + str(record.month) + "/" + str(record.year)
            result.append((record.id, name))
        return result


    def action_print(self):
        date_from = date.today().replace(day=1, month=int(self.month), year=int(self.year))
        date_to = (datetime.now().replace(day=1, month=int(self.month), year=int(self.year)) + relativedelta(months=+1, day=1, days=-1)).date()
        last_g50_month = (date_from + timedelta(days=-1)).month
        last50_year = (date_from + timedelta(days=-1)).year
        last_g50 = self.env['declaration.g50'].search([('month', '=', MONTH_SELECTION[last_g50_month - 1][0]), ('year', '=', str(last50_year))])
        first_g50 = self.env['declaration.g50'].search([], order="year,month asc", limit=1)

        if len(last_g50) == 0 and self.id != first_g50.id:
            raise ValidationError(_('La déclaration du mois précédent est manquante !'))


        state_description_values = {elem[0]: elem[1] for elem in self._fields['month']._description_selection(self.env)}
        data = {
            'ca_imposable': self.ca_imposable,
            'tap': self.tap,
            'ibs': self.ibs,
            'tva': 0 if self.tva < 0 else self.tva,
            'precompte': 0 if self.tva > 0 else abs(self.tva),
            'las_precompte': 0 if len(last_g50) == 0 or last_g50.tva > 0 else abs(last_g50.tva),
            'tva_sale': self.tva_sale,
            'tva_purchase': self.tva_purchase,
            'timbre': self.timbre,
            'refaction_30': 0,
            'no_refaction': self.ca_imposable,
            'amount_total': self.amount_total,
            self.company_id.account_tva_code.replace(' ', ''): [self.ca_imposable, self.tva_sale],
            self.company_id.account_tap_code: self.tap,
            'currency_id': self.company_id.currency_id,
            'nif': self.company_id.vat if self.company_id.vat else " ",
            'nis': self.company_id.nis if self.company_id.nis else " ",
            'ai': self.company_id.ai if self.company_id.ai else " ",
            'code_activite': self.company_id.code_activite if self.company_id.code_activite else " ",
            'company': self.company_id.name,
            'address': self.company_id.street + (self.company_id.city) + " " + (self.company_id.state_id.name if self.company_id.state_id else ''),
            'activity': self.company_id.activite,
            'year': str(self.year),
            'mois': state_description_values.get(self[:1].month).upper(),
            'semestre': state_description_values.get(self[:1].month).upper(),
            'wilaya': self.company_id.account_wilaya,
            'commune': self.company_id.account_commune,
            'recette': self.company_id.account_recette,
            'inspection': self.company_id.account_inspection,

        }

        return self.env.ref('dz_accounting.declaration_g_50_report_action').report_action(self, data=data)

    def unlink(self):
        if any(record.state not in ('draft', 'canceled') for record in self):
            raise UserError('Vous pouvez seulement supprimer les G50 brouillon.')
        return super(G50, self).unlink()
