# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from datetime import  datetime
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    vat = fields.Char(readonly=False)
    nis = fields.Char(readonly=False)
    ai = fields.Char(readonly=False)
    code_activite = fields.Char(readonly=False)
    activite = fields.Char('Activité')
    company_registry = fields.Char(string="R.C", readonly=False)

    # G50
    tap_percentage = fields.Float("Pourcentage de TAP")
    tap_refaction = fields.Float("Pourcentage de rafaction de TAP")
    fait_generateur = fields.Selection([('paiement', 'Encaissement'), ('livraison', 'Facturation')], string="Fait génératuer", default="paiement")

    account_precompte = fields.Float('Précompte')
    account_tap_code = fields.Selection([('C 1 A 11', 'C 1 A 11'),
                                 ('C 1 A 12', 'C 1 A 12'),
                                 ('C 1 A 13', 'C 1 A 13'),
                                 ('C 1 A 14', 'C 1 A 14')]
                                , string="CODE TAP", default="C 1 A 12" )

    account_tva_code = fields.Selection(
        [('E 3 B 11', 'E 3 B 11'),
         ('E 3 B 12', 'E 3 B 12'),
         ('E 3 B 13', 'E 3 B 13'),
         ('E 3 B 14', 'E 3 B 14'),
         ('E 3 B 15', 'E 3 B 15'),
         ('E 3 B 16', 'E 3 B 16'),
         ('E 3 B 21', 'E 3 B 21'),
         ('E 3 B 22', 'E 3 B 22'),
         ('E 3 B 23', 'E 3 B 23'),
         ('E 3 B 24', 'E 3 B 24'),
         ('E 3 B 25', 'E 3 B 25'),
         ('E 3 B 26', 'E 3 B 26'),
         ('E 3 B 28', 'E 3 B 28'),
         ('E 3 B 31', 'E 3 B 31'),
         ('E 3 B 32', 'E 3 B 32'),
         ('E 3 B 33', 'E 3 B 33'),
         ('E 3 B 34', 'E 3 B 34'),
         ('E 3 B 35', 'E 3 B 35'),
         ('E 3 B 36', 'E 3 B 36'),
         ('E 3 B 37', 'E 3 B 37')], default="E 3 B 28", string="CODE TVA")

    account_tap_credit_account_id = fields.Many2one('account.account', string="Compte TAP crédit",  readonly=False)
    account_tap_debit_account_id = fields.Many2one('account.account', string="Compte TAP débit",  readonly=False)
    account_tva_credit_account_id = fields.Many2one('account.account', string="Compte crédit de TVA",  readonly=False)
    account_tva_debit_account_id = fields.Many2one('account.account', string="Compte TVA à décaisser",  readonly=False)
    account_percentage_ibs = fields.Float('IBS Pourcentage', readonly=False)
    account_ibs_credit_account_id = fields.Many2one('account.account', string="IBS Compte crédit", readonly=False)
    account_ibs_debit_account_id = fields.Many2one('account.account', string="IBS Compte débit", readonly=False)
    account_start_year_ibs = fields.Integer('Année début activité', readonly=False)
    capital = fields.Monetary(string='Capital social', currency_field='currency_id')
    account_irg_debit_account_id = fields.Many2one('account.account', string="Compte IRG", readonly=False)

    account_wilaya = fields.Char('Wilaya de', readonly=False)
    account_commune = fields.Char('Commune de', readonly=False)
    account_inspection = fields.Char('Inspection des impôts', readonly=False)
    account_recette = fields.Char('Recette des impôts', readonly=False)

